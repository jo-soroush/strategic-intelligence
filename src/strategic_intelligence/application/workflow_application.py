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
from strategic_intelligence.providers.factory import Providers, build_providers


class WorkflowApplication:
    """Application-owned entry point for executing or resuming the V1 workflow."""

    def __init__(self, executor: WorkflowExecutor, repository: SqliteRepository) -> None:
        self._executor = executor
        self._repository = repository

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
        verification = VerificationService(repository)
        evidence = EvidenceLayerService(repository)
        executor = WorkflowExecutor(
            repository,
            CaseIntakeService(repository),
            ResearchPlanner(llm=resolved_providers.llm),
            CompanyResearchService(resolved_providers.search),
            ExecutiveResearchService(resolved_providers.search),
            evidence,
            verification,
            FollowUpResearchService(repository, evidence, verification),
            GovernanceService(repository, verification),
            StrategicAnalysisService(repository, resolved_providers.llm, verification),
            BriefGeneratorService(repository),
        )
        return cls(executor, repository)

    def execute(self, payload: Mapping[str, object], *, as_of: date) -> WorkflowExecutionResult:
        """Delegate first-run execution to the C18 workflow authority."""
        return self._executor.execute(payload, as_of=as_of)

    def resume(self, run_id: str, *, as_of: date) -> WorkflowExecutionResult:
        """Delegate recovery to the C18 accepted-checkpoint authority."""
        return self._executor.resume(run_id, as_of=as_of)

    def close(self) -> None:
        """Release the local repository after the owning presentation exits."""
        self._repository.close()
