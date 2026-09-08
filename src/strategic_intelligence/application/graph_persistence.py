"""G05 local graph projection and bounded traversal primitives."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.application.relationship_extraction import (
    GovernedRelationshipExtractor,
    RelationshipExtractionStatus,
)
from strategic_intelligence.domain.models import (
    EntityRecord,
    GovernanceDecisionStatus,
    GraphNode,
    RelationshipRecord,
    RelationshipTemporalStatus,
)


@dataclass(frozen=True)
class GraphProjectionResult:
    projected_relationship_ids: tuple[str, ...] = ()
    rejected_relationship_ids: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class GraphIntegrityReport:
    valid: bool
    orphan_edge_ids: tuple[str, ...] = ()
    invalid_edge_ids: tuple[str, ...] = ()
    duplicate_canonical_keys: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()


class GraphPersistenceService:
    """Persists only a rebuildable projection of canonical intelligence."""

    _MAX_HOPS = 3

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository
        self._extractor = GovernedRelationshipExtractor(repository)

    def project(self, relationships: Sequence[RelationshipRecord]) -> GraphProjectionResult:
        projected: list[str] = []
        rejected: list[str] = []
        reasons: list[str] = []
        for relationship in relationships:
            try:
                validated = self._validate_relationship(relationship)
                self._persist_node(validated.source_entity_id)
                self._persist_node(validated.target_entity_id)
                self._repository.save_graph_edge(validated, self._canonical_key(validated))
                projected.append(validated.relationship_id)
            except (KeyError, ValueError) as error:
                rejected.append(relationship.relationship_id)
                reasons.append(f"{relationship.relationship_id}: {error}")
        return GraphProjectionResult(tuple(projected), tuple(rejected), tuple(reasons))

    def rebuild(self) -> tuple[tuple[GraphNode, ...], tuple[RelationshipRecord, ...]]:
        """Reconstruct the projection from durable graph rows after restart."""
        return (tuple(self._repository.list_graph_nodes()), tuple(self._repository.list_graph_edges()))

    def rebuild_from_canonical(self, relationships: Sequence[RelationshipRecord]) -> GraphProjectionResult:
        """Reconcile canonical G04 output without deleting historical projection rows."""
        return self.project(relationships)

    def integrity_check(self) -> GraphIntegrityReport:
        nodes = {node.entity_id: node for node in self._repository.list_graph_nodes()}
        orphan: list[str] = []
        invalid: list[str] = []
        duplicate: list[str] = []
        reasons: list[str] = []
        keys: set[str] = set()
        for node in nodes.values():
            entity = self._repository.get_entity(node.entity_id)
            if entity is None or not self._node_matches_entity(node, entity):
                reasons.append(f"node {node.entity_id} does not match canonical entity")
        for edge in self._repository.list_graph_edges():
            key = self._canonical_key(edge)
            if key in keys:
                duplicate.append(key)
            keys.add(key)
            if edge.source_entity_id not in nodes or edge.target_entity_id not in nodes:
                orphan.append(edge.relationship_id)
                continue
            try:
                self._validate_relationship(edge)
            except (KeyError, ValueError) as error:
                invalid.append(edge.relationship_id)
                reasons.append(f"{edge.relationship_id}: {error}")
        return GraphIntegrityReport(
            valid=not orphan and not invalid and not duplicate and not reasons,
            orphan_edge_ids=tuple(orphan),
            invalid_edge_ids=tuple(invalid),
            duplicate_canonical_keys=tuple(duplicate),
            reasons=tuple(reasons),
        )

    def neighbors(self, entity_id: str) -> tuple[RelationshipRecord, ...]:
        return tuple(
            edge
            for edge in self._repository.list_graph_edges()
            if edge.usable
            and edge.governance_status is GovernanceDecisionStatus.PASS
            and edge.temporal_status is RelationshipTemporalStatus.CURRENT
            and (edge.source_entity_id == entity_id or edge.target_entity_id == entity_id)
        )

    def bounded_paths(self, start_entity_id: str, target_entity_id: str | None = None, *, max_hops: int = 3) -> tuple[tuple[RelationshipRecord, ...], ...]:
        if max_hops < 1 or max_hops > self._MAX_HOPS:
            raise ValueError("graph traversal depth must be between 1 and 3")
        if self._repository.get_graph_node(start_entity_id) is None:
            return ()
        paths: list[tuple[RelationshipRecord, ...]] = []

        def visit(current: str, visited: set[str], path: tuple[RelationshipRecord, ...]) -> None:
            if path and (target_entity_id is None or current == target_entity_id):
                paths.append(path)
                if target_entity_id is not None:
                    return
            if len(path) >= max_hops:
                return
            for edge in self.neighbors(current):
                nxt = edge.target_entity_id if edge.source_entity_id == current else edge.source_entity_id
                if nxt in visited:
                    continue
                visit(nxt, visited | {nxt}, (*path, edge))

        visit(start_entity_id, {start_entity_id}, ())
        return tuple(paths)

    def _validate_relationship(self, relationship: RelationshipRecord) -> RelationshipRecord:
        result = self._extractor.extract(
            relationship.relation_type,
            relationship.source_entity_id,
            relationship.target_entity_id,
            relationship.claim_ids,
            relationship.evidence_ids,
            relationship.research_run_id,
            valid_from=relationship.valid_from,
            valid_to=relationship.valid_to,
            superseded_by=relationship.superseded_by,
        )
        if result.status is not RelationshipExtractionStatus.ACCEPTED or result.relationship is None:
            raise ValueError(result.reason or "relationship failed canonical trust validation")
        canonical = result.relationship
        for field in (
            "source_entity_id", "target_entity_id", "relation_type", "claim_ids",
            "evidence_ids", "source_ids", "governance_ids", "governance_status",
            "research_run_id", "valid_from", "valid_to", "superseded_by",
            "temporal_status", "usable",
        ):
            if getattr(relationship, field) != getattr(canonical, field):
                raise ValueError(f"relationship {field} disagrees with canonical proof")
        return relationship

    def _persist_node(self, entity_id: str) -> GraphNode:
        entity = self._repository.get_entity(entity_id)
        if entity is None:
            raise KeyError(f"canonical entity not found: {entity_id}")
        node = GraphNode(
            entity_id=entity.entity_id,
            entity_type=entity.entity_type,
            canonical_name=entity.canonical_name,
            normalized_name=entity.normalized_name,
        )
        return self._repository.save_graph_node(node)

    @staticmethod
    def _node_matches_entity(node: GraphNode, entity: EntityRecord) -> bool:
        return (
            node.entity_type is entity.entity_type
            and node.canonical_name == entity.canonical_name
            and node.normalized_name == entity.normalized_name
        )

    @staticmethod
    def _canonical_key(relationship: RelationshipRecord) -> str:
        def stamp(value: datetime | None) -> str:
            return "" if value is None else value.isoformat()

        return "|".join((
            relationship.relation_type.value,
            relationship.source_entity_id,
            relationship.target_entity_id,
            relationship.research_run_id,
            stamp(relationship.valid_from),
            stamp(relationship.valid_to),
            relationship.superseded_by or "",
        ))
