"""Deterministic C07/C08 source-retention regressions for C20 coverage repair."""

from datetime import date
from pathlib import Path

from strategic_intelligence.application.case_input import CaseIntakeService
from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.executive_research import ExecutiveResearchService
from strategic_intelligence.application.research_planning import ResearchPlanner
from strategic_intelligence.application.source_acquisition import PublicSourceContent, SourceAcquisitionResult
from strategic_intelligence.domain.models import Case, ResearchCategory, ResearchPlan, ResearchTask, TargetType, WorkflowRun
from strategic_intelligence.harness.workflow_executor import WorkflowExecutor
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository
from strategic_intelligence.providers.contracts import SearchQuery, SearchResult
from strategic_intelligence.providers.fakes import FakeSearchProvider


class _Retriever:
    def __init__(self, pages: dict[str, str]) -> None:
        self._pages = pages
        self.calls: list[str] = []

    def retrieve(self, url: str) -> SourceAcquisitionResult:
        self.calls.append(url)
        text = self._pages[url]
        return SourceAcquisitionResult(content=PublicSourceContent(
            requested_url=url, final_url=url, title="Public professional report", text=text, publication_date=date(2026, 8, 20),
        ))


def _case() -> Case:
    return Case(
        case_id="case", company_id="company", executive_id="executive",
        company_name="Example Co", executive_name="Ava Example",
        meeting_goal="prepare an enterprise AI meeting", company_website="https://example.test",
    )


def _company_task(category: ResearchCategory = ResearchCategory.PROJECTS, task_id: str = "company-task") -> ResearchTask:
    return ResearchTask(
        research_task_id=task_id, case_id="case", target_type=TargetType.COMPANY, category=category,
        query=f"Example Co {category.value} enterprise AI", priority=3,
    )


def test_unusable_retrievals_backfill_without_using_retained_source_capacity() -> None:
    weak = "https://sources.example.test/title"
    cookie = "https://sources.example.test/cookies"
    useful = "https://sources.example.test/report"
    retriever = _Retriever({
        weak: "Public professional report",
        cookie: "Public professional report Accept all cookies Cookie settings Privacy policy Consent preferences",
        useful: "Public professional report Example Co describes measurable AI delivery, governed data foundations, and a current enterprise transformation program with named outcomes.",
    })
    provider = FakeSearchProvider([
        SearchResult("Example Co report", weak, "Example Co enterprise AI report"),
        SearchResult("Example Co report", cookie, "Example Co enterprise AI report"),
        SearchResult("Example Co report", useful, "Example Co enterprise AI report"),
    ])

    result = CompanyResearchService(
        provider, source_retriever=retriever, max_results_per_task=3,
        max_acquisitions_per_task=1, max_candidate_acquisitions_per_task=3,
    ).research(_case(), _company_task())

    assert [item.source_url for item in result.findings] == [useful]
    assert retriever.calls == [weak, cookie, useful]
    assert result.rejected_result_count == 2


def test_canonical_exclusions_deduplicate_harmless_variants_but_not_distinct_resources() -> None:
    duplicate = "https://sources.example.test/report"
    distinct = "https://sources.example.test/report?page=2"
    retriever = _Retriever({
        distinct: "Public professional report This distinct page contains enough substantive enterprise AI strategy and delivery context to support a finding.",
    })
    provider = FakeSearchProvider([
        SearchResult("Example Co report", "https://SOURCES.example.test/report#summary", "Example Co enterprise AI report"),
        SearchResult("Example Co report", distinct, "Example Co enterprise AI report"),
    ])

    result = CompanyResearchService(provider, source_retriever=retriever, max_results_per_task=2).research(
        _case(), _company_task(), excluded_source_urls={duplicate},
    )

    assert [item.source_url for item in result.findings] == [distinct]
    assert retriever.calls == [distinct]


def test_candidate_attempts_remain_bounded_when_all_pages_are_unusable() -> None:
    urls = [f"https://sources.example.test/{index}" for index in range(3)]
    retriever = _Retriever({url: "Public professional report" for url in urls})
    provider = FakeSearchProvider([SearchResult("Example Co report", url, "Example Co enterprise AI report") for url in urls])

    result = CompanyResearchService(
        provider, source_retriever=retriever, max_results_per_task=3,
        max_acquisitions_per_task=1, max_candidate_acquisitions_per_task=2,
    ).research(_case(), _company_task())

    assert result.findings == []
    assert retriever.calls == urls[:2]


def test_exact_duplicate_page_content_does_not_consume_a_second_retained_slot() -> None:
    first = "https://sources.example.test/first"
    duplicate = "https://mirror.example.test/copied"
    alternative = "https://sources.example.test/alternative"
    copied = "Public professional report Example Co publishes substantive enterprise AI strategy, governed delivery, and measurable transformation outcomes for customers."
    retriever = _Retriever({
        first: copied,
        duplicate: copied.upper(),
        alternative: "Public professional report Example Co publishes a distinct substantive project update about data platforms, delivery milestones, and measured operating outcomes.",
    })
    provider = FakeSearchProvider([
        SearchResult("Example Co strategy", duplicate, "Example Co enterprise AI strategy"),
        SearchResult("Example Co project", alternative, "Example Co enterprise AI project"),
    ])

    result = CompanyResearchService(provider, source_retriever=retriever, max_results_per_task=2).research(
        _case(), _company_task(), excluded_content={copied},
    )

    assert [item.source_url for item in result.findings] == [alternative]
    assert retriever.calls == [duplicate, alternative]


def test_workflow_scopes_canonical_source_diversity_across_tasks(tmp_path: Path) -> None:
    shared = "https://sources.example.test/shared"
    alternative = "https://sources.example.test/alternative"

    class _Search:
        def search(self, query: SearchQuery) -> list[SearchResult]:
            if "STRATEGY" in query.query:
                return [SearchResult("Example Co strategy", shared, "Example Co enterprise AI strategy")]
            return [
                SearchResult("Example Co strategy", "https://SOURCES.example.test/shared#overview", "Example Co enterprise AI strategy"),
                SearchResult("Example Co project", alternative, "Example Co enterprise AI project"),
            ]

    retriever = _Retriever({
        shared: "Public professional report Example Co publishes a substantive strategy for governed enterprise AI delivery and measurable transformation outcomes.",
        alternative: "Public professional report Example Co publishes a substantive project update with enterprise AI delivery details and measurable operating outcomes.",
    })
    company = CompanyResearchService(_Search(), source_retriever=retriever, max_results_per_task=2, max_acquisitions_per_task=1)
    executive = ExecutiveResearchService(FakeSearchProvider(), source_retriever=retriever)
    repository = SqliteRepository(tmp_path / "coverage.sqlite")
    try:
        executor = WorkflowExecutor(
            repository, CaseIntakeService(repository), ResearchPlanner(task_budget=2), company, executive,
            object(), object(), object(), object(), object(), object(),
        )
        plan = ResearchPlan(case_id="case", task_budget=2, tasks=[
            _company_task(ResearchCategory.STRATEGY, "strategy"),
            _company_task(ResearchCategory.PROJECTS, "projects"),
        ])
        (company_findings, executive_findings), partial, _ = executor._research(_case(), plan, WorkflowRun(case_id="case"))
    finally:
        repository.close()

    assert executive_findings == []
    assert partial  # the second task truthfully records its skipped duplicate
    assert [item.source_url for item in company_findings] == [shared, alternative]
    assert retriever.calls == [shared, alternative]
