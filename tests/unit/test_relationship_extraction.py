from datetime import datetime, timedelta, timezone
from pathlib import Path

from strategic_intelligence.application.relationship_extraction import GovernedRelationshipExtractor, RelationshipExtractionStatus
from strategic_intelligence.domain.models import (
    Case,
    Claim,
    ClaimEvidenceLink,
    ClaimEvidenceRelationship,
    ClaimType,
    EntityRecord,
    EntityType,
    Evidence,
    FidelityStatus,
    FreshnessStatus,
    GovernanceDecision,
    GovernanceDecisionStatus,
    RelationshipTemporalStatus,
    RelationshipType,
    Source,
    SourceQuality,
    SourceType,
    VerificationResult,
    VerificationStatus,
    WorkflowRun,
    WorkflowRunStatus,
    WorkflowStage,
    WorkflowState,
)
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


def _fixture(tmp_path: Path, *, decision=GovernanceDecisionStatus.PASS, verification=VerificationStatus.VERIFIED):
    repository = SqliteRepository(tmp_path / "relationships.db")
    case = repository.create_case(Case(case_id="case-1", company_id="co-1", executive_id="ex-1", company_name="Acme", executive_name="Ava", meeting_goal="Prepare"))
    person = repository.save_entity(EntityRecord(entity_id="person-1", entity_type=EntityType.PERSON, canonical_name="Ava", normalized_name="ava"))
    company = repository.save_entity(EntityRecord(entity_id="company-1", entity_type=EntityType.COMPANY, canonical_name="Acme", normalized_name="acme"))
    source = repository.save_source(Source(source_id="source-1", case_id=case.case_id, url="https://example.test/claim", title="Claim source", source_type=SourceType.BUSINESS_PUBLICATION))
    evidence = repository.save_evidence(Evidence(evidence_id="evidence-1", case_id=case.case_id, source_id=source.source_id, content="Ava leads Acme.", topic="leadership", relevance="high"))
    claim = Claim(claim_id="claim-1", case_id=case.case_id, text="Ava leads Acme.", claim_type=ClaimType.FACT, topic="leadership", evidence_ids=[evidence.evidence_id])
    repository.save_claim_with_links(claim, [ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id=evidence.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS)])
    result = VerificationResult(claim_id=claim.claim_id, fidelity_status=FidelityStatus.SUPPORTED_BY_EVIDENCE, status=verification, source_quality=SourceQuality.PRIMARY, freshness_status=FreshnessStatus.CURRENT, independent_source_count=1, conflict_detected=verification is VerificationStatus.CONFLICTING)
    run = WorkflowRun(run_id="run-1", case_id=case.case_id, status=WorkflowRunStatus.COMPLETED, current_stage=WorkflowStage.VERIFICATION_COMPLETED, snapshot=WorkflowState(case_context=case, claims=[claim], evidence=[evidence], sources=[source], verification_results=[result]))
    repository.save_workflow_run(run)
    repository.save_governance_decision(GovernanceDecision(governance_id="governance-1", case_id=case.case_id, target_type="claim", target_id=claim.claim_id, decision=decision))
    return repository, person, company, claim, evidence


def test_extracts_only_governed_supported_relationships(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _fixture(tmp_path)
    try:
        result = GovernedRelationshipExtractor(repository).extract(RelationshipType.LEADS, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1")
        assert result.status is RelationshipExtractionStatus.ACCEPTED
        assert result.relationship is not None
        assert result.relationship.usable is True
        assert result.relationship.temporal_status is RelationshipTemporalStatus.CURRENT
        assert result.relationship.source_ids == ["source-1"]
    finally:
        repository.close()


def test_rejects_unsupported_pairs_and_missing_or_cross_run_proof(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _fixture(tmp_path)
    try:
        extractor = GovernedRelationshipExtractor(repository)
        assert extractor.extract(RelationshipType.USES, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1").status is RelationshipExtractionStatus.REJECTED
        assert extractor.extract(RelationshipType.LEADS, person.entity_id, company.entity_id, ["forged"], [evidence.evidence_id], "run-1").status is RelationshipExtractionStatus.REJECTED
        assert extractor.extract(RelationshipType.LEADS, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "missing-run").status is RelationshipExtractionStatus.REJECTED
    finally:
        repository.close()


def test_block_is_rejected_restrict_is_qualified_and_temporal_states_are_not_usable(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _fixture(tmp_path, decision=GovernanceDecisionStatus.RESTRICT, verification=VerificationStatus.STALE)
    try:
        result = GovernedRelationshipExtractor(repository).extract(RelationshipType.LEADS, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1")
        assert result.status is RelationshipExtractionStatus.ACCEPTED
        assert result.relationship is not None
        assert result.relationship.usable is False
        assert result.relationship.governance_status is GovernanceDecisionStatus.RESTRICT
        assert result.relationship.temporal_status is RelationshipTemporalStatus.STALE
        repository.save_governance_decision(GovernanceDecision(case_id="case-1", target_type="claim", target_id=claim.claim_id, decision=GovernanceDecisionStatus.BLOCK))
        assert GovernedRelationshipExtractor(repository).extract(RelationshipType.LEADS, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1").status is RelationshipExtractionStatus.REJECTED
    finally:
        repository.close()


def test_conflicting_and_superseded_relationships_remain_history_but_not_usable(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _fixture(tmp_path, verification=VerificationStatus.CONFLICTING)
    try:
        extractor = GovernedRelationshipExtractor(repository)
        conflict = extractor.extract(RelationshipType.LEADS, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1")
        assert conflict.relationship is not None
        assert conflict.relationship.temporal_status is RelationshipTemporalStatus.CONFLICTING
        assert conflict.relationship.usable is False
        repository.close()
        repository, person, company, claim, evidence = _fixture(tmp_path / "second", verification=VerificationStatus.VERIFIED)
        superseded = GovernedRelationshipExtractor(repository).extract(RelationshipType.LEADS, person.entity_id, company.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1", superseded_by="relationship-new")
        assert superseded.relationship is not None
        assert superseded.relationship.temporal_status is RelationshipTemporalStatus.SUPERSEDED
        assert superseded.relationship.usable is False
    finally:
        repository.close()


def test_partnered_with_is_canonically_ordered(tmp_path: Path) -> None:
    repository, _, company, claim, evidence = _fixture(tmp_path)
    other = repository.save_entity(EntityRecord(entity_id="company-0", entity_type=EntityType.COMPANY, canonical_name="Beta", normalized_name="beta"))
    try:
        result = GovernedRelationshipExtractor(repository).extract(RelationshipType.PARTNERED_WITH, company.entity_id, other.entity_id, [claim.claim_id], [evidence.evidence_id], "run-1")
        assert result.relationship is not None
        assert (result.relationship.source_entity_id, result.relationship.target_entity_id) == ("company-0", "company-1")
    finally:
        repository.close()
