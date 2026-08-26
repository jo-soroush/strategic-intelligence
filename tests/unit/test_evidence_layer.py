from pathlib import Path

from strategic_intelligence.application.evidence_layer import EvidenceLayerErrorCode, EvidenceLayerService, EvidenceLayerStatus
from strategic_intelligence.domain.models import Case, ClaimEvidenceRelationship, RawFinding
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


def _finding(case_id: str = "case", *, url: str = "https://example.test/source", content: str = "Example Co announced an AI partnership.") -> RawFinding:
    return RawFinding(case_id=case_id, research_task_id="task", source_url=url, title="Example announcement", extracted_content=content, topic="AI_ACTIVITY", relevance="meeting relevant")


def _case() -> Case:
    return Case(company_id="company", executive_id="executive", company_name="Example Co", executive_name="Ava Example", meeting_goal="prepare")


def test_critical_path_persists_complete_provenance_chain(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        case = repository.create_case(_case())
        finding = _finding(case.case_id)
        result = EvidenceLayerService(repository).create_candidate(finding, claim_text="Example Co announced an AI partnership.")
        assert result.status is EvidenceLayerStatus.ACCEPTED
        assert result.source and result.evidence and result.candidate_claim and result.link
        assert repository.get_source(result.evidence.source_id) == result.source
        assert repository.get_evidence(result.link.evidence_id) == result.evidence
    finally:
        repository.close()
    assert result.candidate_claim.verification_status is None
    assert result.link.relationship_type is ClaimEvidenceRelationship.SUPPORTS
    assert result.originating_finding_id == finding.finding_id


def test_duplicate_source_is_reused_and_conflicting_evidence_is_preserved(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        case = repository.create_case(_case())
        service = EvidenceLayerService(repository)
        first = service.create_candidate(_finding(case.case_id), claim_text="Example Co announced an AI partnership.")
        second = service.create_candidate(_finding(case.case_id, content="Example Co delayed the AI partnership."), claim_text="The AI partnership timing is disputed.", relationship=ClaimEvidenceRelationship.CONTRADICTS)
        context = service.create_candidate(
            _finding(case.case_id, url="https://example.test/context", content="The announcement did not include a launch date."),
            claim_text="The partnership announcement has no stated launch date.",
            relationship=ClaimEvidenceRelationship.CONTEXT,
        )
    finally:
        repository.close()
    assert first.status is second.status is EvidenceLayerStatus.ACCEPTED
    assert first.source and second.source and first.source.source_id == second.source.source_id
    assert first.evidence and second.evidence and first.evidence.evidence_id != second.evidence.evidence_id
    assert second.link and second.link.relationship_type is ClaimEvidenceRelationship.CONTRADICTS
    assert context.status is EvidenceLayerStatus.ACCEPTED
    assert context.link and context.link.relationship_type is ClaimEvidenceRelationship.CONTEXT


def test_candidate_can_retain_multiple_evidence_links(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        case = repository.create_case(_case())
        result = EvidenceLayerService(repository).create_candidate(
            [
                _finding(case.case_id),
                _finding(case.case_id, url="https://example.test/context", content="The announcement did not include a launch date."),
            ],
            claim_text="Example Co announced an AI partnership, with an unstated launch date.",
            relationship=[ClaimEvidenceRelationship.SUPPORTS, ClaimEvidenceRelationship.CONTEXT],
        )
        assert result.status is EvidenceLayerStatus.ACCEPTED
        assert result.candidate_claim and repository.link_count(result.candidate_claim.claim_id) == 2
    finally:
        repository.close()
    assert [link.relationship_type for link in result.links] == [
        ClaimEvidenceRelationship.SUPPORTS,
        ClaimEvidenceRelationship.CONTEXT,
    ]


def test_missing_provenance_and_blank_claim_fail_closed() -> None:
    malformed = _finding(url="file:///private")
    result = EvidenceLayerService(object()).create_candidate(malformed, claim_text="claim")
    assert result.status is EvidenceLayerStatus.REJECTED
    assert result.errors[0].code is EvidenceLayerErrorCode.INVALID_FINDING
    blank_claim = EvidenceLayerService(object()).create_candidate(_finding(), claim_text="   ")
    assert blank_claim.status is EvidenceLayerStatus.REJECTED
    assert blank_claim.errors[0].code is EvidenceLayerErrorCode.INVALID_CLAIM
