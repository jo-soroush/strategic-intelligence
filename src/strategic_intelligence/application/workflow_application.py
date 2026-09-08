"""Public application composition for the C18 workflow boundary.

The local UI consumes this facade rather than constructing persistence,
providers, or individual trust services.  It wires existing owners only; all
workflow, trust, retry, and recovery behaviour remains in those owners.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

from strategic_intelligence.application.brief_generator import BriefGenerationResult, BriefGenerationStatus, BriefGeneratorService
from strategic_intelligence.application.case_input import CaseIntakeService
from strategic_intelligence.application.company_memory import CompanyMemoryService
from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.executive_research import ExecutiveResearchService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.graph_persistence import GraphPersistenceService
from strategic_intelligence.application.graph_rag import EvidenceBackedGraphRAG, GraphProvenance, GraphQuestion, GraphRAGResult, GraphRAGStatus
from strategic_intelligence.application.research_planning import ResearchPlanner
from strategic_intelligence.application.strategic_analysis import StrategicAnalysisService
from strategic_intelligence.application.source_acquisition import PublicSourceRetriever
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.config import Settings
from strategic_intelligence.evaluation.golden_case import GoldenCaseRuntimeSnapshot
from strategic_intelligence.governance.engine import GovernanceService
from strategic_intelligence.harness.workflow_executor import WorkflowExecutionResult, WorkflowExecutionStatus, WorkflowExecutor
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.observability.audit import AuditReport, AuditTrail, ObservedLLMProvider, ObservedSearchProvider
from strategic_intelligence.providers.factory import Providers, build_providers
from strategic_intelligence.domain.models import GraphNode, RelationshipRecord, TrackedCompany


class WorkflowApplication:
    """Application-owned entry point for executing or resuming the V1 workflow."""

    def __init__(self, executor: WorkflowExecutor, repository: SqliteRepository, audit: AuditTrail, memory: CompanyMemoryService, graph_rag: EvidenceBackedGraphRAG | None = None) -> None:
        self._executor = executor
        self._repository = repository
        self._audit = audit
        self._memory = memory
        self._graph_rag = graph_rag

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
        return cls(executor, repository, audit, CompanyMemoryService(repository), EvidenceBackedGraphRAG(repository, observed.llm))

    def companies_in_memory(self) -> list[TrackedCompany]:
        """Read ordered durable company memory without research side effects."""
        return self._repository.list_tracked_companies()

    def stored_company_result(self, tracked_company_id: str) -> WorkflowExecutionResult | None:
        tracked = self._repository.get_tracked_company(tracked_company_id)
        if tracked is None or tracked.active_run_id is None:
            return None
        run = self._repository.get_workflow_run(tracked.active_run_id)
        if run is None or run.snapshot is None:
            return None
        return self._result_from_persisted_run(run)

    def graph_nodes(self) -> list[GraphNode]:
        return GraphPersistenceService(self._repository).rebuild()[0]

    def graph_edges(self) -> list[RelationshipRecord]:
        return GraphPersistenceService(self._repository).rebuild()[1]

    def graph_provenance(self, relationship_id: str) -> tuple[GraphProvenance, ...]:
        edge = self._repository.get_graph_edge(relationship_id)
        if edge is None or self._graph_rag is None:
            return ()
        return self._graph_rag.provenance_for_relationship(edge)

    def ask_graph(self, query: GraphQuestion) -> GraphRAGResult:
        if self._graph_rag is None:
            return GraphRAGResult(status=GraphRAGStatus.REJECTED, reason="GraphRAG is not configured")
        return self._graph_rag.answer(query)

    def execute(self, payload: Mapping[str, object], *, as_of: date, refresh: bool = False) -> WorkflowExecutionResult:
        """Load active company memory first, or execute a new explicit run."""
        company_name = str(payload.get("company_name", ""))
        tracked = None if refresh else self._memory.lookup(company_name)
        if tracked is not None and tracked.active_run_id:
            run = self._repository.get_workflow_run(tracked.active_run_id)
            if run is not None and run.snapshot is not None:
                return self._result_from_persisted_run(run)
        result = self._executor.execute(payload, as_of=as_of)
        case = result.state.case_context
        if case is not None:
            self._memory.record_run(
                company_id=case.company_id,
                company_name=case.company_name,
                run_id=result.workflow_run.run_id,
                successful=result.status is WorkflowExecutionStatus.COMPLETED,
            )
        return result

    def refresh(self, payload: Mapping[str, object], *, as_of: date) -> WorkflowExecutionResult:
        """Run explicit refresh while preserving the prior active memory run."""
        return self.execute(payload, as_of=as_of, refresh=True)

    @staticmethod
    def _result_from_persisted_run(run) -> WorkflowExecutionResult:
        state = run.snapshot
        assert state is not None
        if run.status.value == "COMPLETED":
            brief = BriefGenerationResult(status=BriefGenerationStatus.ACCEPTED, quick_brief=state.quick_brief, full_brief=state.full_brief)
            return WorkflowExecutionResult(status=WorkflowExecutionStatus.COMPLETED, workflow_run=run, state=state, brief=brief)
        status = WorkflowExecutionStatus.PARTIAL if run.status.value == "PARTIAL" else WorkflowExecutionStatus.FAILED
        return WorkflowExecutionResult(status=status, workflow_run=run, state=state, errors=run.errors)

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
