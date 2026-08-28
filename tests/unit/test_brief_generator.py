from datetime import date

from strategic_intelligence.application.brief_generator import (
    BriefGenerationErrorCode,
    BriefGenerationStatus,
    BriefGeneratorService,
)
from strategic_intelligence.application.strategic_analysis import StrategicAnalysisStatus
from strategic_intelligence.domain.models import AnalysisItem, ClaimType, GovernanceReasonCode, StrategicAnalysis
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from tests.unit.test_strategic_analysis import AS_OF, _analysis, _case, _claim, _govern, _repository, _service


def test_critical_path_projects_real_c13_c15_governed_analysis_to_traceable_briefs(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    permitted = _claim(repository, case)
    restricted = _claim(repository, case, text="Example Co began an earlier programme.", published_at=date(2024, 1, 1))
    blocked = _claim(repository, case, text="Example Co acquired Acme.", evidence_text="Example Co opened a research lab.")
    _govern(repository, permitted)
    _govern(repository, restricted)
    _govern(repository, blocked)

    analysis = _service(repository, _analysis(case, permitted.claim_id)).analyze(case.case_id, as_of=AS_OF)
    result = BriefGeneratorService(repository).generate(case.case_id, analysis)

    assert analysis.status is StrategicAnalysisStatus.ACCEPTED
    assert result.status is BriefGenerationStatus.ACCEPTED
    assert result.quick_brief and result.full_brief
    assert permitted.claim_id in result.quick_brief.key_facts[0].related_claim_ids
    assert all(blocked.claim_id not in item.related_claim_ids for item in result.quick_brief.key_facts)
    assert any(item.is_restricted for item in result.quick_brief.knowledge_gaps)
    assert result.full_brief.source_references
    assert all("Acme" not in reference for reference in result.full_brief.source_references)


def test_brief_rejects_cross_case_analysis_and_unknown_provenance(tmp_path) -> None:
    repository = _repository(tmp_path)
    case_a = _case(repository, name="A")
    claim_a = _claim(repository, case_a)
    _govern(repository, claim_a)
    accepted = _service(repository, _analysis(case_a, claim_a.claim_id)).analyze(case_a.case_id, as_of=AS_OF)
    case_b = _case(repository, name="B")

    cross_case = BriefGeneratorService(repository).generate(case_b.case_id, accepted)
    unknown_analysis = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "company_direction": [AnalysisItem(text="Unknown", type=ClaimType.FACT, related_claim_ids=["missing"])],
    })})
    unknown = BriefGeneratorService(repository).generate(case_a.case_id, unknown_analysis)

    assert cross_case.status is BriefGenerationStatus.REJECTED
    assert cross_case.errors[0].code is BriefGenerationErrorCode.INVALID_ANALYSIS
    assert unknown.status is BriefGenerationStatus.REJECTED
    assert unknown.errors[0].code is BriefGenerationErrorCode.INVALID_PROVENANCE


def test_brief_rejects_empty_or_stale_c15_result(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    claim = _claim(repository, case)
    _govern(repository, claim)
    accepted = _service(repository, _analysis(case, claim.claim_id)).analyze(case.case_id, as_of=AS_OF)
    empty = accepted.model_copy(update={"analysis": StrategicAnalysis(case_id=case.case_id)})
    stale = _service(repository, _analysis(case, claim.claim_id)).analyze(case.case_id, as_of=date(2028, 8, 27))

    assert BriefGeneratorService(repository).generate(case.case_id, empty).errors[0].code is BriefGenerationErrorCode.NO_MEANINGFUL_CONTENT
    assert stale.status is StrategicAnalysisStatus.REJECTED
    assert BriefGeneratorService(repository).generate(case.case_id, stale).errors[0].code is BriefGenerationErrorCode.INVALID_ANALYSIS


def test_brief_rejects_fact_rewrite_and_removed_restriction_metadata(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    permitted = _claim(repository, case)
    restricted = _claim(repository, case, text="Example Co began an earlier programme.", published_at=date(2024, 1, 1))
    _govern(repository, permitted)
    _govern(repository, restricted)
    accepted = _service(repository, _analysis(case, permitted.claim_id)).analyze(case.case_id, as_of=AS_OF)

    rewritten = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "company_direction": [accepted.analysis.company_direction[0].model_copy(update={"text": "Example Co acquired Acme."})],
    })})
    restricted_gap = next(item for item in accepted.analysis.knowledge_gaps if item.is_restricted and item.related_claim_ids)
    unqualified = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "knowledge_gaps": [restricted_gap.model_copy(update={"is_restricted": False, "restriction_reason_codes": []})],
    })})

    assert BriefGeneratorService(repository).generate(case.case_id, rewritten).status is BriefGenerationStatus.REJECTED
    assert BriefGeneratorService(repository).generate(case.case_id, unqualified).status is BriefGenerationStatus.REJECTED


def test_brief_composition_preserves_traceability_after_repository_reload(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    claim = _claim(repository, case)
    _govern(repository, claim)
    repository.close()

    reopened = SqliteRepository(tmp_path / "analysis.sqlite")
    try:
        persisted_case = reopened.get_case(case.case_id)
        persisted_claim = reopened.get_claim(claim.claim_id)
        analysis = _service(reopened, _analysis(persisted_case, persisted_claim.claim_id)).analyze(persisted_case.case_id, as_of=AS_OF)
        result = BriefGeneratorService(reopened).generate(persisted_case.case_id, analysis)
    finally:
        reopened.close()

    assert result.status is BriefGenerationStatus.ACCEPTED
    assert result.full_brief and result.full_brief.source_references


def test_brief_accounts_for_its_own_gap_truncation_and_preserves_full_typed_gap_details(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    claim = _claim(repository, case, text="Example Co began an earlier programme.", published_at=date(2024, 1, 1))
    _govern(repository, claim)
    seed = _claim(repository, case)
    _govern(repository, seed)
    accepted = _service(repository, _analysis(case, seed.claim_id)).analyze(case.case_id, as_of=AS_OF)
    reasons = [GovernanceReasonCode.STALE_INFORMATION, GovernanceReasonCode.UNVERIFIED_FACT]
    gaps = [AnalysisItem(
        text=f"Gap {index}", type=ClaimType.INFERENCE, related_claim_ids=[claim.claim_id],
        rationale="Qualification", is_restricted=True, restriction_reason_codes=reasons,
    ) for index in range(6)]
    bounded = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "knowledge_gaps": gaps, "omitted_restriction_count": 3,
    })})

    result = BriefGeneratorService(repository).generate(case.case_id, bounded)

    assert result.status is BriefGenerationStatus.ACCEPTED
    assert result.quick_brief and len(result.quick_brief.knowledge_gaps) == 5
    assert result.quick_brief.omitted_knowledge_gap_count == 1
    assert result.quick_brief.omitted_restriction_count == 3
    assert result.full_brief and len(result.full_brief.knowledge_gap_details) == 6
    assert result.full_brief.knowledge_gap_details[0].restriction_reason_codes == reasons
    assert result.full_brief.knowledge_gap_details[0].is_restricted


def test_brief_rejects_oversized_or_duplicate_typed_analysis_input(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    claim = _claim(repository, case)
    _govern(repository, claim)
    accepted = _service(repository, _analysis(case, claim.claim_id)).analyze(case.case_id, as_of=AS_OF)
    base = accepted.analysis.company_direction[0]
    too_many = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "company_direction": [base] * 21,
    })})
    duplicate = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "company_direction": [base.model_copy(update={"related_claim_ids": [claim.claim_id, claim.claim_id]})],
    })})
    too_long = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "company_direction": [base.model_copy(update={"text": "x" * 2_001})],
    })})

    service = BriefGeneratorService(repository)
    assert service.generate(case.case_id, too_many).status is BriefGenerationStatus.REJECTED
    assert service.generate(case.case_id, duplicate).status is BriefGenerationStatus.REJECTED
    assert service.generate(case.case_id, too_long).status is BriefGenerationStatus.REJECTED
