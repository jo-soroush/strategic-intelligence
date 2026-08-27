"""DuckDuckGo discovery adapter; normalized results never become Evidence directly."""

from __future__ import annotations

import json
from urllib.error import URLError
from urllib.parse import urlencode

from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchQuery, SearchResult
from strategic_intelligence.security import UnsafeExternalUrlError, open_external_url


class DuckDuckGoSearchAdapter:
    def search(self, query: SearchQuery) -> list[SearchResult]:
        try:
            with open_external_url(f"https://api.duckduckgo.com/?{urlencode({'q': query.query, 'format': 'json', 'no_html': '1'})}", timeout=query.timeout_seconds or 10) as response:
                payload = json.loads(response.read())
        except UnsafeExternalUrlError as error:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "search provider endpoint violates the external URL policy") from error
        except TimeoutError as error:
            raise ProviderError(ProviderErrorCode.TIMEOUT, "search provider timed out", retryable=True) from error
        except (URLError, json.JSONDecodeError) as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "search provider is unavailable", retryable=True) from error
        topics = payload.get("RelatedTopics", [])
        results = [SearchResult(title=item.get("Text", ""), url=item["FirstURL"], snippet=item.get("Text", ""), provider_metadata={"provider": "duckduckgo"}) for item in topics if "FirstURL" in item]
        return results[:query.limit]
