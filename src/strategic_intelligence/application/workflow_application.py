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
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.config import Settings
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
        executor = WorkflowExecutor(
            repository,
            CaseIntakeService(repository),
            ResearchPlanner(llm=observed.llm),
            CompanyResearchService(observed.search),
            ExecutiveResearchService(observed.search),
            evidence,
            verification,
            FollowUpResearchService(repository, evidence, verification),
            GovernanceService(repository, verification),
            StrategicAnalysisService(repository, observed.llm, verification),
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

    def close(self) -> None:
        """Release the local repository after the owning presentation exits."""
        self._repository.close()
