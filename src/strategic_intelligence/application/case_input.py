"""Typed Case intake and deterministic entity-resolution gate for V1-C05."""

from __future__ import annotations

import ipaddress
from enum import Enum
from typing import Any, Mapping, Sequence
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.domain.models import Case, Company, Executive


class IntakeStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class EntityResolutionStatus(str, Enum):
    CONFIRMED = "CONFIRMED"
    AMBIGUOUS = "AMBIGUOUS"


class IntakeErrorCode(str, Enum):
    INVALID_INPUT = "INVALID_INPUT"
    INVALID_URL = "INVALID_URL"
    ENTITY_AMBIGUOUS = "ENTITY_AMBIGUOUS"
    ENTITY_CONFLICT = "ENTITY_CONFLICT"
    PERSISTENCE_FAILED = "PERSISTENCE_FAILED"


class CaseInputModel(BaseModel):
    """Strict application-boundary models; domain records are created only after validation."""

    model_config = ConfigDict(extra="forbid", strict=True)


def _normalize_text(value: str, field_name: str) -> str:
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError(f"{field_name} must not be blank")
    return normalized


def _normalize_optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.split())
    return normalized or None


def _normalize_public_url(value: str) -> str:
    if value != value.strip() or any(character.isspace() for character in value):
        raise ValueError("URL must not contain whitespace")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL must be an absolute http(s) URL without credentials")
    try:
        port = parsed.port
    except ValueError as error:
        raise ValueError("URL has an invalid port") from error
    hostname = parsed.hostname.lower().rstrip(".")
    if hostname == "localhost" or hostname.endswith(".local"):
        raise ValueError("URL host must be publicly routable")
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None and not address.is_global:
        raise ValueError("URL host must be publicly routable")
    netloc = hostname if port is None else f"{hostname}:{port}"
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "", parsed.query, parsed.fragment))


def _identity(value: str) -> str:
    return " ".join(value.split()).casefold()


class CaseSubmission(CaseInputModel):
    company_name: str = Field(min_length=1)
    executive_name: str = Field(min_length=1)
    meeting_goal: str = Field(min_length=1)
    company_website: str | None = None
    company_linkedin_url: str | None = None
    executive_linkedin_url: str | None = None
    extra_context: str | None = None
    company_country: str | None = None
    company_business_unit: str | None = None
    executive_current_title: str | None = None

    @field_validator("company_name", "executive_name", "meeting_goal")
    @classmethod
    def normalize_required_text(cls, value: str, info) -> str:
        return _normalize_text(value, info.field_name)

    @field_validator("extra_context", "company_country", "company_business_unit", "executive_current_title")
    @classmethod
    def normalize_optional_text(cls, value: str | None, info) -> str | None:
        return _normalize_optional_text(value, info.field_name)

    @field_validator("company_website", "company_linkedin_url", "executive_linkedin_url")
    @classmethod
    def validate_optional_url(cls, value: str | None) -> str | None:
        return None if value is None else _normalize_public_url(value)


class CompanyIdentityCandidate(CaseInputModel):
    name: str = Field(min_length=1)
    official_website: str | None = None
    country: str | None = None
    business_unit: str | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_text(value, "name")

    @field_validator("country", "business_unit")
    @classmethod
    def normalize_optional_identity_text(cls, value: str | None, info) -> str | None:
        return _normalize_optional_text(value, info.field_name)

    @field_validator("official_website")
    @classmethod
    def validate_website(cls, value: str | None) -> str | None:
        return None if value is None else _normalize_public_url(value)


class ExecutiveIdentityCandidate(CaseInputModel):
    full_name: str = Field(min_length=1)
    company_name: str = Field(min_length=1)
    current_title: str | None = None
    public_profile_url: str | None = None

    @field_validator("full_name", "company_name")
    @classmethod
    def normalize_required_identity_text(cls, value: str, info) -> str:
        return _normalize_text(value, info.field_name)

    @field_validator("current_title")
    @classmethod
    def normalize_optional_identity_text(cls, value: str | None) -> str | None:
        return _normalize_optional_text(value, "current_title")

    @field_validator("public_profile_url")
    @classmethod
    def validate_profile_url(cls, value: str | None) -> str | None:
        return None if value is None else _normalize_public_url(value)


class IntakeError(CaseInputModel):
    code: IntakeErrorCode
    field: str | None = None
    message: str


class EntityResolution(CaseInputModel):
    status: EntityResolutionStatus
    reasons: list[IntakeError] = Field(default_factory=list)


class CaseIntakeResult(CaseInputModel):
    status: IntakeStatus
    resolution: EntityResolution | None = None
    case: Case | None = None
    company: Company | None = None
    executive: Executive | None = None
    errors: list[IntakeError] = Field(default_factory=list)


class CaseIntakeService:
    """Owns deterministic C05 validation, entity gating, and Case persistence."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def submit(
        self,
        payload: Mapping[str, Any],
        *,
        company_candidates: Sequence[CompanyIdentityCandidate] = (),
        executive_candidates: Sequence[ExecutiveIdentityCandidate] = (),
    ) -> CaseIntakeResult:
        try:
            submission = CaseSubmission.model_validate(payload)
        except ValidationError as error:
            return CaseIntakeResult(status=IntakeStatus.REJECTED, errors=self._validation_errors(error))

        resolution = self._resolve(submission, company_candidates, executive_candidates)
        if resolution.status is EntityResolutionStatus.AMBIGUOUS:
            return CaseIntakeResult(status=IntakeStatus.REJECTED, resolution=resolution, errors=resolution.reasons)

        company = Company(
            name=submission.company_name,
            official_website=submission.company_website,
            linkedin_url=submission.company_linkedin_url,
            country=submission.company_country,
        )
        executive = Executive(
            full_name=submission.executive_name,
            company_id=company.company_id,
            current_title=submission.executive_current_title,
            linkedin_url=submission.executive_linkedin_url,
            public_profile_url=submission.executive_linkedin_url,
        )
        case = Case(
            company_id=company.company_id,
            executive_id=executive.executive_id,
            company_name=company.name,
            executive_name=executive.full_name,
            meeting_goal=submission.meeting_goal,
            extra_context=submission.extra_context,
            company_website=submission.company_website,
            company_linkedin_url=submission.company_linkedin_url,
            executive_linkedin_url=submission.executive_linkedin_url,
        )
        try:
            persisted_case = self._repository.create_case(case)
        except Exception:
            return CaseIntakeResult(
                status=IntakeStatus.REJECTED,
                resolution=resolution,
                errors=[IntakeError(code=IntakeErrorCode.PERSISTENCE_FAILED, message="validated Case could not be persisted")],
            )
        return CaseIntakeResult(
            status=IntakeStatus.ACCEPTED,
            resolution=resolution,
            case=persisted_case,
            company=company,
            executive=executive,
        )

    @staticmethod
    def _validation_errors(error: ValidationError) -> list[IntakeError]:
        issues: list[IntakeError] = []
        for item in error.errors():
            location = item["loc"]
            field = str(location[0]) if location else None
            code = (
                IntakeErrorCode.INVALID_URL
                if field and (field.endswith("url") or field == "company_website")
                else IntakeErrorCode.INVALID_INPUT
            )
            issues.append(IntakeError(code=code, field=field, message=item["msg"]))
        return issues

    @staticmethod
    def _resolve(
        submission: CaseSubmission,
        company_candidates: Sequence[CompanyIdentityCandidate],
        executive_candidates: Sequence[ExecutiveIdentityCandidate],
    ) -> EntityResolution:
        reasons: list[IntakeError] = []
        company_matches = [candidate for candidate in company_candidates if _identity(candidate.name) == _identity(submission.company_name)]
        executive_matches = [candidate for candidate in executive_candidates if _identity(candidate.full_name) == _identity(submission.executive_name)]

        if len(company_matches) > 1:
            reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_AMBIGUOUS, field="company_name", message="multiple company candidates match the supplied name"))
        if len(executive_matches) > 1:
            reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_AMBIGUOUS, field="executive_name", message="multiple executive candidates match the supplied name"))
        if company_matches:
            candidate = company_matches[0]
            if submission.company_website and candidate.official_website and submission.company_website != candidate.official_website:
                reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_CONFLICT, field="company_website", message="company website conflicts with the matched company candidate"))
            if submission.company_country and candidate.country and _identity(submission.company_country) != _identity(candidate.country):
                reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_CONFLICT, field="company_country", message="company country conflicts with the matched company candidate"))
            if submission.company_business_unit and candidate.business_unit and _identity(submission.company_business_unit) != _identity(candidate.business_unit):
                reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_CONFLICT, field="company_business_unit", message="company business unit conflicts with the matched company candidate"))
        if executive_matches:
            candidate = executive_matches[0]
            if _identity(candidate.company_name) != _identity(submission.company_name):
                reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_CONFLICT, field="executive_name", message="matched executive is associated with a different company"))
            if submission.executive_linkedin_url and candidate.public_profile_url and submission.executive_linkedin_url != candidate.public_profile_url:
                reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_CONFLICT, field="executive_linkedin_url", message="executive profile URL conflicts with the matched executive candidate"))

        if not company_matches and not (submission.company_website or submission.company_linkedin_url or (submission.company_country and submission.company_business_unit)):
            reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_AMBIGUOUS, field="company_name", message="company requires a website, public company URL, country/business-unit pair, or a unique candidate"))
        if not executive_matches and not (submission.executive_linkedin_url or submission.executive_current_title):
            reasons.append(IntakeError(code=IntakeErrorCode.ENTITY_AMBIGUOUS, field="executive_name", message="executive requires a public professional URL, current title, or a unique candidate"))

        return EntityResolution(
            status=EntityResolutionStatus.AMBIGUOUS if reasons else EntityResolutionStatus.CONFIRMED,
            reasons=reasons,
        )
