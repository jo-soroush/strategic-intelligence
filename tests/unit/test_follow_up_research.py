from datetime import date

from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.evidence_layer import EvidenceLayerService
from strategic_intelligence.application.follow_up_research import FollowUpResearchService
from strategic_intelligence.application.source_quality import SourceQualityService
from strategic_intelligence.application.verification import VerificationService
from strategic_intelligence.domain.models import Case, Claim, ClaimEvidenceLink, ClaimEvidenceRelationship, ClaimType, Evidence, FollowUpResearchStatus, FreshnessStatus, RawFinding, ResearchCategory, ResearchTask, Source, SourceQuality, SourceType, TargetType, VerificationStatus
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.providers.contracts import SearchResult
from strategic_intelligence.providers.fakes import FakeSearchProvider


def _setup(tmp_path):
    repo = SqliteRepository(tmp_path / "c12.sqlite")
    case = repo.create_case(Case(case_id="case", company_id="company", executive_id="exec", company_name="Example Co", executive_name="Ada", meeting_goal="AI strategy", company_website="https://example.com"))
    source = repo.save_source(Source(case_id=case.case_id, url="https://other.example/old", title="Old", source_type=SourceType.OTHER, quality_class=SourceQuality.OTHER, publication_date=date(2026, 8, 1)))
    evidence = repo.save_evidence(Evidence(case_id=case.case_id, source_id=source.source_id, content="Example Co opened a research lab.", topic="AI", relevance="relevant", publication_date=date(2026, 8, 1)))
    claim = Claim(case_id=case.case_id, text="Example Co opened a research lab.", claim_type=ClaimType.FACT, topic="AI", evidence_ids=[evidence.evidence_id])
    repo.save_claim_with_links(claim, [ClaimEvidenceLink(claim_id=claim.claim_id, evidence_id=evidence.evidence_id, relationship_type=ClaimEvidenceRelationship.SUPPORTS)])
    task = ResearchTask(case_id=case.case_id, target_type=TargetType.COMPANY, category=ResearchCategory.NEWS, query="Example Co research lab", priority=1, max_attempts=2)
    return repo, case, claim, task


def _finding(case, task):
    return RawFinding(case_id=case.case_id, research_task_id=task.research_task_id, source_url="https://example.com/current", title="Current", publisher="Example Co", publication_date=date(2026, 8, 20), extracted_content="Example Co opened a research lab.", topic="AI", relevance="relevant")


def test_critical_path_preserves_provider_metadata_and_resolves(tmp_path):
    repo, case, claim, task = _setup(tmp_path)
    research = CompanyResearchService(FakeSearchProvider(results=[SearchResult(title="Example Co research lab", url="https://example.com/current", snippet="Example Co opened a research lab.", publisher="Example Co", published_at=date(2026, 8, 20))]))
    result = FollowUpResearchService(repo, EvidenceLayerService(repo), VerificationService(repo)).run(case, claim.claim_id, task, lambda c, t: research.research(c, t).findings, as_of=date(2026, 8, 27))
    assert result.status is FollowUpResearchStatus.RESOLVED
    assert result.verification.verification.status is VerificationStatus.VERIFIED
    assert len(repo.list_follow_up_attempts(claim.claim_id)) == 1
    assert len(repo.get_claim(claim.claim_id).evidence_ids) == 2
    retained = repo.get_evidence(result.attempts[0].evidence_ids[0])
    source = repo.get_source(retained.source_id)
    assert source.publisher == "Example Co"
    assert source.publication_date == retained.publication_date == date(2026, 8, 20)
    assert SourceQualityService().assess(source, as_of=date(2026, 8, 27)).freshness_status is FreshnessStatus.CURRENT


def test_follow_up_no_progress_stops_on_first_empty_attempt(tmp_path):
    repo, case, claim, task = _setup(tmp_path)
    result = FollowUpResearchService(repo, EvidenceLayerService(repo), VerificationService(repo)).run(case, claim.claim_id, task, lambda c, t: [], as_of=date(2026, 8, 27))
    assert result.status is FollowUpResearchStatus.NO_PROGRESS
    assert len(result.attempts) == 1 and result.attempts[0].terminal


def test_follow_up_exhausts_the_configured_attempt_budget(tmp_path):
    repo, case, claim, task = _setup(tmp_path)
    calls: list[int] = []

    def discover(current_case, current_task):
        calls.append(1)
        return [_finding(current_case, current_task).model_copy(update={"source_url": f"https://news.example/{len(calls)}"})]

    result = FollowUpResearchService(repo, EvidenceLayerService(repo), VerificationService(repo)).run(case, claim.claim_id, task, discover, as_of=date(2026, 8, 27))
    assert result.status is FollowUpResearchStatus.EXHAUSTED
    assert len(calls) == len(result.attempts) == task.max_attempts
    assert not result.attempts[0].terminal and result.attempts[-1].terminal
    assert len(repo.list_follow_up_attempts(claim.claim_id)) == task.max_attempts


def test_follow_up_no_progress_does_not_promote_claim(tmp_path):
    repo, case, claim, task = _setup(tmp_path)
    result = FollowUpResearchService(repo, EvidenceLayerService(repo), VerificationService(repo)).run(case, claim.claim_id, task, lambda c, t: [], as_of=date(2026, 8, 2))
    assert result.status is FollowUpResearchStatus.NO_PROGRESS
