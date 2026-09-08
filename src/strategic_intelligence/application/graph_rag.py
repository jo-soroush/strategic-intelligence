"""G06 evidence-backed GraphRAG over the bounded G05 projection."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Sequence

from strategic_intelligence.application.entity_resolution import (
    EntityResolutionService,
    ResolutionStatus,
    canonicalize_entity_label,
)
from strategic_intelligence.application.graph_persistence import GraphPersistenceService
from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.domain.models import (
    ClaimEvidenceRelationship,
    EntityType,
    GovernanceDecisionStatus,
    RelationshipRecord,
    RelationshipTemporalStatus,
)
from strategic_intelligence.providers.contracts import LLMProvider, LLMRequest


class GraphQueryCategory(str, Enum):
    DIRECT_RELATIONSHIP = "direct_relationship"
    NEIGHBORHOOD = "neighborhood"
    SHARED_CONNECTION = "shared_connection"
    CROSS_COMPANY_RELATIONSHIP = "cross_company_relationship"
    RECURRING_ENTITY = "recurring_entity"
    BOUNDED_MULTI_HOP_PATH = "bounded_multi_hop_path"


class GraphRAGStatus(str, Enum):
    ANSWERED = "ANSWERED"
    NO_PATH = "NO_PATH"
    REJECTED = "REJECTED"
    PROVIDER_FAILED = "PROVIDER_FAILED"


@dataclass(frozen=True)
class GraphEntityHint:
    label: str
    entity_type: EntityType


@dataclass(frozen=True)
class GraphQuestion:
    question: str
    category: GraphQueryCategory
    entities: tuple[GraphEntityHint, ...] = ()
    max_hops: int = 3
    as_of: datetime | None = None


@dataclass(frozen=True)
class GraphProvenance:
    relationship_id: str
    claim_id: str
    evidence_id: str
    source_id: str
    governance_id: str
    governance_status: GovernanceDecisionStatus
    research_run_id: str
    temporal_status: RelationshipTemporalStatus
    claim_text: str
    evidence_text: str
    source_title: str
    source_url: str


@dataclass(frozen=True)
class GraphRAGResult:
    status: GraphRAGStatus
    answer: str | None = None
    provenance: tuple[GraphProvenance, ...] = ()
    paths: tuple[tuple[RelationshipRecord, ...], ...] = ()
    qualification: str | None = None
    reason: str | None = None


class EvidenceBackedGraphRAG:
    """Read-only GraphRAG orchestration; it never searches or refreshes."""

    _MAX_HOPS = 3

    def __init__(self, repository: PersistenceRepository, provider: LLMProvider) -> None:
        self._repository = repository
        self._provider = provider
        self._graph = GraphPersistenceService(repository)
        self._resolver = EntityResolutionService(repository)

    def answer(self, query: GraphQuestion) -> GraphRAGResult:
        if not query.question.strip():
            return self._reject("question is blank")
        if query.max_hops < 1 or query.max_hops > self._MAX_HOPS:
            return self._reject("graph traversal depth must be between 1 and 3")
        try:
            starts = self._resolve_entities(query)
        except ValueError as error:
            return self._reject(str(error))
        if not starts:
            return self._no_path("no unambiguous query entity was resolved")
        paths = self._retrieve_paths(query, starts)
        if not paths:
            return self._no_path("no supported governed graph path exists")
        provenance = self._supporting_provenance(paths)
        if not provenance:
            return self._no_path("supported paths have no retrievable canonical evidence")
        prompt = self._context_prompt(query, paths, provenance)
        try:
            response = self._provider.generate(LLMRequest(prompt=prompt))
        except Exception:
            return GraphRAGResult(GraphRAGStatus.PROVIDER_FAILED, provenance=provenance, paths=paths, reason="LLM provider failed")
        answer = response.text.strip()
        if not answer:
            return GraphRAGResult(GraphRAGStatus.PROVIDER_FAILED, provenance=provenance, paths=paths, reason="LLM returned an empty answer")
        qualification = "Answer is limited to eligible PASS/CURRENT graph relationships and cited canonical evidence."
        return GraphRAGResult(GraphRAGStatus.ANSWERED, answer=answer, provenance=provenance, paths=paths, qualification=qualification)

    def _resolve_entities(self, query: GraphQuestion) -> tuple[str, ...]:
        if not query.entities:
            question = canonicalize_entity_label(query.question)
            candidates = [entity for entity in self._repository.list_entities() if entity.normalized_name in question]
            duplicate_names = {
                entity.normalized_name
                for entity in candidates
                if sum(other.normalized_name == entity.normalized_name for other in candidates) > 1
            }
            if duplicate_names:
                raise ValueError("query entity resolution is ambiguous")
            return tuple(entity.entity_id for entity in candidates)
        resolved: list[str] = []
        for hint in query.entities:
            result = self._resolver.resolve(hint.entity_type, hint.label)
            if result.status is not ResolutionStatus.RESOLVED or result.entity is None:
                raise ValueError(result.reason or "query entity resolution failed")
            if result.entity.entity_id not in resolved:
                resolved.append(result.entity.entity_id)
        return tuple(resolved)

    def _retrieve_paths(self, query: GraphQuestion, entities: tuple[str, ...]) -> tuple[tuple[RelationshipRecord, ...], ...]:
        as_of = query.as_of or datetime.now(timezone.utc)
        if query.category is GraphQueryCategory.DIRECT_RELATIONSHIP:
            if len(entities) < 2:
                return ()
            paths = self._graph.bounded_paths(entities[0], entities[1], max_hops=1)
        elif query.category is GraphQueryCategory.NEIGHBORHOOD:
            paths = tuple((edge,) for edge in self._graph.neighbors(entities[0]) if self._edge_next(entities[0], edge) is not None)
        elif query.category is GraphQueryCategory.SHARED_CONNECTION:
            if len(entities) < 2:
                return ()
            paths = tuple(path for path in self._graph.bounded_paths(entities[0], entities[1], max_hops=2) if len(path) == 2)
        elif query.category is GraphQueryCategory.CROSS_COMPANY_RELATIONSHIP:
            if len(entities) < 2:
                return ()
            paths = self._graph.bounded_paths(entities[0], entities[1], max_hops=query.max_hops)
        elif query.category is GraphQueryCategory.RECURRING_ENTITY:
            paths = tuple((edge,) for edge in self._graph.neighbors(entities[0]))
        else:
            if len(entities) < 2:
                return ()
            paths = self._graph.bounded_paths(entities[0], entities[1], max_hops=query.max_hops)
        return tuple(
            path for path in paths
            if self._path_is_oriented(entities[0], path)
            and all(self._eligible_at(edge, as_of) for edge in path)
        )

    @staticmethod
    def _edge_next(current: str, edge: RelationshipRecord) -> str | None:
        if edge.source_entity_id == current:
            return edge.target_entity_id
        if edge.relation_type.value == "PARTNERED_WITH" and edge.target_entity_id == current:
            return edge.source_entity_id
        return None

    @classmethod
    def _path_is_oriented(cls, start: str, path: Sequence[RelationshipRecord]) -> bool:
        current = start
        for edge in path:
            current = cls._edge_next(current, edge) or ""
            if not current:
                return False
        return True

    @staticmethod
    def _eligible_at(edge: RelationshipRecord, as_of: datetime) -> bool:
        if not edge.usable or edge.governance_status is not GovernanceDecisionStatus.PASS:
            return False
        if edge.temporal_status is not RelationshipTemporalStatus.CURRENT:
            return False
        if edge.valid_from is not None and edge.valid_from > as_of:
            return False
        if edge.valid_to is not None and as_of >= edge.valid_to:
            return False
        return True

    def _supporting_provenance(self, paths: Sequence[Sequence[RelationshipRecord]]) -> tuple[GraphProvenance, ...]:
        records: list[GraphProvenance] = []
        seen: set[tuple[str, str, str]] = set()
        for path in paths:
            for relationship in path:
                for claim_id in relationship.claim_ids:
                    claim = self._repository.get_claim(claim_id)
                    if claim is None:
                        continue
                    links = self._repository.get_claim_evidence_links(claim_id)
                    for evidence_id in relationship.evidence_ids:
                        if not any(link.evidence_id == evidence_id and link.relationship_type is ClaimEvidenceRelationship.SUPPORTS for link in links):
                            continue
                        evidence = self._repository.get_evidence(evidence_id)
                        if evidence is None or evidence.source_id not in relationship.source_ids:
                            continue
                        source = self._repository.get_source(evidence.source_id)
                        if source is None:
                            continue
                        for governance_id in relationship.governance_ids:
                            key = (relationship.relationship_id, claim_id, evidence_id)
                            if key in seen:
                                continue
                            seen.add(key)
                            records.append(GraphProvenance(
                                relationship_id=relationship.relationship_id,
                                claim_id=claim_id,
                                evidence_id=evidence_id,
                                source_id=evidence.source_id,
                                governance_id=governance_id,
                                governance_status=relationship.governance_status,
                                research_run_id=relationship.research_run_id,
                                temporal_status=relationship.temporal_status,
                                claim_text=claim.text,
                                evidence_text=evidence.content,
                                source_title=source.title,
                                source_url=source.url,
                            ))
        return tuple(records)

    @staticmethod
    def _context_prompt(query: GraphQuestion, paths: Sequence[Sequence[RelationshipRecord]], provenance: Sequence[GraphProvenance]) -> str:
        lines = [
            "Answer the user's graph question using only the governed context below.",
            "Do not infer connections, use outside knowledge, or claim unsupported facts.",
            f"Question: {query.question}",
            "Relationships and evidence:",
        ]
        for item in provenance:
            lines.append(
                f"- relationship={item.relationship_id} claim={item.claim_id} evidence={item.evidence_id} "
                f"source={item.source_id} governance={item.governance_id}:{item.governance_status.value} "
                f"claim_text={item.claim_text} evidence_text={item.evidence_text} "
                f"source_title={item.source_title} source_url={item.source_url}"
            )
        lines.append(f"Retrieved path count: {len(paths)}. If the context does not answer the question, say so clearly.")
        return "\n".join(lines)

    @staticmethod
    def _no_path(reason: str) -> GraphRAGResult:
        return GraphRAGResult(GraphRAGStatus.NO_PATH, reason=reason)

    @staticmethod
    def _reject(reason: str) -> GraphRAGResult:
        return GraphRAGResult(GraphRAGStatus.REJECTED, reason=reason)
