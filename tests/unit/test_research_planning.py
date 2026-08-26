from pathlib import Path

from strategic_intelligence.application.case_input import CaseIntakeService, IntakeStatus
from strategic_intelligence.application.research_planning import (
    PlanningErrorCode, PlanningStatus, ResearchPlanner,
)
from strategic_intelligence.domain.models import (
    Case, ResearchCategory, ResearchCoverage, ResearchCoverageStatus,
    ResearchPlan, TargetType,
)
from strategic_intelligence.providers.fakes import FakeLLMProvider
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


def _case() -> Case:
    return Case(
        company_id="company",
        executive_id="executive",
        company_name="Example Co",
        executive_name="Ava Example",
        meeting_goal="prepare an AI partnership meeting",
        extra_context="focus on responsible AI consulting",
        company_website="https://example.test",
        executive_linkedin_url="https://www.linkedin.com/in/ava-example",
    )


def _signatures(plan: ResearchPlan) -> list[tuple[TargetType, ResearchCategory, str, int, int]]:
    return [
        (task.target_type, task.category, task.query, task.priority, task.max_attempts)
        for task in plan.tasks
    ]


def test_critical_path_builds_a_bounded_separated_typed_plan(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        intake = CaseIntakeService(repository).submit(
            {
                "company_name": "Example Co",
                "executive_name": "Ava Example",
                "meeting_goal": "prepare an AI partnership meeting",
                "company_website": "https://example.test",
                "executive_linkedin_url": "https://www.linkedin.com/in/ava-example",
                "extra_context": "focus on responsible AI consulting",
            },
        )
        assert intake.status is IntakeStatus.ACCEPTED
        assert intake.case is not None
        result = ResearchPlanner().plan(intake.case)

    finally:
        repository.close()

    assert result.status is PlanningStatus.ACCEPTED
    assert result.plan is not None
    assert result.completion_ready is False
    assert len(result.plan.tasks) == result.plan.task_budget == 13
    assert {task.target_type for task in result.plan.tasks} == {TargetType.COMPANY, TargetType.EXECUTIVE}
    assert all(task.max_attempts == 1 and task.status.value == "PENDING" for task in result.plan.tasks)
    assert all("prepare an AI partnership meeting" in task.query for task in result.plan.tasks)
    assert all("focus on responsible AI consulting" in task.query for task in result.plan.tasks)


def test_deterministic_planning_keeps_order_and_content_stable() -> None:
    planner = ResearchPlanner()
    first = planner.plan(_case())
    second = planner.plan(_case())

    assert first.plan is not None and second.plan is not None
    assert _signatures(first.plan) == _signatures(second.plan)


def test_coverage_aware_planning_skips_covered_work_and_retains_high_priority_gaps() -> None:
    case = _case()
    covered = ResearchCoverage(
        case_id=case.case_id,
        target_type=TargetType.COMPANY,
        category=ResearchCategory.STRATEGY,
        status=ResearchCoverageStatus.COVERED,
        retained_source_count=1,
    )
    partial = ResearchCoverage(
        case_id=case.case_id,
        target_type=TargetType.COMPANY,
        category=ResearchCategory.AI_ACTIVITY,
        status=ResearchCoverageStatus.PARTIAL,
        missing_reason="no current official source yet",
    )

    result = ResearchPlanner().plan(case, coverage=[covered, partial])

    assert result.status is PlanningStatus.ACCEPTED
    assert result.plan is not None
    categories = {task.category for task in result.plan.tasks}
    assert ResearchCategory.STRATEGY not in categories
    assert ResearchCategory.AI_ACTIVITY in categories
    assert result.completion_ready is False


def test_invalid_case_coverage_is_rejected_without_creating_a_plan() -> None:
    result = ResearchPlanner().plan(
        _case(),
        coverage=[
            ResearchCoverage(
                case_id="another-case",
                target_type=TargetType.COMPANY,
                category=ResearchCategory.NEWS,
                status=ResearchCoverageStatus.NOT_FOUND,
                missing_reason="not attempted for this Case",
            ),
        ],
    )

    assert result.status is PlanningStatus.REJECTED
    assert result.plan is None
    assert result.errors[0].code is PlanningErrorCode.INVALID_COVERAGE


def test_fake_structured_llm_guidance_is_bounded_and_private_categories_are_rejected() -> None:
    valid_provider = FakeLLMProvider(response_text='{"emphasized_categories":["AI_ACTIVITY"]}')
    valid = ResearchPlanner(llm=valid_provider).plan(_case())
    assert valid.status is PlanningStatus.ACCEPTED
    assert valid.plan is not None
    ai_task = next(task for task in valid.plan.tasks if task.category is ResearchCategory.AI_ACTIVITY)
    assert ai_task.priority == 3
    assert len(valid_provider.calls) == 1

    private_provider = FakeLLMProvider(response_text='{"emphasized_categories":["PERSONAL_LIFE"]}')
    rejected = ResearchPlanner(llm=private_provider).plan(_case())
    assert rejected.status is PlanningStatus.REJECTED
    assert rejected.errors[0].code is PlanningErrorCode.PRIVACY_BOUNDARY

    malformed_provider = FakeLLMProvider(response_text='{"emphasized_categories":"not-a-list"}')
    malformed = ResearchPlanner(llm=malformed_provider).plan(_case())
    assert malformed.status is PlanningStatus.REJECTED
    assert malformed.errors[0].code is PlanningErrorCode.INVALID_GUIDANCE


def test_empty_incomplete_plan_is_rejected_deterministically() -> None:
    case = _case()
    incomplete = ResearchPlan(case_id=case.case_id, required_coverage=ResearchPlanner().plan(case).plan.required_coverage)

    error = ResearchPlanner.validate_plan(incomplete)

    assert error is not None
    assert error.code is PlanningErrorCode.EMPTY_PLAN
