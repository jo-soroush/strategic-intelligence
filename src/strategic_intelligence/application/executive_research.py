"""Bounded, privacy-minimizing executive discovery for V1-C08."""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.domain.models import Case, RawFinding, ResearchCategory, ResearchTask, ResearchTaskStatus, TargetType
from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchProvider, SearchQuery, SearchResult
from strategic_intelligence.security import UnsafeExternalUrlError, normalize_external_url


_EXECUTIVE_CATEGORIES = frozenset({
    ResearchCategory.EXECUTIVE_ROLE,
    ResearchCategory.EXECUTIVE_FOCUS,
    ResearchCategory.PUBLICATIONS,
    ResearchCategory.INTERVIEWS,
    ResearchCategory.PUBLIC_ACTIVITY,
})
_STOP_WORDS = frozenset({"about", "and", "for", "from", "into", "meeting", "the", "this", "with"})
_PROFESSIONAL_TERMS = frozenset({
    "article", "business", "company", "conference", "director", "executive",
    "focus", "interview", "leader", "leadership", "professional", "project",
    "publication", "responsibilities", "responsibility", "role", "speaker",
    "strategy", "talk",
})
_EXCLUDED_PERSONAL_MARKERS = (
    "home address", "lives at", "private relationship", "family details",
    "children", "spouse", "married", "divorce", "personal routine", "daily routine",
    "medical condition", "mental health", "sexual orientation", "religion", "ethnicity",
    "race", "political affiliation", "disability", "unrelated personal activity",
)


class ExecutiveResearchStatus(str, Enum):
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    REJECTED = "REJECTED"


class ExecutiveResearchErrorCode(str, Enum):
    INVALID_TASK = "INVALID_TASK"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    PROVIDER_TIMEOUT = "PROVIDER_TIMEOUT"
    INVALID_PROVIDER_RESULT = "INVALID_PROVIDER_RESULT"


class ExecutiveResearchModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ExecutiveResearchError(ExecutiveResearchModel):
    code: ExecutiveResearchErrorCode
    message: str


class ExecutiveResearchResult(ExecutiveResearchModel):
    """Raw discovery output; it deliberately contains neither Evidence nor Claims."""

    status: ExecutiveResearchStatus
    findings: list[RawFinding] = Field(default_factory=list)
    attempts_used: int = Field(default=0, ge=0)
    attempt_budget: int = Field(ge=1, le=3)
    rejected_result_count: int = Field(default=0, ge=0)
    identity_rejected_result_count: int = Field(default=0, ge=0)
    privacy_rejected_result_count: int = Field(default=0, ge=0)
    errors: list[ExecutiveResearchError] = Field(default_factory=list)
    gap_reason: str | None = None
    retryable_provider_failure: bool | None = None


class ExecutiveResearchService:
    """Consumes one C06 executive task through the provider-neutral C04 boundary."""

    def __init__(self, search: SearchProvider, *, max_results_per_task: int = 5, timeout_seconds: float = 5.0) -> None:
        if not 1 <= max_results_per_task <= 10:
            raise ValueError("max_results_per_task must be between one and ten")
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._search = search
        self._max_results_per_task = max_results_per_task
        self._timeout_seconds = timeout_seconds

    def research(self, case: Case, task: ResearchTask) -> ExecutiveResearchResult:
        task_error = self._validate_task(case, task)
        if task_error is not None:
            return ExecutiveResearchResult(
                status=ExecutiveResearchStatus.REJECTED,
                attempt_budget=task.max_attempts,
                errors=[task_error],
                gap_reason="executive research task was not authorized for this Case",
            )
        try:
            results = self._search.search(SearchQuery(
                query=task.query,
                limit=self._max_results_per_task,
                timeout_seconds=self._timeout_seconds,
            ))
        except ProviderError as error:
            return self._provider_failure(task, error)
        except Exception:
            return ExecutiveResearchResult(
                status=ExecutiveResearchStatus.UNAVAILABLE,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                errors=[ExecutiveResearchError(
                    code=ExecutiveResearchErrorCode.PROVIDER_UNAVAILABLE,
                    message="search provider failed without a normalized response",
                )],
                gap_reason="executive discovery provider is unavailable",
            )

        if not isinstance(results, list):
            return ExecutiveResearchResult(
                status=ExecutiveResearchStatus.REJECTED,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                errors=[ExecutiveResearchError(
                    code=ExecutiveResearchErrorCode.INVALID_PROVIDER_RESULT,
                    message="search provider returned a non-list result",
                )],
                gap_reason="executive discovery response could not be validated",
            )

        findings: list[RawFinding] = []
        seen_urls: set[str] = set()
        rejected_count = identity_rejected = privacy_rejected = malformed_count = 0
        for result in results[:self._max_results_per_task]:
            finding, reason = self._to_finding(case, task, result)
            if finding is None:
                rejected_count += 1
                identity_rejected += int(reason == "identity")
                privacy_rejected += int(reason == "privacy")
                malformed_count += int(reason == "malformed")
                continue
            source_key = finding.source_url.casefold()
            if source_key in seen_urls:
                rejected_count += 1
                continue
            seen_urls.add(source_key)
            findings.append(finding)

        errors = ([ExecutiveResearchError(
            code=ExecutiveResearchErrorCode.INVALID_PROVIDER_RESULT,
            message="one or more search results did not satisfy the discovery contract",
        )] if malformed_count else [])
        if findings:
            return ExecutiveResearchResult(
                status=ExecutiveResearchStatus.PARTIAL if rejected_count else ExecutiveResearchStatus.COMPLETED,
                findings=findings,
                attempts_used=1,
                attempt_budget=task.max_attempts,
                rejected_result_count=rejected_count,
                identity_rejected_result_count=identity_rejected,
                privacy_rejected_result_count=privacy_rejected,
                errors=errors,
                gap_reason=("some discovery results did not meet identity, privacy, or retention rules" if rejected_count else None),
            )
        return ExecutiveResearchResult(
            status=ExecutiveResearchStatus.REJECTED if malformed_count else ExecutiveResearchStatus.NOT_FOUND,
            attempts_used=1,
            attempt_budget=task.max_attempts,
            rejected_result_count=rejected_count,
            identity_rejected_result_count=identity_rejected,
            privacy_rejected_result_count=privacy_rejected,
            errors=errors,
            gap_reason=("executive discovery response could not be validated" if malformed_count else "no valid public-professional executive discovery results were retained"),
        )

    @staticmethod
    def _validate_task(case: Case, task: ResearchTask) -> ExecutiveResearchError | None:
        if task.case_id != case.case_id:
            return ExecutiveResearchError(code=ExecutiveResearchErrorCode.INVALID_TASK, message="research task does not belong to the supplied Case")
        if task.target_type is not TargetType.EXECUTIVE or task.category not in _EXECUTIVE_CATEGORIES:
            return ExecutiveResearchError(code=ExecutiveResearchErrorCode.INVALID_TASK, message="C08 accepts only approved EXECUTIVE research tasks")
        if task.status is not ResearchTaskStatus.PENDING:
            return ExecutiveResearchError(code=ExecutiveResearchErrorCode.INVALID_TASK, message="C08 accepts only pending research tasks")
        return None

    def _to_finding(self, case: Case, task: ResearchTask, result: object) -> tuple[RawFinding | None, str | None]:
        if not isinstance(result, SearchResult):
            return None, "malformed"
        url = _public_discovery_url(result.url)
        title = result.title.strip()
        snippet = result.snippet.strip()
        if url is None or not title or not snippet:
            return None, "malformed"
        corpus_text = " ".join(filter(None, (title, snippet, result.publisher)))
        if _contains_excluded_personal_data(corpus_text):
            return None, "privacy"
        corpus = _terms(corpus_text)
        if not _terms(case.executive_name).issubset(corpus):
            return None, "identity"
        if not self._is_professionally_relevant(case, task, corpus):
            return None, "relevance"
        return RawFinding(
            case_id=case.case_id,
            research_task_id=task.research_task_id,
            source_url=url,
            title=title,
            publisher=result.publisher,
            publication_date=result.published_at,
            extracted_content=snippet,
            topic=task.category.value,
            relevance="PUBLIC_PROFESSIONAL_MEETING_RELEVANT_DISCOVERY",
        ), None

    @staticmethod
    def _is_professionally_relevant(case: Case, task: ResearchTask, corpus: set[str]) -> bool:
        company_context_terms = _terms(case.company_name) - _terms(case.executive_name)
        return bool(
            corpus & company_context_terms
            or corpus & _terms(case.meeting_goal)
            or corpus & _terms(task.category.value.replace("_", " "))
            or corpus & _PROFESSIONAL_TERMS
        )

    @staticmethod
    def _provider_failure(task: ResearchTask, error: ProviderError) -> ExecutiveResearchResult:
        code = ExecutiveResearchErrorCode.PROVIDER_TIMEOUT if error.code is ProviderErrorCode.TIMEOUT else ExecutiveResearchErrorCode.PROVIDER_UNAVAILABLE
        return ExecutiveResearchResult(
            status=ExecutiveResearchStatus.UNAVAILABLE,
            attempts_used=1,
            attempt_budget=task.max_attempts,
            errors=[ExecutiveResearchError(code=code, message="executive discovery provider is unavailable")],
            gap_reason="executive discovery provider is unavailable",
            retryable_provider_failure=error.retryable,
        )


def _terms(value: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9]+", value.casefold()) if len(term) > 2 and term not in _STOP_WORDS}


def _contains_excluded_personal_data(value: str) -> bool:
    normalized = " ".join(value.casefold().split())
    return any(marker in normalized for marker in _EXCLUDED_PERSONAL_MARKERS)


def _public_discovery_url(value: str) -> str | None:
    try:
        return normalize_external_url(value)
    except UnsafeExternalUrlError:
        return None
