from datetime import date
from pathlib import Path

import pytest

from strategic_intelligence.application.source_quality import (
    SourceMetadataErrorCode,
    SourceMetadataStatus,
    SourceFreshnessPolicy,
    SourceQualityService,
)
from strategic_intelligence.domain.models import Case, FreshnessStatus, Source, SourceQuality, SourceType
from strategic_intelligence.infrastructure.sqlite_repository import SqliteRepository


AS_OF = date(2026, 8, 26)


def _source(
    source_type: SourceType,
    *,
    publication_date: date | None = None,
    retrieval_date: date = AS_OF,
    origin_source_id: str | None = None,
) -> Source:
    return Source(
        case_id="case",
        url="https://example.test/source",
        title="Source",
        source_type=source_type,
        publication_date=publication_date,
        retrieval_date=retrieval_date,
        origin_source_id=origin_source_id,
    )


def _case() -> Case:
    return Case(
        company_id="company",
        executive_id="executive",
        company_name="Example Co",
        executive_name="Ava Example",
        meeting_goal="prepare",
    )


def test_critical_path_assesses_a_real_persisted_source(tmp_path: Path) -> None:
    repository = SqliteRepository(tmp_path / "data" / "strategic_intelligence.db")
    try:
        case = repository.create_case(_case())
        saved = repository.save_source(
            _source(SourceType.OFFICIAL_REPORT, publication_date=date(2026, 8, 1)).model_copy(
                update={"case_id": case.case_id},
            ),
        )
        persisted = repository.get_source(saved.source_id)
        assert persisted is not None
        result = SourceQualityService().assess(persisted, as_of=AS_OF)
        assert result.status is SourceMetadataStatus.ACCEPTED
        assert result.quality_class is SourceQuality.PRIMARY
        assert result.freshness_status is FreshnessStatus.CURRENT
        assert repository.get_source(saved.source_id) == saved
    finally:
        repository.close()


def test_primary_and_strong_secondary_classification_is_deterministic() -> None:
    service = SourceQualityService()
    primary = service.assess(_source(SourceType.OFFICIAL_COMPANY), as_of=AS_OF)
    secondary = service.assess(_source(SourceType.BUSINESS_PUBLICATION), as_of=AS_OF)
    supporting = service.assess(_source(SourceType.CONFERENCE), as_of=AS_OF)
    assert primary.quality_class is SourceQuality.PRIMARY
    assert secondary.quality_class is SourceQuality.STRONG_SECONDARY
    assert supporting.quality_class is SourceQuality.OTHER


def test_publication_and_retrieval_dates_remain_distinct_with_staleness() -> None:
    source = _source(
        SourceType.OFFICIAL_REPORT,
        publication_date=date(2025, 1, 1),
        retrieval_date=AS_OF,
    )
    result = SourceQualityService().assess(source, as_of=AS_OF)
    assert result.status is SourceMetadataStatus.ACCEPTED
    assert result.source and result.source.publication_date == date(2025, 1, 1)
    assert result.source.retrieval_date == AS_OF
    assert result.freshness_status is FreshnessStatus.STALE


def test_missing_or_future_publication_date_is_unknown() -> None:
    service = SourceQualityService()
    assert service.assess(_source(SourceType.NEWS), as_of=AS_OF).freshness_status is FreshnessStatus.UNKNOWN
    future = _source(SourceType.NEWS, publication_date=date(2026, 8, 27))
    assert service.assess(future, as_of=AS_OF).freshness_status is FreshnessStatus.UNKNOWN


def test_freshness_policy_rejects_an_inverted_window() -> None:
    with pytest.raises(ValueError, match="aging freshness window"):
        SourceFreshnessPolicy(current_max_age_days=91, aging_max_age_days=90)


def test_duplicate_origin_signal_is_preserved_and_self_reference_fails_closed() -> None:
    duplicate = _source(SourceType.NEWS, origin_source_id="original-source")
    result = SourceQualityService().assess(duplicate, as_of=AS_OF)
    assert result.status is SourceMetadataStatus.ACCEPTED
    assert result.has_duplicate_origin is True
    self_referential = duplicate.model_copy(update={"origin_source_id": duplicate.source_id})
    rejected = SourceQualityService().assess(self_referential, as_of=AS_OF)
    assert rejected.status is SourceMetadataStatus.REJECTED
    assert rejected.errors[0].code is SourceMetadataErrorCode.INVALID_ORIGIN
