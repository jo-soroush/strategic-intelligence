from datetime import date

from strategic_intelligence.application.brief_generator import (
    BriefGenerationErrorCode,
    BriefGenerationStatus,
    BriefGeneratorService,
)
from strategic_intelligence.application.strategic_analysis import StrategicAnalysisStatus
from strategic_intelligence.domain.models import (
    AnalysisItem,
    ClaimType,
    GovernanceReasonCode,
    MeetingQuestion,
    Opportunity,
    SourceType,
    StrategicAnalysis,
    WorkflowRun,
    WorkflowState,
)
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from tests.unit.test_strategic_analysis import AS_OF, _analysis, _case, _claim, _govern, _repository, _service


def _accepted_mixed_nested_analysis(tmp_path):
    repository = _repository(tmp_path)
    case = _case(repository)
    passed = _claim(repository, case, text="Example Co opened a current research lab.")
    restricted = _claim(repository, case, text="Example Co began a legacy programme.", published_at=date(2024, 1, 1))
    blocked = _claim(repository, case, text="Example Co acquired Acme.", evidence_text="Example Co opened a current research lab.")
    for claim in (passed, restricted, blocked):
        _govern(repository, claim)
    candidate = StrategicAnalysis(
        case_id=case.case_id,
        company_direction=[AnalysisItem(text=passed.text, type=ClaimType.FACT, related_claim_ids=[passed.claim_id])],
        opportunity_areas=[
            Opportunity(
                case_id=case.case_id, title="Current opportunity", description="Discuss the current lab.",
                related_claim_ids=[passed.claim_id], relevance_to_goal="meeting relevant",
            ),
            Opportunity(
                case_id=case.case_id, title="Qualified opportunity", description="Discuss the legacy programme carefully.",
                related_claim_ids=[passed.claim_id, restricted.claim_id], relevance_to_goal="meeting relevant",
            ),
        ],
        smart_questions=[
            MeetingQuestion(
                case_id=case.case_id, question="Which current lab priorities matter?", reason="The lab is current.",
                related_claim_ids=[passed.claim_id], priority=1,
            ),
            MeetingQuestion(
                case_id=case.case_id, question="How should the legacy programme be validated?", reason="It remains unresolved.",
                related_claim_ids=[restricted.claim_id], priority=2,
            ),
        ],
    )
    service = _service(repository, candidate)
    accepted = service.analyze(case.case_id, as_of=AS_OF)
    assert accepted.analysis is not None
    current = service.revalidate_current(case.case_id, accepted.analysis, as_of=AS_OF)
    assert current.status is StrategicAnalysisStatus.ACCEPTED
    return repository, case, passed, restricted, blocked, candidate, current


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


def test_current_c15_mixed_restricted_nested_items_generate_a_qualified_brief(tmp_path) -> None:
    repository, case, passed, restricted, _, _, current = _accepted_mixed_nested_analysis(tmp_path)

    result = BriefGeneratorService(repository).generate(case.case_id, current)

    assert result.status is BriefGenerationStatus.ACCEPTED
    assert result.full_brief and result.quick_brief
    opportunity = result.full_brief.opportunity_map[1]
    question = result.full_brief.questions[1]
    assert opportunity.related_claim_ids == [passed.claim_id, restricted.claim_id]
    assert opportunity.is_restricted is True
    assert opportunity.restriction_reason_codes
    assert question.related_claim_ids == [restricted.claim_id]
    assert question.is_restricted is True
    assert question.restriction_reason_codes == opportunity.restriction_reason_codes
    takeaways = result.full_brief.meeting_takeaways
    assert len(takeaways) <= BriefGeneratorService._MEETING_TAKEAWAY_LIMIT
    qualified_opportunity = next(item for item in takeaways if item.text == opportunity.title)
    qualified_question = next(item for item in takeaways if item.text == question.question)
    assert qualified_opportunity.supporting_claim_ids == opportunity.related_claim_ids
    assert qualified_opportunity.is_restricted is True
    assert qualified_opportunity.restriction_reason_codes == opportunity.restriction_reason_codes
    assert qualified_question.supporting_claim_ids == question.related_claim_ids
    assert qualified_question.is_restricted is True
    assert qualified_question.restriction_reason_codes == question.restriction_reason_codes
    assert result.full_brief.source_references


def test_meeting_takeaways_are_bounded_non_fact_projections_with_exact_provenance() -> None:
    analysis = StrategicAnalysis(
        case_id="case",
        executive_priorities=[AnalysisItem(text="Executive priority", type=ClaimType.INFERENCE, related_claim_ids=["claim-exec"])],
        strategic_signals=[AnalysisItem(text="Strategic signal", type=ClaimType.INFERENCE, related_claim_ids=["claim-signal"])],
        opportunity_areas=[Opportunity(
            case_id="case", title="Opportunity", description="Existing concise opportunity.",
            related_claim_ids=["claim-opportunity"], relevance_to_goal="Relevant",
        )],
        smart_questions=[MeetingQuestion(
            case_id="case", question="Question?", reason="Existing concise question.",
            related_claim_ids=["claim-question"], priority=1,
        )],
        risks=[
            AnalysisItem(text="Risk", type=ClaimType.INFERENCE, related_claim_ids=["claim-risk"]),
            AnalysisItem(text="Excluded sixth item", type=ClaimType.INFERENCE, related_claim_ids=["claim-six"]),
        ],
    )

    takeaways = BriefGeneratorService._meeting_takeaways(analysis)

    assert [item.text for item in takeaways] == [
        "Executive priority", "Strategic signal", "Opportunity", "Question?", "Risk",
    ]
    assert [item.supporting_claim_ids for item in takeaways] == [
        ["claim-exec"], ["claim-signal"], ["claim-opportunity"], ["claim-question"], ["claim-risk"],
    ]
    assert all(item.type is not ClaimType.FACT for item in takeaways)


def test_brief_rejects_invalid_nested_restriction_and_provenance_shapes(tmp_path) -> None:
    repository, case, _, restricted, blocked, _, current = _accepted_mixed_nested_analysis(tmp_path)
    assert current.analysis is not None
    qualified_opportunity = current.analysis.opportunity_areas[1]
    qualified_question = current.analysis.smart_questions[1]
    wrong_reason = (
        GovernanceReasonCode.UNVERIFIED_FACT
        if GovernanceReasonCode.UNVERIFIED_FACT not in qualified_question.restriction_reason_codes
        else GovernanceReasonCode.STALE_INFORMATION
    )
    service = BriefGeneratorService(repository)

    unqualified_opportunity = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "opportunity_areas": [qualified_opportunity.model_copy(update={"is_restricted": False, "restriction_reason_codes": []})],
    })})
    wrong_reason_question = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "smart_questions": [qualified_question.model_copy(update={"restriction_reason_codes": [wrong_reason]})],
    })})
    blocked_opportunity = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "opportunity_areas": [qualified_opportunity.model_copy(update={"related_claim_ids": [blocked.claim_id]})],
    })})
    blocked_question = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "smart_questions": [qualified_question.model_copy(update={"related_claim_ids": [blocked.claim_id]})],
    })})
    other_case = _case(repository, name="Other Co")
    other_claim = _claim(repository, other_case)
    _govern(repository, other_claim)
    wrong_case_opportunity = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "opportunity_areas": [qualified_opportunity.model_copy(update={"related_claim_ids": [other_claim.claim_id]})],
    })})
    unknown_question = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "smart_questions": [qualified_question.model_copy(update={"related_claim_ids": ["unknown-claim"]})],
    })})
    missing_question_provenance = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "smart_questions": [qualified_question.model_copy(update={"related_claim_ids": []})],
    })})

    for invalid in (
        unqualified_opportunity,
        wrong_reason_question,
        blocked_opportunity,
        blocked_question,
        wrong_case_opportunity,
        unknown_question,
        missing_question_provenance,
    ):
        result = service.generate(case.case_id, invalid)
        assert result.status is BriefGenerationStatus.REJECTED
        assert result.errors[0].code is BriefGenerationErrorCode.INVALID_PROVENANCE

    assert restricted.claim_id not in blocked_opportunity.analysis.opportunity_areas[0].related_claim_ids


def test_brief_preserves_multiple_authoritative_restriction_reasons_on_nested_items(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    passed = _claim(repository, case, text="Example Co opened a current research lab.")
    stale = _claim(repository, case, text="Example Co began a legacy programme.", published_at=date(2024, 1, 1))
    unresolved = _claim(repository, case, text="Example Co announced an unverified programme.", source_type=SourceType.OTHER)
    for claim in (passed, stale, unresolved):
        _govern(repository, claim)
    candidate = StrategicAnalysis(
        case_id=case.case_id,
        opportunity_areas=[Opportunity(
            case_id=case.case_id, title="Qualified opportunity", description="Discuss carefully.",
            related_claim_ids=[passed.claim_id, stale.claim_id, unresolved.claim_id], relevance_to_goal="meeting relevant",
        )],
        smart_questions=[MeetingQuestion(
            case_id=case.case_id, question="What needs validation?", reason="Restrictions remain.",
            related_claim_ids=[stale.claim_id, unresolved.claim_id], priority=1,
        )],
    )
    service = _service(repository, candidate)
    accepted = service.analyze(case.case_id, as_of=AS_OF)
    assert accepted.analysis is not None
    current = service.revalidate_current(case.case_id, accepted.analysis, as_of=AS_OF)

    result = BriefGeneratorService(repository).generate(case.case_id, current)

    assert result.status is BriefGenerationStatus.ACCEPTED
    expected = {GovernanceReasonCode.STALE_INFORMATION, GovernanceReasonCode.UNVERIFIED_FACT}
    assert set(result.full_brief.opportunity_map[0].restriction_reason_codes) == expected
    assert set(result.full_brief.questions[0].restriction_reason_codes) == expected


def test_c16_fact_fidelity_matches_c15_unicode_formatting_equivalence(tmp_path) -> None:
    repository = _repository(tmp_path)
    case = _case(repository)
    claim = _claim(repository, case, text="Café launches 产品。", evidence_text="Café launches 产品。")
    _govern(repository, claim)
    candidate = StrategicAnalysis(
        case_id=case.case_id,
        company_direction=[AnalysisItem(
            text="Cafe\u0301 launches 产品。", type=ClaimType.FACT, related_claim_ids=[claim.claim_id],
        )],
    )
    service = _service(repository, candidate)
    accepted = service.analyze(case.case_id, as_of=AS_OF)
    assert accepted.analysis is not None
    current = service.revalidate_current(case.case_id, accepted.analysis, as_of=AS_OF)

    assert current.status is StrategicAnalysisStatus.ACCEPTED
    assert BriefGeneratorService(repository).generate(case.case_id, current).status is BriefGenerationStatus.ACCEPTED

    changed = current.model_copy(update={"analysis": current.analysis.model_copy(update={
        "company_direction": [current.analysis.company_direction[0].model_copy(update={"text": "Café launches 收购。"})],
    })})
    assert BriefGeneratorService(repository).generate(case.case_id, changed).status is BriefGenerationStatus.REJECTED


def test_restricted_nested_items_survive_persistence_reload_before_c16(tmp_path) -> None:
    repository, case, _, _, _, candidate, current = _accepted_mixed_nested_analysis(tmp_path)
    assert current.analysis is not None
    run = repository.save_workflow_run(WorkflowRun(
        case_id=case.case_id,
        snapshot=WorkflowState(case_context=case, strategic_analysis=current.analysis),
    ))
    repository.close()

    reopened = SqliteRepository(tmp_path / "analysis.sqlite")
    try:
        persisted = reopened.get_workflow_run(run.run_id)
        assert persisted and persisted.snapshot and persisted.snapshot.strategic_analysis
        revalidated = _service(reopened, candidate).revalidate_current(
            case.case_id, persisted.snapshot.strategic_analysis, as_of=AS_OF,
        )
        result = BriefGeneratorService(reopened).generate(case.case_id, revalidated)
    finally:
        reopened.close()

    assert revalidated.status is StrategicAnalysisStatus.ACCEPTED
    assert result.status is BriefGenerationStatus.ACCEPTED


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
    too_long_inference = accepted.model_copy(update={"analysis": accepted.analysis.model_copy(update={
        "strategic_signals": [accepted.analysis.strategic_signals[0].model_copy(update={"text": "x" * 2_001})],
    })})

    service = BriefGeneratorService(repository)
    assert service.generate(case.case_id, too_many).status is BriefGenerationStatus.REJECTED
    assert service.generate(case.case_id, duplicate).status is BriefGenerationStatus.REJECTED
    assert service.generate(case.case_id, too_long).status is BriefGenerationStatus.REJECTED
    assert service.generate(case.case_id, too_long_inference).status is BriefGenerationStatus.REJECTED
