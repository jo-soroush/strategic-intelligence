"""Public application composition for the C18 workflow boundary.

The local UI consumes this facade rather than constructing persistence,
providers, or individual trust services.  It wires existing owners only; all
workflow, trust, retry, and recovery behaviour remains in those owners.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from strategic_intelligence.application.brief_generator import BriefGeneratorService
from strategic_intelligence.application.case_input import CaseIntakeService
from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.executive_research import ExecutiveResearchService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.research_planning import ResearchPlanner
from strategic_intelligence.application.strategic_analysis import StrategicAnalysisService
from strategic_intelligence.application.source_acquisition import PublicSourceRetriever
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.config import Settings
from strategic_intelligence.evaluation.golden_case import GoldenCaseRuntimeSnapshot
from strategic_intelligence.governance.engine import GovernanceService
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult, WorkflowExecutor
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.observability.audit import AuditReport, AuditTrail, ObservedLLMProvider, ObservedSearchProvider
from strategic_intelligence.providers.factory import Providers, build_providers


class WorkflowApplication:
    """Application-owned entry point for executing or resuming the V1 workflow."""

    def __init__(self, executor: WorkflowExecutor, repository: SqliteRepository, audit: AuditTrail) -> None:
        self._executor = executor
        self._repository = repository
        self._audit = audit

    @classmethod
    def from_environment(cls) -> "WorkflowApplication":
        """Build the local-first runtime from the approved environment settings."""
        return cls.from_settings(Settings.from_environment())

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        *,
        providers: Providers | None = None,
    ) -> "WorkflowApplication":
        """Build one runtime using approved persistence and provider boundaries.

        ``providers`` is an explicit application/test composition seam.  Local
        presentation callers use :meth:`from_environment` and never construct
        individual services.
        """
        resolved_providers = providers or build_providers(settings)
        repository = SqliteRepository(settings.database_path)
        audit = AuditTrail(repository)
        observed = Providers(llm=ObservedLLMProvider(resolved_providers.llm, audit), search=ObservedSearchProvider(resolved_providers.search, audit))
        verification = VerificationService(repository)
        evidence = EvidenceLayerService(repository)
        source_retriever = None if settings.search_provider == "fake" else PublicSourceRetriever(audit=audit)
        executor = WorkflowExecutor(
            repository,
            CaseIntakeService(repository),
            ResearchPlanner(llm=observed.llm),
            CompanyResearchService(observed.search, source_retriever=source_retriever),
            ExecutiveResearchService(observed.search, source_retriever=source_retriever),
            evidence,
            verification,
            FollowUpResearchService(repository, evidence, verification),
            GovernanceService(repository, verification),
            StrategicAnalysisService(repository, observed.llm, verification, audit=audit),
            BriefGeneratorService(repository),
            audit=audit,
        )
        return cls(executor, repository, audit)

    def execute(self, payload: Mapping[str, object], *, as_of: date) -> WorkflowExecutionResult:
        """Delegate first-run execution to the C18 workflow authority."""
        return self._executor.execute(payload, as_of=as_of)

    def resume(self, run_id: str, *, as_of: date) -> WorkflowExecutionResult:
        """Delegate recovery to the C18 accepted-checkpoint authority."""
        return self._executor.resume(run_id, as_of=as_of)

    def audit_report(self, run_id: str) -> AuditReport:
        """Return C19's typed, redacted reconstruction for one workflow run."""
        return self._audit.report(run_id)

    def golden_case_snapshot(self, run_id: str) -> GoldenCaseRuntimeSnapshot:
        """Expose persisted C03/C19 truth for post-run C20 evaluation only."""
        run = self._repository.get_workflow_run(run_id)
        if run is None:
            raise KeyError("workflow run was not found")
        claims = self._repository.list_claims(run.case_id)
        evidence = [
            item for claim in claims for evidence_id in claim.evidence_ids
            if (item := self._repository.get_evidence(evidence_id)) is not None
        ]
        sources = [
            item for evidence_item in evidence
            if (item := self._repository.get_source(evidence_item.source_id)) is not None
        ]
        state = run.snapshot
        return GoldenCaseRuntimeSnapshot(
            workflow_run=run, claims=claims, evidence=evidence, sources=sources,
            verification_results=[] if state is None else state.verification_results,
            governance_decisions=[] if state is None else state.governance_decisions,
            audit_report=self.audit_report(run_id),
        )

    def close(self) -> None:
        """Release the local repository after the owning presentation exits."""
        self._repository.close()
