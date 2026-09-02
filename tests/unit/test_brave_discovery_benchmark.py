"""C20 benchmark harness tests; no live provider, retrieval, or answer-key access."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from strategic_intelligence.application.source_acquisition import PublicSourceContent, SourceAcquisitionResult
from strategic_intelligence.domain.models import Case, ResearchCategory, ResearchTask, TargetType
from strategic_intelligence.evaluation.brave_discovery_benchmark import (
    ALL_VARIANTS,
    CONTROL,
    V1_RESULT_DEPTH,
    V2_PAGINATION,
    V3_FIRST_PARTY_PRIORITY,
    BenchmarkExecutionStatus,
    BraveDiscoveryBenchmark,
    DiscoverySuccess,
    FrozenResearchInputs,
    PostFreezeTargets,
    compare_scores,
    score_frozen_report,
)
from strategic_intelligence.providers.contracts import SearchQuery, SearchResult
from strategic_intelligence.providers.fakes import FakeSearchProvider


class _Retriever:
    def __init__(self) -> None:
        self.calls: list[str] = []

    def retrieve(self, url: str) -> SourceAcquisitionResult:
        self.calls.append(url)
        return SourceAcquisitionResult(content=PublicSourceContent(
            requested_url=url, final_url=url, title="Example official report",
            text="Example official report " + "substantive enterprise research content " * 15,
            publication_date=date(2026, 8, 30),
        ))


def _case(*, website: str | None = "https://example.test") -> Case:
    return Case(
        case_id="case", company_id="company", executive_id="executive", company_name="Example Co",
        executive_name="Ava Example", meeting_goal="prepare an enterprise AI meeting", company_website=website,
    )


def _inputs(count: int = 2) -> FrozenResearchInputs:
    tasks = [
        ResearchTask(
            research_task_id=f"task-{index}", case_id="case",
            target_type=TargetType.COMPANY if index == 0 else TargetType.EXECUTIVE,
            category=ResearchCategory.STRATEGY if index == 0 else ResearchCategory.EXECUTIVE_ROLE,
            query=f"Example Co research task {index}", priority=3,
        )
        for index in range(count)
    ]
    return FrozenResearchInputs.create(tasks)


def _results(count: int = 10) -> list[SearchResult]:
    return [SearchResult(
        title=f"Example Co report {index}", url=f"https://example.test/report-{index}",
        snippet="Example Co enterprise AI strategy report", publisher="Example Co",
    ) for index in range(count)]


def _run(variant=CONTROL, *, website: str | None = "https://example.test"):
    return BraveDiscoveryBenchmark(FakeSearchProvider(_results()), _Retriever()).run(_case(website=website), _inputs(), variant)


def test_control_and_v1_use_existing_c04_c07_c08_boundaries_with_predeclared_limits() -> None:
    control = _run(CONTROL)
    depth = _run(V1_RESULT_DEPTH)
    assert control.status is BenchmarkExecutionStatus.FROZEN
    assert control.api_calls == 2 and control.results_returned == 10 and control.candidates_inspected == 10
    assert all(item.requested_count == 5 and item.offset == 0 for item in control.candidates)
    assert depth.status is BenchmarkExecutionStatus.FROZEN
    assert depth.api_calls == 2 and depth.results_returned == 20 and depth.candidates_inspected == 20
    assert all(item.requested_count == 10 and item.offset == 0 for item in depth.candidates)
    assert control.input_fingerprint == depth.input_fingerprint
    assert len(control.retained_source_hashes) <= 4 and len(depth.retained_source_hashes) <= 4


def test_v2_fails_closed_when_the_existing_c04_contract_cannot_express_offset() -> None:
    report = _run(V2_PAGINATION)
    assert report.status is BenchmarkExecutionStatus.NOT_EXECUTABLE_WITH_CURRENT_CONTRACT
    assert report.api_calls == report.results_returned == report.candidates_inspected == 0


def test_v3_requires_a_normal_case_domain_and_never_uses_an_external_answer_key_domain() -> None:
    assert _run(V3_FIRST_PARTY_PRIORITY, website=None).status is BenchmarkExecutionStatus.INELIGIBLE_NO_RUNTIME_DOMAIN
    report = _run(V3_FIRST_PARTY_PRIORITY)
    assert report.status is BenchmarkExecutionStatus.FROZEN
    assert report.input_fingerprint == _run(CONTROL).input_fingerprint


def test_frozen_inputs_and_variant_configuration_are_bounded_and_reproducible() -> None:
    inputs = _inputs()
    assert inputs.fingerprint == FrozenResearchInputs.create(inputs.tasks).fingerprint
    assert [(item.variant_id.value, item.count, item.offsets, item.max_calls) for item in ALL_VARIANTS] == [
        ("CONTROL", 5, (0,), 13), ("V1_RESULT_DEPTH", 10, (0,), 13),
        ("V2_PAGINATION", 5, (0, 1), 26), ("V3_FIRST_PARTY_PRIORITY", 5, (0,), 13),
    ]
    with pytest.raises(ValueError, match="predeclared"):
        type(CONTROL)(CONTROL.variant_id, 20, (0,))
    with pytest.raises(ValueError, match="one to thirteen"):
        FrozenResearchInputs.create([])


def test_observations_are_redacted_and_content_minimized() -> None:
    report = _run(CONTROL)
    candidate = report.candidates[0]
    assert candidate.canonical_url_hash and "example.test" not in candidate.canonical_url_hash
    assert candidate.acquisition_attempted is True
    assert candidate.acquisition_outcome == "SUCCESS"
    assert candidate.suitability_outcome == "SUBSTANTIVE"
    assert "content" not in candidate.__dict__ and "credential" not in candidate.__dict__
    assert not hasattr(report, "page_bodies")


def test_scoring_requires_a_frozen_report_and_safe_zero_denominators() -> None:
    report = _run(CONTROL)
    targets = PostFreezeTargets(
        official_page_hashes=frozenset(report.retained_source_hashes[:1]),
        authoritative_url_hashes=frozenset(report.retained_source_hashes[:1]),
        proposition_source_hashes=frozenset(report.retained_source_hashes[:1]),
        useful_source_hashes=frozenset(report.retained_source_hashes[:1]),
    )
    score = score_frozen_report(report, targets)
    assert score.exact_official_persisted == score.proposition_source_hits == 1
    assert score.authoritative_per_api_call > 0
    with pytest.raises(ValueError, match="only frozen"):
        score_frozen_report(_run(V2_PAGINATION), targets)


def test_predeclared_success_categories_are_deterministic() -> None:
    control_report = _run(CONTROL)
    variant_report = _run(V1_RESULT_DEPTH)
    retained = variant_report.retained_source_hashes
    control_targets = PostFreezeTargets(frozenset(retained[:2]), frozenset(retained[:2]), frozenset(retained[:2]), frozenset(retained[:2]))
    control = score_frozen_report(control_report, control_targets)
    variant = score_frozen_report(variant_report, control_targets)
    assert compare_scores(control, variant).success is DiscoverySuccess.NO_IMPROVEMENT

    empty_targets = PostFreezeTargets(frozenset(retained[:2]), frozenset(retained[:2]), frozenset(retained[:2]), frozenset(retained[:2]))
    # Synthetic values prove classification independently of a live response.
    marginal = variant.__class__(variant.variant_id, 0, 0, 1, 0, 0, 1, 10, 1, 1, 0.1, 0, 0, 1, 0)
    meaningful = variant.__class__(variant.variant_id, 1, 1, 1, 1, 1, 1, 10, 1, 1, 0.1, 1, 0.5, 1, 1)
    strong = variant.__class__(variant.variant_id, 2, 2, 2, 2, 2, 1, 10, 1, 1, 0.2, 2, 1, 2, 1)
    baseline = variant.__class__(control.variant_id, 0, 0, 0, 0, 0, 1, 10, 1, 1, 0.1, 0, 0, 0, 0)
    assert compare_scores(baseline, marginal).success is DiscoverySuccess.MARGINAL
    assert compare_scores(baseline, meaningful).success is DiscoverySuccess.MEANINGFUL
    assert compare_scores(baseline, strong).success is DiscoverySuccess.STRONG
    assert empty_targets.official_page_hashes


def test_discovery_module_has_no_answer_key_or_runtime_authority_import() -> None:
    source = Path("src/strategic_intelligence/evaluation/brave_discovery_benchmark.py").read_text(encoding="utf-8")
    assert "golden_case import" not in source
    assert "GroundTruth" not in source
    assert "VerificationService" not in source and "GovernanceService" not in source
