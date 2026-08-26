from pathlib import Path

from strategic_intelligence.application.case_input import (
    CaseIntakeService, CompanyIdentityCandidate, EntityResolutionStatus,
    ExecutiveIdentityCandidate, IntakeErrorCode, IntakeStatus,
)
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


def _service(tmp_path: Path) -> tuple[CaseIntakeService, SqliteRepository]:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    return CaseIntakeService(repository), repository


def _valid_submission() -> dict[str, str]:
    return {
        "company_name": "  Example   Co  ",
        "executive_name": "  Ava   Example ",
        "meeting_goal": " Prepare a partnership meeting ",
        "company_website": "https://EXAMPLE.test/about",
        "executive_linkedin_url": "https://www.linkedin.com/in/ava-example",
    }


def test_critical_path_validates_normalizes_resolves_and_persists_with_real_repository(tmp_path: Path) -> None:
    service, repository = _service(tmp_path)
    try:
        result = service.submit(_valid_submission())
        assert result.status is IntakeStatus.ACCEPTED
        assert result.resolution is not None and result.resolution.status is EntityResolutionStatus.CONFIRMED
        assert result.case is not None
        assert result.case.company_name == "Example Co"
        assert result.case.executive_name == "Ava Example"
        assert result.case.company_website == "https://example.test/about"
        assert repository.get_case(result.case.case_id) == result.case
    finally:
        repository.close()


def test_missing_required_input_returns_structured_rejection_without_persistence(tmp_path: Path) -> None:
    service, repository = _service(tmp_path)
    try:
        result = service.submit({"company_name": "Example", "meeting_goal": "Prepare"})
        assert result.status is IntakeStatus.REJECTED
        assert result.case is None
        assert result.errors[0].code is IntakeErrorCode.INVALID_INPUT
        assert result.errors[0].field == "executive_name"
    finally:
        repository.close()


def test_unsafe_or_malformed_urls_return_structured_rejection(tmp_path: Path) -> None:
    service, repository = _service(tmp_path)
    try:
        payload = _valid_submission()
        payload["company_website"] = "file:///tmp/company"
        result = service.submit(payload)
        assert result.status is IntakeStatus.REJECTED
        assert result.errors[0].code is IntakeErrorCode.INVALID_URL

        payload["company_website"] = "http://127.0.0.1/internal"
        result = service.submit(payload)
        assert result.status is IntakeStatus.REJECTED
        assert result.errors[0].code is IntakeErrorCode.INVALID_URL
    finally:
        repository.close()


def test_same_name_executive_and_moved_executive_are_blocked_as_conflicts(tmp_path: Path) -> None:
    service, repository = _service(tmp_path)
    try:
        result = service.submit(
            _valid_submission(),
            executive_candidates=[
                ExecutiveIdentityCandidate(full_name="Ava Example", company_name="Example Co", public_profile_url="https://www.linkedin.com/in/ava-one"),
                ExecutiveIdentityCandidate(full_name="Ava Example", company_name="Other Co", public_profile_url="https://www.linkedin.com/in/ava-two"),
            ],
        )
        assert result.status is IntakeStatus.REJECTED
        assert result.resolution is not None and result.resolution.status is EntityResolutionStatus.AMBIGUOUS
        assert any(error.code is IntakeErrorCode.ENTITY_AMBIGUOUS for error in result.errors)

        result = service.submit(
            _valid_submission(),
            executive_candidates=[ExecutiveIdentityCandidate(full_name="Ava Example", company_name="Former Co", public_profile_url="https://www.linkedin.com/in/ava-example")],
        )
        assert result.status is IntakeStatus.REJECTED
        assert any(error.code is IntakeErrorCode.ENTITY_CONFLICT for error in result.errors)
    finally:
        repository.close()


def test_conflicting_company_url_and_ambiguous_business_unit_are_blocked(tmp_path: Path) -> None:
    service, repository = _service(tmp_path)
    try:
        result = service.submit(
            _valid_submission(),
            company_candidates=[CompanyIdentityCandidate(name="Example Co", official_website="https://different.test")],
        )
        assert result.status is IntakeStatus.REJECTED
        assert any(error.code is IntakeErrorCode.ENTITY_CONFLICT for error in result.errors)

        payload = _valid_submission() | {"company_business_unit": "Consulting", "company_country": "Sweden"}
        result = service.submit(
            payload,
            company_candidates=[
                CompanyIdentityCandidate(name="Example Co", country="Sweden", business_unit="Consulting"),
                CompanyIdentityCandidate(name="Example Co", country="Sweden", business_unit="Technology"),
            ],
        )
        assert result.status is IntakeStatus.REJECTED
        assert any(error.code is IntakeErrorCode.ENTITY_AMBIGUOUS for error in result.errors)
    finally:
        repository.close()


def test_insufficient_identity_evidence_blocks_research_entry(tmp_path: Path) -> None:
    service, repository = _service(tmp_path)
    try:
        result = service.submit({"company_name": "Example", "executive_name": "Ava Example", "meeting_goal": "Prepare"})
        assert result.status is IntakeStatus.REJECTED
        assert result.resolution is not None and result.resolution.status is EntityResolutionStatus.AMBIGUOUS
        assert {error.field for error in result.errors} == {"company_name", "executive_name"}
    finally:
        repository.close()
