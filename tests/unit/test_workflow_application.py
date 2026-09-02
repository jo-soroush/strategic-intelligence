import json
from datetime import date
from pathlib import Path

from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.config import Settings
from strategic_intelligence.domain.models import AnalysisItem, ClaimType, WorkflowStage
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult, WorkflowExecutionStatus
from strategic_intelligence.providers.contracts import LLMRequest, SearchResult
from strategic_intelligence.providers.factory import Providers
from strategic_intelligence.providers.fakes import FakeSearchProvider


AS_OF = date(2026, 8, 27)


class _ComposedProvider:
    """A deterministic external double; real composition/trust services remain live."""

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
            strategic_signals=[AnalysisItem(
                text="A governed signal is available.",
                type=ClaimType.INFERENCE,
                related_claim_ids=[claim["claim_alias"]],
            )],
        )


def _settings() -> Settings:
    return Settings(
        environment="test", log_level="INFO", data_dir=Path("data"), log_dir=Path("logs"),
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )


def _payload() -> dict[str, str]:
    return {
        "company_name": "Example Co", "executive_name": "Ava Example",
        "meeting_goal": "Prepare a partnership discussion", "company_website": "https://example.test",
        "executive_current_title": "Director",
    }


def _application(search: FakeSearchProvider) -> WorkflowApplication:
    return WorkflowApplication.from_settings(
        _settings(), providers=Providers(llm=_ComposedProvider(), search=search),
    )


def test_public_application_facade_executes_and_resumes_without_service_assembly(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    application = _application(FakeSearchProvider(results=[SearchResult(
        title="Ava Example at Example Co", url="https://example.test/announcement",
        snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
    )]))
    try:
        result = application.execute(_payload(), as_of=AS_OF)
        assert isinstance(result, WorkflowExecutionResult)
        assert result.status is WorkflowExecutionStatus.COMPLETED
        assert result.brief and result.brief.quick_brief and result.brief.full_brief
        assert result.brief.quick_brief.omitted_restriction_count == 0
        assert result.brief.quick_brief.omitted_knowledge_gap_count == 0

        resumed = application.resume(result.workflow_run.run_id, as_of=AS_OF)
        assert resumed.status is WorkflowExecutionStatus.COMPLETED
        assert resumed.brief and resumed.brief.full_brief == result.brief.full_brief
    finally:
        application.close()


def test_public_application_facade_preserves_partial_and_sanitized_failure_results(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    application = _application(FakeSearchProvider())
    try:
        partial = application.execute(_payload(), as_of=AS_OF)
        assert partial.status is WorkflowExecutionStatus.PARTIAL
        assert partial.errors[0].stage is WorkflowStage.RESEARCH_COMPLETED

        failed = application.execute({"company_name": "Example Co"}, as_of=AS_OF)
        assert failed.status is WorkflowExecutionStatus.FAILED
        assert failed.errors[0].stage is WorkflowStage.CASE_VALIDATED
        assert "secret" not in failed.errors[0].message
    finally:
        application.close()


def test_public_application_facade_preserves_governed_gaps_and_omission_disclosures(tmp_path: Path, monkeypatch) -> None:
    class _PublicOnlySearch:
        def __init__(self) -> None:
            self.calls = 0

        def search(self, query):
            self.calls += 1
            return [SearchResult(
                title=f"Ava Example at Example Co {self.calls}",
                url=f"https://public.example.org/news-{self.calls}",
                snippet=f"Example Co public announcement {self.calls}.",
                publisher="Public News", published_at=date(2026, 8, 1),
            )]

    monkeypatch.chdir(tmp_path)
    application = _application(_PublicOnlySearch())
    try:
        result = application.execute(_payload(), as_of=AS_OF)
        assert result.status is WorkflowExecutionStatus.COMPLETED
        assert result.brief and result.brief.quick_brief and result.brief.full_brief
        assert result.brief.quick_brief.omitted_restriction_count > 0
        assert result.brief.quick_brief.omitted_knowledge_gap_count > 0
        assert any(item.is_restricted for item in result.brief.full_brief.knowledge_gap_details)
        assert result.brief.full_brief.knowledge_gaps
    finally:
        application.close()
