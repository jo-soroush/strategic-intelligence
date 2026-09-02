"""C18 bounded composition of the existing V1 application authorities."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from strategic_intelligence.application.brief_generator import BriefGenerationResult, BriefGenerationStatus, BriefGeneratorService
from strategic_intelligence.application.case_input import CaseIntakeService, IntakeStatus
from strategic_intelligence.application.company_research import CompanyResearchResult, CompanyResearchStatus, CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService, EvidenceLayerStatus
from strategic_intelligence.application.executive_research import ExecutiveResearchResult, ExecutiveResearchStatus, ExecutiveResearchService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.application.research_planning import PlanningStatus, ResearchPlanner
from strategic_intelligence.application.strategic_analysis import StrategicAnalysisResult, StrategicAnalysisStatus, StrategicAnalysisService
from strategic_intelligence.application.verification import VerificationAssessment, VerificationAssessmentStatus, VerificationService
from strategic_intelligence.domain.models import (
    Case, Claim, RawFinding, ResearchTask, TargetType, VerificationStatus,
    WorkflowError, WorkflowErrorCode, WorkflowRun, WorkflowRunStatus, WorkflowStage, WorkflowState,
)
from strategic_intelligence.governance.engine import GovernanceAssessmentStatus, GovernanceService
from strategic_intelligence.observability.audit import AuditTrail
from strategic_intelligence.security import UnsafeExternalUrlError, normalize_external_url


class WorkflowExecutionStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class WorkflowExecutionResult(BaseModel):
    """The narrow typed output consumed later by C17, never a UI model."""

    model_config = ConfigDict(extra="forbid", strict=True)

    status: WorkflowExecutionStatus
    workflow_run: WorkflowRun
    state: WorkflowState
    brief: BriefGenerationResult | None = None
    errors: list[WorkflowError] = Field(default_factory=list)

    @model_validator(mode="after")
    def _terminal_result_is_safe(self) -> "WorkflowExecutionResult":
        if self.workflow_run.case_id != (self.state.case_context.case_id if self.state.case_context else self.workflow_run.case_id):
            raise ValueError("workflow result state must belong to its run Case")
        if self.status is WorkflowExecutionStatus.COMPLETED and (
            self.brief is None or self.brief.status is not BriefGenerationStatus.ACCEPTED
        ):
            raise ValueError("completed workflow requires an accepted Brief")
        if self.status is WorkflowExecutionStatus.COMPLETED and self.workflow_run.status is not WorkflowRunStatus.COMPLETED:
            raise ValueError("completed result requires completed WorkflowRun")
        return self


class WorkflowExecutor:
    """Coordinates V1 stages; each stage retains its own business/trust authority."""

    _NEXT_STAGE: dict[WorkflowStage, WorkflowStage] = {
        WorkflowStage.CASE_VALIDATED: WorkflowStage.RESEARCH_PLANNED,
        WorkflowStage.RESEARCH_PLANNED: WorkflowStage.RESEARCH_COMPLETED,
        WorkflowStage.RESEARCH_COMPLETED: WorkflowStage.EVIDENCE_BUILT,
        WorkflowStage.EVIDENCE_BUILT: WorkflowStage.VERIFICATION_COMPLETED,
        WorkflowStage.VERIFICATION_COMPLETED: WorkflowStage.GOVERNANCE_COMPLETED,
        WorkflowStage.GOVERNANCE_COMPLETED: WorkflowStage.ANALYSIS_COMPLETED,
        WorkflowStage.ANALYSIS_COMPLETED: WorkflowStage.BRIEF_GENERATED,
        WorkflowStage.BRIEF_GENERATED: WorkflowStage.CASE_COMPLETED,
    }
    _CHECKPOINT_ORDER = tuple(_NEXT_STAGE)
    _MAX_RESEARCH_RETRIES = 1

    def __init__(
        self,
        repository: PersistenceRepository,
        intake: CaseIntakeService,
        planner: ResearchPlanner,
        company_research: CompanyResearchService,
        executive_research: ExecutiveResearchService,
        evidence: EvidenceLayerService,
        verification: VerificationService,
        follow_up: FollowUpResearchService,
        governance: GovernanceService,
        analysis: StrategicAnalysisService,
        briefs: BriefGeneratorService,
        audit: AuditTrail | None = None,
    ) -> None:
        self._repository = repository
        self._intake = intake
        self._planner = planner
        self._company_research = company_research
        self._executive_research = executive_research
        self._evidence = evidence
        self._verification = verification
        self._follow_up = follow_up
        self._governance = governance
        self._analysis = analysis
        self._briefs = briefs
        self._audit = audit

    def execute(self, payload: Mapping[str, object], *, as_of: date) -> WorkflowExecutionResult:
        intake = self._intake.submit(payload)
        if intake.status is not IntakeStatus.ACCEPTED or intake.case is None:
            run = WorkflowRun(case_id="unpersisted", status=WorkflowRunStatus.FAILED)
            error = self._error("unpersisted", WorkflowErrorCode.INVALID_INPUT, "Case intake was rejected", WorkflowStage.CASE_VALIDATED)
            return WorkflowExecutionResult(status=WorkflowExecutionStatus.FAILED, workflow_run=run, state=WorkflowState(errors=[error]), errors=[error])
        state = WorkflowState(case_context=intake.case, current_stage=WorkflowStage.CASE_VALIDATED)
        run = self._repository.save_workflow_run(WorkflowRun(case_id=intake.case.case_id, current_stage=WorkflowStage.CASE_VALIDATED, snapshot=state))
        self._activate_audit(run, state)
        self._observe("RUN", "workflow_executor", "STARTED")
        checkpointed = self._checkpoint(run, state, WorkflowStage.CASE_VALIDATED, [("case", intake.case.case_id), ("workflow_run", run.run_id)])
        if checkpointed is None:
            return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "Case checkpoint could not be accepted")
        run = checkpointed
        return self._continue(run, state, as_of=as_of)

    def resume(self, run_id: str, *, as_of: date) -> WorkflowExecutionResult:
        run = self._repository.get_workflow_run(run_id)
        if run is None or run.snapshot is None or run.snapshot.case_context is None:
            state = WorkflowState()
            failed = WorkflowRun(run_id=run_id, case_id="unknown", status=WorkflowRunStatus.FAILED)
            return self._failed(failed, state, WorkflowErrorCode.WORKFLOW_FAILED, "workflow snapshot is unavailable")
        state = run.snapshot
        self._activate_audit(run, state)
        self._observe("RUN", "workflow_executor", "RESUMED")
        if state.case_context.case_id != run.case_id or self._repository.get_case(run.case_id) is None:
            return self._failed(run, WorkflowState(), WorkflowErrorCode.WORKFLOW_FAILED, "workflow snapshot Case does not match persisted run")
        checkpoint = self._repository.latest_accepted_checkpoint(run_id)
        if run.status is WorkflowRunStatus.COMPLETED:
            if checkpoint is not WorkflowStage.BRIEF_GENERATED:
                return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "completed workflow has no accepted Brief checkpoint")
            return WorkflowExecutionResult(status=WorkflowExecutionStatus.COMPLETED, workflow_run=run, state=state, brief=BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=state.quick_brief, full_brief=state.full_brief))
        if checkpoint is None:
            return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "workflow has no accepted checkpoint")
        if (
            run.status is WorkflowRunStatus.RUNNING
            and checkpoint in {
                WorkflowStage.VERIFICATION_COMPLETED,
                WorkflowStage.GOVERNANCE_COMPLETED,
                WorkflowStage.ANALYSIS_COMPLETED,
                WorkflowStage.BRIEF_GENERATED,
            }
            and self._repository.checkpoint_is_accepted(run_id, WorkflowStage.EVIDENCE_BUILT)
        ):
            # Research provenance is durable, but Verification, Governance, and
            # downstream trust are currentness-sensitive. Resume them from the
            # Evidence boundary so their owning services re-establish authority.
            checkpoint = WorkflowStage.EVIDENCE_BUILT
        accepted_state = self._last_valid_checkpoint_state(run, checkpoint)
        if accepted_state is None:
            return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "workflow has no valid accepted checkpoint snapshot")
        if run.status is not WorkflowRunStatus.RUNNING:
            status = WorkflowExecutionStatus.PARTIAL if run.status is WorkflowRunStatus.PARTIAL else WorkflowExecutionStatus.FAILED
            return WorkflowExecutionResult(status=status, workflow_run=run, state=accepted_state, errors=run.errors)
        if run.current_stage is not accepted_state.current_stage:
            run = self._repository.save_workflow_run(run.model_copy(update={
                "current_stage": accepted_state.current_stage,
                "snapshot": accepted_state,
            }))
        return self._continue(run, accepted_state, as_of=as_of)

    def _last_valid_checkpoint_state(self, run: WorkflowRun, latest: WorkflowStage) -> WorkflowState | None:
        """Fall back deterministically to the newest repository-accepted safe state."""
        try:
            latest_index = self._CHECKPOINT_ORDER.index(latest)
        except ValueError:
            return None
        for stage in reversed(self._CHECKPOINT_ORDER[: latest_index + 1]):
            state = run.accepted_snapshots.get(stage)
            if (
                self._repository.checkpoint_is_accepted(run.run_id, stage)
                and state is not None
                and state.current_stage is stage
                and state.case_context is not None
                and state.case_context.case_id == run.case_id
            ):
                return state
        return None

    def _continue(self, run: WorkflowRun, state: WorkflowState, *, as_of: date) -> WorkflowExecutionResult:
        case = state.case_context
        assert case is not None
        try:
            if state.current_stage is WorkflowStage.CASE_VALIDATED:
                self._observe_stage(state.current_stage, "STARTED")
                planned = self._planner.plan(case)
                if planned.status is not PlanningStatus.ACCEPTED or planned.plan is None:
                    return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "research planning was rejected")
                state = state.model_copy(update={"research_plan": planned.plan, "current_stage": WorkflowStage.RESEARCH_PLANNED})
                checkpointed = self._checkpoint(run, state, WorkflowStage.RESEARCH_PLANNED, [("case", case.case_id), ("workflow_run", run.run_id)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "research-plan checkpoint failed")
                run = checkpointed
                self._observe_stage(state.current_stage, "COMPLETED")
            if state.current_stage is WorkflowStage.RESEARCH_PLANNED:
                self._observe_stage(state.current_stage, "STARTED")
                findings, partial, run = self._research(case, state.research_plan, run)
                state = state.model_copy(update={"company_findings": findings[0], "executive_findings": findings[1], "current_stage": WorkflowStage.RESEARCH_COMPLETED})
                checkpointed = self._checkpoint(run, state, WorkflowStage.RESEARCH_COMPLETED, [("case", case.case_id), ("workflow_run", run.run_id)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "research checkpoint failed")
                run = checkpointed
                self._observe_stage(state.current_stage, "COMPLETED", {"finding_count": len(findings[0]) + len(findings[1])})
                if partial and not [*findings[0], *findings[1]]:
                    return self._partial(run, state, "research completed without retainable findings")
            if state.current_stage is WorkflowStage.RESEARCH_COMPLETED:
                claims = self._persist_findings(case, [*state.company_findings, *state.executive_findings])
                if not claims:
                    return self._partial(run, state, "no traceable candidate Claims were retained")
                state = state.model_copy(update={"claims": claims, "current_stage": WorkflowStage.EVIDENCE_BUILT})
                checkpointed = self._checkpoint(run, state, WorkflowStage.EVIDENCE_BUILT, [("case", case.case_id), ("workflow_run", run.run_id), *(("claim", item.claim_id) for item in claims)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "evidence checkpoint failed")
                run = checkpointed
            if state.current_stage is WorkflowStage.EVIDENCE_BUILT:
                self._observe_stage(state.current_stage, "STARTED")
                assessments = [self._verification.verify(item.claim_id, as_of=as_of) for item in state.claims]
                for assessment in assessments:
                    self._observe("VERIFICATION", "verification", assessment.status.value, target_id=assessment.claim.claim_id if assessment.claim else None, metadata={"result": assessment.verification.status.value if assessment.verification else None})
                self._follow_up_unresolved(case, state, assessments, as_of=as_of)
                assessments = [self._verification.verify(item.claim_id, as_of=as_of) for item in state.claims]
                state = state.model_copy(update={"verification_results": [item.verification for item in assessments if item.verification is not None], "current_stage": WorkflowStage.VERIFICATION_COMPLETED})
                checkpointed = self._checkpoint(run, state, WorkflowStage.VERIFICATION_COMPLETED, [("case", case.case_id), ("workflow_run", run.run_id), *(("claim", item.claim_id) for item in state.claims)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "verification checkpoint failed")
                run = checkpointed
                self._observe_stage(state.current_stage, "COMPLETED", {"claim_count": len(state.claims)})
            if state.current_stage is WorkflowStage.VERIFICATION_COMPLETED:
                self._observe_stage(state.current_stage, "STARTED")
                governance = [self._governance.evaluate(item.claim_id, as_of=as_of) for item in state.claims]
                for assessment in governance:
                    self._observe("GOVERNANCE", "governance", assessment.status.value, target_id=assessment.claim.claim_id if assessment.claim else None, metadata={"decision": assessment.decision.decision.value if assessment.decision else None})
                decisions = [item.decision for item in governance]
                if any(item is None for item in decisions):
                    return self._failed(run, state, WorkflowErrorCode.GOVERNANCE_BLOCKED, "Governance could not decide every persisted Claim")
                state = state.model_copy(update={"governance_decisions": [item for item in decisions if item is not None], "current_stage": WorkflowStage.GOVERNANCE_COMPLETED})
                checkpointed = self._checkpoint(run, state, WorkflowStage.GOVERNANCE_COMPLETED, [("case", case.case_id), ("workflow_run", run.run_id), *(("claim", item.claim_id) for item in state.claims)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "Governance checkpoint failed")
                run = checkpointed
                self._observe_stage(state.current_stage, "COMPLETED", {"decision_count": len(decisions)})
            if state.current_stage is WorkflowStage.GOVERNANCE_COMPLETED:
                analysis = self._analysis.analyze(case.case_id, as_of=as_of)
                if analysis.status is not StrategicAnalysisStatus.ACCEPTED or analysis.analysis is None:
                    return self._partial(run, state, "no current governed analysis is available")
                state = state.model_copy(update={"strategic_analysis": analysis.analysis, "current_stage": WorkflowStage.ANALYSIS_COMPLETED})
                checkpointed = self._checkpoint(run, state, WorkflowStage.ANALYSIS_COMPLETED, [("case", case.case_id), ("workflow_run", run.run_id)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "analysis checkpoint failed")
                run = checkpointed
            if state.current_stage is WorkflowStage.ANALYSIS_COMPLETED:
                # Analysis is currentness-sensitive and its controlled context is
                # intentionally transient; deterministically re-establish it
                # before final use without regenerating accepted semantics.
                if state.strategic_analysis is None:
                    return self._partial(run, state, "current governed analysis is unavailable")
                analysis_result = self._analysis.revalidate_current(case.case_id, state.strategic_analysis, as_of=as_of)
                if analysis_result.status is not StrategicAnalysisStatus.ACCEPTED:
                    return self._partial(run, state, "current governed analysis could not be re-established")
                brief = self._briefs.generate(case.case_id, analysis_result)
                if brief.status is not BriefGenerationStatus.ACCEPTED:
                    return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "Brief generation rejected the governed analysis")
                state = state.model_copy(update={"quick_brief": brief.quick_brief, "full_brief": brief.full_brief, "current_stage": WorkflowStage.BRIEF_GENERATED})
                checkpointed = self._checkpoint(run, state, WorkflowStage.BRIEF_GENERATED, [("case", case.case_id), ("workflow_run", run.run_id)])
                if checkpointed is None:
                    return self._failed(run, state, WorkflowErrorCode.PERSISTENCE_FAILED, "Brief checkpoint failed")
                run = checkpointed
                terminal = state.model_copy(update={"current_stage": WorkflowStage.CASE_COMPLETED})
                completed = self._repository.save_workflow_run(run.model_copy(update={"status": WorkflowRunStatus.COMPLETED, "current_stage": WorkflowStage.CASE_COMPLETED, "snapshot": terminal}))
                self._observe("TERMINAL", "workflow_executor", "COMPLETED")
                return WorkflowExecutionResult(status=WorkflowExecutionStatus.COMPLETED, workflow_run=completed, state=terminal, brief=brief)
        except Exception:
            return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "workflow stage failed safely")
        return self._failed(run, state, WorkflowErrorCode.WORKFLOW_FAILED, "workflow state has no legal continuation")

    def _research(self, case: Case, plan, run: WorkflowRun) -> tuple[tuple[list[RawFinding], list[RawFinding]], bool, WorkflowRun]:
        company: list[RawFinding] = []
        executive: list[RawFinding] = []
        retained_source_urls: set[str] = set()
        retained_content: set[str] = set()
        partial = False
        for task in plan.tasks:
            result: CompanyResearchResult | ExecutiveResearchResult
            if task.target_type is TargetType.COMPANY:
                result = self._company_research.research(case, task, excluded_source_urls=retained_source_urls, excluded_content=retained_content)
                if result.retryable_provider_failure is True and run.retry_count < self._MAX_RESEARCH_RETRIES:
                    run = self._repository.save_workflow_run(run.model_copy(update={"retry_count": run.retry_count + 1}))
                    self._observe("RETRY", "workflow_executor", "PERFORMED", metadata={"retry_count": run.retry_count})
                    result = self._company_research.research(case, task, excluded_source_urls=retained_source_urls, excluded_content=retained_content)
                company.extend(result.findings)
                retained_source_urls.update(_finding_urls(result.findings))
                retained_content.update(_finding_content(result.findings))
                partial |= result.status is not CompanyResearchStatus.COMPLETED
            else:
                result = self._executive_research.research(case, task, excluded_source_urls=retained_source_urls, excluded_content=retained_content)
                if result.retryable_provider_failure is True and run.retry_count < self._MAX_RESEARCH_RETRIES:
                    run = self._repository.save_workflow_run(run.model_copy(update={"retry_count": run.retry_count + 1}))
                    self._observe("RETRY", "workflow_executor", "PERFORMED", metadata={"retry_count": run.retry_count})
                    result = self._executive_research.research(case, task, excluded_source_urls=retained_source_urls, excluded_content=retained_content)
                executive.extend(result.findings)
                retained_source_urls.update(_finding_urls(result.findings))
                retained_content.update(_finding_content(result.findings))
                partial |= result.status is not ExecutiveResearchStatus.COMPLETED
        return (company, executive), partial, run

    def _persist_findings(self, case: Case, findings: list[RawFinding]) -> list[Claim]:
        claims: list[Claim] = []
        seen: set[str] = set()
        existing = {item.text: item for item in self._repository.list_claims(case.case_id)}
        for finding in findings:
            if finding.case_id != case.case_id or finding.extracted_content in seen:
                continue
            if persisted := existing.get(finding.extracted_content):
                claims.append(persisted)
                seen.add(finding.extracted_content)
                continue
            result = self._evidence.create_candidate(finding, claim_text=finding.extracted_content)
            if result.status is EvidenceLayerStatus.ACCEPTED and result.candidate_claim is not None:
                claims.append(result.candidate_claim)
                seen.add(finding.extracted_content)
        return claims

    def _follow_up_unresolved(self, case: Case, state: WorkflowState, assessments: list[VerificationAssessment], *, as_of: date) -> None:
        """Delegate a single bounded C12 follow-up to its existing authority."""
        if state.research_plan is None:
            return
        unresolved = {
            item.verification.claim_id
            for item in assessments
            if item.status is VerificationAssessmentStatus.ACCEPTED
            and item.verification is not None
            and item.verification.status not in {VerificationStatus.VERIFIED, VerificationStatus.SUPPORTED}
        }
        for claim in state.claims:
            if claim.claim_id not in unresolved:
                continue
            task = self._follow_up_task(state, claim)
            if task is None:
                continue
            self._follow_up.run(case, claim.claim_id, task, self._discover, as_of=as_of)

    def _follow_up_task(self, state: WorkflowState, claim: Claim) -> ResearchTask | None:
        finding_ids = {
            finding.research_task_id
            for finding in [*state.company_findings, *state.executive_findings]
            if finding.extracted_content == claim.text
        }
        return next((task for task in (state.research_plan.tasks if state.research_plan else []) if task.research_task_id in finding_ids), None)

    def _discover(self, case: Case, task: ResearchTask) -> list[RawFinding]:
        if task.target_type is TargetType.COMPANY:
            return self._company_research.research(case, task).findings
        return self._executive_research.research(case, task).findings

    def _checkpoint(self, run: WorkflowRun, state: WorkflowState, stage: WorkflowStage, records: list[tuple[str, str]]) -> WorkflowRun | None:
        if (
            state.case_context is None
            or state.case_context.case_id != run.case_id
            or state.current_stage is not stage
            or (
                run.current_stage is not None
                and run.current_stage is not stage
                and self._NEXT_STAGE.get(run.current_stage) is not stage
            )
        ):
            return None
        try:
            snapshots = {**run.accepted_snapshots, stage: state}
            persisted = self._repository.save_workflow_run(run.model_copy(update={
                "current_stage": stage, "snapshot": state, "accepted_snapshots": snapshots,
            }))
            self._repository.accept_checkpoint(persisted.run_id, stage, records)
            self._observe("CHECKPOINT", "repository", "ACCEPTED", metadata={"required_record_count": len(records)})
            return persisted
        except Exception:
            self._observe("CHECKPOINT", "repository", "REJECTED")
            return None

    def _partial(self, run: WorkflowRun, state: WorkflowState, message: str) -> WorkflowExecutionResult:
        error = self._error(run.case_id, WorkflowErrorCode.INSUFFICIENT_EVIDENCE, message, state.current_stage)
        persisted = self._repository.save_workflow_run(run.model_copy(update={"status": WorkflowRunStatus.PARTIAL, "current_stage": state.current_stage, "errors": [*run.errors, error], "snapshot": state.model_copy(update={"errors": [*state.errors, error]})}))
        self._observe("ERROR", "workflow_executor", error.error_code.value, metadata={"retryable": error.retryable})
        self._observe("TERMINAL", "workflow_executor", "PARTIAL")
        return WorkflowExecutionResult(status=WorkflowExecutionStatus.PARTIAL, workflow_run=persisted, state=persisted.snapshot or state, errors=[error])

    def _failed(self, run: WorkflowRun, state: WorkflowState, code: WorkflowErrorCode, message: str) -> WorkflowExecutionResult:
        error = self._error(run.case_id, code, message, state.current_stage)
        persisted = self._repository.save_workflow_run(run.model_copy(update={"status": WorkflowRunStatus.FAILED, "errors": [*run.errors, error], "snapshot": state.model_copy(update={"errors": [*state.errors, error]})}))
        self._observe("ERROR", "workflow_executor", error.error_code.value, metadata={"retryable": error.retryable})
        self._observe("TERMINAL", "workflow_executor", "FAILED")
        return WorkflowExecutionResult(status=WorkflowExecutionStatus.FAILED, workflow_run=persisted, state=persisted.snapshot or state, errors=[error])

    def _activate_audit(self, run: WorkflowRun, state: WorkflowState) -> None:
        if self._audit is not None and state.case_context is not None:
            self._audit.activate(state.case_context.case_id, run.run_id, state.current_stage)

    def _observe_stage(self, stage: WorkflowStage, status: str, metadata: dict[str, str | int | float | bool | None] | None = None) -> None:
        if self._audit is not None:
            self._audit.stage(stage)
        self._observe("STAGE", "workflow_executor", status, metadata=metadata)

    def _observe(self, event_type: str, component: str, status: str, *, target_id: str | None = None, metadata: dict[str, str | int | float | bool | None] | None = None) -> None:
        if self._audit is not None:
            self._audit.record(event_type, component, status, target_id=target_id, metadata=metadata)

    @staticmethod
    def _error(case_id: str, code: WorkflowErrorCode, message: str, stage: WorkflowStage | None) -> WorkflowError:
        return WorkflowError(case_id=case_id, component="workflow_executor", error_code=code, message=message, stage=stage)


def _finding_urls(findings: list[RawFinding]) -> set[str]:
    """Return run-scoped canonical discovery identities for retained findings."""

    urls: set[str] = set()
    for finding in findings:
        for value in (finding.source_url, finding.discovery_url):
            if value is None:
                continue
            try:
                urls.add(normalize_external_url(value))
            except UnsafeExternalUrlError:
                continue
    return urls


def _finding_content(findings: list[RawFinding]) -> set[str]:
    return {" ".join(finding.extracted_content.casefold().split()) for finding in findings}
