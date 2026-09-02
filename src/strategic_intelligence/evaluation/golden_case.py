"""Evaluation-only Golden Case fixtures and deterministic comparison.

This module never participates in research, verification, governance, analysis,
or brief generation.  It evaluates persisted output only after a workflow run.
"""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, model_validator

from strategic_intelligence.domain.models import Claim, Evidence, GovernanceDecision, Source, VerificationResult, WorkflowRun
from strategic_intelligence.observability.audit import AuditReport


class GroundTruthVerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"


class GroundTruthMatchStatus(str, Enum):
    FOUND = "FOUND"
    PARTIAL = "PARTIAL"
    NOT_FOUND = "NOT_FOUND"
    CONTRADICTED = "CONTRADICTED"


class MeetingValueStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class GroundTruthItem(_StrictModel):
    fact_id: str = Field(pattern=r"^GT\d{2}$")
    statement: str = Field(min_length=1)
    category: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    source_class: str = Field(min_length=1)
    expected_relevance: str = Field(min_length=1)
    verification_status: GroundTruthVerificationStatus
    notes: str | None = None


class GoldenCaseFixture(_StrictModel):
    golden_case_id: str = Field(min_length=1)
    version: str = Field(min_length=1)
    company: str = Field(min_length=1)
    executive: str = Field(min_length=1)
    meeting_goal: str = Field(min_length=1)
    research_boundary: str = Field(min_length=1)
    manual_review_status: str = Field(min_length=1)
    source_references: dict[str, str] = Field(min_length=1)
    ground_truth: list[GroundTruthItem] = Field(min_length=1)

    @model_validator(mode="after")
    def _truth_ids_are_unique_and_source_backed(self) -> "GoldenCaseFixture":
        ids = [item.fact_id for item in self.ground_truth]
        if len(ids) != len(set(ids)):
            raise ValueError("Golden Case Ground Truth fact IDs must be unique")
        if any(item.source_url not in self.source_references.values() for item in self.ground_truth):
            raise ValueError("every Ground Truth item must use a declared source reference")
        return self

    @property
    def verified_items(self) -> list[GroundTruthItem]:
        return [item for item in self.ground_truth if item.verification_status is GroundTruthVerificationStatus.VERIFIED]


class GroundTruthMatch(_StrictModel):
    fact_id: str = Field(pattern=r"^GT\d{2}$")
    status: GroundTruthMatchStatus
    claim_id: str | None = None
    reviewer_note: str | None = None

    @model_validator(mode="after")
    def _positive_matches_need_a_runtime_claim(self) -> "GroundTruthMatch":
        if self.status in {GroundTruthMatchStatus.FOUND, GroundTruthMatchStatus.PARTIAL} and not self.claim_id:
            raise ValueError("FOUND and PARTIAL Ground Truth matches require a runtime Claim ID")
        return self


class MeetingValueReview(_StrictModel):
    relevance_to_goal: int | None = Field(default=None, ge=1, le=5)
    company_understanding: int | None = Field(default=None, ge=1, le=5)
    executive_understanding: int | None = Field(default=None, ge=1, le=5)
    strategic_opportunities: int | None = Field(default=None, ge=1, le=5)
    meeting_questions: int | None = Field(default=None, ge=1, le=5)
    clarity: int | None = Field(default=None, ge=1, le=5)
    traceability: int | None = Field(default=None, ge=1, le=5)
    reviewer: str | None = None
    notes: str | None = None

    @property
    def status(self) -> MeetingValueStatus:
        values = [
            self.relevance_to_goal, self.company_understanding, self.executive_understanding,
            self.strategic_opportunities, self.meeting_questions, self.clarity, self.traceability,
        ]
        if any(value is None for value in values):
            return MeetingValueStatus.MANUAL_REVIEW_REQUIRED
        scores = [value for value in values if value is not None]
        return MeetingValueStatus.PASS if min(scores) >= 3 and sum(scores) / len(scores) >= 4 else MeetingValueStatus.FAIL


class GoldenCaseRuntimeSnapshot(_StrictModel):
    """Persisted runtime truth exposed by the application only after execution."""

    workflow_run: WorkflowRun
    claims: list[Claim]
    evidence: list[Evidence]
    sources: list[Source]
    verification_results: list[VerificationResult]
    governance_decisions: list[GovernanceDecision]
    audit_report: AuditReport

    @model_validator(mode="after")
    def _snapshot_is_run_and_case_scoped(self) -> "GoldenCaseRuntimeSnapshot":
        case_id = self.workflow_run.case_id
        if any(item.case_id != case_id for item in [*self.claims, *self.evidence, *self.sources]):
            raise ValueError("Golden Case snapshot records must belong to the workflow Case")
        if self.audit_report.run_id != self.workflow_run.run_id:
            raise ValueError("Golden Case audit report must belong to the workflow run")
        return self


class GoldenCaseEvaluation(_StrictModel):
    golden_case_id: str
    golden_case_version: str
    run_id: str
    matches: list[GroundTruthMatch]
    verified_ground_truth_count: int = Field(ge=0)
    coverage_percent: float = Field(ge=0, le=100)
    traceability_pass: bool
    verification_trace_pass: bool
    governance_trace_pass: bool
    trust_invariants_pass: bool
    meeting_value_status: MeetingValueStatus
    audit_report: AuditReport


def load_golden_case_fixture(path: Path) -> GoldenCaseFixture:
    """Load a versioned answer key for evaluation, never for workflow input."""
    # JSON necessarily represents Enum values as strings; the resulting model
    # remains typed and strict for all callers after this boundary.
    return GoldenCaseFixture.model_validate(json.loads(path.read_text(encoding="utf-8")), strict=False)


def evaluate_golden_case(
    fixture: GoldenCaseFixture,
    snapshot: GoldenCaseRuntimeSnapshot,
    matches: list[GroundTruthMatch],
    meeting_value_review: MeetingValueReview,
) -> GoldenCaseEvaluation:
    """Compare post-run persisted truth against manually reviewed matches.

    The evaluator deliberately has no lexical/semantic auto-match mechanism:
    a human must map a fact to an actual Claim ID after runtime output exists.
    This prevents answer-key keyword overlap from masquerading as recovered truth.
    """
    verified_ids = {item.fact_id for item in fixture.verified_items}
    by_id = {item.fact_id: item for item in matches}
    if set(by_id) - {item.fact_id for item in fixture.ground_truth}:
        raise ValueError("Ground Truth match refers to an unknown fact")
    claims = {claim.claim_id: claim for claim in snapshot.claims}
    evidence_ids = {item.evidence_id for item in snapshot.evidence}
    source_ids = {item.source_id for item in snapshot.sources}
    checked: list[GroundTruthMatch] = []
    for fact in fixture.ground_truth:
        match = by_id.get(fact.fact_id, GroundTruthMatch(fact_id=fact.fact_id, status=GroundTruthMatchStatus.NOT_FOUND))
        if match.claim_id is not None:
            claim = claims.get(match.claim_id)
            if claim is None:
                raise ValueError("Ground Truth match must refer to a persisted runtime Claim")
            if not claim.evidence_ids or not set(claim.evidence_ids).issubset(evidence_ids):
                raise ValueError("positive Ground Truth match requires persisted Claim-to-Evidence traceability")
        checked.append(match)
    found = sum(1 for item in checked if item.fact_id in verified_ids and item.status in {GroundTruthMatchStatus.FOUND, GroundTruthMatchStatus.PARTIAL})
    coverage = 0.0 if not verified_ids else round(found * 100 / len(verified_ids), 2)
    traceable_claims = all(claim.evidence_ids and set(claim.evidence_ids).issubset(evidence_ids) for claim in snapshot.claims)
    source_traceable = all(item.source_id in source_ids for item in snapshot.evidence)
    verification_claims = {item.claim_id for item in snapshot.verification_results}
    governance_claims = {item.target_id for item in snapshot.governance_decisions}
    verification_trace = all(claim.claim_id in verification_claims for claim in snapshot.claims)
    governance_trace = all(claim.claim_id in governance_claims for claim in snapshot.claims)
    unsupported_fact = any(claim.claim_type.value == "FACT" and not claim.evidence_ids for claim in snapshot.claims)
    brief_items = _brief_items(snapshot.workflow_run)
    brief_claim_ids = {claim_id for item in brief_items for claim_id in item.related_claim_ids}
    decisions = {item.target_id: item for item in snapshot.governance_decisions}
    blocked_leak = any(decisions.get(claim_id) and decisions[claim_id].decision.value == "BLOCK" for claim_id in brief_claim_ids)
    restriction_lost = any(
        decisions.get(claim_id) and decisions[claim_id].decision.value == "RESTRICT"
        and not any(claim_id in item.related_claim_ids and item.is_restricted and set(decisions[claim_id].reason_codes).issubset(item.restriction_reason_codes) for item in brief_items)
        for claim_id in brief_claim_ids
    )
    trust_pass = traceable_claims and source_traceable and verification_trace and governance_trace and not unsupported_fact and not blocked_leak and not restriction_lost
    return GoldenCaseEvaluation(
        golden_case_id=fixture.golden_case_id, golden_case_version=fixture.version,
        run_id=snapshot.workflow_run.run_id, matches=checked,
        verified_ground_truth_count=len(verified_ids), coverage_percent=coverage,
        traceability_pass=traceable_claims and source_traceable,
        verification_trace_pass=verification_trace,
        governance_trace_pass=governance_trace,
        trust_invariants_pass=trust_pass,
        meeting_value_status=meeting_value_review.status,
        audit_report=snapshot.audit_report,
    )


def _brief_items(run: WorkflowRun):
    """Return only typed C16 presentation items; never reinterpret their trust state."""
    state = run.snapshot
    if state is None:
        return []
    full = state.full_brief
    quick = state.quick_brief
    items = []
    if full is not None:
        items.extend([
            *full.company_situation, *full.strategy_direction, *full.projects_client_cases, *full.ai_activity,
            *full.executive_intelligence, *full.strategic_signals, *full.user_relevance, *full.meeting_strategy,
            *full.knowledge_gap_details, *full.opportunity_map, *full.questions,
        ])
    if quick is not None:
        items.extend([
            *quick.key_facts, *quick.key_signals, *quick.major_risks, *quick.knowledge_gaps,
            *quick.top_opportunities, *quick.top_questions,
        ])
    return items
