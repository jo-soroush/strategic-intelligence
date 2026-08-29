from datetime import date
from pathlib import Path

from strategic_intelligence.application.case_input import CaseIntakeService, IntakeStatus
from strategic_intelligence.application.company_research import (
    CompanyResearchErrorCode, CompanyResearchService, CompanyResearchStatus,
)
from strategic_intelligence.application.research_planning import PlanningStatus, ResearchPlanner
from strategic_intelligence.domain.models import Case, ResearchCategory, ResearchTask, TargetType
from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchQuery, SearchResult
from strategic_intelligence.providers.fakes import FakeSearchProvider
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


def _case() -> Case:
    return Case(
        company_id="company",
        executive_id="executive",
        company_name="Example Co",
        executive_name="Ava Example",
        meeting_goal="prepare an AI partnership meeting",
        company_website="https://example.test",
        executive_linkedin_url="https://www.linkedin.com/in/ava-example",
    )


def _task(category: ResearchCategory = ResearchCategory.PROJECTS, *, target: TargetType = TargetType.COMPANY, case_id: str = "case") -> ResearchTask:
    return ResearchTask(
        research_task_id="company-task",
        case_id=case_id,
        target_type=target,
        category=category,
        query="Example Co current projects for an AI partnership meeting",
        priority=3,
    )


def test_critical_path_executes_a_real_company_service_from_c05_and_c06(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        intake = CaseIntakeService(repository).submit({
            "company_name": "Example Co",
            "executive_name": "Ava Example",
            "meeting_goal": "prepare an AI partnership meeting",
            "company_website": "https://example.test",
            "executive_linkedin_url": "https://www.linkedin.com/in/ava-example",
        })
        assert intake.status is IntakeStatus.ACCEPTED and intake.case is not None
        plan = ResearchPlanner().plan(intake.case)
        assert plan.status is PlanningStatus.ACCEPTED and plan.plan is not None
        task = next(item for item in plan.plan.tasks if item.target_type is TargetType.COMPANY and item.category is ResearchCategory.PROJECTS)
        provider = FakeSearchProvider([SearchResult(
            title="Example Co launches AI transformation project",
            url="https://news.example.test/projects/ai",
            snippet="Example Co announced an AI project for enterprise partners.",
            publisher="Example News",
            published_at=date(2026, 8, 20),
        )])
        result = CompanyResearchService(provider).research(intake.case, task)
    finally:
        repository.close()

    assert result.status is CompanyResearchStatus.COMPLETED
    assert result.attempts_used == result.attempt_budget == 1
    assert len(provider.calls) == 1
    assert provider.calls[0].query == task.query
    assert result.findings[0].research_task_id == task.research_task_id
    assert result.findings[0].source_url == "https://news.example.test/projects/ai"
    assert result.findings[0].topic == "PROJECTS"
    assert result.findings[0].relevance == "MEETING_RELEVANT_DISCOVERY"
    assert result.findings[0].publisher == "Example News"
    assert result.findings[0].publication_date == date(2026, 8, 20)


def test_empty_duplicate_blocked_and_irrelevant_results_are_explicit_and_bounded() -> None:
    case = _case().model_copy(update={"case_id": "case"})
    task = _task()
    provider = FakeSearchProvider([
        SearchResult("Example Co projects", "https://example.test/project", "Example Co AI project for partners"),
        SearchResult("Example Co projects copy", "https://example.test/project", "Example Co AI project for partners"),
        SearchResult("Blocked Example Co project", "https://blocked.example.test/project", "Example Co project", provider_metadata={"access_status": "BLOCKED"}),
        SearchResult("Unrelated cooking", "https://other.example.test/recipe", "Simple cooking tips"),
    ])

    result = CompanyResearchService(provider, max_results_per_task=4).research(case, task)

    assert result.status is CompanyResearchStatus.PARTIAL
    assert len(result.findings) == 1
    assert result.blocked_result_count == 1
    assert result.rejected_result_count == 2
    assert len(provider.calls) == 1
    assert provider.calls[0].limit == 4

    empty = CompanyResearchService(FakeSearchProvider()).research(case, task)
    assert empty.status is CompanyResearchStatus.NOT_FOUND
    assert empty.findings == []
    assert empty.attempts_used == 1


def test_invalid_task_malformed_results_and_provider_failures_fail_closed() -> None:
    case = _case().model_copy(update={"case_id": "case"})
    executive_task = _task(ResearchCategory.EXECUTIVE_ROLE, target=TargetType.EXECUTIVE)
    rejected = CompanyResearchService(FakeSearchProvider()).research(case, executive_task)
    assert rejected.status is CompanyResearchStatus.REJECTED
    assert rejected.errors[0].code is CompanyResearchErrorCode.INVALID_TASK

    class MalformedSearchProvider:
        def search(self, query: SearchQuery):
            return [object(), SearchResult("Bad URL", "file:///etc/passwd", "Example Co project")]

    malformed = CompanyResearchService(MalformedSearchProvider()).research(case, _task())
    assert malformed.status is CompanyResearchStatus.REJECTED
    assert malformed.rejected_result_count == 2
    assert malformed.errors[0].code is CompanyResearchErrorCode.INVALID_PROVIDER_RESULT

    class TimeoutSearchProvider:
        def search(self, query: SearchQuery):
            raise ProviderError(ProviderErrorCode.TIMEOUT, "timeout", retryable=True)

    timeout = CompanyResearchService(TimeoutSearchProvider()).research(case, _task())
    assert timeout.status is CompanyResearchStatus.UNAVAILABLE
    assert timeout.errors[0].code is CompanyResearchErrorCode.PROVIDER_TIMEOUT
    assert timeout.attempts_used == 1
    assert timeout.retryable_provider_failure is True

    class ConfigurationSearchProvider:
        def search(self, query: SearchQuery):
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "token=secret", retryable=False)

    configuration = CompanyResearchService(ConfigurationSearchProvider()).research(case, _task())
    assert configuration.retryable_provider_failure is False
    assert "secret" not in configuration.errors[0].message


def test_same_inputs_retain_the_same_discovery_content_without_creating_evidence() -> None:
    case = _case().model_copy(update={"case_id": "case"})
    task = _task(ResearchCategory.AI_ACTIVITY)
    results = [SearchResult("Example Co AI activity", "https://example.test/ai", "Example Co expands AI activity for partners")]

    first = CompanyResearchService(FakeSearchProvider(results)).research(case, task)
    second = CompanyResearchService(FakeSearchProvider(results)).research(case, task)

    assert [(item.source_url, item.title, item.extracted_content, item.topic, item.relevance) for item in first.findings] == [
        (item.source_url, item.title, item.extracted_content, item.topic, item.relevance) for item in second.findings
    ]
    assert not hasattr(first, "evidence")


def test_research_uses_one_visible_attempt_even_when_a_task_allows_more() -> None:
    case = _case().model_copy(update={"case_id": "case"})
    task = _task().model_copy(update={"max_attempts": 3})
    provider = FakeSearchProvider([SearchResult("Example Co projects", "https://example.test/projects", "Example Co project")])

    result = CompanyResearchService(provider).research(case, task)

    assert result.status is CompanyResearchStatus.COMPLETED
    assert result.attempts_used == 1
    assert result.attempt_budget == 3
    assert len(provider.calls) == 1
