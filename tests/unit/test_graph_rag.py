from pathlib import Path

from strategic_intelligence.application.graph_persistence import GraphPersistenceService
from strategic_intelligence.application.graph_rag import (
    EvidenceBackedGraphRAG,
    GraphEntityHint,
    GraphQuestion,
    GraphQueryCategory,
    GraphRAGStatus,
)
from strategic_intelligence.application.relationship_extraction import GovernedRelationshipExtractor
from strategic_intelligence.domain.models import EntityRecord, EntityType, RelationshipType, VerificationStatus
from strategic_intelligence.providers.fakes import FakeLLMProvider

from tests.unit.test_relationship_extraction import _fixture


def _graph(tmp_path: Path, *, verification=VerificationStatus.VERIFIED):
    repository, person, company, claim, evidence = _fixture(tmp_path, verification=verification)
    relationship = GovernedRelationshipExtractor(repository).extract(
        RelationshipType.LEADS, person.entity_id, company.entity_id,
        [claim.claim_id], [evidence.evidence_id], "run-1",
    ).relationship
    assert relationship is not None
    assert GraphPersistenceService(repository).project([relationship]).rejected_relationship_ids == ()
    return repository, person, company, claim, evidence


def test_graph_rag_retrieves_bounded_path_and_structured_provenance(tmp_path: Path) -> None:
    repository, person, company, claim, evidence = _graph(tmp_path)
    provider = FakeLLMProvider(response_text="Ava leads Acme based on the governed source.")
    try:
        result = EvidenceBackedGraphRAG(repository, provider).answer(GraphQuestion(
            question="Who leads Acme?",
            category=GraphQueryCategory.DIRECT_RELATIONSHIP,
            entities=(GraphEntityHint("Ava", EntityType.PERSON), GraphEntityHint("Acme", EntityType.COMPANY)),
        ))
        assert result.status is GraphRAGStatus.ANSWERED
        assert result.answer and "Ava" in result.answer
        assert len(result.paths) == 1
        assert result.provenance[0].claim_id == claim.claim_id
        assert result.provenance[0].evidence_id == evidence.evidence_id
        assert result.provenance[0].source_url == "https://example.test/claim"
        assert len(provider.calls) == 1
        assert "evidence-1" in provider.calls[0].prompt
    finally:
        repository.close()


def test_no_path_is_explicit_and_does_not_call_provider(tmp_path: Path) -> None:
    repository, _, _, _, _ = _graph(tmp_path)
    repository.save_entity(EntityRecord(entity_id="technology-1", entity_type=EntityType.TECHNOLOGY, canonical_name="Nova", normalized_name="nova"))
    provider = FakeLLMProvider(response_text="must not be used")
    try:
        result = EvidenceBackedGraphRAG(repository, provider).answer(GraphQuestion(
            question="What develops Acme?",
            category=GraphQueryCategory.DIRECT_RELATIONSHIP,
            entities=(GraphEntityHint("Acme", EntityType.COMPANY), GraphEntityHint("Nova", EntityType.TECHNOLOGY)),
        ))
        assert result.status is GraphRAGStatus.NO_PATH
        assert provider.calls == []
    finally:
        repository.close()


def test_stale_graph_knowledge_is_not_retrieved(tmp_path: Path) -> None:
    repository, person, company, _, _ = _graph(tmp_path, verification=VerificationStatus.STALE)
    provider = FakeLLMProvider(response_text="must not be used")
    try:
        result = EvidenceBackedGraphRAG(repository, provider).answer(GraphQuestion(
            question="Who leads Acme?",
            category=GraphQueryCategory.DIRECT_RELATIONSHIP,
            entities=(GraphEntityHint("Ava", EntityType.PERSON), GraphEntityHint("Acme", EntityType.COMPANY)),
        ))
        assert result.status is GraphRAGStatus.NO_PATH
        assert provider.calls == []
    finally:
        repository.close()


def test_query_categories_and_three_edge_bound_are_closed(tmp_path: Path) -> None:
    repository, _, _, _, _ = _graph(tmp_path)
    provider = FakeLLMProvider(response_text="unused")
    try:
        assert {item.value for item in GraphQueryCategory} == {
            "direct_relationship", "neighborhood", "shared_connection",
            "cross_company_relationship", "recurring_entity", "bounded_multi_hop_path",
        }
        result = EvidenceBackedGraphRAG(repository, provider).answer(GraphQuestion(
            question="path", category=GraphQueryCategory.BOUNDED_MULTI_HOP_PATH,
            entities=(GraphEntityHint("Ava", EntityType.PERSON), GraphEntityHint("Acme", EntityType.COMPANY)),
            max_hops=4,
        ))
        assert result.status is GraphRAGStatus.REJECTED
        assert provider.calls == []
    finally:
        repository.close()
