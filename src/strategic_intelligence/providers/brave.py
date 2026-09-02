"""Brave public-web discovery behind the application-owned provider contract."""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request

from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchQuery, SearchResult
from strategic_intelligence.security import UnsafeExternalUrlError, open_external_request


class BraveSearchAdapter:
    """Call Brave's public web-search API without exposing credentials or content bodies."""

    _ENDPOINT = "https://api.search.brave.com/res/v1/web/search"

    def __init__(self, api_key: str | None, *, timeout_seconds: float = 10.0) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds

    def search(self, query: SearchQuery) -> list[SearchResult]:
        if not self._api_key:
            raise ProviderError(ProviderErrorCode.AUTHENTICATION_FAILED, "Brave Search API key is not configured")

        url = f"{self._ENDPOINT}?{urlencode({'q': query.query, 'count': query.limit})}"
        request = Request(url, headers={
            "Accept": "application/json",
            "X-Subscription-Token": self._api_key,
        })
        try:
            with open_external_request(request, timeout=query.timeout_seconds or self._timeout_seconds) as response:
                body = json.loads(response.read())
        except HTTPError as error:
            raise self._http_error(error) from error
        except TimeoutError as error:
            raise ProviderError(ProviderErrorCode.TIMEOUT, "Brave Search request timed out", retryable=True) from error
        except URLError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "Brave Search is unavailable", retryable=True) from error
        except UnsafeExternalUrlError as error:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "Brave Search endpoint violates the external URL policy") from error
        except (json.JSONDecodeError, TypeError, ValueError) as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "Brave Search returned an invalid response") from error

        try:
            records = body["web"]["results"]
            if not isinstance(records, list):
                raise TypeError("results must be a list")
            return [self._result(record) for record in records[:query.limit]]
        except (KeyError, TypeError, ValueError) as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "Brave Search returned malformed web results") from error

    @staticmethod
    def _result(record: object) -> SearchResult:
        if not isinstance(record, dict):
            raise TypeError("result must be an object")
        title = record.get("title")
        url = record.get("url")
        description = record.get("description", "")
        if not isinstance(title, str) or not title.strip() or not isinstance(url, str) or not url.strip() or not isinstance(description, str):
            raise TypeError("result fields are invalid")
        return SearchResult(
            title=title.strip(),
            url=url.strip(),
            snippet=description.strip(),
            provider_metadata={"provider": "brave"},
        )

    @staticmethod
    def _http_error(error: HTTPError) -> ProviderError:
        if error.code in {401, 403}:
            return ProviderError(ProviderErrorCode.AUTHENTICATION_FAILED, "Brave Search authentication failed")
        if error.code == 429:
            return ProviderError(ProviderErrorCode.RATE_LIMITED, "Brave Search rate limit reached", retryable=True)
        if error.code in {408, 504}:
            return ProviderError(ProviderErrorCode.TIMEOUT, "Brave Search request timed out", retryable=True)
        return ProviderError(
            ProviderErrorCode.UNAVAILABLE,
            f"Brave Search returned HTTP {error.code}",
            retryable=error.code >= 500,
        )
