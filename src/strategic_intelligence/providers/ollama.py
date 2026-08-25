"""Ollama adapter; vendor HTTP details remain inside this module."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from strategic_intelligence.providers.contracts import LLMProvider, LLMRequest, LLMResponse, ProviderError, ProviderErrorCode


class OllamaAdapter(LLMProvider):
    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(self, request: LLMRequest) -> LLMResponse:
        payload = json.dumps({"model": request.model or self._model, "prompt": request.prompt, "stream": False}).encode()
        try:
            with urlopen(Request(f"{self._base_url}/api/generate", data=payload, headers={"Content-Type": "application/json"}), timeout=request.timeout_seconds or self._timeout_seconds) as response:
                body = json.loads(response.read())
        except TimeoutError as error:
            raise ProviderError(ProviderErrorCode.TIMEOUT, "local provider timed out", retryable=True) from error
        except HTTPError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, f"local provider returned HTTP {error.code}", retryable=error.code >= 500) from error
        except URLError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "local provider is unavailable", retryable=True) from error
        except (json.JSONDecodeError, KeyError, TypeError) as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "local provider returned an invalid response") from error
        return LLMResponse(text=str(body["response"]), provider="ollama", model=str(body.get("model", self._model)))

    def generate_structured(self, request: LLMRequest, schema):
        try:
            return schema.model_validate_json(self.generate(request).text)
        except ValueError as error:
            raise ProviderError(ProviderErrorCode.STRUCTURED_OUTPUT_INVALID, "provider output did not satisfy the requested schema") from error
