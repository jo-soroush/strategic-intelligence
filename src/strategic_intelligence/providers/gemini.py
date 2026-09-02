"""Gemini Developer API adapter behind the existing C04 provider contract."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request

from strategic_intelligence.providers.contracts import (
    LLMRequest,
    LLMResponse,
    ProviderError,
    ProviderErrorCode,
    StructuredOutputFailureReason,
)
from strategic_intelligence.security import UnsafeExternalUrlError, open_external_request


class GeminiSchemaProjectionError(ValueError):
    """The application schema cannot be safely represented for Gemini."""


_REMOVED_RESPONSE_SCHEMA_KEYWORDS = frozenset({"minLength", "maxLength", "default"})
_SUPPORTED_RESPONSE_SCHEMA_KEYWORDS = frozenset({
    "$id", "$defs", "$ref", "$anchor", "type", "format", "title", "description", "enum",
    "items", "prefixItems", "minItems", "maxItems", "minimum", "maximum", "anyOf", "oneOf",
    "properties", "additionalProperties", "required", "const",
})


def project_gemini_response_json_schema(application_schema: dict[str, Any]) -> dict[str, Any]:
    """Project Pydantic JSON Schema to Gemini's documented response-schema subset.

    The projection is intentionally provider-local: Pydantic remains the
    application contract and rejects all constraints Gemini cannot enforce.
    """

    return _project_schema_node(application_schema, "$")


def _project_schema_node(node: object, path: str) -> dict[str, Any]:
    if not isinstance(node, dict):
        raise GeminiSchemaProjectionError(f"Gemini schema node at {path} must be an object")
    projected: dict[str, Any] = {}
    singleton_constant: object | None = None
    for key, value in node.items():
        if key in _REMOVED_RESPONSE_SCHEMA_KEYWORDS:
            continue
        if key not in _SUPPORTED_RESPONSE_SCHEMA_KEYWORDS:
            raise GeminiSchemaProjectionError(f"unsupported Gemini schema keyword at {path}")
        if key == "const":
            if isinstance(value, (dict, list)):
                raise GeminiSchemaProjectionError(f"invalid singleton enum at {path}")
            singleton_constant = deepcopy(value)
        elif key in {"properties", "$defs"}:
            if not isinstance(value, dict) or not all(isinstance(name, str) for name in value):
                raise GeminiSchemaProjectionError(f"invalid schema map at {path}/{key}")
            projected[key] = {
                name: _project_schema_node(child, f"{path}/{key}/{name}")
                for name, child in value.items()
            }
        elif key in {"anyOf", "oneOf", "prefixItems"}:
            if not isinstance(value, list):
                raise GeminiSchemaProjectionError(f"invalid schema list at {path}/{key}")
            projected[key] = [_project_schema_node(child, f"{path}/{key}/{index}") for index, child in enumerate(value)]
        elif key == "items":
            # JSON Schema tuple validation belongs in ``prefixItems``.  Gemini
            # accepts a single schema object for ``items``; accepting an array
            # here would silently project malformed input.
            projected[key] = _project_schema_node(value, f"{path}/{key}")
        elif key == "additionalProperties":
            if isinstance(value, bool):
                projected[key] = value
            else:
                projected[key] = _project_schema_node(value, f"{path}/{key}")
        elif key == "required":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                raise GeminiSchemaProjectionError(f"invalid required fields at {path}")
            projected[key] = deepcopy(value)
        elif key == "enum":
            if not isinstance(value, list) or any(isinstance(item, (dict, list)) for item in value):
                raise GeminiSchemaProjectionError(f"invalid enum at {path}")
            projected[key] = deepcopy(value)
        elif key in {"minItems", "maxItems"}:
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise GeminiSchemaProjectionError(f"invalid collection bound at {path}/{key}")
            projected[key] = value
        elif key in {"minimum", "maximum"}:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise GeminiSchemaProjectionError(f"invalid numeric bound at {path}/{key}")
            projected[key] = value
        elif key == "type":
            if not isinstance(value, str) and not (isinstance(value, list) and all(isinstance(item, str) for item in value)):
                raise GeminiSchemaProjectionError(f"invalid type at {path}")
            projected[key] = deepcopy(value)
        elif key in {"$id", "$ref", "$anchor", "format", "title", "description"}:
            if not isinstance(value, str):
                raise GeminiSchemaProjectionError(f"invalid scalar schema value at {path}/{key}")
            projected[key] = value

    # Pydantic emits `const` for singleton Literal values; Gemini documents
    # `enum`, so preserve the identical one-value constraint in that form.
    if singleton_constant is not None:
        if "enum" in projected and projected["enum"] != [singleton_constant]:
            raise GeminiSchemaProjectionError(f"conflicting enum constraints at {path}")
        projected["enum"] = [singleton_constant]
    return projected


class GeminiAdapter:
    """Opt-in, bounded HTTPS Gemini adapter; credentials are process supplied."""

    _BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"

    def __init__(self, api_key: str | None, model: str, timeout_seconds: float) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key, self._model, self._timeout_seconds = api_key, model, timeout_seconds

    def generate(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(text=self._request(request, None), provider="gemini", model=request.model or self._model)

    def generate_structured(self, request: LLMRequest, schema):
        try:
            gemini_schema = project_gemini_response_json_schema(schema.model_json_schema())
        except Exception as error:
            raise ProviderError(
                ProviderErrorCode.CONFIGURATION_INVALID,
                "Gemini structured schema is not provider-compatible",
                structured_output_failure_reason=StructuredOutputFailureReason.DYNAMIC_SCHEMA_GENERATION_FAILED,
            ) from error
        try:
            response_text = self._request(request, gemini_schema)
            json.loads(response_text)
        except json.JSONDecodeError as error:
            raise ProviderError(
                ProviderErrorCode.STRUCTURED_OUTPUT_INVALID,
                "Gemini structured output was not valid JSON",
                structured_output_failure_reason=StructuredOutputFailureReason.INNER_JSON_DECODE_FAILED,
            ) from error
        try:
            return schema.model_validate_json(response_text)
        except ValueError as error:
            raise ProviderError(
                ProviderErrorCode.STRUCTURED_OUTPUT_INVALID,
                "Gemini structured output violated the requested schema",
                structured_output_failure_reason=StructuredOutputFailureReason.PYDANTIC_VALIDATION_FAILED,
            ) from error

    def _request(self, request: LLMRequest, schema: dict | None) -> str:
        if not self._api_key:
            raise ProviderError(ProviderErrorCode.AUTHENTICATION_FAILED, "Gemini API key is not configured")
        payload_data: dict[str, object] = {"contents": [{"parts": [{"text": request.prompt}]}]}
        if schema is not None:
            payload_data["generationConfig"] = {"responseMimeType": "application/json", "responseJsonSchema": schema}
        payload = json.dumps(payload_data).encode("utf-8")
        model = request.model or self._model
        outbound = Request(f"{self._BASE_URL}/{model}:generateContent", data=payload, headers={"Content-Type": "application/json", "x-goog-api-key": self._api_key}, method="POST")
        try:
            with open_external_request(outbound, timeout=request.timeout_seconds or self._timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            if error.code in {401, 403}:
                raise ProviderError(ProviderErrorCode.AUTHENTICATION_FAILED, "Gemini authentication failed") from error
            if error.code == 429:
                raise ProviderError(ProviderErrorCode.RATE_LIMITED, "Gemini rate limit reached", retryable=True) from error
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "Gemini provider returned an HTTP error", retryable=error.code >= 500) from error
        except TimeoutError as error:
            raise ProviderError(ProviderErrorCode.TIMEOUT, "Gemini request timed out", retryable=True) from error
        except URLError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "Gemini network request failed", retryable=True) from error
        except UnsafeExternalUrlError as error:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "Gemini endpoint violates the external URL policy") from error
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "Gemini returned an invalid response") from error
        try:
            text = body["candidates"][0]["content"]["parts"][0]["text"]
            if not isinstance(text, str) or not text:
                raise TypeError
            return text
        except (KeyError, IndexError, TypeError) as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "Gemini response had no usable content") from error
