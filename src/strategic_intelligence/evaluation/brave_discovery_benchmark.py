"""C20-only, frozen Brave discovery benchmark.

This module evaluates bounded discovery mechanics.  It is deliberately not
part of workflow composition and never imports the Golden Case answer key.
Discovery reports are frozen before a caller may supply post-run scoring
targets.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
from math import ceil
from time import perf_counter
from typing import Protocol, Sequence

from strategic_intelligence.application.company_research import CompanyResearchService
from strategic_intelligence.application.executive_research import ExecutiveResearchService
from strategic_intelligence.application.source_acquisition import (
    PublicSourceRetriever,
    SourceAcquisitionResult,
    assess_source_suitability,
)
from strategic_intelligence.domain.models import Case, ResearchTask, TargetType
from strategic_intelligence.providers.contracts import SearchProvider, SearchQuery, SearchResult
from strategic_intelligence.security.boundaries import UnsafeExternalUrlError, normalize_external_url


class BenchmarkVariantId(str, Enum):
    CONTROL = "CONTROL"
    V1_RESULT_DEPTH = "V1_RESULT_DEPTH"
    V2_PAGINATION = "V2_PAGINATION"
    V3_FIRST_PARTY_PRIORITY = "V3_FIRST_PARTY_PRIORITY"


class BenchmarkExecutionStatus(str, Enum):
    FROZEN = "FROZEN"
    NOT_EXECUTABLE_WITH_CURRENT_CONTRACT = "NOT_EXECUTABLE_WITH_CURRENT_CONTRACT"
    INELIGIBLE_NO_RUNTIME_DOMAIN = "INELIGIBLE_NO_RUNTIME_DOMAIN"


class DiscoverySuccess(str, Enum):
    NO_IMPROVEMENT = "NO_IMPROVEMENT"
    MARGINAL = "MARGINAL"
    MEANINGFUL = "MEANINGFUL"
    STRONG = "STRONG"


@dataclass(frozen=True)
class BenchmarkVariant:
    variant_id: BenchmarkVariantId
    count: int
    offsets: tuple[int, ...]
    requires_company_website: bool = False

    def __post_init__(self) -> None:
        expected = {
            BenchmarkVariantId.CONTROL: (5, (0,), False),
            BenchmarkVariantId.V1_RESULT_DEPTH: (10, (0,), False),
            BenchmarkVariantId.V2_PAGINATION: (5, (0, 1), False),
            BenchmarkVariantId.V3_FIRST_PARTY_PRIORITY: (5, (0,), True),
        }[self.variant_id]
        if (self.count, self.offsets, self.requires_company_website) != expected:
            raise ValueError("benchmark variant must use its predeclared bounded configuration")

    @property
    def max_calls(self) -> int:
        return 26 if self.variant_id is BenchmarkVariantId.V2_PAGINATION else 13

    @property
    def max_candidates(self) -> int:
        return self.max_calls * self.count


CONTROL = BenchmarkVariant(BenchmarkVariantId.CONTROL, 5, (0,))
V1_RESULT_DEPTH = BenchmarkVariant(BenchmarkVariantId.V1_RESULT_DEPTH, 10, (0,))
V2_PAGINATION = BenchmarkVariant(BenchmarkVariantId.V2_PAGINATION, 5, (0, 1))
V3_FIRST_PARTY_PRIORITY = BenchmarkVariant(BenchmarkVariantId.V3_FIRST_PARTY_PRIORITY, 5, (0,), True)
ALL_VARIANTS = (CONTROL, V1_RESULT_DEPTH, V2_PAGINATION, V3_FIRST_PARTY_PRIORITY)


@dataclass(frozen=True)
class FrozenResearchInputs:
    """The pre-evaluation C06 task set; reports expose hashes, never queries."""

    tasks: tuple[ResearchTask, ...]
    fingerprint: str

    @classmethod
    def create(cls, tasks: Sequence[ResearchTask]) -> "FrozenResearchInputs":
        frozen = tuple(tasks)
        if not frozen or len(frozen) > 13:
            raise ValueError("benchmark requires one to thirteen frozen C06 tasks")
        if len({item.research_task_id for item in frozen}) != len(frozen):
            raise ValueError("frozen task IDs must be unique")
        payload = "\n".join(
            f"{item.research_task_id}|{item.case_id}|{item.target_type.value}|{item.category.value}|{item.query}"
            for item in frozen
        )
        return cls(tasks=frozen, fingerprint=_fingerprint(payload))


@dataclass(frozen=True)
class CandidateObservation:
    variant_id: BenchmarkVariantId
    task_id: str
    query_fingerprint: str
    requested_count: int
    offset: int
    ordinal: int
    canonical_url_hash: str | None
    provider_result_present: bool
    acquisition_attempted: bool | None
    acquisition_outcome: str
    suitability_outcome: str
    dedupe_outcome: str
    retained: bool
    error_class: str | None
    elapsed_ms: int


@dataclass(frozen=True)
class FrozenVariantReport:
    variant: BenchmarkVariant
    status: BenchmarkExecutionStatus
    input_fingerprint: str
    api_calls: int
    results_returned: int
    candidates: tuple[CandidateObservation, ...]
    retained_source_hashes: tuple[str, ...]
    acquired_page_count: int
    elapsed_ms: int

    @property
    def candidates_inspected(self) -> int:
        return len(self.candidates)


@dataclass(frozen=True)
class PostFreezeTargets:
    """Answer-key-derived hashes supplied only after every report is frozen."""

    official_page_hashes: frozenset[str]
    authoritative_url_hashes: frozenset[str]
    proposition_source_hashes: frozenset[str]
    useful_source_hashes: frozenset[str]

    def __post_init__(self) -> None:
        if not self.official_page_hashes:
            raise ValueError("post-freeze targets require at least one official page")


@dataclass(frozen=True)
class BenchmarkScore:
    variant_id: BenchmarkVariantId
    exact_official_discovered: int
    exact_official_persisted: int
    authoritative_urls_discovered: int
    useful_unique_sources: int
    proposition_source_hits: int
    api_calls: int
    candidates_inspected: int
    acquired_pages: int
    elapsed_ms: int
    authoritative_per_candidate: float
    useful_per_acquired_page: float
    proposition_recall_per_retained_slot: float
    authoritative_per_api_call: float
    elapsed_per_useful_source: float


@dataclass(frozen=True)
class BenchmarkComparison:
    control: BenchmarkScore
    variant: BenchmarkScore
    success: DiscoverySuccess


class _RetrievalBoundary(Protocol):
    def retrieve(self, url: str) -> SourceAcquisitionResult: ...


@dataclass(frozen=True)
class _RetrievalObservation:
    url_hash: str | None
    outcome: str
    suitability: str
    elapsed_ms: int


class _RecordingRetriever:
    """Observes the existing protected retriever without retaining page content."""

    def __init__(self, delegate: _RetrievalBoundary) -> None:
        self._delegate = delegate
        self.observations: list[_RetrievalObservation] = []

    def retrieve(self, url: str) -> SourceAcquisitionResult:
        started = perf_counter()
        result = self._delegate.retrieve(url)
        suitability = "NOT_MEASURED"
        if result.content is not None:
            suitability = assess_source_suitability(result.content).value
        self.observations.append(_RetrievalObservation(
            url_hash=_url_hash(url),
            outcome="SUCCESS" if result.content is not None else (result.failure.value if result.failure else "UNKNOWN"),
            suitability=suitability,
            elapsed_ms=max(0, int((perf_counter() - started) * 1000)),
        ))
        return result


class _RecordingSearch:
    def __init__(self, delegate: SearchProvider) -> None:
        self._delegate = delegate
        self.calls: list[tuple[SearchQuery, list[SearchResult], int]] = []

    def search(self, query: SearchQuery) -> list[SearchResult]:
        started = perf_counter()
        results = self._delegate.search(query)
        self.calls.append((query, results, max(0, int((perf_counter() - started) * 1000))))
        return results


class BraveDiscoveryBenchmark:
    """Runs only frozen C06 discovery through existing C04/C07/C08/C14 boundaries."""

    def __init__(self, search: SearchProvider, source_retriever: _RetrievalBoundary) -> None:
        self._search = search
        self._source_retriever = source_retriever

    def run(self, case: Case, inputs: FrozenResearchInputs, variant: BenchmarkVariant) -> FrozenVariantReport:
        if any(task.case_id != case.case_id for task in inputs.tasks):
            raise ValueError("frozen tasks must belong to the benchmark Case")
        if variant.variant_id is BenchmarkVariantId.V2_PAGINATION:
            return FrozenVariantReport(variant, BenchmarkExecutionStatus.NOT_EXECUTABLE_WITH_CURRENT_CONTRACT, inputs.fingerprint, 0, 0, (), (), 0, 0)
        if variant.requires_company_website and not case.company_website:
            return FrozenVariantReport(variant, BenchmarkExecutionStatus.INELIGIBLE_NO_RUNTIME_DOMAIN, inputs.fingerprint, 0, 0, (), (), 0, 0)

        started = perf_counter()
        search = _RecordingSearch(self._search)
        retriever = _RecordingRetriever(self._source_retriever)
        company = CompanyResearchService(search, max_results_per_task=variant.count, source_retriever=retriever, max_acquisitions_per_task=2, max_candidate_acquisitions_per_task=variant.count)
        executive = ExecutiveResearchService(search, max_results_per_task=variant.count, source_retriever=retriever, max_acquisitions_per_task=2, max_candidate_acquisitions_per_task=variant.count)
        retained_urls: set[str] = set()
        retained_content: set[str] = set()
        retained_hashes: set[str] = set()
        candidates: list[CandidateObservation] = []
        for task in inputs.tasks:
            before_calls = len(search.calls)
            before_retrievals = len(retriever.observations)
            if task.target_type is TargetType.COMPANY:
                result = company.research(case, task, excluded_source_urls=retained_urls, excluded_content=retained_content)
            else:
                result = executive.research(case, task, excluded_source_urls=retained_urls, excluded_content=retained_content)
            if len(search.calls) != before_calls + 1:
                raise ValueError("benchmark discovery must make exactly one C04 call per executable task")
            query, results, elapsed = search.calls[-1]
            if query.limit != variant.count or len(results) > variant.count:
                raise ValueError("provider result bound was violated")
            retrievals = {item.url_hash: item for item in retriever.observations[before_retrievals:]}
            finding_hashes = {_url_hash(item.source_url) for item in result.findings}
            finding_hashes.update(_url_hash(item.discovery_url) for item in result.findings if item.discovery_url)
            for ordinal, item in enumerate(results, start=1):
                url_hash = _url_hash(item.url)
                retrieval = retrievals.get(url_hash)
                candidates.append(CandidateObservation(
                    variant.variant_id, task.research_task_id, _fingerprint(task.query), variant.count, 0, ordinal,
                    url_hash, True, retrieval is not None,
                    "NOT_MEASURED" if retrieval is None else retrieval.outcome,
                    "NOT_MEASURED" if retrieval is None else retrieval.suitability,
                    "RETAINED" if url_hash in finding_hashes else "NOT_MEASURED",
                    url_hash in finding_hashes, None, elapsed,
                ))
            retained_urls.update(item.source_url for item in result.findings)
            retained_content.update(item.extracted_content for item in result.findings)
            retained_hashes.update(hash_value for hash_value in finding_hashes if hash_value is not None)
        if len(search.calls) > variant.max_calls or len(candidates) > variant.max_candidates:
            raise ValueError("benchmark bounds were violated")
        return FrozenVariantReport(
            variant, BenchmarkExecutionStatus.FROZEN, inputs.fingerprint, len(search.calls),
            sum(len(results) for _, results, _ in search.calls), tuple(candidates), tuple(sorted(retained_hashes)),
            len(retriever.observations), max(0, int((perf_counter() - started) * 1000)),
        )


def score_frozen_report(report: FrozenVariantReport, targets: PostFreezeTargets) -> BenchmarkScore:
    """Score a frozen report only; discovery has no access to these targets."""
    if report.status is not BenchmarkExecutionStatus.FROZEN:
        raise ValueError("only frozen executable reports may be scored")
    discovered = {item.canonical_url_hash for item in report.candidates if item.canonical_url_hash}
    retained = set(report.retained_source_hashes)
    official_discovered = len(discovered & targets.official_page_hashes)
    official_persisted = len(retained & targets.official_page_hashes)
    authoritative = len(discovered & targets.authoritative_url_hashes)
    useful = len(retained & targets.useful_source_hashes)
    proposition = len(retained & targets.proposition_source_hashes)
    return BenchmarkScore(
        report.variant.variant_id, official_discovered, official_persisted, authoritative, useful, proposition,
        report.api_calls, report.candidates_inspected, report.acquired_page_count, report.elapsed_ms,
        _ratio(authoritative, report.candidates_inspected), _ratio(useful, report.acquired_page_count),
        _ratio(proposition, len(report.retained_source_hashes)), _ratio(authoritative, report.api_calls),
        _ratio(report.elapsed_ms, useful),
    )


def compare_scores(control: BenchmarkScore, variant: BenchmarkScore, *, trust_regression: bool = False, proposition_target_count: int = 20) -> BenchmarkComparison:
    """Apply predeclared categories; two proposition sources is material at 20 targets."""
    if proposition_target_count <= 0:
        raise ValueError("proposition target count must be positive")
    persisted_gain = variant.exact_official_persisted - control.exact_official_persisted
    proposition_gain = variant.proposition_source_hits - control.proposition_source_hits
    discovered_gain = variant.authoritative_urls_discovered - control.authoritative_urls_discovered
    within_cost = variant.api_calls <= control.api_calls * 2
    material_gain = max(2, ceil(proposition_target_count * 0.10))
    if persisted_gain >= 2 and proposition_gain >= material_gain and not trust_regression and within_cost and variant.authoritative_per_candidate > control.authoritative_per_candidate:
        outcome = DiscoverySuccess.STRONG
    elif persisted_gain >= 1 and proposition_gain > 0 and not trust_regression and within_cost:
        outcome = DiscoverySuccess.MEANINGFUL
    elif discovered_gain >= 1:
        outcome = DiscoverySuccess.MARGINAL
    else:
        outcome = DiscoverySuccess.NO_IMPROVEMENT
    return BenchmarkComparison(control, variant, outcome)


def _fingerprint(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def _url_hash(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return _fingerprint(normalize_external_url(value))
    except UnsafeExternalUrlError:
        return None


def _ratio(numerator: int, denominator: int) -> float:
    return 0.0 if denominator == 0 else round(numerator / denominator, 6)
