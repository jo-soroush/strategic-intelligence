"""Bounded company discovery for V1-C07; discovery results never become Evidence."""

from __future__ import annotations

import re
from urllib.parse import urlsplit
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.domain.models import Case, ContentOrigin, RawFinding, ResearchCategory, ResearchTask, ResearchTaskStatus, TargetType
from strategic_intelligence.application.source_acquisition import PublicSourceRetriever, SourceSuitability, assess_source_suitability
from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchProvider, SearchQuery, SearchResult
from strategic_intelligence.security import UnsafeExternalUrlError, normalize_external_url


_COMPANY_CATEGORIES = frozenset({
    ResearchCategory.STRATEGY,
    ResearchCategory.PROJECTS,
    ResearchCategory.AI_ACTIVITY,
    ResearchCategory.CLIENT_CASES,
    ResearchCategory.PARTNERSHIPS,
    ResearchCategory.NEWS,
    ResearchCategory.HIRING,
    ResearchCategory.EVENTS,
})
_STOP_WORDS = frozenset({"about", "and", "for", "from", "into", "meeting", "the", "this", "with"})


class CompanyResearchStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    REJECTED = "REJECTED"


class CompanyResearchErrorCode(str, Enum):
    INVALID_TASK = "INVALID_TASK"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    INVALID_PROVIDER_RESULT = "INVALID_PROVIDER_RESULT"


class CompanyResearchModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class CompanyResearchError(CompanyResearchModel):
    code: CompanyResearchErrorCode
    message: str


class CompanyResearchResult(CompanyResearchModel):
    """Raw, traceable discovery output; it deliberately contains no Evidence or Claim."""

    status: CompanyResearchStatus
    findings: list[RawFinding] = Field(default_factory=list)
    attempts_used: int = Field(default=0, ge=0)
    attempt_budget: int = Field(ge=1, le=3)
    rejected_result_count: int = Field(default=0, ge=0)
    blocked_result_count: int = Field(default=0, ge=0)
    errors: list[CompanyResearchError] = Field(default_factory=list)
    gap_reason: str | None = None
    retryable_provider_failure: bool | None = None


class CompanyResearchService:
    """Consumes one C06 company task through the provider-neutral C04 boundary."""

    def __init__(self, search: SearchProvider, *, max_results_per_task: int = 5, timeout_seconds: float = 5.0, source_retriever: PublicSourceRetriever | None = None, max_acquisitions_per_task: int = 2, max_candidate_acquisitions_per_task: int | None = None) -> None:
        if not 1 <= max_results_per_task <= 10:
            raise ValueError("max_results_per_task must be between one and ten")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        candidate_budget = max_results_per_task if max_candidate_acquisitions_per_task is None else max_candidate_acquisitions_per_task
        if not 1 <= max_acquisitions_per_task <= candidate_budget <= max_results_per_task:
            raise ValueError("source acquisition budgets are invalid")
        self._search = search
        self._max_results_per_task = max_results_per_task
        self._timeout_seconds = timeout_seconds
        self._source_retriever = source_retriever
        self._max_acquisitions_per_task = max_acquisitions_per_task
        self._max_candidate_acquisitions_per_task = candidate_budget

    def research(self, case: Case, task: ResearchTask, *, excluded_source_urls: set[str] | frozenset[str] | None = None, excluded_content: set[str] | frozenset[str] | None = None) -> CompanyResearchResult:
        task_error = self._validate_task(case, task)
        if task_error is not None:
            return CompanyResearchResult(
                status=CompanyResearchStatus.REJECTED,
                attempt_budget=task.max_attempts,
                errors=[task_error],
                gap_reason="company research task was not authorized for this Case",
            )

        # C06 sets an explicit maximum. C07 deliberately makes one visible
        # provider call and never adds implicit retry or fallback behavior.
        try:
            results = self._search.search(
                SearchQuery(
                    query=task.query,
                    limit=self._max_results_per_task,
                    timeout_seconds=self._timeout_seconds,
                ),
            )
        except ProviderError as error:
            return self._provider_failure(task, error)
        except Exception:
            return CompanyResearchResult(
                status=CompanyResearchStatus.UNAVAILABLE,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                errors=[CompanyResearchError(
                    code=CompanyResearchErrorCode.PROVIDER_UNAVAILABLE,
                    message="search provider failed without a normalized response",
                )],
                gap_reason="company discovery provider is unavailable",
            )

        if not isinstance(results, list):
            return CompanyResearchResult(
                status=CompanyResearchStatus.REJECTED,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                errors=[CompanyResearchError(
                    code=CompanyResearchErrorCode.INVALID_PROVIDER_RESULT,
                    message="search provider returned a non-list result",
                )],
                gap_reason="company discovery response could not be validated",
            )

        findings: list[RawFinding] = []
        seen_urls = _canonical_urls(excluded_source_urls or ())
        seen_content = {_content_key(value) for value in (excluded_content or ())}
        rejected_count = 0
        blocked_count = 0
        malformed_count = 0
        retained = 0
        candidate_acquisitions = 0
        for result in sorted(results[:self._max_results_per_task], key=lambda item: self._acquisition_priority(case, item)):
            if self._is_blocked(result):
                blocked_count += 1
                continue
            finding, malformed = self._to_finding(case, task, result)
            if finding is None:
                rejected_count += 1
                malformed_count += int(malformed)
                continue
            candidate_key = _canonical_url(finding.source_url)
            if candidate_key in seen_urls:
                rejected_count += 1
                continue
            if self._source_retriever is not None:
                if retained >= self._max_acquisitions_per_task or candidate_acquisitions >= self._max_candidate_acquisitions_per_task:
                    rejected_count += 1
                    continue
                candidate_acquisitions += 1
                acquired = self._source_retriever.retrieve(finding.source_url)
                if acquired.content is None:
                    rejected_count += 1
                    continue
                if assess_source_suitability(acquired.content) is not SourceSuitability.SUBSTANTIVE:
                    rejected_count += 1
                    continue
                finding = finding.model_copy(update={
                    "source_url": acquired.content.final_url,
                    "discovery_url": acquired.content.requested_url,
                    "title": acquired.content.title,
                    "publication_date": acquired.content.publication_date,
                    "extracted_content": acquired.content.text,
                    "content_origin": ContentOrigin.PUBLIC_PAGE,
                })
            content_key = _content_key(finding.extracted_content)
            if content_key in seen_content:
                rejected_count += 1
                continue
            source_key = _canonical_url(finding.source_url)
            if source_key in seen_urls:
                rejected_count += 1
                continue
            seen_urls.add(source_key)
            if finding.discovery_url:
                seen_urls.add(_canonical_url(finding.discovery_url))
            seen_content.add(content_key)
            findings.append(finding)
            retained += 1

        if findings:
            errors = ([CompanyResearchError(
                code=CompanyResearchErrorCode.INVALID_PROVIDER_RESULT,
                message="one or more search results did not satisfy the discovery contract",
            )] if malformed_count else [])
            return CompanyResearchResult(
                status=CompanyResearchStatus.PARTIAL if rejected_count or blocked_count else CompanyResearchStatus.COMPLETED,
                findings=findings,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                rejected_result_count=rejected_count,
                blocked_result_count=blocked_count,
                errors=errors,
                gap_reason=("some discovery results were unavailable or did not meet retention rules" if rejected_count or blocked_count else None),
            )
        if blocked_count:
            return CompanyResearchResult(
                status=CompanyResearchStatus.UNAVAILABLE,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                rejected_result_count=rejected_count,
                blocked_result_count=blocked_count,
                gap_reason="all candidate company sources were blocked or unavailable",
            )
        return CompanyResearchResult(
            status=CompanyResearchStatus.REJECTED if malformed_count else CompanyResearchStatus.NOT_FOUND,
            attempts_used=1,
            attempt_budget=task.max_attempts,
            rejected_result_count=rejected_count,
            errors=([CompanyResearchError(
                code=CompanyResearchErrorCode.INVALID_PROVIDER_RESULT,
                message="search results did not satisfy the discovery contract",
            )] if malformed_count else []),
            gap_reason=("company discovery response could not be validated" if malformed_count else "no valid meeting-relevant company discovery results were retained"),
        )

    @staticmethod
    def _validate_task(case: Case, task: ResearchTask) -> CompanyResearchError | None:
        if task.case_id != case.case_id:
            return CompanyResearchError(code=CompanyResearchErrorCode.INVALID_TASK, message="research task does not belong to the supplied Case")
        if task.target_type is not TargetType.COMPANY or task.category not in _COMPANY_CATEGORIES:
            return CompanyResearchError(code=CompanyResearchErrorCode.INVALID_TASK, message="C07 accepts only approved COMPANY research tasks")
        if task.status is not ResearchTaskStatus.PENDING:
            return CompanyResearchError(code=CompanyResearchErrorCode.INVALID_TASK, message="C07 accepts only pending research tasks")
        return None

    def _to_finding(self, case: Case, task: ResearchTask, result: object) -> tuple[RawFinding | None, bool]:
        if not isinstance(result, SearchResult):
            return None, True
        url = _public_discovery_url(result.url)
        title = result.title.strip()
        snippet = result.snippet.strip()
        if url is None or not title or not snippet:
            return None, True
        if not self._is_relevant(case, task, result):
            return None, False
        return RawFinding(
            case_id=case.case_id,
            research_task_id=task.research_task_id,
            source_url=url,
            title=title,
            publisher=result.publisher,
            publication_date=result.published_at,
            extracted_content=snippet,
            topic=task.category.value,
            relevance="MEETING_RELEVANT_DISCOVERY",
        ), False

    @staticmethod
    def _is_blocked(result: object) -> bool:
        return isinstance(result, SearchResult) and str(result.provider_metadata.get("access_status", "")).upper() == "BLOCKED"

    @staticmethod
    def _is_relevant(case: Case, task: ResearchTask, result: SearchResult) -> bool:
        corpus = _terms(" ".join(filter(None, (result.title, result.snippet, result.publisher))))
        company_terms = _terms(case.company_name)
        goal_terms = _terms(case.meeting_goal)
        category_terms = _terms(task.category.value.replace("_", " "))
        return bool(corpus & company_terms or corpus & goal_terms or corpus & category_terms)

    @staticmethod
    def _acquisition_priority(case: Case, result: object) -> int:
        if not isinstance(result, SearchResult) or not case.company_website:
            return 1
        expected = urlsplit(case.company_website).hostname or ""
        actual = urlsplit(result.url).hostname or ""
        return 0 if actual == expected or actual.endswith(f".{expected}") else 1

    @staticmethod
    def _provider_failure(task: ResearchTask, error: ProviderError) -> CompanyResearchResult:
        code = (
            CompanyResearchErrorCode.PROVIDER_TIMEOUT
            if error.code is ProviderErrorCode.TIMEOUT
            else CompanyResearchErrorCode.PROVIDER_UNAVAILABLE
        )
        return CompanyResearchResult(
            status=CompanyResearchStatus.UNAVAILABLE,
            attempts_used=1,
            attempt_budget=task.max_attempts,
            errors=[CompanyResearchError(code=code, message="company discovery provider is unavailable")],
            gap_reason="company discovery provider is unavailable",
            retryable_provider_failure=error.retryable,
        )


def _terms(value: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", value.casefold()) if len(term) > 2 and term not in _STOP_WORDS}


def _public_discovery_url(value: str) -> str | None:
    try:
        return normalize_external_url(value)
    except UnsafeExternalUrlError:
        return None


def _canonical_url(value: str) -> str:
    return normalize_external_url(value)


def _canonical_urls(values: set[str] | frozenset[str]) -> set[str]:
    canonical: set[str] = set()
    for value in values:
        try:
            canonical.add(_canonical_url(value))
        except UnsafeExternalUrlError:
            continue
    return canonical


def _content_key(value: str) -> str:
    return " ".join(value.casefold().split())
