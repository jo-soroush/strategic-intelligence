from datetime import date

import pytest

from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.domain.models import (
    Case, Claim, ClaimEvidenceLink, ClaimEvidenceRelationship, ClaimType, Evidence,
    FollowUpResearchStatus, GovernanceDecisionStatus, GovernanceReasonCode,
    ResearchCategory, ResearchTask, Source, SourceQuality, SourceType, TargetType,
)
from strategic_intelligence.governance.engine import GovernanceAssessmentStatus, GovernanceService
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.providers.contracts import SearchResult
from strategic_intelligence.providers.fakes import FakeSearchProvider


AS_OF = date(2026, 8, 27)


def _persist_claim(
    repository: SqliteRepository,
    *,
    claim_type: ClaimType = ClaimType.FACT,
    claim_text: str = "Example Co opened a research lab.",
    evidence_specs: list[tuple[str, ClaimEvidenceRelationship, SourceType, date | None]] | None = None,
) -> tuple[Case, Claim]:
    case = repository.create_case(Case(
        company_id="company", executive_id="executive", company_name="Example Co",
        executive_name="Ava Example", meeting_goal="Prepare",
    ))
    specs = evidence_specs if evidence_specs is not None else [
        (claim_text, ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, date(2026, 8, 1)),
    ]
    evidence_ids: list[str] = []
    links: list[ClaimEvidenceLink] = []
    for index, (content, relationship, source_type, published_at) in enumerate(specs):
        source = repository.save_source(Source(
            case_id=case.case_id, url=f"https://example.test/{index}", title=f"Source {index}",
            source_type=source_type, quality_class=SourceQuality.OTHER,
            publication_date=published_at,
        ))
        evidence = repository.save_evidence(Evidence(
            case_id=case.case_id, source_id=source.source_id, content=content,
            topic="strategy", relevance="high", publication_date=published_at,
        ))
        evidence_ids.append(evidence.evidence_id)
        links.append(ClaimEvidenceLink(
            claim_id="pending", evidence_id=evidence.evidence_id, relationship_type=relationship,
        ))
    claim = Claim(
        case_id=case.case_id, text=claim_text, claim_type=claim_type, topic="strategy",
        evidence_ids=evidence_ids,
    )
    repository.save_claim_with_links(claim, [link.model_copy(update={"claim_id": claim.claim_id}) for link in links])
    return case, claim


def _service(repository: SqliteRepository) -> GovernanceService:
    return GovernanceService(repository, VerificationService(repository))


def test_critical_path_governs_real_c12_resolved_claim_and_persists_decision(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    case = repository.create_case(Case(
        company_id="company", executive_id="executive", company_name="Example Co",
        executive_name="Ava Example", meeting_goal="Prepare", company_website="https://example.com",
    ))
    source = repository.save_source(Source(
        case_id=case.case_id, url="https://other.example/old", title="Old source",
        source_type=SourceType.OTHER, quality_class=SourceQuality.OTHER,
        publication_date=date(2026, 8, 1),
    ))
    evidence = repository.save_evidence(Evidence(
        case_id=case.case_id, source_id=source.source_id, content="Example Co opened a research lab.",
        topic="strategy", relevance="high", publication_date=date(2026, 8, 1),
    ))
    claim = Claim(
        case_id=case.case_id, text="Example Co opened a research lab.", claim_type=ClaimType.FACT,
        topic="strategy", evidence_ids=[evidence.evidence_id],
    )
    repository.save_claim_with_links(claim, [ClaimEvidenceLink(
        claim_id=claim.claim_id, evidence_id=evidence.evidence_id,
        relationship_type=ClaimEvidenceRelationship.SUPPORTS,
    )])
    task = ResearchTask(
        case_id=case.case_id, target_type=TargetType.COMPANY, category=ResearchCategory.NEWS,
        query="Example Co research lab", priority=1, max_attempts=2,
    )
    research = CompanyResearchService(FakeSearchProvider(results=[SearchResult(
        title="Example Co research lab", url="https://example.com/current",
        snippet="Example Co opened a research lab.", publisher="Example Co",
        published_at=date(2026, 8, 20),
    )]))
    follow_up = FollowUpResearchService(repository, EvidenceLayerService(repository), VerificationService(repository)).run(
        case, claim.claim_id, task, lambda current_case, current_task: research.research(current_case, current_task).findings,
        as_of=AS_OF,
    )
    assessment = _service(repository).evaluate(claim.claim_id, as_of=AS_OF)

    assert follow_up.status is FollowUpResearchStatus.RESOLVED
    assert assessment.status is GovernanceAssessmentStatus.ACCEPTED
    assert assessment.decision is not None
    assert assessment.decision.decision is GovernanceDecisionStatus.PASS
    assert repository.list_governance_decisions(claim.claim_id) == [assessment.decision]


@pytest.mark.parametrize(
    ("specs", "reason"),
    [
        ([("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, date(2024, 1, 1))], GovernanceReasonCode.STALE_INFORMATION),
        ([
            ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, date(2026, 8, 1)),
            ("Example Co did not open a research lab.", ClaimEvidenceRelationship.CONTRADICTS, SourceType.BUSINESS_PUBLICATION, date(2026, 8, 2)),
        ], GovernanceReasonCode.CONFLICTING_EVIDENCE),
    ],
)
def test_stale_and_conflicting_facts_are_restricted_with_visible_reason(tmp_path, specs, reason) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    _, claim = _persist_claim(repository, evidence_specs=specs)

    assessment = _service(repository).evaluate(claim.claim_id, as_of=AS_OF)

    assert assessment.decision is not None
    assert assessment.decision.decision is GovernanceDecisionStatus.RESTRICT
    assert assessment.decision.reason_codes == [reason]


def test_unsupported_and_untraceable_facts_are_blocked(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    _, unsupported = _persist_claim(repository, evidence_specs=[
        ("Example Co announced a hiring program.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, date(2026, 8, 1)),
    ])
    unsupported_assessment = _service(repository).evaluate(unsupported.claim_id, as_of=AS_OF)
    assert unsupported_assessment.decision is not None
    assert unsupported_assessment.decision.decision is GovernanceDecisionStatus.BLOCK
    assert unsupported_assessment.decision.reason_codes == [GovernanceReasonCode.UNVERIFIED_FACT]

    _, untraceable = _persist_claim(repository)
    with repository._connection:
        repository._connection.execute("DELETE FROM claim_evidence_links WHERE claim_id = ?", (untraceable.claim_id,))
    untraceable_assessment = _service(repository).evaluate(untraceable.claim_id, as_of=AS_OF)
    assert untraceable_assessment.decision is not None
    assert untraceable_assessment.decision.decision is GovernanceDecisionStatus.BLOCK
    assert untraceable_assessment.decision.reason_codes == [GovernanceReasonCode.UNTRACEABLE_CLAIM]


def test_missing_evidence_fails_closed_and_evidence_without_source_is_blocked(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    _, missing_evidence = _persist_claim(repository)
    missing_payload = missing_evidence.model_copy(update={"evidence_ids": []})
    with repository._connection:
        repository._connection.execute(
            "UPDATE claims SET payload = ? WHERE id = ?", (repository._dump(missing_payload), missing_evidence.claim_id),
        )
    missing_assessment = _service(repository).evaluate(missing_evidence.claim_id, as_of=AS_OF)
    assert missing_assessment.status is GovernanceAssessmentStatus.REJECTED
    assert missing_assessment.decision is None

    _, source_missing = _persist_claim(repository)
    evidence = repository.get_evidence(source_missing.evidence_ids[0])
    repository._connection.execute("PRAGMA foreign_keys = OFF")
    repository._connection.execute("DELETE FROM sources WHERE id = ?", (evidence.source_id,))
    repository._connection.commit()
    repository._connection.execute("PRAGMA foreign_keys = ON")
    source_assessment = _service(repository).evaluate(source_missing.claim_id, as_of=AS_OF)
    assert source_assessment.decision is not None
    assert source_assessment.decision.decision is GovernanceDecisionStatus.BLOCK
    assert source_assessment.decision.reason_codes == [GovernanceReasonCode.UNTRACEABLE_CLAIM]


def test_inference_and_recommendation_remain_non_factual_and_qualified(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    _, inference = _persist_claim(repository, claim_type=ClaimType.INFERENCE)
    _, recommendation = _persist_claim(repository, claim_type=ClaimType.RECOMMENDATION, evidence_specs=[])

    inference_assessment = _service(repository).evaluate(inference.claim_id, as_of=AS_OF)
    recommendation_assessment = _service(repository).evaluate(recommendation.claim_id, as_of=AS_OF)

    assert inference_assessment.decision is not None
    assert inference_assessment.decision.decision is GovernanceDecisionStatus.RESTRICT
    assert inference_assessment.decision.reason_codes == [GovernanceReasonCode.INFERENCE_REQUIRES_QUALIFICATION]
    assert recommendation_assessment.decision is not None
    assert recommendation_assessment.decision.decision is GovernanceDecisionStatus.RESTRICT
    assert recommendation_assessment.decision.reason_codes == [GovernanceReasonCode.RECOMMENDATION_REQUIRES_QUALIFICATION]
    assert repository.get_claim(inference.claim_id).claim_type is ClaimType.INFERENCE
    assert repository.get_claim(recommendation.claim_id).claim_type is ClaimType.RECOMMENDATION


def test_private_personal_information_is_blocked_before_final_use(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    _, claim = _persist_claim(repository, claim_text="Ava's personal phone is 555 123 4567.")

    assessment = _service(repository).evaluate(claim.claim_id, as_of=AS_OF)

    assert assessment.decision is not None
    assert assessment.decision.decision is GovernanceDecisionStatus.BLOCK
    assert assessment.decision.reason_codes == [GovernanceReasonCode.PRIVACY_BOUNDARY]


def test_repeated_evaluation_is_deterministic_and_auditable(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "governance.sqlite")
    _, claim = _persist_claim(repository, evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OTHER, date(2026, 8, 1)),
    ])

    first = _service(repository).evaluate(claim.claim_id, as_of=AS_OF)
    second = _service(repository).evaluate(claim.claim_id, as_of=AS_OF)

    assert first.decision is not None and second.decision is not None
    assert first.decision.decision is second.decision.decision is GovernanceDecisionStatus.RESTRICT
    assert first.decision.reason_codes == second.decision.reason_codes == [GovernanceReasonCode.UNVERIFIED_FACT]
    assert len(repository.list_governance_decisions(claim.claim_id)) == 2
