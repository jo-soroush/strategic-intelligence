from datetime import datetime, timezone
from pathlib import Path

from strategic_intelligence.application.brief_generator import BriefGenerationResult, BriefGenerationStatus
from strategic_intelligence.application.company_memory import CompanyMemoryService
from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult, WorkflowExecutionStatus
from strategic_intelligence.domain.models import Case, QuickBrief, MeetingBrief, TrackedCompany, WorkflowRun, WorkflowRunStatus, WorkflowStage, WorkflowState
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.observability.audit import AuditTrail


def test_tracked_company_memory_preserves_order_and_survives_reopen(tmp_path: Path) -> None:
    database = tmp_path / "memory.db"
    repository = SqliteRepository(database)
    memory = CompanyMemoryService(repository)
    repository.create_case(Case(case_id="case-1", company_id="c1", executive_id="e1", company_name="Capgemini", executive_name="Ava", meeting_goal="Prepare"))
    repository.create_case(Case(case_id="case-2", company_id="c2", executive_id="e2", company_name="Spotify", executive_name="Bea", meeting_goal="Prepare"))
    repository.save_workflow_run(WorkflowRun(run_id="r1", case_id="case-1"))
    repository.save_workflow_run(WorkflowRun(run_id="r2", case_id="case-2"))
    first = memory.record_run(company_id="c1", company_name="  Capgemini ", run_id="r1", successful=True)
    second = memory.record_run(company_id="c2", company_name="Spotify", run_id="r2", successful=True)
    assert [item.normalized_name for item in repository.list_tracked_companies()] == ["capgemini", "spotify"]
    assert first.insertion_order == 0 and second.insertion_order == 1
    repository.close()

    reopened = SqliteRepository(database)
    try:
        assert reopened.get_tracked_company_by_normalized_name("capgemini").active_run_id == "r1"
        assert [item.display_name for item in reopened.list_tracked_companies()] == ["  Capgemini ", "Spotify"]
    finally:
        reopened.close()


def test_failed_refresh_keeps_prior_active_run_and_history() -> None:
    repository = SqliteRepository(Path(":memory:"))
    try:
        memory = CompanyMemoryService(repository)
        repository.create_case(Case(case_id="case-1", company_id="c1", executive_id="e1", company_name="Capgemini", executive_name="Ava", meeting_goal="Prepare"))
        repository.create_case(Case(case_id="case-2", company_id="c1", executive_id="e2", company_name="Capgemini", executive_name="Bea", meeting_goal="Prepare"))
        repository.save_workflow_run(WorkflowRun(run_id="r1", case_id="case-1"))
        repository.save_workflow_run(WorkflowRun(run_id="r2", case_id="case-2"))
        prior = memory.record_run(company_id="c1", company_name="Capgemini", run_id="r1", successful=True)
        after_failure = memory.record_run(company_id="c1", company_name="CAPGEMINI", run_id="r2", successful=False)
        assert after_failure.run_ids == ["r1", "r2"]
        assert after_failure.active_run_id == prior.active_run_id == "r1"
    finally:
        repository.close()


class _StubExecutor:
    def __init__(self, result: WorkflowExecutionResult) -> None:
        self.result = result
        self.calls = 0

    def execute(self, payload, *, as_of):
        self.calls += 1
        return self.result


def test_application_loads_active_memory_without_executing_again() -> None:
    repository = SqliteRepository(Path(":memory:"))
    case = Case(company_id="c1", executive_id="e1", company_name="Capgemini", executive_name="Ava", meeting_goal="Prepare")
    repository.create_case(case)
    state = WorkflowState(case_context=case, current_stage=WorkflowStage.CASE_COMPLETED, quick_brief=QuickBrief(case_id=case.case_id), full_brief=MeetingBrief(case_id=case.case_id, version=1))
    run = repository.save_workflow_run(WorkflowRun(case_id=case.case_id, status=WorkflowRunStatus.COMPLETED, current_stage=WorkflowStage.CASE_COMPLETED, snapshot=state))
    result = WorkflowExecutionResult(
        status=WorkflowExecutionStatus.COMPLETED,
        workflow_run=run,
        state=state,
        brief=BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=state.quick_brief, full_brief=state.full_brief),
    )
    executor = _StubExecutor(result)
    app = WorkflowApplication(executor, repository, AuditTrail(repository), CompanyMemoryService(repository))
    try:
        app._memory.record_run(company_id="c1", company_name="Capgemini", run_id=run.run_id, successful=True)
        loaded = app.execute({"company_name": "  CAPGEMINI  "}, as_of=datetime.now(timezone.utc).date())
        assert loaded.workflow_run.run_id == run.run_id
        assert executor.calls == 0
    finally:
        repository.close()
