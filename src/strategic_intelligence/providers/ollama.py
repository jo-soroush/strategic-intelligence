"""Ollama adapter; vendor HTTP details remain inside this module."""

from __future__ import annotations

import json
import ipaddress
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from strategic_intelligence.providers.contracts import LLMProvider, LLMRequest, LLMResponse, ProviderError, ProviderErrorCode
from strategic_intelligence.security import UnsafeExternalUrlError, open_external_request


class OllamaAdapter(LLMProvider):
    def __init__(self, base_url: str, model: str, timeout_seconds: float, *, allow_remote: bool = False) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds
        hostname = urlsplit(self._base_url).hostname
        try:
            self._is_loopback = bool(hostname and ipaddress.ip_address(hostname).is_loopback)
        except ValueError:
            self._is_loopback = bool(hostname and (hostname.lower() == "localhost" or hostname.lower().endswith(".localhost")))
        if not self._is_loopback and not allow_remote:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "remote Ollama requires explicit cloud-provider enablement")

    def generate(self, request: LLMRequest) -> LLMResponse:
        return self._request(request)

    def _request(self, request: LLMRequest, *, response_format: dict | None = None, think: bool | None = None) -> LLMResponse:
        payload_data: dict[str, object] = {"model": request.model or self._model, "prompt": request.prompt, "stream": False}
        if response_format is not None:
            payload_data["format"] = response_format
        if think is not None:
            payload_data["think"] = think
        payload = json.dumps(payload_data).encode()
        try:
            outbound = Request(f"{self._base_url}/api/generate", data=payload, headers={"Content-Type": "application/json"})
            opener = urlopen if self._is_loopback else open_external_request
            with opener(outbound, timeout=request.timeout_seconds or self._timeout_seconds) as response:
                body = json.loads(response.read())
        except TimeoutError as error:
            raise ProviderError(ProviderErrorCode.TIMEOUT, "local provider timed out", retryable=True) from error
        except HTTPError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, f"local provider returned HTTP {error.code}", retryable=error.code >= 500) from error
        except URLError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "local provider is unavailable", retryable=True) from error
        except UnsafeExternalUrlError as error:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "remote provider destination is not permitted") from error
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "local provider returned an invalid response") from error
        return LLMResponse(text=str(body["response"]), provider="ollama", model=str(body.get("model", self._model)))

    def generate_structured(self, request: LLMRequest, schema):
        try:
            # The provider boundary, not a workflow stage, supplies the schema
            # contract.  Disabling optional reasoning avoids spending the
            # bounded local request budget on text that cannot satisfy it.
            response = self._request(request, response_format=schema.model_json_schema(), think=False)
            return schema.model_validate_json(response.text)
        except ValueError as error:
            raise ProviderError(ProviderErrorCode.STRUCTURED_OUTPUT_INVALID, "provider output did not satisfy the requested schema") from error
