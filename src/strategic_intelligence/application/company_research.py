"""Bounded company discovery for V1-C07; discovery results never become Evidence."""

from __future__ import annotations

import ipaddress
import re
from enum import Enum
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.domain.models import Case, RawFinding, ResearchCategory, ResearchTask, ResearchTaskStatus, TargetType
from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchProvider, SearchQuery, SearchResult


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


class CompanyResearchService:
    """Consumes one C06 company task through the provider-neutral C04 boundary."""

    def __init__(self, search: SearchProvider, *, max_results_per_task: int = 5, timeout_seconds: float = 5.0) -> None:
        if not 1 <= max_results_per_task <= 10:
            raise ValueError("max_results_per_task must be between one and ten")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._search = search
        self._max_results_per_task = max_results_per_task
        self._timeout_seconds = timeout_seconds

    def research(self, case: Case, task: ResearchTask) -> CompanyResearchResult:
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
        seen_urls: set[str] = set()
        rejected_count = 0
        blocked_count = 0
        malformed_count = 0
        for result in results[:self._max_results_per_task]:
            if self._is_blocked(result):
                blocked_count += 1
                continue
            finding, malformed = self._to_finding(case, task, result)
            if finding is None:
                rejected_count += 1
                malformed_count += int(malformed)
                continue
            source_key = finding.source_url.casefold()
            if source_key in seen_urls:
                rejected_count += 1
                continue
            seen_urls.add(source_key)
            findings.append(finding)

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
        )


def _terms(value: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", value.casefold()) if len(term) > 2 and term not in _STOP_WORDS}


def _public_discovery_url(value: str) -> str | None:
    if value != value.strip() or any(character.isspace() for character in value):
        return None
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".local"):
        return None
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        return None
    netloc = hostname if port is None else f"{hostname}:{port}"
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "", parsed.query, ""))
