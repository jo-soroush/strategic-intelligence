import json
from datetime import date
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

from strategic_intelligence.application.brief_generator import BriefGenerationResult, BriefGenerationStatus
from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.config import Settings
from strategic_intelligence.domain.models import (
    AnalysisItem, Claim, ClaimType, GovernanceReasonCode, MeetingBrief, MeetingTakeaway, QuickBrief, ResearchCategory, WorkflowError, WorkflowErrorCode,
    WorkflowRun, WorkflowRunStatus, WorkflowStage, WorkflowState,
)
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult, WorkflowExecutionStatus
from strategic_intelligence.providers.contracts import LLMRequest, SearchResult
from strategic_intelligence.providers.factory import Providers
from strategic_intelligence.providers.fakes import FakeSearchProvider
from strategic_intelligence.ui.local_app import LocalUi, render_result


class _WorkflowBoundary:
    def __init__(self, result: WorkflowExecutionResult) -> None:
        self.result = result
        self.payloads: list[dict[str, str]] = []

    def execute(self, payload, *, as_of: date) -> WorkflowExecutionResult:
        self.payloads.append(dict(payload))
        return self.result


class _ComposedProvider:
    def generate(self, request: LLMRequest):
        raise AssertionError("structured generation is required")

    def generate_structured(self, request: LLMRequest, schema):
        if "TRUSTED_CONTEXT_JSON" not in request.prompt:
            return schema()
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        claim = context["claims"][0]
        return schema(
            company_direction=[AnalysisItem(
                text=claim["text"],
                type=ClaimType.FACT if claim["governance_decision"] == "PASS" else ClaimType.INFERENCE,
                related_claim_ids=[claim["claim_alias"]],
            )],
            strategic_signals=[AnalysisItem(text="A governed signal is available.", type=ClaimType.INFERENCE, related_claim_ids=[claim["claim_alias"]])],
        )


def _completed() -> WorkflowExecutionResult:
    restricted_gap = AnalysisItem(
        text="<gap>", type=ClaimType.INFERENCE, rationale="<qualification>", is_restricted=True,
    )
    quick = QuickBrief(
        case_id="case", key_facts=[AnalysisItem(text="<fact>", type=ClaimType.FACT)],
        knowledge_gaps=[restricted_gap], omitted_restriction_count=2, omitted_knowledge_gap_count=3,
    )
    full = MeetingBrief(
        case_id="case", version=1, executive_summary="<summary>", knowledge_gaps=["<gap>"],
        meeting_takeaways=[MeetingTakeaway(
            text="<takeaway>", type=ClaimType.INFERENCE, supporting_claim_ids=["claim"],
            rationale="<takeaway qualification>", is_restricted=True,
            restriction_reason_codes=[GovernanceReasonCode.UNVERIFIED_FACT],
        )],
        company_situation=[AnalysisItem(text="<detailed fact>", type=ClaimType.FACT)],
        knowledge_gap_details=[restricted_gap], do_not_assume=["<do not assume>"], source_references=["https://example.test/?q=<unsafe>"],
    )
    state = WorkflowState(current_stage=WorkflowStage.CASE_COMPLETED)
    run = WorkflowRun(case_id="case", status=WorkflowRunStatus.COMPLETED, current_stage=WorkflowStage.CASE_COMPLETED)
    return WorkflowExecutionResult(
        status=WorkflowExecutionStatus.COMPLETED, workflow_run=run, state=state,
        brief=BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=quick, full_brief=full),
    )


def _result(status: WorkflowExecutionStatus) -> WorkflowExecutionResult:
    error = WorkflowError(
        case_id="case", component="workflow", error_code=WorkflowErrorCode.WORKFLOW_FAILED,
        message="provider token=<secret>", stage=WorkflowStage.RESEARCH_COMPLETED,
    )
    run_status = WorkflowRunStatus.PARTIAL if status is WorkflowExecutionStatus.PARTIAL else WorkflowRunStatus.FAILED
    return WorkflowExecutionResult(
        status=status, workflow_run=WorkflowRun(case_id="case", status=run_status, current_stage=WorkflowStage.RESEARCH_COMPLETED),
        state=WorkflowState(current_stage=WorkflowStage.RESEARCH_COMPLETED), errors=[error],
    )


def _call(ui: LocalUi, *, method: str = "GET", values: dict[str, str] | None = None) -> tuple[str, str]:
    raw = urlencode(values or {}).encode()
    captured: dict[str, object] = {}
    body = ui({
        "REQUEST_METHOD": method, "CONTENT_LENGTH": str(len(raw)), "wsgi.input": BytesIO(raw),
    }, lambda status, headers: captured.update(status=status, headers=headers))
    return str(captured["status"]), b"".join(body).decode()


def _valid_form() -> dict[str, str]:
    return {
        "company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare",
        "company_website": "https://example.test", "company_country": "Sweden",
        "company_business_unit": "Consulting", "executive_linkedin_url": "https://www.linkedin.com/in/ava",
        "executive_current_title": "Director", "extra_context": "Context",
    }


def test_form_maps_supported_case_input_without_reimplementing_c05_validation() -> None:
    workflow = _WorkflowBoundary(_completed())
    status, page = _call(LocalUi(workflow), method="POST", values=_valid_form())

    assert status == "200 OK"
    assert workflow.payloads == [_valid_form()]
    assert "resume" not in page.casefold()


def test_entry_screen_has_branded_two_column_context_and_collapsed_support() -> None:
    status, page = _call(LocalUi(None), method="GET")

    assert status == "200 OK"
    assert "Strategic Intelligence" in page
    assert 'class="entry-layout"' in page and 'class="context-panel"' in page
    assert "Public-source research" in page
    assert "Governed evidence" in page
    assert "Meeting-ready insights" in page
    assert "Prepare brief" in page
    assert '<details class="form-support">' in page
    assert "Brief Preview" in page and "From research to ready." in page
    assert 'class="meeting-room-image"' in page
    assert "/assets/strategic-intelligence-meeting-room.webp" in page
    assert 'class="panel-overlay"' in page
    assert 'class="visual-orb"' not in page
    assert 'class="visual-nav"' in page
    assert 'class="visual-search"' in page
    for item in ("Home", "Library", "Insights", "Settings"):
        assert item in page
    for label in ("Meeting Brief", "What You Need to Know", "Executive Intelligence", "Strategic View", "Questions to Ask", "Knowledge Gaps"):
        assert label in page
    assert 'href="' not in page


def test_local_meeting_room_asset_is_served_as_a_static_local_asset() -> None:
    captured: dict[str, object] = {}
    body = LocalUi(None)({
        "REQUEST_METHOD": "GET",
        "PATH_INFO": "/assets/strategic-intelligence-meeting-room.webp",
    }, lambda status, headers: captured.update(status=status, headers=headers))

    assert captured["status"] == "200 OK"
    assert b"image/png" in str(captured["headers"]).encode()
    assert b"\x89PNG" in b"".join(body)


def test_completed_result_escapes_and_preserves_brief_trust_disclosures() -> None:
    page = render_result(_completed())
    default = page.split("<details", 1)[0]

    assert "Status: COMPLETED" in page
    assert "Meeting Snapshot" in default
    assert "What You Need to Know" in default
    assert "Executive Intelligence" in default
    assert "Strategic View" in default
    assert "Questions to Ask" in default
    assert "Knowledge Gaps" in default
    assert "Full Brief" in page
    assert "Key facts" not in default
    assert "&lt;fact&gt;" not in default
    assert "RESTRICTED:" in page
    assert "2 governed restriction(s)" in page and "3 knowledge gap(s)" in page
    assert "Do not assume" in page
    assert "Company situation" in page
    assert "&lt;detailed fact&gt;" in page
    assert "Sources" in page and "Provenance" in page and "Governance" in page
    assert ">-<" not in page
    assert "What You Need to Know" in page
    assert "Executive evidence is limited." in default
    assert "&lt;summary&gt;" in page and "&lt;unsafe&gt;" in page and "&lt;takeaway&gt;" in page
    assert "<unsafe>" not in page and "<takeaway>" not in page
    assert page.index("What You Need to Know") < page.index("Company situation")
    assert '<details class="disclosure">' in page
    assert '<details class="nested-disclosure">' in page
    assert page.index('<details class="disclosure">') > page.index("Executive Intelligence")
    assert 'class="brief-grid"' in page and 'class="status-pill"' in page


def test_partial_and_failed_results_render_only_typed_sanitized_error_fields() -> None:
    for status in (WorkflowExecutionStatus.PARTIAL, WorkflowExecutionStatus.FAILED):
        page = render_result(_result(status))
        assert f"Status: {status.value}" in page
        assert "WORKFLOW_FAILED" in page
        assert "RESEARCH_COMPLETED" in page
        assert "&lt;secret&gt;" not in page
        assert "provider token=[REDACTED]" in page


def test_form_accepts_missing_identity_support_for_c05_to_decide() -> None:
    workflow = _WorkflowBoundary(_result(WorkflowExecutionStatus.FAILED))
    values = {"company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare"}
    _call(LocalUi(workflow), method="POST", values=values)

    assert workflow.payloads == [values]


def test_local_request_uses_real_workflow_application_and_renders_typed_result(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    class _FixedDate:
        @staticmethod
        def today() -> date:
            return date(2026, 8, 27)

    monkeypatch.setattr("strategic_intelligence.ui.local_app.date", _FixedDate)
    settings = Settings(
        environment="test", log_level="INFO", data_dir=Path("data"), log_dir=Path("logs"),
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )
    workflow = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_ComposedProvider(), search=FakeSearchProvider(results=[SearchResult(
            title="Ava Example at Example Co", url="https://example.test/announcement",
            snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
        )]),
    ))
    try:
        status, page = _call(LocalUi(workflow), method="POST", values=_valid_form())
        assert status == "200 OK"
        assert "Status: COMPLETED" in page
        assert "Meeting Snapshot" in page and "Strategic View" in page
    finally:
        workflow.close()


def test_ui_module_depends_only_on_the_public_workflow_boundary_and_models() -> None:
    source = (Path(__file__).parents[2] / "src/strategic_intelligence/ui/local_app.py").read_text()
    for forbidden in (
        "sqlite_repository", "providers.factory", "WorkflowExecutor", "VerificationService",
        "FollowUpResearchService", "GovernanceService", "StrategicAnalysisService", "BriefGeneratorService", "brief_generator",
    ):
        assert forbidden not in source


def test_default_view_applies_approved_counts_and_display_only_text_clamp() -> None:
    long_text = "x" * 300
    completed = _completed()
    assert completed.brief is not None and completed.brief.quick_brief is not None and completed.brief.full_brief is not None
    quick = completed.brief.quick_brief.model_copy(update={
        "key_signals": [AnalysisItem(text=f"signal-{index}", type=ClaimType.INFERENCE) for index in range(5)],
        "top_opportunities": [completed.brief.quick_brief.top_opportunities[0]] * 3 if completed.brief.quick_brief.top_opportunities else [],
        "major_risks": [AnalysisItem(text=f"risk-{index}", type=ClaimType.INFERENCE) for index in range(4)],
        "top_questions": [],
        "knowledge_gaps": [AnalysisItem(text=f"gap-{index}", type=ClaimType.INFERENCE) for index in range(5)],
    })
    full = completed.brief.full_brief.model_copy(update={
        "meeting_takeaways": [MeetingTakeaway(text=long_text, type=ClaimType.INFERENCE, supporting_claim_ids=["claim"]) for _ in range(6)],
        "executive_intelligence": [AnalysisItem(text=f"executive-{index}", type=ClaimType.INFERENCE, related_claim_ids=[f"exec-{index}"]) for index in range(6)],
    })
    state = completed.state.model_copy(update={
        "claims": [Claim(claim_id=f"exec-{index}", case_id="case", text=f"executive-{index}", claim_type=ClaimType.RECOMMENDATION, topic=ResearchCategory.EXECUTIVE_ROLE.value) for index in range(6)],
    })
    result = completed.model_copy(update={
        "state": state,
        "brief": BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=quick, full_brief=full),
    })
    page = render_result(result)
    default = page.split("<details", 1)[0]

    assert default.count("signal-") == 3
    assert default.count("risk-") == 2
    assert default.count("executive-") == 5
    assert default.count("gap-") == 3
    assert default.count("…") >= 1
    assert long_text not in default
    assert long_text in page


def test_executive_card_filters_company_items_and_evidence_is_safe() -> None:
    completed = _completed()
    assert completed.brief is not None and completed.brief.full_brief is not None
    executive = AnalysisItem(text="Executive role evidence", type=ClaimType.FACT, related_claim_ids=["exec-claim"])
    company = AnalysisItem(text="General AI activity", type=ClaimType.FACT, related_claim_ids=["company-claim"])
    full = completed.brief.full_brief.model_copy(update={
        "executive_intelligence": [executive, company],
        "source_references": ["-", "https://example.test/executive"],
    })
    state = completed.state.model_copy(update={
        "claims": [
            Claim(claim_id="exec-claim", case_id="case", text="Executive role evidence", claim_type=ClaimType.RECOMMENDATION, topic=ResearchCategory.EXECUTIVE_ROLE.value),
            Claim(claim_id="company-claim", case_id="case", text="General AI activity", claim_type=ClaimType.RECOMMENDATION, topic=ResearchCategory.AI_ACTIVITY.value),
        ],
    })
    page = render_result(completed.model_copy(update={
        "state": state,
        "brief": BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=completed.brief.quick_brief, full_brief=full),
    }))
    default = page.split("<details", 1)[0]

    assert "Executive role evidence" in default
    assert "General AI activity" not in default
    assert "Executive evidence is limited." not in default
    assert "https://example.test/executive" in page
    assert "Claim reference: exec-claim" in page
    assert ">-<" not in page
