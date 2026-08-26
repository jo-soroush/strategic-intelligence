"""Bounded, typed research planning for V1-C06; this module never executes research."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from strategic_intelligence.domain.models import (
    Case, ResearchCategory, ResearchCoverage, ResearchCoverageRequirement,
    ResearchCoverageStatus, ResearchPlan, ResearchTask, ResearchTaskStatus,
    TargetType,
)
from strategic_intelligence.providers.contracts import LLMProvider, LLMRequest, ProviderError


class PlanningStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class PlanningErrorCode(str, Enum):
    INVALID_CASE = "INVALID_CASE"
    INVALID_COVERAGE = "INVALID_COVERAGE"
    INVALID_GUIDANCE = "INVALID_GUIDANCE"
    PRIVACY_BOUNDARY = "PRIVACY_BOUNDARY"
    EMPTY_PLAN = "EMPTY_PLAN"


class PlanningModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class PlanningError(PlanningModel):
    code: PlanningErrorCode
    message: str


class ResearchPlanningGuidance(PlanningModel):
    """Optional provider output can only emphasize existing approved categories."""

    emphasized_categories: list[str] = Field(default_factory=list, max_length=13)


class ResearchPlanningResult(PlanningModel):
    status: PlanningStatus
    plan: ResearchPlan | None = None
    completion_ready: bool = False
    errors: list[PlanningError] = Field(default_factory=list)


@dataclass(frozen=True)
class _TaskTemplate:
    target_type: TargetType
    category: ResearchCategory
    priority: int
    topic: str


_TASK_TEMPLATES: tuple[_TaskTemplate, ...] = (
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.STRATEGY, 3, "strategy and direction"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.PROJECTS, 3, "current and recent projects"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.AI_ACTIVITY, 3, "AI and data activity"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.CLIENT_CASES, 2, "public client case studies"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.PARTNERSHIPS, 2, "relevant partnerships"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.NEWS, 2, "important recent news"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.HIRING, 1, "hiring and expansion signals"),
    _TaskTemplate(TargetType.COMPANY, ResearchCategory.EVENTS, 1, "events and conferences"),
    _TaskTemplate(TargetType.EXECUTIVE, ResearchCategory.EXECUTIVE_ROLE, 3, "current role and responsibilities"),
    _TaskTemplate(TargetType.EXECUTIVE, ResearchCategory.EXECUTIVE_FOCUS, 3, "professional focus"),
    _TaskTemplate(TargetType.EXECUTIVE, ResearchCategory.PUBLICATIONS, 2, "public articles and publications"),
    _TaskTemplate(TargetType.EXECUTIVE, ResearchCategory.INTERVIEWS, 2, "public interviews and talks"),
    _TaskTemplate(TargetType.EXECUTIVE, ResearchCategory.PUBLIC_ACTIVITY, 2, "recent public professional activity"),
)


class ResearchPlanner:
    """Build a bounded plan; search, source collection, and workflow execution stay downstream."""

    def __init__(self, *, task_budget: int = len(_TASK_TEMPLATES), attempt_budget_per_task: int = 1, llm: LLMProvider | None = None) -> None:
        if not 1 <= task_budget <= len(_TASK_TEMPLATES):
            raise ValueError("task_budget must be within the approved C06 limit")
        if not 1 <= attempt_budget_per_task <= 3:
            raise ValueError("attempt_budget_per_task must be between one and three")
        self._task_budget = task_budget
        self._attempt_budget_per_task = attempt_budget_per_task
        self._llm = llm

    def plan(self, case: Case, *, coverage: Sequence[ResearchCoverage] = ()) -> ResearchPlanningResult:
        coverage_error = self._validate_coverage(case, coverage)
        if coverage_error is not None:
            return self._rejected(coverage_error)

        emphasized, guidance_error = self._guidance(case)
        if guidance_error is not None:
            return self._rejected(guidance_error)

        coverage_by_key = {(item.target_type, item.category): item for item in coverage}
        required_coverage = [
            ResearchCoverageRequirement(target_type=template.target_type, category=template.category, priority=template.priority)
            for template in _TASK_TEMPLATES
        ]
        eligible = [
            template for template in _TASK_TEMPLATES
            if coverage_by_key.get((template.target_type, template.category), None) is None
            or coverage_by_key[(template.target_type, template.category)].status not in {
                ResearchCoverageStatus.COVERED,
                ResearchCoverageStatus.NOT_RELEVANT,
            }
        ]
        ordered = sorted(eligible, key=lambda item: (-self._priority(item, emphasized), item.target_type.value, item.category.value))
        tasks = [self._task(case, template, self._priority(template, emphasized)) for template in ordered[:self._task_budget]]
        plan = ResearchPlan(
            case_id=case.case_id,
            tasks=tasks,
            required_coverage=required_coverage,
            coverage=list(coverage),
            task_budget=self._task_budget,
            attempt_budget_per_task=self._attempt_budget_per_task,
        )
        validation_error = self.validate_plan(plan)
        if validation_error is not None:
            return self._rejected(validation_error)
        return ResearchPlanningResult(
            status=PlanningStatus.ACCEPTED,
            plan=plan,
            completion_ready=self.is_completion_ready(plan),
        )

    @staticmethod
    def validate_plan(plan: ResearchPlan) -> PlanningError | None:
        if not plan.tasks and not ResearchPlanner.is_completion_ready(plan):
            return PlanningError(
                code=PlanningErrorCode.EMPTY_PLAN,
                message="an incomplete coverage state requires at least one research task",
            )
        if any(task.status is not ResearchTaskStatus.PENDING for task in plan.tasks):
            return PlanningError(code=PlanningErrorCode.INVALID_CASE, message="new research plans may contain only pending tasks")
        return None

    @staticmethod
    def is_completion_ready(plan: ResearchPlan) -> bool:
        coverage_by_key = {(item.target_type, item.category): item for item in plan.coverage}
        return bool(plan.required_coverage) and all(
            (coverage := coverage_by_key.get((requirement.target_type, requirement.category))) is not None
            and coverage.status in {ResearchCoverageStatus.COVERED, ResearchCoverageStatus.NOT_RELEVANT}
            for requirement in plan.required_coverage
        )

    def _guidance(self, case: Case) -> tuple[set[ResearchCategory], PlanningError | None]:
        if self._llm is None:
            return set(), None
        try:
            guidance = self._llm.generate_structured(
                LLMRequest(prompt=self._guidance_prompt(case)), ResearchPlanningGuidance,
            )
        except (ProviderError, ValidationError):
            return set(), PlanningError(code=PlanningErrorCode.INVALID_GUIDANCE, message="provider guidance could not be validated")
        categories: set[ResearchCategory] = set()
        for value in guidance.emphasized_categories:
            try:
                categories.add(ResearchCategory(value))
            except ValueError:
                return set(), PlanningError(
                    code=PlanningErrorCode.PRIVACY_BOUNDARY,
                    message="provider guidance requested a category outside the public-professional research boundary",
                )
        return categories, None

    @staticmethod
    def _guidance_prompt(case: Case) -> str:
        context = f" Context: {case.extra_context}." if case.extra_context else ""
        return (
            "Select only approved research categories to emphasize for a meeting goal. "
            f"Company: {case.company_name}. Executive: {case.executive_name}. Goal: {case.meeting_goal}.{context}"
        )

    @staticmethod
    def _validate_coverage(case: Case, coverage: Sequence[ResearchCoverage]) -> PlanningError | None:
        keys = [(item.target_type, item.category) for item in coverage]
        if any(item.case_id != case.case_id for item in coverage) or len(keys) != len(set(keys)):
            return PlanningError(code=PlanningErrorCode.INVALID_COVERAGE, message="coverage must be unique and belong to the planned Case")
        allowed = {(template.target_type, template.category) for template in _TASK_TEMPLATES}
        if any(key not in allowed for key in keys):
            return PlanningError(code=PlanningErrorCode.PRIVACY_BOUNDARY, message="coverage contains a category outside the approved public-professional plan")
        return None

    def _task(self, case: Case, template: _TaskTemplate, priority: int) -> ResearchTask:
        subject = case.company_name if template.target_type is TargetType.COMPANY else case.executive_name
        context = f" Context: {case.extra_context}" if case.extra_context else ""
        return ResearchTask(
            case_id=case.case_id,
            target_type=template.target_type,
            category=template.category,
            query=f"{subject}: {template.topic} for {case.meeting_goal}.{context}",
            priority=priority,
            max_attempts=self._attempt_budget_per_task,
        )

    @staticmethod
    def _priority(template: _TaskTemplate, emphasized: set[ResearchCategory]) -> int:
        return min(3, template.priority + (1 if template.category in emphasized else 0))

    @staticmethod
    def _rejected(error: PlanningError) -> ResearchPlanningResult:
        return ResearchPlanningResult(status=PlanningStatus.REJECTED, errors=[error])
