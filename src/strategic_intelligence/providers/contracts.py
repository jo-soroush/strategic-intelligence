"""Application-owned provider contracts and normalized failure types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Any, Protocol, TypeVar

from pydantic import BaseModel


class ProviderErrorCode(str, Enum):
    UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    TIMEOUT = "PROVIDER_TIMEOUT"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    RATE_LIMITED = "RATE_LIMITED"
    INVALID_RESPONSE = "INVALID_PROVIDER_RESPONSE"
    MODEL_NOT_AVAILABLE = "MODEL_NOT_AVAILABLE"
    STRUCTURED_OUTPUT_INVALID = "STRUCTURED_OUTPUT_INVALID"
    CONFIGURATION_INVALID = "PROVIDER_CONFIGURATION_INVALID"


class StructuredOutputFailureReason(str, Enum):
    """Safe, bounded detail for structured-output failures."""

    DYNAMIC_SCHEMA_GENERATION_FAILED = "DYNAMIC_SCHEMA_GENERATION_FAILED"
    INNER_JSON_DECODE_FAILED = "INNER_JSON_DECODE_FAILED"
    PYDANTIC_VALIDATION_FAILED = "PYDANTIC_VALIDATION_FAILED"


class ProviderError(RuntimeError):
    def __init__(
        self,
        code: ProviderErrorCode,
        message: str,
        *,
        retryable: bool = False,
        structured_output_failure_reason: StructuredOutputFailureReason | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = retryable
        self.structured_output_failure_reason = structured_output_failure_reason


@dataclass(frozen=True)
class LLMRequest:
    prompt: str
    model: str | None = None
    timeout_seconds: float | None = None


@dataclass(frozen=True)
class LLMResponse:
    text: str
    provider: str
    model: str
    metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True)
class SearchQuery:
    query: str
    limit: int = 5
    timeout_seconds: float | None = None


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str = ""
    publisher: str | None = None
    published_at: date | None = None
    provider_metadata: dict[str, str | int | float | bool] = field(default_factory=dict)


T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    def generate(self, request: LLMRequest) -> LLMResponse: ...
    def generate_structured(self, request: LLMRequest, schema: type[T]) -> T: ...


class SearchProvider(Protocol):
    def search(self, query: SearchQuery) -> list[SearchResult]: ...
