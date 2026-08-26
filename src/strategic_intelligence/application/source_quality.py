"""Deterministic C10 source-quality and freshness metadata."""

from __future__ import annotations

from datetime import date
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from strategic_intelligence.domain.models import FreshnessStatus, Source, SourceQuality, SourceType


class SourceMetadataStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class SourceMetadataErrorCode(str, Enum):
    INVALID_ORIGIN = "INVALID_ORIGIN"


class SourceMetadataModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class SourceFreshnessPolicy(SourceMetadataModel):
    """Explicit deterministic thresholds; verification owns their later use."""

    current_max_age_days: int = Field(default=90, ge=0)
    aging_max_age_days: int = Field(default=365, ge=0)

    @model_validator(mode="after")
    def _aging_window_contains_current_window(self) -> "SourceFreshnessPolicy":
        if self.aging_max_age_days < self.current_max_age_days:
            raise ValueError("aging freshness window must include the current window")
        return self

    def freshness_for(self, publication_date: date | None, *, as_of: date) -> FreshnessStatus:
        if publication_date is None or publication_date > as_of:
            return FreshnessStatus.UNKNOWN
        age_days = (as_of - publication_date).days
        if age_days <= self.current_max_age_days:
            return FreshnessStatus.CURRENT
        if age_days <= self.aging_max_age_days:
            return FreshnessStatus.AGING
        return FreshnessStatus.STALE


class SourceMetadataError(SourceMetadataModel):
    code: SourceMetadataErrorCode
    message: str


class SourceMetadataResult(SourceMetadataModel):
    status: SourceMetadataStatus
    source: Source | None = None
    quality_class: SourceQuality | None = None
    freshness_status: FreshnessStatus | None = None
    has_duplicate_origin: bool = False
    errors: list[SourceMetadataError] = Field(default_factory=list)


class SourceQualityService:
    """Classifies source metadata without assigning claim truth or verification."""

    _PRIMARY_TYPES = frozenset({
        SourceType.OFFICIAL_COMPANY,
        SourceType.OFFICIAL_REPORT,
        SourceType.CASE_STUDY,
        SourceType.EXECUTIVE_DIRECT,
    })
    _STRONG_SECONDARY_TYPES = frozenset({SourceType.NEWS, SourceType.BUSINESS_PUBLICATION})

    def __init__(self, freshness_policy: SourceFreshnessPolicy | None = None) -> None:
        self._freshness_policy = freshness_policy or SourceFreshnessPolicy()

    def assess(self, source: Source, *, as_of: date) -> SourceMetadataResult:
        if source.origin_source_id == source.source_id:
            return SourceMetadataResult(
                status=SourceMetadataStatus.REJECTED,
                errors=[SourceMetadataError(
                    code=SourceMetadataErrorCode.INVALID_ORIGIN,
                    message="a source cannot identify itself as its origin",
                )],
            )
        quality_class = self._quality_for(source.source_type)
        classified_source = source.model_copy(update={"quality_class": quality_class})
        return SourceMetadataResult(
            status=SourceMetadataStatus.ACCEPTED,
            source=classified_source,
            quality_class=quality_class,
            freshness_status=self._freshness_policy.freshness_for(source.publication_date, as_of=as_of),
            has_duplicate_origin=source.origin_source_id is not None,
        )

    @classmethod
    def _quality_for(cls, source_type: SourceType) -> SourceQuality:
        if source_type in cls._PRIMARY_TYPES:
            return SourceQuality.PRIMARY
        if source_type in cls._STRONG_SECONDARY_TYPES:
            return SourceQuality.STRONG_SECONDARY
        return SourceQuality.OTHER
