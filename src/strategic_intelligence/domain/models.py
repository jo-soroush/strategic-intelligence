"""Application-owned, provider-independent V1 domain contracts."""

from __future__ import annotations

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator


def new_id() -> str:
    """Return an opaque stable record identifier independent of display names."""
    return str(uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DomainModel(BaseModel):
    """Strict JSON-compatible base contract with timezone-aware datetimes."""

    model_config = ConfigDict(extra="forbid", use_enum_values=False)

    @model_validator(mode="after")
    def _timestamps_are_timezone_aware(self) -> "DomainModel":
        for value in self.__dict__.values():
            if isinstance(value, datetime) and value.tzinfo is None:
                raise ValueError("timestamps must be timezone-aware")
        return self


class CaseStatus(str, Enum):
    CREATED = "CREATED"
    RESEARCHING = "RESEARCHING"
    VERIFYING = "VERIFYING"
    ANALYZING = "ANALYZING"
    GOVERNING = "GOVERNING"
    GENERATING_BRIEF = "GENERATING_BRIEF"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class TargetType(str, Enum):
    COMPANY = "COMPANY"
    EXECUTIVE = "EXECUTIVE"


class ResearchCategory(str, Enum):
    STRATEGY = "STRATEGY"
    PROJECTS = "PROJECTS"
    CLIENT_CASES = "CLIENT_CASES"
    AI_ACTIVITY = "AI_ACTIVITY"
    PARTNERSHIPS = "PARTNERSHIPS"
    HIRING = "HIRING"
    NEWS = "NEWS"
    EVENTS = "EVENTS"
    EXECUTIVE_ROLE = "EXECUTIVE_ROLE"
    EXECUTIVE_FOCUS = "EXECUTIVE_FOCUS"
    PUBLICATIONS = "PUBLICATIONS"
    INTERVIEWS = "INTERVIEWS"
    PUBLIC_ACTIVITY = "PUBLIC_ACTIVITY"


class ResearchTaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class ResearchCoverageStatus(str, Enum):
    COVERED = "COVERED"
    PARTIAL = "PARTIAL"
    NOT_FOUND = "NOT_FOUND"
    UNAVAILABLE = "UNAVAILABLE"
    NOT_RELEVANT = "NOT_RELEVANT"


class SourceType(str, Enum):
    OFFICIAL_COMPANY = "OFFICIAL_COMPANY"
    OFFICIAL_REPORT = "OFFICIAL_REPORT"
    CASE_STUDY = "CASE_STUDY"
    EXECUTIVE_DIRECT = "EXECUTIVE_DIRECT"
    NEWS = "NEWS"
    BUSINESS_PUBLICATION = "BUSINESS_PUBLICATION"
    CONFERENCE = "CONFERENCE"
    PUBLIC_LINKEDIN = "PUBLIC_LINKEDIN"
    JOB_POSTING = "JOB_POSTING"
    OTHER = "OTHER"


class SourceQuality(str, Enum):
    PRIMARY = "PRIMARY"
    STRONG_SECONDARY = "STRONG_SECONDARY"
    OTHER = "OTHER"


class AccessStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PARTIAL = "PARTIAL"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


class ClaimType(str, Enum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    RECOMMENDATION = "RECOMMENDATION"


class ClaimEvidenceRelationship(str, Enum):
    SUPPORTS = "SUPPORTS"
    CONTRADICTS = "CONTRADICTS"
    CONTEXT = "CONTEXT"


class FidelityStatus(str, Enum):
    SUPPORTED_BY_EVIDENCE = "SUPPORTED_BY_EVIDENCE"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    NOT_SUPPORTED = "NOT_SUPPORTED"
    AMBIGUOUS = "AMBIGUOUS"


class VerificationStatus(str, Enum):
    VERIFIED = "VERIFIED"
    SUPPORTED = "SUPPORTED"
    CONFLICTING = "CONFLICTING"
    STALE = "STALE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class FreshnessStatus(str, Enum):
    CURRENT = "CURRENT"
    AGING = "AGING"
    STALE = "STALE"
    UNKNOWN = "UNKNOWN"


class GovernanceDecisionStatus(str, Enum):
    PASS = "PASS"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class GovernanceReasonCode(str, Enum):
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    UNVERIFIED_FACT = "UNVERIFIED_FACT"
    STALE_INFORMATION = "STALE_INFORMATION"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    UNCERTAINTY_NOT_VISIBLE = "UNCERTAINTY_NOT_VISIBLE"
    PRIVACY_BOUNDARY = "PRIVACY_BOUNDARY"
    PERSONAL_DATA_NOT_RELEVANT = "PERSONAL_DATA_NOT_RELEVANT"
    UNTRACEABLE_CLAIM = "UNTRACEABLE_CLAIM"
    MISCLASSIFIED_INFERENCE = "MISCLASSIFIED_INFERENCE"


class WorkflowStage(str, Enum):
    CASE_VALIDATED = "CASE_VALIDATED"
    RESEARCH_PLANNED = "RESEARCH_PLANNED"
    RESEARCH_COMPLETED = "RESEARCH_COMPLETED"
    EVIDENCE_BUILT = "EVIDENCE_BUILT"
    VERIFICATION_COMPLETED = "VERIFICATION_COMPLETED"
    ANALYSIS_COMPLETED = "ANALYSIS_COMPLETED"
    GOVERNANCE_COMPLETED = "GOVERNANCE_COMPLETED"
    BRIEF_GENERATED = "BRIEF_GENERATED"
    CASE_COMPLETED = "CASE_COMPLETED"


class WorkflowRunStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class WorkflowErrorCode(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    SEARCH_FAILED = "SEARCH_FAILED"
    SOURCE_UNAVAILABLE = "SOURCE_UNAVAILABLE"
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    INVALID_PROVIDER_RESPONSE = "INVALID_PROVIDER_RESPONSE"
    PERSISTENCE_FAILED = "PERSISTENCE_FAILED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    GOVERNANCE_BLOCKED = "GOVERNANCE_BLOCKED"
    WORKFLOW_FAILED = "WORKFLOW_FAILED"


class Company(DomainModel):
    company_id: str = Field(default_factory=new_id, min_length=1)
    name: str = Field(min_length=1)
    official_website: str | None = None
    linkedin_url: str | None = None
    country: str | None = None
    industry: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Executive(DomainModel):
    executive_id: str = Field(default_factory=new_id, min_length=1)
    full_name: str = Field(min_length=1)
    company_id: str = Field(min_length=1)
    current_title: str | None = None
    linkedin_url: str | None = None
    public_profile_url: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Case(DomainModel):
    case_id: str = Field(default_factory=new_id, min_length=1)
    company_id: str = Field(min_length=1)
    executive_id: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    executive_name: str = Field(min_length=1)
    meeting_goal: str = Field(min_length=1)
    extra_context: str | None = None
    company_website: str | None = None
    company_linkedin_url: str | None = None
    executive_linkedin_url: str | None = None
    status: CaseStatus = CaseStatus.CREATED
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class ResearchTask(DomainModel):
    research_task_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    target_type: TargetType
    category: ResearchCategory
    query: str = Field(min_length=1)
    priority: int = Field(ge=0)
    max_attempts: int = Field(default=1, ge=1, le=3)
    status: ResearchTaskStatus = ResearchTaskStatus.PENDING
    created_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class ResearchCoverageRequirement(DomainModel):
    target_type: TargetType
    category: ResearchCategory
    priority: int = Field(ge=0)


class ResearchCoverage(DomainModel):
    case_id: str = Field(min_length=1)
    target_type: TargetType
    category: ResearchCategory
    status: ResearchCoverageStatus
    retained_source_count: int = Field(default=0, ge=0)
    missing_reason: str | None = None

    @model_validator(mode="after")
    def _coverage_status_is_explainable(self) -> "ResearchCoverage":
        if self.status is ResearchCoverageStatus.COVERED and self.retained_source_count == 0:
            raise ValueError("covered research requires at least one retained source")
        if self.status in {
            ResearchCoverageStatus.PARTIAL,
            ResearchCoverageStatus.NOT_FOUND,
            ResearchCoverageStatus.UNAVAILABLE,
        } and not self.missing_reason:
            raise ValueError("incomplete research coverage requires a missing reason")
        return self


class ResearchPlan(DomainModel):
    case_id: str = Field(min_length=1)
    tasks: list[ResearchTask] = Field(default_factory=list)
    required_coverage: list[ResearchCoverageRequirement] = Field(default_factory=list)
    coverage: list[ResearchCoverage] = Field(default_factory=list)
    task_budget: int = Field(default=13, ge=1, le=13)
    attempt_budget_per_task: int = Field(default=1, ge=1, le=3)
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _plan_is_consistent(self) -> "ResearchPlan":
        if len(self.tasks) > self.task_budget:
            raise ValueError("research task count exceeds plan budget")
        task_keys = [(task.target_type, task.category) for task in self.tasks]
        if len(task_keys) != len(set(task_keys)):
            raise ValueError("research plan cannot contain duplicate target/category tasks")
        if any(task.case_id != self.case_id for task in self.tasks):
            raise ValueError("research task case_id must match research plan")
        if any(task.max_attempts > self.attempt_budget_per_task for task in self.tasks):
            raise ValueError("research task attempt budget exceeds research plan")
        coverage_keys = [(coverage.target_type, coverage.category) for coverage in self.coverage]
        if len(coverage_keys) != len(set(coverage_keys)):
            raise ValueError("research coverage cannot contain duplicate target/category records")
        if any(coverage.case_id != self.case_id for coverage in self.coverage):
            raise ValueError("research coverage case_id must match research plan")
        return self


class RawFinding(DomainModel):
    finding_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    research_task_id: str = Field(min_length=1)
    source_url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    extracted_content: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    relevance: str = Field(min_length=1)
    discovered_at: datetime = Field(default_factory=utc_now)


class Source(DomainModel):
    source_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    url: str = Field(min_length=1)
    title: str = Field(min_length=1)
    publisher: str | None = None
    source_type: SourceType
    publication_date: date | None = None
    retrieval_date: date = Field(default_factory=lambda: utc_now().date())
    quality_class: SourceQuality = SourceQuality.OTHER
    access_status: AccessStatus = AccessStatus.AVAILABLE
    origin_source_id: str | None = None


class Evidence(DomainModel):
    evidence_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    topic: str = Field(min_length=1)
    relevance: str = Field(min_length=1)
    publication_date: date | None = None
    extracted_at: datetime = Field(default_factory=utc_now)


class Claim(DomainModel):
    claim_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    text: str = Field(min_length=1)
    claim_type: ClaimType
    topic: str = Field(min_length=1)
    evidence_ids: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus | None = None
    created_at: datetime = Field(default_factory=utc_now)

    @model_validator(mode="after")
    def _supported_claims_have_evidence(self) -> "Claim":
        if self.claim_type in {ClaimType.FACT, ClaimType.INFERENCE} and not self.evidence_ids:
            raise ValueError("FACT and INFERENCE claims require evidence identifiers")
        return self


class ClaimEvidenceLink(DomainModel):
    claim_id: str = Field(min_length=1)
    evidence_id: str = Field(min_length=1)
    relationship_type: ClaimEvidenceRelationship


class VerificationResult(DomainModel):
    verification_id: str = Field(default_factory=new_id, min_length=1)
    claim_id: str = Field(min_length=1)
    fidelity_status: FidelityStatus
    status: VerificationStatus
    source_quality: SourceQuality
    freshness_status: FreshnessStatus
    independent_source_count: int = Field(ge=0)
    conflict_detected: bool = False
    duplicate_risk: bool = False
    notes: str | None = None
    verified_at: datetime = Field(default_factory=utc_now)


class AnalysisItem(DomainModel):
    item_id: str = Field(default_factory=new_id, min_length=1)
    text: str = Field(min_length=1)
    type: ClaimType
    related_claim_ids: list[str] = Field(default_factory=list)
    rationale: str | None = None


class Opportunity(DomainModel):
    opportunity_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    related_claim_ids: list[str] = Field(default_factory=list)
    relevance_to_goal: str = Field(min_length=1)
    confidence: str | None = None
    assumptions: list[str] = Field(default_factory=list)


class MeetingQuestion(DomainModel):
    question_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    related_claim_ids: list[str] = Field(default_factory=list)
    priority: int = Field(ge=0)


class StrategicAnalysis(DomainModel):
    analysis_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    company_direction: list[AnalysisItem] = Field(default_factory=list)
    executive_priorities: list[AnalysisItem] = Field(default_factory=list)
    project_meaning: list[AnalysisItem] = Field(default_factory=list)
    strategic_signals: list[AnalysisItem] = Field(default_factory=list)
    opportunity_areas: list[Opportunity] = Field(default_factory=list)
    user_relevance: list[AnalysisItem] = Field(default_factory=list)
    meeting_topics: list[AnalysisItem] = Field(default_factory=list)
    smart_questions: list[MeetingQuestion] = Field(default_factory=list)
    risks: list[AnalysisItem] = Field(default_factory=list)
    knowledge_gaps: list[AnalysisItem] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=utc_now)


class GovernanceDecision(DomainModel):
    governance_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    target_type: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    decision: GovernanceDecisionStatus
    reason_codes: list[GovernanceReasonCode] = Field(default_factory=list)
    notes: str | None = None
    decided_at: datetime = Field(default_factory=utc_now)


class MeetingBrief(DomainModel):
    brief_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    version: int = Field(ge=1)
    executive_summary: str | None = None
    company_situation: list[AnalysisItem] = Field(default_factory=list)
    strategy_direction: list[AnalysisItem] = Field(default_factory=list)
    projects_client_cases: list[AnalysisItem] = Field(default_factory=list)
    ai_activity: list[AnalysisItem] = Field(default_factory=list)
    executive_intelligence: list[AnalysisItem] = Field(default_factory=list)
    strategic_signals: list[AnalysisItem] = Field(default_factory=list)
    opportunity_map: list[Opportunity] = Field(default_factory=list)
    user_relevance: list[AnalysisItem] = Field(default_factory=list)
    meeting_strategy: list[AnalysisItem] = Field(default_factory=list)
    questions: list[MeetingQuestion] = Field(default_factory=list)
    do_not_assume: list[str] = Field(default_factory=list)
    knowledge_gaps: list[str] = Field(default_factory=list)
    source_references: list[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class QuickBrief(DomainModel):
    brief_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    key_facts: list[AnalysisItem] = Field(default_factory=list)
    key_signals: list[AnalysisItem] = Field(default_factory=list)
    top_opportunities: list[Opportunity] = Field(default_factory=list)
    top_questions: list[MeetingQuestion] = Field(default_factory=list)
    major_risks: list[AnalysisItem] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=utc_now)


class AuditEvent(DomainModel):
    audit_event_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    event_type: str = Field(min_length=1)
    component: str = Field(min_length=1)
    target_id: str | None = None
    status: str = Field(min_length=1)
    timestamp: datetime = Field(default_factory=utc_now)
    metadata: dict[str, str | int | float | bool | None] = Field(default_factory=dict)


class WorkflowError(DomainModel):
    error_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    component: str = Field(min_length=1)
    error_code: WorkflowErrorCode
    message: str = Field(min_length=1)
    retryable: bool = False
    occurred_at: datetime = Field(default_factory=utc_now)


class WorkflowRun(DomainModel):
    run_id: str = Field(default_factory=new_id, min_length=1)
    case_id: str = Field(min_length=1)
    status: WorkflowRunStatus = WorkflowRunStatus.RUNNING
    current_stage: WorkflowStage | None = None
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None


class UserContext(DomainModel):
    case_id: str = Field(min_length=1)
    professional_background: str | None = None
    capabilities: list[str] = Field(default_factory=list)
    meeting_objective: str | None = None
    constraints: list[str] = Field(default_factory=list)
    notes: str | None = None


class WorkflowState(DomainModel):
    """Transient structured execution state; explicitly not a persistence model."""

    case_context: Case | None = None
    research_plan: ResearchPlan | None = None
    company_findings: list[RawFinding] = Field(default_factory=list)
    executive_findings: list[RawFinding] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    verification_results: list[VerificationResult] = Field(default_factory=list)
    strategic_analysis: StrategicAnalysis | None = None
    governance_decisions: list[GovernanceDecision] = Field(default_factory=list)
    quick_brief: QuickBrief | None = None
    full_brief: MeetingBrief | None = None
    errors: list[WorkflowError] = Field(default_factory=list)
    current_stage: WorkflowStage | None = None
