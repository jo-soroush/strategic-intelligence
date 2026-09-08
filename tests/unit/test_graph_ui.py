from datetime import date
from io import BytesIO
from pathlib import Path
from urllib.parse import urlencode

from strategic_intelligence.application.graph_rag import GraphProvenance, GraphRAGResult, GraphRAGStatus
from strategic_intelligence.domain.models import EntityType, GraphNode, GovernanceDecisionStatus, RelationshipRecord, RelationshipTemporalStatus, RelationshipType, TrackedCompany
from strategic_intelligence.ui.local_app import LocalUi

from tests.unit.test_local_ui import _completed


class _GraphUiWorkflow:
    def __init__(self) -> None:
        self.refresh_calls: list[dict[str, str]] = []
        self.execute_calls: list[dict[str, str]] = []
        self.ask_calls = []
        self.result = _completed()
        self.company = TrackedCompany(company_id="co", display_name="Example Co", exact_name="Example Co", normalized_name="example co", insertion_order=0, run_ids=["run-1"], active_run_id="run-1")
        self.node = GraphNode(entity_id="entity-1", entity_type=EntityType.COMPANY, canonical_name="Example Co", normalized_name="example co")
        self.edge = RelationshipRecord(source_entity_id="entity-1", target_entity_id="entity-2", relation_type=RelationshipType.USES, claim_ids=["claim-1"], evidence_ids=["evidence-1"], source_ids=["source-1"], governance_ids=["governance-1"], governance_status=GovernanceDecisionStatus.PASS, research_run_id="run-1", temporal_status=RelationshipTemporalStatus.CURRENT, usable=True)

    def companies_in_memory(self):
        return [self.company]

    def stored_company_result(self, tracked_company_id):
        return self.result if tracked_company_id == self.company.tracked_company_id else None

    def graph_nodes(self):
        return [self.node]

    def graph_edges(self):
        return [self.edge]

    def graph_provenance(self, relationship_id):
        return (GraphProvenance("rel", "claim-1", "evidence-1", "source-1", "governance-1", GovernanceDecisionStatus.PASS, "run-1", RelationshipTemporalStatus.CURRENT, "Example uses Nova.", "Example uses Nova.", "Example source", "https://example.test/source"),)

    def ask_graph(self, query):
        self.ask_calls.append(query)
        return GraphRAGResult(GraphRAGStatus.NO_PATH, reason="No supported graph path exists.")

    def refresh(self, payload, *, as_of: date):
        self.refresh_calls.append(dict(payload))
        return self.result

    def execute(self, payload, *, as_of: date):
        self.execute_calls.append(dict(payload))
        return self.result


def _call(ui: LocalUi, *, method: str, path: str, values: dict[str, str] | None = None, query: str = ""):
    raw = urlencode(values or {}).encode()
    captured = {}
    body = ui({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query, "CONTENT_LENGTH": str(len(raw)), "wsgi.input": BytesIO(raw)}, lambda status, headers: captured.update(status=status))
    return captured["status"], b"".join(body).decode()


def test_memory_open_is_read_only_and_refresh_is_explicit() -> None:
    workflow = _GraphUiWorkflow()
    ui = LocalUi(workflow)
    status, page = _call(ui, method="GET", path="/memory", query=f"tracked={workflow.company.tracked_company_id}")
    assert status == "200 OK"
    assert "Loaded from durable memory" in page
    assert workflow.execute_calls == [] and workflow.refresh_calls == []
    status, _ = _call(ui, method="POST", path="/refresh", values={"company_name": "Example Co", "executive_name": "Ava", "meeting_goal": "Prepare"})
    assert status == "200 OK"
    assert workflow.refresh_calls == [{"company_name": "Example Co", "executive_name": "Ava", "meeting_goal": "Prepare"}]
    assert workflow.execute_calls == []


def test_graph_view_inspects_edges_and_safe_provenance() -> None:
    workflow = _GraphUiWorkflow()
    status, page = _call(LocalUi(workflow), method="GET", path="/graph")
    assert status == "200 OK"
    for text in ("Graph View", "USES", "claim-1", "evidence-1", "Example source", "PASS", "run-1", "CURRENT"):
        assert text in page
    assert "https://example.test/source" in page


def test_ask_graph_uses_read_only_g06_boundary() -> None:
    workflow = _GraphUiWorkflow()
    status, page = _call(LocalUi(workflow), method="POST", path="/ask-graph", values={
        "question": "What uses Example Co?", "category": "direct_relationship",
        "entity_label_1": "Example Co", "entity_type_1": "Company",
    })
    assert status == "200 OK"
    assert "No Path" in page
    assert len(workflow.ask_calls) == 1
    assert workflow.execute_calls == [] and workflow.refresh_calls == []
