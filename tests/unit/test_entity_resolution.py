from pathlib import Path

import pytest

from strategic_intelligence.application.entity_resolution import EntityResolutionService, ResolutionStatus, canonicalize_entity_label
from strategic_intelligence.domain.models import Case, Claim, ClaimEvidenceLink, ClaimEvidenceRelationship, ClaimType, EntityType, GovernanceDecision, GovernanceDecisionStatus, Evidence, Source, SourceType
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


def test_canonicalization_is_safe_and_type_isolated(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "entities.db")
    try:
        service = EntityResolutionService(repository)
        assert canonicalize_entity_label("  Telefonaktiebolaget  LM Ericsson ") == "telefonaktiebolaget lm ericsson"
        company = service.resolve(EntityType.COMPANY, "Acme")
        technology = service.resolve(EntityType.TECHNOLOGY, "Acme")
        project = service.resolve(EntityType.PROJECT, "Acme")
        event = service.resolve(EntityType.EVENT, "Acme")
        assert company.status is ResolutionStatus.CREATED
        assert technology.status is ResolutionStatus.CREATED
        assert project.status is event.status is ResolutionStatus.CREATED
        assert company.entity.entity_id != technology.entity.entity_id
    finally:
        repository.close()


def test_same_name_people_never_merge_without_context(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "entities.db")
    try:
        service = EntityResolutionService(repository)
        first = service.resolve(EntityType.PERSON, "Alex Smith", context_key="company-a")
        second = service.resolve(EntityType.PERSON, "Alex Smith", context_key="company-b")
        ambiguous = service.resolve(EntityType.PERSON, "Alex Smith")
        assert first.status is second.status is ResolutionStatus.CREATED
        assert first.entity.entity_id != second.entity.entity_id
        assert ambiguous.status is ResolutionStatus.AMBIGUOUS
    finally:
        repository.close()


def test_alias_reuse_requires_governed_support_and_preserves_id(tmp_path: Path) -> None:
    database = tmp_path / "entities.db"
    repository = SqliteRepository(database)
    service = EntityResolutionService(repository)
    created = service.resolve(EntityType.COMPANY, "Ericsson")
    case = repository.create_case(Case(case_id="case-1", company_id="company-1", executive_id="executive-1", company_name="Ericsson", executive_name="Ava", meeting_goal="Prepare"))
    source = repository.save_source(Source(case_id=case.case_id, url="https://example.test/ericsson", title="Ericsson", source_type=SourceType.OFFICIAL_COMPANY))
    evidence = repository.save_evidence(Evidence(case_id=case.case_id, source_id=source.source_id, content="Ericsson is Telefonaktiebolaget LM Ericsson.", topic="identity", relevance="high"))
    claim = Claim(case_id=case.case_id, text="Ericsson is Telefonaktiebolaget LM Ericsson.", claim_type=ClaimType.FACT, topic="identity", evidence_ids=[evidence.evidence_id])
    repository.save_claim_with_links(claim, [ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id=evidence.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS)])
    governance = repository.save_governance_decision(GovernanceDecision(case_id=case.case_id, target_type="claim", target_id=claim.claim_id, decision=GovernanceDecisionStatus.PASS))
    with pytest.raises(ValueError, match="governed Claim"):
        service.add_alias(
            created.entity.entity_id, "Telefonaktiebolaget LM Ericsson", context_key=None,
            supporting_claim_ids=["claim-1"], supporting_evidence_ids=["evidence-1"], governance_id="g1",
            governance_status=GovernanceDecisionStatus.PASS,
        )
    service.add_alias(
        created.entity.entity_id, "Telefonaktiebolaget LM Ericsson", context_key=None,
        supporting_claim_ids=[claim.claim_id], supporting_evidence_ids=[evidence.evidence_id], governance_id=governance.governance_id,
        governance_status=GovernanceDecisionStatus.PASS,
    )
    repository.close()

    reopened = SqliteRepository(database)
    try:
        resolved = EntityResolutionService(reopened).resolve(
            EntityType.COMPANY, "Telefonaktiebolaget LM Ericsson",
            supporting_claim_ids=[claim.claim_id], supporting_evidence_ids=[evidence.evidence_id],
            governance_id=governance.governance_id, governance_status=GovernanceDecisionStatus.PASS,
        )
        assert resolved.status is ResolutionStatus.RESOLVED
        assert resolved.entity.entity_id == created.entity.entity_id
    finally:
        reopened.close()


def test_unproven_alias_does_not_merge(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "entities.db")
    try:
        service = EntityResolutionService(repository)
        service.resolve(EntityType.PROJECT, "Atlas", context_key="company-a")
        result = service.resolve(EntityType.PROJECT, "Project Atlas", context_key="company-a")
        assert result.status is ResolutionStatus.CREATED
    finally:
        repository.close()
