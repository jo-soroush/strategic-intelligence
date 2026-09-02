"""Typed, content-minimized audit observation for the existing workflow."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from strategic_intelligence.application.persistence import PersistenceRepository
from strategic_intelligence.domain.models import AuditEvent, WorkflowStage
from strategic_intelligence.observability.logging import configured_secret_values, redact_secrets
from strategic_intelligence.providers.contracts import LLMProvider, LLMRequest, LLMResponse, ProviderError, SearchProvider, SearchQuery, SearchResult


class AuditReport(BaseModel):
    """Developer-facing reconstruction of one persisted workflow run."""

    model_config = ConfigDict(extra="forbid", strict=True)

    run_id: str
    events: list[AuditEvent]
    total_duration_ms: int = Field(ge=0)
    stage_duration_ms: dict[str, int] = Field(default_factory=dict)
    provider_call_count: int = Field(ge=0)
    retry_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
    checkpoint_count: int = Field(ge=0)
    verification_count: int = Field(ge=0)
    governance_count: int = Field(ge=0)
    terminal_status: str | None = None


@dataclass(frozen=True)
class _Context:
    case_id: str
    run_id: str
    stage: WorkflowStage | None = None


class AuditTrail:
    """Records observations only; it never chooses workflow or trust outcomes."""

    def __init__(self, repository: PersistenceRepository) -> None:
        self._repository = repository
        self._context: _Context | None = None
        self._sequence: dict[str, int] = {}
        self._stage_started: dict[tuple[str, str], float] = {}
        self._run_started: dict[str, float] = {}

    def activate(self, case_id: str, run_id: str, stage: WorkflowStage | None = None) -> None:
        self._context = _Context(case_id, run_id, stage)
        self._run_started.setdefault(run_id, perf_counter())

    def stage(self, stage: WorkflowStage | None) -> None:
        if self._context is not None:
            self._context = _Context(self._context.case_id, self._context.run_id, stage)

    def record(self, event_type: str, component: str, status: str, *, target_id: str | None = None, metadata: dict[str, str | int | float | bool | None] | None = None) -> AuditEvent | None:
        if self._context is None:
            return None
        try:
            run_id = self._context.run_id
            sequence = self._sequence.get(run_id, len(self._repository.list_audit_events(run_id)))
            values = dict(metadata or {})
            if event_type == "STAGE" and self._context.stage is not None:
                key = (run_id, self._context.stage.value)
                if status == "STARTED":
                    self._stage_started[key] = perf_counter()
                elif status == "COMPLETED" and key in self._stage_started:
                    values.setdefault("duration_ms", int((perf_counter() - self._stage_started.pop(key)) * 1000))
                elif status == "COMPLETED":
                    values.setdefault("duration_ms", 0)
            if event_type == "TERMINAL" and run_id in self._run_started:
                values.setdefault("total_duration_ms", int((perf_counter() - self._run_started[run_id]) * 1000))
            safe = {
                key: redact_secrets(value, configured_secret_values()) if isinstance(value, str) else value
                for key, value in values.items()
            }
            saved = self._repository.save_audit_event(AuditEvent(
                case_id=self._context.case_id, run_id=run_id, sequence=sequence,
                event_type=event_type, component=component, status=status,
                target_id=target_id, stage=self._context.stage, metadata=safe,
            ))
            self._sequence[run_id] = sequence + 1
            return saved
        except Exception:
            # Observability is an observer: an audit-store fault cannot change
            # provider, checkpoint, retry, or terminal workflow semantics.
            return None

    def report(self, run_id: str) -> AuditReport:
        events = self._repository.list_audit_events(run_id)
        metrics = {"provider_call_count": 0, "retry_count": 0, "error_count": 0, "checkpoint_count": 0, "verification_count": 0, "governance_count": 0}
        durations: dict[str, int] = {}
        terminal: str | None = None
        total = 0
        for event in events:
            if event.event_type == "PROVIDER_CALL": metrics["provider_call_count"] += 1
            if event.event_type == "RETRY": metrics["retry_count"] += 1
            if event.event_type == "ERROR": metrics["error_count"] += 1
            if event.event_type == "CHECKPOINT": metrics["checkpoint_count"] += 1
            if event.event_type == "VERIFICATION": metrics["verification_count"] += 1
            if event.event_type == "GOVERNANCE": metrics["governance_count"] += 1
            duration = event.metadata.get("duration_ms")
            if isinstance(duration, int) and event.stage is not None:
                durations[event.stage.value] = durations.get(event.stage.value, 0) + duration
            if event.event_type == "TERMINAL":
                terminal = event.status
                total = event.metadata.get("total_duration_ms") if isinstance(event.metadata.get("total_duration_ms"), int) else total
        return AuditReport(run_id=run_id, events=events, total_duration_ms=total, stage_duration_ms=durations, terminal_status=terminal, **metrics)


T = TypeVar("T", bound=BaseModel)


class ObservedLLMProvider:
    def __init__(self, provider: LLMProvider, audit: AuditTrail) -> None:
        self._provider, self._audit = provider, audit

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self._call("generate", lambda: self._provider.generate(request))

    def generate_structured(self, request: LLMRequest, schema: type[T]) -> T:
        return self._call("generate_structured", lambda: self._provider.generate_structured(request, schema))

    def _call(self, operation: str, call):
        started = perf_counter()
        try:
            result = call()
        except ProviderError as error:
            metadata: dict[str, str | int | float | bool] = {
                "operation": operation,
                "duration_ms": int((perf_counter() - started) * 1000),
                "retryable": error.retryable,
            }
            if error.structured_output_failure_reason is not None:
                metadata["structured_output_failure_reason"] = error.structured_output_failure_reason.value
            self._audit.record("PROVIDER_CALL", "llm", error.code.value, metadata=metadata)
            raise
        except Exception:
            self._audit.record("PROVIDER_CALL", "llm", "ERROR", metadata={"operation": operation, "duration_ms": int((perf_counter() - started) * 1000)})
            raise
        self._audit.record("PROVIDER_CALL", "llm", "SUCCESS", metadata={"operation": operation, "duration_ms": int((perf_counter() - started) * 1000)})
        return result


class ObservedSearchProvider:
    def __init__(self, provider: SearchProvider, audit: AuditTrail) -> None:
        self._provider, self._audit = provider, audit

    def search(self, query: SearchQuery) -> list[SearchResult]:
        started = perf_counter()
        try:
            results = self._provider.search(query)
        except ProviderError as error:
            self._audit.record("PROVIDER_CALL", "search", error.code.value, metadata={"operation": "search", "duration_ms": int((perf_counter() - started) * 1000), "retryable": error.retryable})
            raise
        except Exception:
            self._audit.record("PROVIDER_CALL", "search", "ERROR", metadata={"operation": "search", "duration_ms": int((perf_counter() - started) * 1000)})
            raise
        self._audit.record("PROVIDER_CALL", "search", "SUCCESS", metadata={"operation": "search", "duration_ms": int((perf_counter() - started) * 1000), "result_count": len(results)})
        return results
