from datetime import date
from pathlib import Path

from strategic_intelligence.application.case_input import CaseIntakeService, IntakeStatus
from strategic_intelligence.application.executive_research import (
    ExecutiveResearchErrorCode, ExecutiveResearchService, ExecutiveResearchStatus,
)
from strategic_intelligence.application.research_planning import PlanningStatus, ResearchPlanner
from strategic_intelligence.domain.models import Case, ResearchCategory, ResearchTask, TargetType
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchQuery, SearchResult
from strategic_intelligence.providers.fakes import FakeSearchProvider


def _case() -> Case:
    return Case(
        case_id="case",
        company_id="company",
        executive_id="executive",
        company_name="Example Co",
        executive_name="Ava Example",
        meeting_goal="prepare an AI partnership meeting",
        company_website="https://example.test",
    )


def _task(category: ResearchCategory = ResearchCategory.EXECUTIVE_ROLE, *, target: TargetType = TargetType.EXECUTIVE) -> ResearchTask:
    return ResearchTask(
        research_task_id="executive-task",
        case_id="case",
        target_type=target,
        category=category,
        query="Ava Example current role and responsibilities for an AI partnership meeting",
        priority=3,
    )


def test_critical_path_uses_c05_c06_and_real_privacy_aware_executive_research(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        intake = CaseIntakeService(repository).submit({
            "company_name": "Example Co",
            "executive_name": "Ava Example",
            "executive_current_title": "Chief Strategy Officer",
            "meeting_goal": "prepare an AI partnership meeting",
            "company_website": "https://example.test",
        })
        assert intake.status is IntakeStatus.ACCEPTED and intake.case is not None
        assert intake.case.executive_linkedin_url is None
        plan = ResearchPlanner().plan(intake.case)
        assert plan.status is PlanningStatus.ACCEPTED and plan.plan is not None
        task = next(item for item in plan.plan.tasks if item.target_type is TargetType.EXECUTIVE and item.category is ResearchCategory.EXECUTIVE_ROLE)
        provider = FakeSearchProvider([SearchResult(
            title="Ava Example named Chief Strategy Officer at Example Co",
            url="https://news.example.test/ava-example-role",
            snippet="Ava Example leads strategy and AI partnerships for Example Co.",
            publisher="Example Co newsroom",
            published_at=date(2026, 8, 20),
        )])
        result = ExecutiveResearchService(provider).research(intake.case, task)
    finally:
        repository.close()

    assert result.status is ExecutiveResearchStatus.COMPLETED
    assert result.attempts_used == result.attempt_budget == 1
    assert len(provider.calls) == 1
    assert provider.calls[0].query == task.query
    assert result.findings[0].research_task_id == task.research_task_id
    assert result.findings[0].source_url == "https://news.example.test/ava-example-role"
    assert result.findings[0].relevance == "PUBLIC_PROFESSIONAL_MEETING_RELEVANT_DISCOVERY"
    assert result.findings[0].publisher == "Example Co newsroom"
    assert result.findings[0].publication_date == date(2026, 8, 20)


def test_privacy_identity_relevance_and_duplicates_are_rejected_before_retention() -> None:
    provider = FakeSearchProvider([
        SearchResult("Ava Example interview", "https://example.test/interview", "Ava Example discusses Example Co strategy and partnerships."),
        SearchResult("Ava Example interview copy", "https://example.test/interview", "Ava Example discusses Example Co strategy and partnerships."),
        SearchResult("Ava Example family", "https://private.example.test/ava", "Ava Example shares family details and children."),
        SearchResult("Ava Example personal profile", "https://private.example.test/profile", "Ava Example discusses religion and personal routines."),
        SearchResult("Ava Other role", "https://other.example.test/ava", "Ava Other is a director at Another Co."),
        SearchResult("Ava Example cooking", "https://other.example.test/cooking", "Ava Example shares cooking ideas."),
    ])

    result = ExecutiveResearchService(provider, max_results_per_task=6).research(_case(), _task())

    assert result.status is ExecutiveResearchStatus.PARTIAL
    assert len(result.findings) == 1
    assert result.privacy_rejected_result_count == 2
    assert result.identity_rejected_result_count == 1
    assert result.rejected_result_count == 5
    assert len(provider.calls) == 1
    assert provider.calls[0].limit == 6


def test_invalid_task_malformed_timeout_and_empty_results_fail_closed() -> None:
    company_task = _task(ResearchCategory.PROJECTS, target=TargetType.COMPANY)
    rejected = ExecutiveResearchService(FakeSearchProvider()).research(_case(), company_task)
    assert rejected.status is ExecutiveResearchStatus.REJECTED
    assert rejected.errors[0].code is ExecutiveResearchErrorCode.INVALID_TASK

    class MalformedSearchProvider:
        def search(self, query: SearchQuery):
            return [object(), SearchResult("Ava Example", "file:///etc/passwd", "Ava Example professional role")]

    malformed = ExecutiveResearchService(MalformedSearchProvider()).research(_case(), _task())
    assert malformed.status is ExecutiveResearchStatus.REJECTED
    assert malformed.errors[0].code is ExecutiveResearchErrorCode.INVALID_PROVIDER_RESULT

    class TimeoutSearchProvider:
        def search(self, query: SearchQuery):
            raise ProviderError(ProviderErrorCode.TIMEOUT, "timeout", retryable=True)

    timeout = ExecutiveResearchService(TimeoutSearchProvider()).research(_case(), _task())
    assert timeout.status is ExecutiveResearchStatus.UNAVAILABLE
    assert timeout.errors[0].code is ExecutiveResearchErrorCode.PROVIDER_TIMEOUT
    assert timeout.attempts_used == 1
    assert timeout.retryable_provider_failure is True

    class ConfigurationSearchProvider:
        def search(self, query: SearchQuery):
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "token=secret", retryable=False)

    configuration = ExecutiveResearchService(ConfigurationSearchProvider()).research(_case(), _task())
    assert configuration.retryable_provider_failure is False
    assert "secret" not in configuration.errors[0].message

    empty = ExecutiveResearchService(FakeSearchProvider()).research(_case(), _task())
    assert empty.status is ExecutiveResearchStatus.NOT_FOUND
    assert empty.findings == []
    assert empty.retryable_provider_failure is None


def test_inputs_are_deterministic_and_raw_findings_are_not_evidence() -> None:
    task = _task().model_copy(update={"max_attempts": 3})
    results = [SearchResult("Ava Example professional activity", "https://example.test/activity", "Ava Example speaks about Example Co AI strategy.")]

    first_provider = FakeSearchProvider(results)
    first = ExecutiveResearchService(first_provider).research(_case(), task)
    second = ExecutiveResearchService(FakeSearchProvider(results)).research(_case(), task)

    assert first.status is ExecutiveResearchStatus.COMPLETED
    assert first.attempts_used == 1
    assert first.attempt_budget == 3
    assert len(first_provider.calls) == 1
    assert [(item.source_url, item.title, item.extracted_content, item.topic, item.relevance) for item in first.findings] == [
        (item.source_url, item.title, item.extracted_content, item.topic, item.relevance) for item in second.findings
    ]
    assert not hasattr(first, "evidence")
