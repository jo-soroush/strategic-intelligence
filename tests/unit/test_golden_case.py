"""C20 deterministic evaluation proof; the answer key is post-run only."""

import json
from datetime import date
from pathlib import Path

from strategic_intelligence.application.workflow_application import WorkflowApplication
from strategic_intelligence.config import Settings
from strategic_intelligence.domain.models import AnalysisItem, ClaimType
from strategic_intelligence.evaluation.golden_case import (
    GroundTruthMatch,
    GroundTruthMatchStatus,
    MeetingValueReview,
    evaluate_golden_case,
    load_golden_case_fixture,
)
from strategic_intelligence.providers.contracts import LLMRequest, SearchResult
from strategic_intelligence.providers.factory import Providers
from strategic_intelligence.providers.fakes import FakeSearchProvider


FIXTURE = Path(__file__).parents[2] / "evaluations/fixtures/c20_capgemini_invent_arash_afsarian_v1.json"


class _DeterministicLLM:
    def generate(self, request: LLMRequest):
        raise AssertionError("structured generation is required")

    def generate_structured(self, request: LLMRequest, schema):
        if "TRUSTED_CONTEXT_JSON" not in request.prompt:
            return schema()
        context = json.loads(request.prompt.split("TRUSTED_CONTEXT_JSON:\n", 1)[1])
        claim = context["claims"][0]
        return schema(company_direction=[AnalysisItem(
            text=claim["text"], type=ClaimType.FACT, related_claim_ids=[claim["claim_alias"]],
        )])


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        environment="test", log_level="INFO", data_dir=tmp_path / "data", log_dir=tmp_path / "logs",
        llm_provider="fake", llm_model="fake", llm_timeout_seconds=1.0,
        ollama_base_url="http://127.0.0.1:11434", search_provider="fake", cloud_providers_enabled=False,
    )


def _payload() -> dict[str, str]:
    return {
        "company_name": "Capgemini Invent", "executive_name": "Arash Afsarian",
        "meeting_goal": "Prepare an enterprise AI strategy discussion",
        "company_website": "https://www.capgemini.com", "executive_current_title": "Vice President AI and D&A",
    }


def test_c20_fixture_is_versioned_source_backed_and_evaluation_only() -> None:
    fixture = load_golden_case_fixture(FIXTURE)
    assert fixture.golden_case_id == "c20-capgemini-invent-arash-afsarian"
    assert len(fixture.ground_truth) == 20
    assert len(fixture.verified_items) == 20
    # Runtime composition cannot import the fixture or receive it as input.
    runtime_sources = [
        Path("src/strategic_intelligence/application/workflow_application.py").read_text(),
        Path("src/strategic_intelligence/harness/workflow_executor.py").read_text(),
    ]
    assert all("c20_capgemini" not in source and "GoldenCaseFixture" not in source for source in runtime_sources)


def test_c20_evaluates_real_workflow_output_only_after_execution_and_reload(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    app = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_DeterministicLLM(),
        search=FakeSearchProvider(results=[SearchResult(
            title="Arash Afsarian at Capgemini Invent", url="https://www.capgemini.com/example",
            snippet="Arash Afsarian works at Capgemini Invent.", publisher="Capgemini", published_at=date(2026, 1, 1),
        )]),
    ))
    try:
        result = app.execute(_payload(), as_of=date(2026, 8, 30))
        snapshot = app.golden_case_snapshot(result.workflow_run.run_id)
        assert snapshot.workflow_run.run_id == result.workflow_run.run_id
        assert snapshot.claims and snapshot.evidence and snapshot.sources
        claim = snapshot.claims[0]
        evaluation = evaluate_golden_case(
            load_golden_case_fixture(FIXTURE), snapshot,
            [GroundTruthMatch(fact_id="GT01", status=GroundTruthMatchStatus.FOUND, claim_id=claim.claim_id)],
            MeetingValueReview(
                relevance_to_goal=4, company_understanding=4, executive_understanding=4,
                strategic_opportunities=4, meeting_questions=4, clarity=4, traceability=4,
                reviewer="independent manual review",
            ),
        )
        assert evaluation.coverage_percent == 5.0
        assert evaluation.traceability_pass and evaluation.verification_trace_pass and evaluation.governance_trace_pass
        assert evaluation.trust_invariants_pass
        assert evaluation.audit_report.run_id == result.workflow_run.run_id
    finally:
        app.close()

    reopened = WorkflowApplication.from_settings(settings, providers=Providers(llm=_DeterministicLLM(), search=FakeSearchProvider()))
    try:
        reloaded = reopened.golden_case_snapshot(result.workflow_run.run_id)
        assert reloaded.audit_report.model_dump() == snapshot.audit_report.model_dump()
        assert [item.claim_id for item in reloaded.claims] == [item.claim_id for item in snapshot.claims]
    finally:
        reopened.close()


def test_c20_does_not_auto_promote_keyword_overlap_or_incomplete_manual_review(tmp_path: Path) -> None:
    settings = _settings(tmp_path)
    app = WorkflowApplication.from_settings(settings, providers=Providers(
        llm=_DeterministicLLM(), search=FakeSearchProvider(results=[SearchResult(
            title="Capgemini", url="https://www.capgemini.com/example", snippet="AI strategy", publisher="Capgemini", published_at=date(2026, 1, 1),
        )]),
    ))
    try:
        result = app.execute(_payload(), as_of=date(2026, 8, 30))
        snapshot = app.golden_case_snapshot(result.workflow_run.run_id)
        evaluation = evaluate_golden_case(load_golden_case_fixture(FIXTURE), snapshot, [], MeetingValueReview())
        assert evaluation.coverage_percent == 0
        assert evaluation.meeting_value_status.value == "MANUAL_REVIEW_REQUIRED"
    finally:
        app.close()
