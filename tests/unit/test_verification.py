from datetime import date
import json
from pathlib import Path

from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.verification import (
    VerificationAssessmentStatus,
    VerificationErrorCode,
    VerificationService,
)
from strategic_intelligence.domain.models import (
    Case,
    Claim,
    ClaimEvidenceLink,
    ClaimEvidenceRelationship,
    ClaimType,
    Evidence,
    FidelityStatus,
    RawFinding,
    Source,
    SourceQuality,
    SourceType,
    VerificationStatus,
)
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


AS_OF = date(2026, 8, 27)


def _persist_candidate(
    repository: SqliteRepository,
    *,
    claim_text: str,
    evidence_specs: list[tuple[str, ClaimEvidenceRelationship, SourceType, SourceQuality, date | None, str | None]],
    claim_type: ClaimType = ClaimType.FACT,
) -> Claim:
    case = repository.create_case(Case(company_id="company", executive_id="executive", company_name="Example Co", executive_name="Ava Example", meeting_goal="Prepare"))
    evidence_ids: list[str] = []
    links: list[ClaimEvidenceLink] = []
    for index, (content, relationship, source_type, quality, published, origin_source_id) in enumerate(evidence_specs):
        source = Source(
            case_id=case.case_id,
            url=f"https://example.com/source-{index}",
            title=f"Source {index}",
            source_type=source_type,
            quality_class=quality,
            publication_date=published,
            origin_source_id=origin_source_id,
        )
        evidence = Evidence(case_id=case.case_id, source_id=source.source_id, content=content, topic="strategy", relevance="high")
        repository.save_source(source)
        repository.save_evidence(evidence)
        evidence_ids.append(evidence.evidence_id)
        links.append(ClaimEvidenceLink(claim_id="pending", evidence_id=evidence.evidence_id, relationship_type=relationship))
    claim = Claim(case_id=case.case_id, text=claim_text, claim_type=claim_type, topic="strategy", evidence_ids=evidence_ids)
    repository.save_claim_with_links(claim, [link.model_copy(update={"claim_id": claim.claim_id}) for link in links])
    return claim


def test_critical_path_reads_real_c09_candidate_without_promoting_it(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    case = repository.create_case(Case(company_id="company", executive_id="executive", company_name="Example Co", executive_name="Ava Example", meeting_goal="Prepare"))
    result = EvidenceLayerService(repository).create_candidate(
        RawFinding(case_id=case.case_id, research_task_id="task", source_url="https://example.com/announcement", title="Announcement", extracted_content="Example Co opened a research lab.", topic="strategy", relevance="high"),
        claim_text="Example Co opened a research lab.",
        claim_type=ClaimType.FACT,
        relationship=ClaimEvidenceRelationship.SUPPORTS,
    )

    assert result.candidate_claim is not None
    assessment = VerificationService(repository).verify(result.candidate_claim.claim_id, as_of=AS_OF)

    assert assessment.status is VerificationAssessmentStatus.ACCEPTED
    assert assessment.fidelity_status is FidelityStatus.SUPPORTED_BY_EVIDENCE
    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.INSUFFICIENT_EVIDENCE
    assert repository.get_claim(result.candidate_claim.claim_id).verification_status is None


def test_primary_current_direct_support_is_verified(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
    ])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.VERIFIED
    assert assessment.verification.independent_source_count == 1


def test_only_fact_claims_can_enter_factual_verification(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    for claim_type in (ClaimType.INFERENCE, ClaimType.RECOMMENDATION):
        claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", claim_type=claim_type, evidence_specs=[
            ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
        ])
        assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)
        assert assessment.status is VerificationAssessmentStatus.REJECTED
        assert assessment.verification is None
        assert assessment.errors[0].code is VerificationErrorCode.INVALID_PROVENANCE


def test_independent_primary_and_secondary_confirmation_is_verified(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.BUSINESS_PUBLICATION, SourceQuality.STRONG_SECONDARY, date(2026, 8, 2), None),
    ])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.VERIFIED
    assert assessment.verification.independent_source_count == 2
    assert assessment.verification.duplicate_risk is False


def test_overstrong_candidate_is_not_promoted_by_available_evidence(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    claim = _persist_candidate(repository, claim_text="Example Co announced an AI partnership with Acme.", evidence_specs=[
        ("Example Co announced an AI partnership.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
    ])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.fidelity_status is FidelityStatus.PARTIALLY_SUPPORTED
    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.INSUFFICIENT_EVIDENCE


def test_non_supporting_evidence_is_not_promoted(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co announced a new hiring program.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
    ])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.fidelity_status is FidelityStatus.NOT_SUPPORTED
    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.INSUFFICIENT_EVIDENCE


def test_context_is_not_treated_as_support(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co discussed research priorities.", ClaimEvidenceRelationship.CONTEXT, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
    ])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.fidelity_status is FidelityStatus.AMBIGUOUS
    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.INSUFFICIENT_EVIDENCE


def test_contradictory_evidence_is_preserved_as_conflicting(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
        ("Example Co did not open a research lab.", ClaimEvidenceRelationship.CONTRADICTS, SourceType.BUSINESS_PUBLICATION, SourceQuality.STRONG_SECONDARY, date(2026, 8, 2), None),
    ])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.verification is not None
    assert assessment.verification.status is VerificationStatus.CONFLICTING
    assert assessment.verification.conflict_detected is True
    assert len(assessment.contradictory_evidence_ids) == 1


def test_stale_evidence_and_duplicate_origin_affect_judgment(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    stale = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2024, 1, 1), None),
    ])
    stale_assessment = VerificationService(repository).verify(stale.claim_id, as_of=AS_OF)
    assert stale_assessment.verification is not None
    assert stale_assessment.verification.status is VerificationStatus.STALE

    duplicate = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), "wire-1"),
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.BUSINESS_PUBLICATION, SourceQuality.STRONG_SECONDARY, date(2026, 8, 2), "wire-1"),
    ])
    duplicate_assessment = VerificationService(repository).verify(duplicate.claim_id, as_of=AS_OF)
    assert duplicate_assessment.verification is not None
    assert duplicate_assessment.verification.status is VerificationStatus.SUPPORTED
    assert duplicate_assessment.verification.duplicate_risk is True
    assert duplicate_assessment.verification.independent_source_count == 1


def test_missing_or_invalid_provenance_fails_closed(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    missing = VerificationService(repository).verify("missing", as_of=AS_OF)
    assert missing.status is VerificationAssessmentStatus.REJECTED
    assert missing.errors[0].code is VerificationErrorCode.MISSING_CLAIM

    claim = _persist_candidate(repository, claim_text="Example Co opened a research lab.", evidence_specs=[
        ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
    ])
    with repository._connection:
        repository._connection.execute("DELETE FROM claim_evidence_links WHERE claim_id = ?", (claim.claim_id,))
    invalid = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)
    assert invalid.status is VerificationAssessmentStatus.REJECTED
    assert invalid.errors[0].code is VerificationErrorCode.INVALID_PROVENANCE


def test_cross_case_evidence_cannot_verify_a_claim(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    first_case = repository.create_case(Case(company_id="company-1", executive_id="executive-1", company_name="First Co", executive_name="Ava First", meeting_goal="Prepare"))
    second_case = repository.create_case(Case(company_id="company-2", executive_id="executive-2", company_name="Second Co", executive_name="Ava Second", meeting_goal="Prepare"))
    source = repository.save_source(Source(case_id=second_case.case_id, url="https://example.com/second", title="Second", source_type=SourceType.OFFICIAL_COMPANY))
    evidence = repository.save_evidence(Evidence(case_id=second_case.case_id, source_id=source.source_id, content="First Co opened a research lab.", topic="strategy", relevance="high"))
    claim = Claim(case_id=first_case.case_id, text="First Co opened a research lab.", claim_type=ClaimType.FACT, topic="strategy", evidence_ids=[evidence.evidence_id])
    repository.save_claim_with_links(claim, [ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id=evidence.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS)])

    assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)

    assert assessment.status is VerificationAssessmentStatus.REJECTED
    assert assessment.errors[0].code is VerificationErrorCode.INVALID_PROVENANCE


def test_unusable_normalized_claim_text_fails_closed(tmp_path) -> None:
    repository = SqliteRepository(tmp_path / "case.db")
    for claim_text in ("!!!", "東京"):
        claim = _persist_candidate(repository, claim_text=claim_text, evidence_specs=[
            ("Example Co opened a research lab.", ClaimEvidenceRelationship.SUPPORTS, SourceType.OFFICIAL_COMPANY, SourceQuality.PRIMARY, date(2026, 8, 1), None),
        ])
        assessment = VerificationService(repository).verify(claim.claim_id, as_of=AS_OF)
        assert assessment.status is VerificationAssessmentStatus.REJECTED
        assert assessment.verification is None
        assert assessment.errors[0].code is VerificationErrorCode.INVALID_PROVENANCE


def test_labeled_c11_baseline_expected_results_match_actual_judgments(tmp_path) -> None:
    fixture = json.loads((Path(__file__).parents[2] / "evaluations" / "fixtures" / "c11_verification_baseline.json").read_text())
    for index, scenario in enumerate(fixture["cases"]):
        repository = SqliteRepository(tmp_path / f"baseline-{index}.db")
        if scenario.get("setup") == "MISSING_CLAIM":
            assessment = VerificationService(repository).verify("missing-baseline-claim", as_of=date.fromisoformat(fixture["as_of"]))
            assert assessment.status.value == scenario["expected_assessment"], scenario["label"]
            assert assessment.errors[0].code.value == scenario["expected_error"], scenario["label"]
            continue
        specs = [
            (
                item["content"],
                ClaimEvidenceRelationship(item["relationship"]),
                SourceType(item["source_type"]),
                SourceQuality.OTHER,
                date.fromisoformat(item["publication_date"]) if item["publication_date"] else None,
                item.get("origin_source_id"),
            )
            for item in scenario["evidence"]
        ]
        claim = _persist_candidate(repository, claim_text=scenario["claim_text"], evidence_specs=specs)
        if scenario.get("setup") == "MISSING_LINK":
            with repository._connection:
                repository._connection.execute("DELETE FROM claim_evidence_links WHERE claim_id = ?", (claim.claim_id,))
        assessment = VerificationService(repository).verify(claim.claim_id, as_of=date.fromisoformat(fixture["as_of"]))
        if scenario.get("setup") == "MISSING_LINK":
            assert assessment.status.value == scenario["expected_assessment"], scenario["label"]
            assert assessment.errors[0].code.value == scenario["expected_error"], scenario["label"]
            continue
        assert assessment.fidelity_status is FidelityStatus(scenario["expected_fidelity"]), scenario["label"]
        assert assessment.verification is not None
        assert assessment.verification.status is VerificationStatus(scenario["expected_verification"]), scenario["label"]
