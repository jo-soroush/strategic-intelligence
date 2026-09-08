"""G02 durable, user-controlled tracked-company memory boundary."""

from __future__ import annotations

from datetime import datetime, timezone

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.domain.models import TrackedCompany


def normalize_company_name(value: str) -> str:
    """Normalize only whitespace/case; never infer aliases or real-world identity."""
    return " ".join(value.split()).casefold()


class CompanyMemoryService:
    """Indexes existing workflow records without duplicating trust artifacts."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository

    def lookup(self, company_name: str) -> TrackedCompany | None:
        return self._repository.get_tracked_company_by_normalized_name(normalize_company_name(company_name))

    def record_run(self, *, company_id: str, company_name: str, run_id: str, successful: bool) -> TrackedCompany:
        if self._repository.get_workflow_run(run_id) is None:
            raise ValueError("tracked company memory requires an existing WorkflowRun")
        now = datetime.now(timezone.utc)
        normalized = normalize_company_name(company_name)
        existing = self._repository.get_tracked_company_by_normalized_name(normalized)
        if existing is None:
            tracked = TrackedCompany(
                company_id=company_id,
                display_name=company_name,
                exact_name=company_name,
                normalized_name=normalized,
                insertion_order=len(self._repository.list_tracked_companies()),
                run_ids=[run_id],
                active_run_id=run_id if successful else None,
                created_at=now,
                updated_at=now,
            )
        else:
            run_ids = [*existing.run_ids] if run_id in existing.run_ids else [*existing.run_ids, run_id]
            tracked = existing.model_copy(update={
                "run_ids": run_ids,
                "active_run_id": run_id if successful else existing.active_run_id,
                "updated_at": now,
            })
        return self._repository.save_tracked_company(tracked)
