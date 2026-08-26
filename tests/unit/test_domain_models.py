from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from strategic_intelligence.domain.models import (
    AnalysisItem, AuditEvent, Case, Claim, ClaimEvidenceLink, ClaimEvidenceRelationship,
    ClaimType, Company, Evidence, Executive, GovernanceDecision,
    GovernanceDecisionStatus, MeetingBrief, MeetingQuestion, Opportunity, QuickBrief,
    RawFinding, ResearchCategory, ResearchPlan, ResearchTask, Source, SourceQuality,
    SourceType, TargetType, UserContext, VerificationResult, VerificationStatus,
    WorkflowError, WorkflowErrorCode, WorkflowRun, WorkflowState,
)


def test_case_company_and_executive_use_stable_ids_and_aware_timestamps() -> None:
    company = Company(name="Example Co")
    executive = Executive(full_name="Ava Example", company_id=company.company_id)
    case = Case(company_id=company.company_id, executive_id=executive.executive_id, company_name=company.name, executive_name=executive.full_name, meeting_goal="Prepare")

    assert company.company_id != executive.executive_id
    assert case.created_at.tzinfo is not None
    assert case.updated_at.tzinfo is not None


def test_required_fields_and_unknown_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Company()
    with pytest.raises(ValidationError):
        Company(name="Example", vendor_client="not allowed")


def test_enum_and_non_negative_invariants_are_validated() -> None:
    with pytest.raises(ValidationError):
        ResearchTask(case_id="case", target_type="PERSON", category=ResearchCategory.NEWS, query="news", priority=1)
    with pytest.raises(ValidationError):
        ResearchTask(case_id="case", target_type=TargetType.COMPANY, category=ResearchCategory.NEWS, query="news", priority=-1)


def test_fact_and_inference_require_evidence_identifiers() -> None:
    with pytest.raises(ValidationError):
        Claim(case_id="case", text="A fact", claim_type=ClaimType.FACT, topic="strategy")
    claim = Claim(case_id="case", text="An inference", claim_type=ClaimType.INFERENCE, topic="strategy", evidence_ids=["evidence-1"])
    assert claim.evidence_ids == ["evidence-1"]


def test_source_evidence_claim_traceability_round_trips_as_json() -> None:
    source = Source(case_id="case", url="https://example.com", title="Announcement", source_type=SourceType.OFFICIAL_COMPANY, quality_class=SourceQuality.PRIMARY)
    evidence = Evidence(case_id="case", source_id=source.source_id, content="A relevant statement", topic="strategy", relevance="high")
    claim = Claim(case_id="case", text="Example has a strategy", claim_type=ClaimType.FACT, topic="strategy", evidence_ids=[evidence.evidence_id])
    link = ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id=evidence.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS)

    restored = Claim.model_validate_json(claim.model_dump_json())
    assert restored == claim
    assert link.evidence_id == evidence.evidence_id


def test_datetime_must_be_timezone_aware() -> None:
    with pytest.raises(ValidationError):
        Company(name="Example", created_at=datetime(2026, 1, 1), updated_at=datetime.now(timezone.utc))


def test_verification_governance_and_error_contracts_are_structured() -> None:
    verification = VerificationResult(claim_id="claim", status=VerificationStatus.SUPPORTED, source_quality=SourceQuality.PRIMARY, freshness_status="CURRENT", independent_source_count=1)
    governance = GovernanceDecision(case_id="case", target_type="claim", target_id="claim", decision=GovernanceDecisionStatus.RESTRICT)
    error = WorkflowError(case_id="case", component="research", error_code=WorkflowErrorCode.SEARCH_FAILED, message="unavailable")

    assert verification.claim_id == "claim"
    assert governance.decision is GovernanceDecisionStatus.RESTRICT
    assert error.retryable is False


def test_nested_research_plan_and_transient_workflow_state_are_serializable() -> None:
    task = ResearchTask(case_id="case", target_type=TargetType.COMPANY, category=ResearchCategory.STRATEGY, query="Example strategy", priority=1)
    plan = ResearchPlan(case_id="case", tasks=[task])
    state = WorkflowState(research_plan=plan)

    restored = WorkflowState.model_validate_json(state.model_dump_json())
    assert restored.research_plan is not None
    assert restored.research_plan.tasks[0].research_task_id == task.research_task_id


def test_remaining_contracts_have_json_compatible_typed_defaults() -> None:
    item = AnalysisItem(text="Relevant signal", type=ClaimType.INFERENCE, related_claim_ids=["claim"])
    opportunity = Opportunity(case_id="case", title="Opportunity", description="Potential fit", related_claim_ids=["claim"], relevance_to_goal="high")
    question = MeetingQuestion(case_id="case", question="How?", reason="Relevant", related_claim_ids=["claim"], priority=1)
    finding = RawFinding(case_id="case", research_task_id="task", source_url="https://example.com", title="Title", extracted_content="Content", topic="topic", relevance="high")
    brief = MeetingBrief(case_id="case", version=1, company_situation=[item], opportunity_map=[opportunity], questions=[question])
    quick = QuickBrief(case_id="case", key_signals=[item], top_opportunities=[opportunity], top_questions=[question])
    audit = AuditEvent(case_id="case", event_type="CASE_CREATED", component="case", status="ok", metadata={"attempt": 1})
    run = WorkflowRun(case_id="case")
    context = UserContext(case_id="case", capabilities=["research"])

    for model in (finding, brief, quick, audit, run, context):
        assert model.model_validate_json(model.model_dump_json()) == model
