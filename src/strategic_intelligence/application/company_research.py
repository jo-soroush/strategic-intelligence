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
_GENERIC_COMPANY_TERMS = frozenset({
    "ai", "co", "company", "corp", "corporation", "group", "inc", "lab", "labs",
    "limited", "llc", "ltd", "org", "organization", "systems", "technologies",
})


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
                if not self._is_acquired_relevant(case, finding, result.publisher):
                    rejected_count += 1
                    continue
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
        corpus_text = " ".join(filter(None, (result.title, result.snippet, result.publisher)))
        return _company_identity_supported(case, corpus_text, result.url)

    @staticmethod
    def _is_acquired_relevant(case: Case, finding: RawFinding, publisher: str | None) -> bool:
        page_text = " ".join(filter(None, (finding.title, finding.extracted_content)))
        return _company_identity_supported(case, page_text, finding.source_url, publisher=publisher)

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


def _normalized_words(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.casefold())


def _contains_company_phrase(text: str, company_name: str) -> bool:
    words = _normalized_words(company_name)
    if not words:
        return False
    last = words[-1]
    variants = {last}
    if last in {"lab", "labs"}:
        variants.add("labs" if last == "lab" else "lab")
    corpus_words = _normalized_words(text)
    return any(
        corpus_words[index:index + len(words) - 1] == words[:-1]
        and corpus_words[index + len(words) - 1] in variants
        for index in range(len(corpus_words) - len(words) + 1)
    )


def _company_identity_supported(case: Case, content_text: str, source_url: str, *, publisher: str | None = None) -> bool:
    # The configured official domain (and its subdomains) is the primary,
    # strong company-identity anchor; it alone is sufficient.
    if _matches_company_domain(case.company_website, source_url):
        return True

    content_terms = _terms(content_text)
    company_terms = _terms(case.company_name)
    meaningful_company_terms = company_terms - _GENERIC_COMPANY_TERMS
    publisher_terms = _terms(publisher or "")
    name_signal = bool(
        _contains_company_phrase(content_text, case.company_name)
        or (
            len(meaningful_company_terms) >= 2
            and meaningful_company_terms.issubset(content_terms | publisher_terms)
            and bool(meaningful_company_terms & content_terms)
        )
    )
    if not name_signal:
        return False
    if not case.company_website:
        # No official domain is configured; preserve the prior name-based
        # determination rather than requiring an anchor that does not exist.
        return True
    # Off the official domain, a same- or similar-name match alone does not
    # establish identity: unrelated real entities can share the same name.
    # Require a deterministic, literal tie back to the configured domain.
    return (
        _contains_official_domain_reference(content_text, case.company_website)
        or _contains_official_domain_reference(publisher or "", case.company_website)
    )


def _matches_company_domain(company_website: str | None, result_url: str) -> bool:
    """The configured official host, or a valid subdomain of it, is a strong anchor."""
    if not company_website:
        return False
    expected = (urlsplit(company_website).hostname or "").casefold().removeprefix("www.")
    actual = (urlsplit(result_url).hostname or "").casefold().removeprefix("www.")
    return bool(expected) and (actual == expected or actual.endswith(f".{expected}"))


def _contains_official_domain_reference(text: str, company_website: str | None) -> bool:
    """A literal, deterministic mention of the configured official domain."""
    if not company_website:
        return False
    host = (urlsplit(company_website).hostname or "").casefold().removeprefix("www.")
    host_words = _normalized_words(host)
    if not host_words:
        return False
    corpus_words = _normalized_words(text)
    return any(
        corpus_words[index:index + len(host_words)] == host_words
        for index in range(len(corpus_words) - len(host_words) + 1)
    )


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
