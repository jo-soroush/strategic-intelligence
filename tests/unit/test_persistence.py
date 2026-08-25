from pathlib import Path
import sqlite3

import pytest

from strategic_intelligence.domain.models import (
    Case, Claim, ClaimEvidenceLink, ClaimEvidenceRelationship, ClaimType, Evidence,
    Source, SourceType, WorkflowRun, WorkflowStage,
)
from strategic_intelligence.application.persistence import ArtifactReference
from strategic_intelligence.infrastructure.artifacts import ArtifactNotFoundError, LocalArtifactStore
from strategic_intelligence.infrastructure.sqlite_repository import CheckpointRejectedError, SqliteRepository


@pytest.fixture
def repository(tmp_path: Path) -> SqliteRepository:
    store = SqliteRepository(tmp_path / "configured-data" / "strategic_intelligence.db")
    yield store
    store.close()


def _case() -> Case:
    return Case(company_id="company", executive_id="executive", meeting_goal="prepare")


def _traceability(repository: SqliteRepository, case: Case) -> tuple[Source, Evidence, Claim]:
    source = repository.save_source(Source(case_id=case.case_id, url="https://example.test/a", title="A", source_type=SourceType.OFFICIAL_COMPANY))
    evidence = repository.save_evidence(Evidence(case_id=case.case_id, source_id=source.source_id, content="supported", topic="strategy", relevance="high"))
    claim = Claim(case_id=case.case_id, text="Supported fact", claim_type=ClaimType.FACT, topic="strategy", evidence_ids=[evidence.evidence_id])
    repository.save_claim_with_links(claim, [ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id=evidence.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS)])
    return source, evidence, claim


def test_case_create_read_update_and_run_persistence(repository: SqliteRepository) -> None:
    case = repository.create_case(_case())
    assert repository.get_case(case.case_id) == case
    updated = case.model_copy(update={"meeting_goal": "updated"})
    assert repository.update_case(updated) == updated
    run = repository.save_workflow_run(WorkflowRun(case_id=case.case_id))
    assert run.case_id == case.case_id
    assert repository.get_workflow_run(run.run_id) == run


def test_case_and_run_survive_repository_reopen(tmp_path: Path) -> None:
    database_path = tmp_path / "configured-data" / "strategic_intelligence.db"
    first = SqliteRepository(database_path)
    case = first.create_case(_case())
    run = first.save_workflow_run(WorkflowRun(case_id=case.case_id))
    first.close()

    reopened = SqliteRepository(database_path)
    try:
        assert reopened.get_case(case.case_id) == case
        assert reopened.get_workflow_run(run.run_id) == run
    finally:
        reopened.close()


def test_source_is_idempotent_and_traceability_links_persist(repository: SqliteRepository) -> None:
    case = repository.create_case(_case())
    source, _, claim = _traceability(repository, case)
    duplicate = repository.save_source(Source(case_id=case.case_id, url=source.url, title="changed", source_type=SourceType.NEWS))
    assert duplicate.source_id == source.source_id
    assert repository.get_source(source.source_id) == source
    assert repository.get_evidence(claim.evidence_ids[0]) is not None
    assert repository.get_claim(claim.claim_id) == claim
    assert repository.link_count(claim.claim_id) == 1


def test_claim_link_transaction_rolls_back_on_missing_evidence(repository: SqliteRepository) -> None:
    case = repository.create_case(_case())
    claim = Claim(case_id=case.case_id, text="Fact", claim_type=ClaimType.FACT, topic="topic", evidence_ids=["missing"])
    with pytest.raises(sqlite3.IntegrityError):
        repository.save_claim_with_links(claim, [ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id="missing", relationship_type=ClaimEvidenceRelationship.SUPPORTS)])
    assert repository.get_claim(claim.claim_id) is None
    assert repository.link_count(claim.claim_id) == 0


def test_checkpoint_requires_persisted_records_and_never_accepts_failed_input(repository: SqliteRepository) -> None:
    case = repository.create_case(_case())
    run = repository.save_workflow_run(WorkflowRun(case_id=case.case_id))
    with pytest.raises(CheckpointRejectedError):
        repository.accept_checkpoint(run.run_id, WorkflowStage.CASE_VALIDATED, [("case", "missing")])
    assert not repository.checkpoint_is_accepted(run.run_id, WorkflowStage.CASE_VALIDATED)
    repository.accept_checkpoint(run.run_id, WorkflowStage.CASE_VALIDATED, [("case", case.case_id), ("workflow_run", run.run_id)])
    assert repository.checkpoint_is_accepted(run.run_id, WorkflowStage.CASE_VALIDATED)


def test_artifacts_use_configured_root_stable_references_and_safe_deletion(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "configured-data" / "cases")
    reference = store.write("case_1", "run_1", b"brief", ".md")
    assert store.read(reference) == b"brief"
    store.delete_case("case_1")
    with pytest.raises(ArtifactNotFoundError):
        store.read(reference)


def test_artifacts_reject_traversal_and_report_missing_artifacts(tmp_path: Path) -> None:
    store = LocalArtifactStore(tmp_path / "root")
    with pytest.raises(ValueError):
        store.write("../escape", "run_1", b"no")
    with pytest.raises(ArtifactNotFoundError):
        store.read(ArtifactReference("case_1", "run_1", "missing", ".bin"))
