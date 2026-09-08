from pathlib import Path

import pytest

from strategic_intelligence.application.graph_persistence import GraphPersistenceService
from strategic_intelligence.application.relationship_extraction import GovernedRelationshipExtractor
from strategic_intelligence.domain.models import RelationshipTemporalStatus, RelationshipType, VerificationStatus
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from tests.unit.test_relationship_extraction import _fixture


def test_projection_is_incremental_idempotent_and_restart_safe(tmp_path: Path) -> None:
    database = tmp_path / "relationships.db"
    source_repository, person, company, claim, evidence = _fixture(tmp_path)
    try:
        relationship = GovernedRelationshipExtractor(source_repository).extract(
            RelationshipType.LEADS, person.entity_id, company.entity_id,
            [claim.claim_id], [evidence.evidence_id], "run-1",
        ).relationship
        assert relationship is not None
        graph = GraphPersistenceService(source_repository)
        first = graph.project([relationship])
        second = graph.project([relationship])
        reconciled = graph.rebuild_from_canonical([relationship])
        assert first.projected_relationship_ids == (relationship.relationship_id,)
        assert second.projected_relationship_ids == (relationship.relationship_id,)
        assert reconciled.projected_relationship_ids == (relationship.relationship_id,)
        assert graph.integrity_check().valid
    finally:
        source_repository.close()
    reopened = SqliteRepository(database)
    try:
        nodes, edges = GraphPersistenceService(reopened).rebuild()
        assert len(nodes) == 2 and edges == (relationship,)
        assert GraphPersistenceService(reopened).integrity_check().valid
    finally:
        reopened.close()


def test_projection_rejects_forged_or_duplicate_canonical_edges(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _fixture(tmp_path)
    try:
        relationship = GovernedRelationshipExtractor(repository).extract(
            RelationshipType.LEADS, person.entity_id, company.entity_id,
            [claim.claim_id], [evidence.evidence_id], "run-1",
        ).relationship
        assert relationship is not None
        graph = GraphPersistenceService(repository)
        assert graph.project([relationship]).rejected_relationship_ids == ()
        duplicate = relationship.model_copy(update={"relationship_id": "different-id"})
        result = graph.project([duplicate])
        assert result.rejected_relationship_ids == ("different-id",)
        forged = relationship.model_copy(update={"source_entity_id": "forged-entity"})
        assert graph.project([forged]).rejected_relationship_ids == (relationship.relationship_id,)
        repository._connection.execute("DELETE FROM graph_nodes WHERE id = ?", (company.entity_id,))
        report = graph.integrity_check()
        assert report.valid is False and report.orphan_edge_ids == (relationship.relationship_id,)
    finally:
        repository.close()


def test_bounded_traversal_excludes_non_current_relationships(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _fixture(tmp_path, verification=VerificationStatus.STALE)
    try:
        relationship = GovernedRelationshipExtractor(repository).extract(
            RelationshipType.LEADS, person.entity_id, company.entity_id,
            [claim.claim_id], [evidence.evidence_id], "run-1",
        ).relationship
        assert relationship is not None
        assert relationship.temporal_status is RelationshipTemporalStatus.STALE
        graph = GraphPersistenceService(repository)
        graph.project([relationship])
        assert graph.neighbors(person.entity_id) == ()
        assert graph.bounded_paths(person.entity_id, company.entity_id) == ()
        with pytest.raises(ValueError, match="between 1 and 3"):
            graph.bounded_paths(person.entity_id, max_hops=4)
    finally:
        repository.close()
