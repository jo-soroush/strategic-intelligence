import json
from datetime import date
from pathlib import Path

import pytest

from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.application.brief_generator import BriefGeneratorService
from strategic_intelligence.application.case_input import CaseIntakeService
from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.executive_research import ExecutiveResearchService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.research_planning import ResearchPlanner
from strategic_intelligence.application.strategic_analysis import (
    StrategicAnalysisFidelityFailureMode,
    StrategicAnalysisPostParseValidatorRule,
    StrategicAnalysisRejectionReason,
    StrategicAnalysisSemanticPayload,
    StrategicAnalysisService,
)
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.config import Settings
from strategic_intelligence.domain.models import AnalysisItem, ClaimType, WorkflowStage
from strategic_intelligence.governance.engine import GovernanceService
from strategic_intelligence.harness.workflow_executor import WorkflowExecutor, WorkflowExecutionStatus
from strategic_intelligence.infrastructure.sqlite_repository import CheckpointRejectedError, SqliteRepository
from strategic_intelligence.observability.audit import AuditTrail, ObservedLLMProvider, ObservedSearchProvider
from strategic_intelligence.providers.contracts import (
    LLMRequest,
    ProviderError,
    ProviderErrorCode,
    SearchQuery,
    SearchResult,
    StructuredOutputFailureReason,
)
from strategic_intelligence.providers.factory import Providers
from strategic_intelligence.providers.fakes import FakeSearchProvider


def test_audit_trace_is_ordered_redacted_and_survives_reload(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("C19_API_KEY", "secret-value")
    path = tmp_path / "audit.db"
    repository = SqliteRepository(path)
    trail = AuditTrail(repository)
    trail.activate("case", "run")
    trail.record("RUN", "workflow", "STARTED")
    trail.record("ERROR", "provider", "FAILED", metadata={"message": "token=secret-value", "duration_ms": 7})
    trail.record("TERMINAL", "workflow", "FAILED")
    assert [event.sequence for event in trail.report("run").events] == [0, 1, 2]
    assert "secret-value" not in str(trail.report("run").events)
    assert trail.report("run").error_count == 1
    repository.close()

    reopened = SqliteRepository(path)
    report = AuditTrail(reopened).report("run")
    assert [event.event_type for event in report.events] == ["RUN", "ERROR", "TERMINAL"]
    assert report.events[1].metadata["message"] == "token=[REDACTED]"
    reopened.close()


def test_provider_observer_keeps_c04_result_and_records_bounded_metadata(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "audit.db")
    trail = AuditTrail(repository)
    trail.activate("case", "run")
    provider = ObservedSearchProvider(FakeSearchProvider(results=[SearchResult(title="title", url="https://example.test")]), trail)
    assert provider.search(SearchQuery(query="company"))[0].url == "https://example.test"
    report = trail.report("run")
    assert report.provider_call_count == 1
    assert report.events[0].metadata["result_count"] == 1
    assert "company" not in str(report.events[0].metadata)
    repository.close()


def test_llm_observer_records_only_safe_structured_output_reason(tmp_path: Path) -> None:
    class FailingProvider:
        def generate(self, request: LLMRequest):
            raise AssertionError("structured path required")

        def generate_structured(self, request: LLMRequest, schema):
            raise ProviderError(
                ProviderErrorCode.STRUCTURED_OUTPUT_INVALID,
                "raw model output token=secret-value",
                structured_output_failure_reason=StructuredOutputFailureReason.PYDANTIC_VALIDATION_FAILED,
            )

    repository = SqliteRepository(tmp_path / "audit.db")
    trail = AuditTrail(repository)
    trail.activate("case", "run")
    provider = ObservedLLMProvider(FailingProvider(), trail)

    with pytest.raises(ProviderError):
        provider.generate_structured(LLMRequest("raw prompt secret-value"), StrategicAnalysisSemanticPayload)

    event = trail.report("run").events[0]
    assert event.status == ProviderErrorCode.STRUCTURED_OUTPUT_INVALID.value
    assert event.metadata["structured_output_failure_reason"] == "PYDANTIC_VALIDATION_FAILED"
    assert "secret-value" not in str(event)
    assert "raw prompt" not in str(event)
    repository.close()


def test_audit_traces_are_isolated_by_run_after_reload(tmp_path: Path) -> None:
    path = tmp_path / "audit.db"
    repository = SqliteRepository(path)
    trail = AuditTrail(repository)
    trail.activate("case-a", "run-a")
    trail.record("RUN", "workflow", "STARTED")
    trail.record("TERMINAL", "workflow", "COMPLETED")
    trail.activate("case-b", "run-b")
    trail.record("RUN", "workflow", "STARTED")
    trail.record("ERROR", "workflow", "FAILED")
    trail.record("TERMINAL", "workflow", "FAILED")
    assert [event.run_id for event in trail.report("run-a").events] == ["run-a", "run-a"]
    assert [event.run_id for event in trail.report("run-b").events] == ["run-b", "run-b", "run-b"]
    repository.close()

    reopened = SqliteRepository(path)
    reloaded = AuditTrail(reopened)
    assert reloaded.report("run-a").terminal_status == "COMPLETED"
    assert reloaded.report("run-b").terminal_status == "FAILED"
    assert reloaded.report("missing' run").events == []
    reopened.close()


class _ComposedProvider:
    def generate(self, request: LLMRequest):
        raise AssertionError("structured generation is required")

    def generate_structured(self, request: LLMRequest, schema):
        if "TRUSTED_CONTEXT_JSON" not in request.prompt:
            return schema()
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        claim = context["claims"][0]
        return schema(fact_selections=[{
            "section": "company_direction", "fact_claim_alias": claim["claim_alias"],
        }])


class _DuplicateC15AliasProvider(_ComposedProvider):
    """C15 schema succeeds; C15 itself must reject the duplicate transient alias."""

    def generate_structured(self, request: LLMRequest, schema):
        if "TRUSTED_CONTEXT_JSON" not in request.prompt:
            return super().generate_structured(request, schema)
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        claim = context["claims"][0]
        return schema(strategic_signals=[AnalysisItem(
            text="token=c15-observation-secret duplicate alias",
            type=ClaimType.INFERENCE,
            related_claim_ids=[claim["claim_alias"], claim["claim_alias"]],
        )])


class _OverLimitC15Provider(_ComposedProvider):
    """Schema-valid C15 output which must preserve C18's existing partial path."""

    def generate_structured(self, request: LLMRequest, schema):
        if "TRUSTED_CONTEXT_JSON" not in request.prompt:
            return super().generate_structured(request, schema)
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        claim = context["claims"][0]
        return schema(strategic_signals=[AnalysisItem(
            text="A bounded signal may matter.",
            type=ClaimType.INFERENCE,
            related_claim_ids=[claim["claim_alias"]],
        )] * 21)


class _GovernedFactRejectionC15Provider(_ComposedProvider):
    """Schema-valid ineligible FACT selection that C15 rejects while C18 remains fail closed."""

    def generate_structured(self, request: LLMRequest, schema):
        if "TRUSTED_CONTEXT_JSON" not in request.prompt:
            return super().generate_structured(request, schema)
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        return StrategicAnalysisSemanticPayload.model_validate({
            "fact_selections": [{"section": "company_direction", "fact_claim_alias": "CLAIM_999"}],
        })


def test_real_workflow_persists_reconstructable_observations(tmp_path: Path) -> None:
    settings = Settings(
        environment="test", log_level="INFO", data_dir=tmp_path / "data", log_dir=tmp_path / "logs",
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )
    app = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_ComposedProvider(), search=FakeSearchProvider(results=[SearchResult(
            title="Ava Example at Example Co", url="https://example.test/announcement",
            snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
        )]),
    ))
    result = app.execute({
        "company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare",
        "company_website": "https://example.test", "executive_current_title": "Director",
    }, as_of=date(2026, 8, 27))
    report = app.audit_report(result.workflow_run.run_id)
    assert report.events and report.terminal_status == result.status.value
    assert report.checkpoint_count >= 1 and report.provider_call_count >= 1
    assert any(event.event_type == "CHECKPOINT" and event.status == "ACCEPTED" for event in report.events)
    assert report.verification_count >= 1 and report.governance_count >= 1
    assert report.total_duration_ms >= 0 and report.stage_duration_ms
    assert report.provider_call_count == len([event for event in report.events if event.event_type == "PROVIDER_CALL"])
    assert report.checkpoint_count == len([event for event in report.events if event.event_type == "CHECKPOINT"])
    assert report.verification_count == len([event for event in report.events if event.event_type == "VERIFICATION"])
    assert report.governance_count == len([event for event in report.events if event.event_type == "GOVERNANCE"])
    app.close()

    reloaded = WorkflowApplication.from_settings(settings, providers=Providers(llm=_ComposedProvider(), search=FakeSearchProvider()))
    reloaded_report = reloaded.audit_report(result.workflow_run.run_id)
    assert reloaded_report.model_dump() == report.model_dump()
    reloaded.close()


def test_real_c18_retry_is_observed_without_changing_retry_semantics(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("C19_TOKEN", "retry-secret")
    class RetryOnceSearch:
        calls = 0
        def search(self, query):
            self.calls += 1
            if self.calls == 1:
                raise ProviderError(ProviderErrorCode.TIMEOUT, "token=retry-secret", retryable=True)
            return [SearchResult("Ava Example at Example Co", "https://example.test/announcement", "Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1))]

    settings = Settings(environment="test", log_level="INFO", data_dir=tmp_path / "data", log_dir=tmp_path / "logs", llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0, ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False)
    search = RetryOnceSearch()
    app = WorkflowApplication.from_settings(settings, providers=Providers(llm=_ComposedProvider(), search=search))
    result = app.execute({"company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare", "company_website": "https://example.test", "executive_current_title": "Director"}, as_of=date(2026, 8, 27))
    report = app.audit_report(result.workflow_run.run_id)
    assert result.workflow_run.retry_count == 1 and report.retry_count == 1
    assert any(event.event_type == "PROVIDER_CALL" and event.status == "PROVIDER_TIMEOUT" for event in report.events)
    assert len([event for event in report.events if event.event_type == "PROVIDER_CALL" and event.component == "search"]) == search.calls
    assert report.provider_call_count == len([event for event in report.events if event.event_type == "PROVIDER_CALL"])
    assert "retry-secret" not in str(report)
    app.close()


def test_c15_post_provider_rejection_is_persisted_before_c18_keeps_generic_partial(tmp_path: Path) -> None:
    settings = Settings(
        environment="test", log_level="INFO", data_dir=tmp_path / "data", log_dir=tmp_path / "logs",
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )
    app = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_DuplicateC15AliasProvider(),
        search=FakeSearchProvider(results=[SearchResult(
            title="Ava Example at Example Co", url="https://example.test/announcement",
            snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
        )]),
    ))
    result = app.execute({
        "company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare",
        "company_website": "https://example.test", "executive_current_title": "Director",
    }, as_of=date(2026, 8, 27))
    report = app.audit_report(result.workflow_run.run_id)
    c15_events = [event for event in report.events if event.event_type == "C15_REJECTION"]

    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert result.errors[0].error_code.value == "INSUFFICIENT_EVIDENCE"
    assert len(c15_events) == 1
    assert c15_events[0].stage is WorkflowStage.GOVERNANCE_COMPLETED
    assert c15_events[0].metadata == {
        "reason_code": StrategicAnalysisRejectionReason.DUPLICATE_CLAIM_REFERENCE.value,
        "validator_stage": "ALIAS_RESOLUTION",
    }
    assert "c15-observation-secret" not in str(report)
    run_id = result.workflow_run.run_id
    app.close()

    reopened = WorkflowApplication.from_settings(settings, providers=Providers(llm=_DuplicateC15AliasProvider(), search=FakeSearchProvider()))
    reloaded = [event for event in reopened.audit_report(run_id).events if event.event_type == "C15_REJECTION"]
    assert len(reloaded) == 1 and reloaded[0].metadata == c15_events[0].metadata
    reopened.close()


def test_c15_fidelity_subrule_persists_before_c18_keeps_generic_partial(tmp_path: Path) -> None:
    settings = Settings(
        environment="test", log_level="INFO", data_dir=tmp_path / "data", log_dir=tmp_path / "logs",
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )
    app = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_GovernedFactRejectionC15Provider(),
        search=FakeSearchProvider(results=[SearchResult(
            title="Ava Example at Example Co", url="https://example.test/announcement",
            snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
        )]),
    ))
    result = app.execute({
        "company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare",
        "company_website": "https://example.test", "executive_current_title": "Director",
    }, as_of=date(2026, 8, 27))
    report = app.audit_report(result.workflow_run.run_id)
    c15_events = [event for event in report.events if event.event_type == "C15_REJECTION"]

    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert result.errors[0].error_code.value == "INSUFFICIENT_EVIDENCE"
    assert len(c15_events) == 1
    assert c15_events[0].metadata == {
        "reason_code": StrategicAnalysisRejectionReason.ALIAS_RESOLUTION_FAILED.value,
        "validator_stage": "ALIAS_RESOLUTION",
    }
    assert "c15-fidelity-secret" not in str(report)
    run_id = result.workflow_run.run_id
    app.close()

    reopened = WorkflowApplication.from_settings(settings, providers=Providers(llm=_GovernedFactRejectionC15Provider(), search=FakeSearchProvider()))
    reloaded = [event for event in reopened.audit_report(run_id).events if event.event_type == "C15_REJECTION"]
    assert len(reloaded) == 1 and reloaded[0].metadata == c15_events[0].metadata
    reopened.close()


def test_generic_c15_rule_persists_without_changing_c18_partial_semantics(tmp_path: Path) -> None:
    settings = Settings(
        environment="test", log_level="INFO", data_dir=tmp_path / "data", log_dir=tmp_path / "logs",
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )
    app = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_OverLimitC15Provider(),
        search=FakeSearchProvider(results=[SearchResult(
            title="Ava Example at Example Co", url="https://example.test/announcement",
            snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
        )]),
    ))
    result = app.execute({
        "company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare",
        "company_website": "https://example.test", "executive_current_title": "Director",
    }, as_of=date(2026, 8, 27))
    report = app.audit_report(result.workflow_run.run_id)
    c15_events = [event for event in report.events if event.event_type == "C15_REJECTION"]

    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert result.errors[0].error_code.value == "INSUFFICIENT_EVIDENCE"
    assert len(c15_events) == 1
    assert c15_events[0].metadata == {
        "reason_code": StrategicAnalysisRejectionReason.POST_PARSE_VALIDATION_FAILED.value,
        "validator_stage": "POST_PARSE_VALIDATION",
        "post_parse_validator_rule": StrategicAnalysisPostParseValidatorRule.SECTION_ITEM_LIMIT_EXCEEDED.value,
    }
    run_id = result.workflow_run.run_id
    app.close()

    reopened = WorkflowApplication.from_settings(settings, providers=Providers(llm=_OverLimitC15Provider(), search=FakeSearchProvider()))
    reloaded = [event for event in reopened.audit_report(run_id).events if event.event_type == "C15_REJECTION"]
    assert len(reloaded) == 1 and reloaded[0].metadata == c15_events[0].metadata
    reopened.close()


def test_real_c03_checkpoint_failure_is_observed_and_reloads(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("C19_TOKEN", "checkpoint-secret")

    class RejectResearchPlanCheckpoint(SqliteRepository):
        attempted = False
        def accept_checkpoint(self, run_id, stage, required_records):
            if stage is WorkflowStage.RESEARCH_PLANNED:
                self.attempted = True
                raise CheckpointRejectedError("token=checkpoint-secret")
            return super().accept_checkpoint(run_id, stage, required_records)

    path = tmp_path / "workflow.sqlite"
    repository = RejectResearchPlanCheckpoint(path)
    audit = AuditTrail(repository)
    verification = VerificationService(repository)
    executor = WorkflowExecutor(
        repository, CaseIntakeService(repository), ResearchPlanner(task_budget=1),
        CompanyResearchService(FakeSearchProvider()), ExecutiveResearchService(FakeSearchProvider()),
        EvidenceLayerService(repository), verification, FollowUpResearchService(repository, EvidenceLayerService(repository), verification),
        GovernanceService(repository, verification), StrategicAnalysisService(repository, _ComposedProvider(), verification),
        BriefGeneratorService(repository), audit=audit,
    )
    result = executor.execute({"company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare", "company_website": "https://example.test", "executive_current_title": "Director"}, as_of=date(2026, 8, 27))
    report = audit.report(result.workflow_run.run_id)
    rejected = [event for event in report.events if event.event_type == "CHECKPOINT" and event.status == "REJECTED"]
    assert repository.attempted and result.status is WorkflowExecutionStatus.FAILED
    assert rejected and not any(event.event_type == "CHECKPOINT" and event.status == "ACCEPTED" and event.stage is WorkflowStage.RESEARCH_PLANNED for event in report.events)
    assert "checkpoint-secret" not in str(report) and report.checkpoint_count == len([event for event in report.events if event.event_type == "CHECKPOINT"])
    run_id = result.workflow_run.run_id
    repository.close()
    reopened = SqliteRepository(path)
    reloaded = AuditTrail(reopened).report(run_id)
    assert any(event.event_type == "CHECKPOINT" and event.status == "REJECTED" for event in reloaded.events)
    reopened.close()


def test_audit_write_failure_does_not_change_real_c18_checkpoint_or_terminal_semantics(tmp_path: Path) -> None:
    class FailingAuditWrites(SqliteRepository):
        def save_audit_event(self, event):
            raise RuntimeError("audit store unavailable")

    repository = FailingAuditWrites(tmp_path / "workflow.sqlite")
    audit = AuditTrail(repository)
    verification = VerificationService(repository)
    executor = WorkflowExecutor(
        repository, CaseIntakeService(repository), ResearchPlanner(task_budget=1),
        CompanyResearchService(FakeSearchProvider(results=[SearchResult(
            "Ava Example at Example Co", "https://example.test/announcement", "Example Co opened a research lab.",
            publisher="Example Co", published_at=date(2026, 8, 1),
        )])), ExecutiveResearchService(FakeSearchProvider()), EvidenceLayerService(repository), verification,
        FollowUpResearchService(repository, EvidenceLayerService(repository), verification),
        GovernanceService(repository, verification), StrategicAnalysisService(repository, _ComposedProvider(), verification),
        BriefGeneratorService(repository), audit=audit,
    )
    result = executor.execute({
        "company_name": "Example Co", "executive_name": "Ava Example", "meeting_goal": "Prepare",
        "company_website": "https://example.test", "executive_current_title": "Director",
    }, as_of=date(2026, 8, 27))
    # This controlled fixture normally reaches C18's genuine PARTIAL outcome;
    # failed observation must not convert accepted checkpoints into failure.
    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert result.workflow_run.accepted_snapshots
    assert audit.report(result.workflow_run.run_id).events == []
    repository.close()
