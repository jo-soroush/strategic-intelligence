import json
from datetime import date
from pathlib import Path

import pytest
from strategic_intelligence.application.brief_generator import BriefGeneratorService
from strategic_intelligence.application.case_input import CaseIntakeService
from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.executive_research import ExecutiveResearchService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.research_planning import ResearchPlanner
from strategic_intelligence.application.strategic_analysis import StrategicAnalysisService
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.application.brief_generator import BriefGenerationResult, BriefGenerationStatus
from strategic_intelligence.domain.models import AnalysisItem, ClaimType, WorkflowRun, WorkflowRunStatus, WorkflowStage, WorkflowState, StrategicAnalysis
from strategic_intelligence.governance.engine import GovernanceService
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult, WorkflowExecutionStatus, WorkflowExecutor
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.infrastructure.sqlite_repository import CheckpointRejectedError
from strategic_intelligence.providers.contracts import LLMRequest, SearchResult
from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode
from strategic_intelligence.providers.fakes import FakeSearchProvider


AS_OF = date(2026, 8, 27)


class _ComposedProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate_structured(self, request: LLMRequest, schema):
        self.calls += 1
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        claim = context["claims"][0]
        fact_selections = []
        company_direction = []
        if claim["governance_decision"] == "PASS" and claim["claim_type"] == "FACT":
            fact_selections = [{"section": "company_direction", "fact_claim_alias": claim["claim_alias"]}]
        else:
            company_direction = [AnalysisItem(
                text="A governed item is available.", type=ClaimType.INFERENCE, related_claim_ids=[claim["claim_alias"]],
            )]
        return schema(
            fact_selections=fact_selections,
            company_direction=company_direction,
            strategic_signals=[AnalysisItem(text="A governed signal is available.", type=ClaimType.INFERENCE, related_claim_ids=[claim["claim_alias"]])],
            # C16's provenance boundary requires all presentation items derived
            # from restricted material to carry restriction metadata. Keep this
            # composition fixture intentionally narrow: it proves the C18 path
            # with a valid restricted AnalysisItem rather than inventing a
            # governed Opportunity implementation in the test provider.
        )


def _executor(tmp_path: Path, search=None, repository: SqliteRepository | None = None, task_budget: int = 13) -> tuple[WorkflowExecutor, SqliteRepository]:
    repository = repository or SqliteRepository(tmp_path / "workflow.sqlite")
    search = search or FakeSearchProvider(results=[SearchResult(
        title="Ava Example at Example Co", url="https://example.test/announcement",
        snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1),
    )])
    verification = VerificationService(repository)
    evidence = EvidenceLayerService(repository)
    return WorkflowExecutor(
        repository, CaseIntakeService(repository), ResearchPlanner(task_budget=task_budget),
        CompanyResearchService(search), ExecutiveResearchService(search), evidence,
        verification, FollowUpResearchService(repository, evidence, verification),
        GovernanceService(repository, verification), StrategicAnalysisService(repository, _ComposedProvider()),
        BriefGeneratorService(repository),
    ), repository


def _payload() -> dict[str, str]:
    return {
        "company_name": "Example Co", "executive_name": "Ava Example",
        "meeting_goal": "Prepare a partnership discussion", "company_website": "https://example.test",
        "executive_current_title": "Director",
    }


def test_critical_path_executes_and_reloads_completed_workflow(tmp_path: Path) -> None:
    executor, repository = _executor(tmp_path)
    result = executor.execute(_payload(), as_of=AS_OF)

    assert result.status is WorkflowExecutionStatus.COMPLETED
    assert result.brief and result.brief.quick_brief and result.brief.full_brief
    assert executor._analysis._provider.calls == 1
    assert repository.latest_accepted_checkpoint(result.workflow_run.run_id).value == "BRIEF_GENERATED"
    repository.close()

    reopened = SqliteRepository(tmp_path / "workflow.sqlite")
    resumed = _executor_with_repository(reopened).resume(result.workflow_run.run_id, as_of=AS_OF)
    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    assert resumed.state.full_brief and resumed.state.quick_brief


def test_resume_rejects_case_mismatched_snapshot(tmp_path: Path) -> None:
    executor, repository = _executor(tmp_path)
    result = executor.execute(_payload(), as_of=AS_OF)
    assert result.workflow_run.snapshot and result.workflow_run.snapshot.case_context
    other_case = result.workflow_run.snapshot.case_context.model_copy(update={"case_id": "other-case"})
    corrupted = result.workflow_run.model_copy(update={"snapshot": result.workflow_run.snapshot.model_copy(update={"case_context": other_case})})
    repository.save_workflow_run(corrupted)

    resumed = executor.resume(corrupted.run_id, as_of=AS_OF)
    assert resumed.status is WorkflowExecutionStatus.FAILED


def test_completed_resume_is_idempotent_and_illegal_checkpoint_is_rejected(tmp_path: Path) -> None:
    executor, repository = _executor(tmp_path)
    completed = executor.execute(_payload(), as_of=AS_OF)
    resumed = executor.resume(completed.workflow_run.run_id, as_of=AS_OF)

    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    original = completed.workflow_run.accepted_snapshots[WorkflowStage.CASE_VALIDATED]
    assert executor._checkpoint(completed.workflow_run, original, WorkflowStage.GOVERNANCE_COMPLETED, []) is None
    assert repository.latest_accepted_checkpoint(completed.workflow_run.run_id) is WorkflowStage.BRIEF_GENERATED


def test_resume_falls_back_to_previous_valid_accepted_checkpoint(tmp_path: Path) -> None:
    executor, repository = _executor(tmp_path)
    completed = executor.execute(_payload(), as_of=AS_OF)
    snapshots = dict(completed.workflow_run.accepted_snapshots)
    snapshots[WorkflowStage.BRIEF_GENERATED] = snapshots[WorkflowStage.ANALYSIS_COMPLETED]
    interrupted = repository.save_workflow_run(completed.workflow_run.model_copy(update={
        "status": WorkflowRunStatus.RUNNING,
        "current_stage": WorkflowStage.BRIEF_GENERATED,
        "accepted_snapshots": snapshots,
    }))

    resumed = executor.resume(interrupted.run_id, as_of=AS_OF)
    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    assert resumed.workflow_run.status is WorkflowRunStatus.COMPLETED


def test_completed_result_requires_accepted_brief() -> None:
    with pytest.raises(ValueError, match="accepted Brief"):
        WorkflowExecutionResult(
            status=WorkflowExecutionStatus.COMPLETED,
            workflow_run=WorkflowRun(case_id="case", status=WorkflowRunStatus.COMPLETED),
            state=WorkflowState(),
            brief=BriefGenerationResult(status=BriefGenerationStatus.REJECTED),
        )


def test_retryable_research_failure_is_retried_once_and_persisted(tmp_path: Path) -> None:
    class RetryOnceSearch:
        calls = 0

        def search(self, query):
            self.calls += 1
            if self.calls == 1:
                raise ProviderError(ProviderErrorCode.TIMEOUT, "token=secret", retryable=True)
            return [SearchResult("Ava Example at Example Co", "https://example.test/announcement", "Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1))]

    executor, repository = _executor(tmp_path, RetryOnceSearch())
    result = executor.execute(_payload(), as_of=AS_OF)
    assert result.status is WorkflowExecutionStatus.COMPLETED
    assert result.workflow_run.retry_count == 1
    assert repository.get_workflow_run(result.workflow_run.run_id).retry_count == 1


@pytest.mark.parametrize("retryable", [False, None])
def test_non_retryable_and_ordinary_unavailable_do_not_retry(tmp_path: Path, retryable: bool | None) -> None:
    class UnavailableSearch:
        calls = 0
        def search(self, query):
            self.calls += 1
            if retryable is None:
                raise RuntimeError("token=secret")
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "token=secret", retryable=retryable)

    provider = UnavailableSearch()
    result = _executor(tmp_path, provider, task_budget=1)[0].execute(_payload(), as_of=AS_OF)
    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert provider.calls == 1
    assert result.workflow_run.retry_count == 0
    assert "secret" not in result.errors[0].message


def test_safe_incomplete_research_produces_typed_partial_not_completed_or_failed(tmp_path: Path) -> None:
    result = _executor(tmp_path, FakeSearchProvider(), task_budget=1)[0].execute(_payload(), as_of=AS_OF)
    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert result.workflow_run.status is WorkflowRunStatus.PARTIAL
    assert result.brief is None
    assert result.errors and result.errors[0].error_code.value == "INSUFFICIENT_EVIDENCE"
    assert result.errors[0].stage is WorkflowStage.RESEARCH_COMPLETED


def test_follow_up_official_evidence_routes_to_current_pass_and_brief(tmp_path: Path) -> None:
    class DiscoveryThenOfficial:
        calls = 0
        def search(self, query):
            self.calls += 1
            url = "https://public.example.org/news" if self.calls == 1 else "https://example.test/official"
            return [SearchResult("Example Co research", url, "Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1))]

    provider = DiscoveryThenOfficial()
    result = _executor(tmp_path, provider, task_budget=1)[0].execute(_payload(), as_of=AS_OF)
    assert result.status is WorkflowExecutionStatus.COMPLETED
    assert result.workflow_run.snapshot and result.workflow_run.snapshot.governance_decisions[0].decision.value == "PASS"
    assert provider.calls == 2
    assert result.brief and result.brief.full_brief


def test_resolved_resumed_verification_does_not_invoke_follow_up_again(tmp_path: Path) -> None:
    class DiscoveryThenOfficial:
        calls = 0
        def search(self, query):
            self.calls += 1
            url = "https://public.example.org/news" if self.calls == 1 else "https://example.test/official"
            return [SearchResult("Example Co research", url, "Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1))]
    executor, repository = _executor(tmp_path, DiscoveryThenOfficial(), task_budget=1)
    completed = executor.execute(_payload(), as_of=AS_OF)
    attempts_before = repository._connection.execute("SELECT COUNT(*) FROM follow_up_attempts").fetchone()[0]
    run_id = completed.workflow_run.run_id
    snapshots = {stage: state for stage, state in completed.workflow_run.accepted_snapshots.items() if stage.value <= WorkflowStage.GOVERNANCE_COMPLETED.value}
    repository._connection.execute("DELETE FROM checkpoints WHERE run_id = ? AND stage NOT IN (?, ?)", (run_id, WorkflowStage.EVIDENCE_BUILT.value, WorkflowStage.GOVERNANCE_COMPLETED.value))
    repository._connection.commit()
    repository.save_workflow_run(completed.workflow_run.model_copy(update={"status": WorkflowRunStatus.RUNNING, "current_stage": WorkflowStage.GOVERNANCE_COMPLETED, "snapshot": snapshots[WorkflowStage.GOVERNANCE_COMPLETED], "accepted_snapshots": snapshots}))
    resumed = executor.resume(run_id, as_of=AS_OF)
    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    assert repository._connection.execute("SELECT COUNT(*) FROM follow_up_attempts").fetchone()[0] == attempts_before


def test_retry_budget_and_research_artifacts_survive_intermediate_reload(tmp_path: Path) -> None:
    class RetryThenResults:
        calls = 0
        def search(self, query):
            self.calls += 1
            if self.calls == 1:
                raise ProviderError(ProviderErrorCode.TIMEOUT, "token=secret", retryable=True)
            return [SearchResult("Example Co research", "https://example.test/official", "Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 1))]

    executor, repository = _executor(tmp_path, RetryThenResults(), task_budget=1)
    completed = executor.execute(_payload(), as_of=AS_OF)
    run_id = completed.workflow_run.run_id
    before = [repository._connection.execute(query).fetchall() for query in ("SELECT id FROM sources ORDER BY id", "SELECT id FROM evidence ORDER BY id", "SELECT id FROM claims ORDER BY id", "SELECT claim_id, evidence_id, relationship_type FROM claim_evidence_links ORDER BY claim_id, evidence_id, relationship_type")]
    research_state = completed.workflow_run.accepted_snapshots[WorkflowStage.RESEARCH_COMPLETED]
    snapshots = {stage: state for stage, state in completed.workflow_run.accepted_snapshots.items() if stage.value <= WorkflowStage.RESEARCH_COMPLETED.value}
    repository._connection.execute("DELETE FROM checkpoints WHERE run_id = ? AND stage != ?", (run_id, WorkflowStage.RESEARCH_COMPLETED.value))
    repository._connection.commit()
    repository.save_workflow_run(completed.workflow_run.model_copy(update={"status": WorkflowRunStatus.RUNNING, "current_stage": WorkflowStage.RESEARCH_COMPLETED, "snapshot": research_state, "accepted_snapshots": snapshots}))
    repository.close()
    reopened = SqliteRepository(tmp_path / "workflow.sqlite")
    resumed = _executor_with_repository(reopened).resume(run_id, as_of=AS_OF)
    after = [reopened._connection.execute(query).fetchall() for query in ("SELECT id FROM sources ORDER BY id", "SELECT id FROM evidence ORDER BY id", "SELECT id FROM claims ORDER BY id", "SELECT claim_id, evidence_id, relationship_type FROM claim_evidence_links ORDER BY claim_id, evidence_id, relationship_type")]
    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    assert resumed.workflow_run.retry_count == 1
    assert before == after


def test_retry_exhaustion_persists_budget_and_reload_cannot_retry_again(tmp_path: Path) -> None:
    class AlwaysTimeout:
        calls = 0
        def search(self, query):
            self.calls += 1
            raise ProviderError(ProviderErrorCode.TIMEOUT, "token=secret", retryable=True)

    provider = AlwaysTimeout()
    executor, repository = _executor(tmp_path, provider, task_budget=1)
    result = executor.execute(_payload(), as_of=AS_OF)
    assert result.status is WorkflowExecutionStatus.PARTIAL
    assert provider.calls == 2
    assert result.workflow_run.retry_count == 1
    assert "secret" not in result.errors[0].message
    repository.close()
    reopened = SqliteRepository(tmp_path / "workflow.sqlite")
    resumed = _executor_with_repository(reopened).resume(result.workflow_run.run_id, as_of=AS_OF)
    assert resumed.status is WorkflowExecutionStatus.PARTIAL
    assert resumed.workflow_run.retry_count == 1


def test_checkpoint_failure_preserves_previous_accepted_state(tmp_path: Path) -> None:
    class RejectResearchPlanCheckpoint(SqliteRepository):
        def accept_checkpoint(self, run_id, stage, required_records):
            if stage is WorkflowStage.RESEARCH_PLANNED:
                raise CheckpointRejectedError("controlled persistence fault")
            return super().accept_checkpoint(run_id, stage, required_records)

    repository = RejectResearchPlanCheckpoint(tmp_path / "workflow.sqlite")
    executor, _ = _executor(tmp_path, repository=repository, task_budget=1)
    result = executor.execute(_payload(), as_of=AS_OF)
    assert result.status is WorkflowExecutionStatus.FAILED
    assert repository.checkpoint_is_accepted(result.workflow_run.run_id, WorkflowStage.CASE_VALIDATED)
    assert not repository.checkpoint_is_accepted(result.workflow_run.run_id, WorkflowStage.RESEARCH_PLANNED)
    assert result.workflow_run.status is WorkflowRunStatus.FAILED
    assert result.errors[0].stage is WorkflowStage.RESEARCH_PLANNED
    assert repository.get_workflow_run(result.workflow_run.run_id).errors[0].stage is WorkflowStage.RESEARCH_PLANNED


def test_research_side_resume_reuses_persisted_claim_artifacts(tmp_path: Path) -> None:
    executor, repository = _executor(tmp_path, task_budget=1)
    completed = executor.execute(_payload(), as_of=AS_OF)
    run_id = completed.workflow_run.run_id
    source_count = repository._connection.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
    evidence_count = repository._connection.execute("SELECT COUNT(*) FROM evidence").fetchone()[0]
    claim_count = repository._connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0]
    link_count = repository._connection.execute("SELECT COUNT(*) FROM claim_evidence_links").fetchone()[0]
    snapshots = {
        stage: state for stage, state in completed.workflow_run.accepted_snapshots.items()
        if stage.value <= WorkflowStage.RESEARCH_COMPLETED.value
    }
    research_state = snapshots[WorkflowStage.RESEARCH_COMPLETED]
    repository._connection.execute("DELETE FROM checkpoints WHERE run_id = ? AND stage != ?", (run_id, WorkflowStage.RESEARCH_COMPLETED.value))
    repository._connection.commit()
    repository.save_workflow_run(completed.workflow_run.model_copy(update={
        "status": WorkflowRunStatus.RUNNING, "current_stage": WorkflowStage.RESEARCH_COMPLETED,
        "snapshot": research_state, "accepted_snapshots": snapshots,
    }))
    repository.close()

    reopened = SqliteRepository(tmp_path / "workflow.sqlite")
    resumed = _executor_with_repository(reopened).resume(run_id, as_of=AS_OF)
    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    assert [reopened._connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in ("sources", "evidence", "claims", "claim_evidence_links")] == [source_count, evidence_count, claim_count, link_count]


def test_trust_side_resume_restarts_from_evidence_not_historical_governance(tmp_path: Path) -> None:
    executor, repository = _executor(tmp_path, task_budget=1)
    completed = executor.execute(_payload(), as_of=AS_OF)
    run_id = completed.workflow_run.run_id
    snapshots = {
        stage: state for stage, state in completed.workflow_run.accepted_snapshots.items()
        if stage.value <= WorkflowStage.GOVERNANCE_COMPLETED.value
    }
    governance_state = snapshots[WorkflowStage.GOVERNANCE_COMPLETED]
    repository._connection.execute("DELETE FROM checkpoints WHERE run_id = ? AND stage NOT IN (?, ?)", (run_id, WorkflowStage.EVIDENCE_BUILT.value, WorkflowStage.GOVERNANCE_COMPLETED.value))
    repository._connection.commit()
    repository.save_workflow_run(completed.workflow_run.model_copy(update={
        "status": WorkflowRunStatus.RUNNING, "current_stage": WorkflowStage.GOVERNANCE_COMPLETED,
        "snapshot": governance_state, "accepted_snapshots": snapshots,
    }))
    resumed = executor.resume(run_id, as_of=date(2027, 8, 27))
    assert resumed.status is WorkflowExecutionStatus.COMPLETED
    assert resumed.state.governance_decisions[0].decision.value == "RESTRICT"


def _executor_with_repository(repository: SqliteRepository) -> WorkflowExecutor:
    search = FakeSearchProvider(results=[])
    verification = VerificationService(repository)
    evidence = EvidenceLayerService(repository)
    return WorkflowExecutor(
        repository, CaseIntakeService(repository), ResearchPlanner(), CompanyResearchService(search),
        ExecutiveResearchService(search), evidence, verification,
        FollowUpResearchService(repository, evidence, verification), GovernanceService(repository, verification),
        StrategicAnalysisService(repository, _ComposedProvider()), BriefGeneratorService(repository),
    )
