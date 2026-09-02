"""DuckDuckGo public-web discovery behind the application-owned provider contract."""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import parse_qs, unquote, urlencode, urljoin, urlsplit

from strategic_intelligence.providers.contracts import ProviderError, ProviderErrorCode, SearchQuery, SearchResult
from strategic_intelligence.security import UnsafeExternalUrlError, open_external_url


class _ResultsParser(HTMLParser):
    """Extract only bounded title, URL, and snippet fields from public results."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, str]] = []
        self._title: list[str] | None = None
        self._href: str | None = None
        self._snippet: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "a" and ({"result-link", "result__a"} & classes):
            self._title, self._href = [], values.get("href")
        elif {"result-snippet", "result__snippet"} & classes:
            self._snippet = []

    def handle_data(self, data: str) -> None:
        if self._title is not None:
            self._title.append(data)
        if self._snippet is not None:
            self._snippet.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._title is not None:
            title = " ".join("".join(self._title).split())
            if title and self._href:
                self.rows.append({"title": title, "url": self._href, "snippet": ""})
            self._title, self._href = None, None
        elif self._snippet is not None and tag in {"a", "div", "span", "td"}:
            snippet = " ".join("".join(self._snippet).split())
            if self.rows and snippet and not self.rows[-1]["snippet"]:
                self.rows[-1]["snippet"] = snippet
            self._snippet = None


class DuckDuckGoSearchAdapter:
    """Discover public web sources; results never become Evidence directly."""

    _ENDPOINT = "https://html.duckduckgo.com/html/?"

    def search(self, query: SearchQuery) -> list[SearchResult]:
        try:
            with open_external_url(f"{self._ENDPOINT}{urlencode({'q': query.query})}", timeout=query.timeout_seconds or 10) as response:
                status = getattr(response, "status", 200)
                body = response.read().decode("utf-8", "replace")
        except UnsafeExternalUrlError as error:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "search provider endpoint violates the external URL policy") from error
        except TimeoutError as error:
            raise ProviderError(ProviderErrorCode.TIMEOUT, "search provider timed out", retryable=True) from error
        except URLError as error:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, "search provider is unavailable", retryable=True) from error
        if status == 202:
            raise ProviderError(ProviderErrorCode.RATE_LIMITED, "search provider temporarily challenged the request", retryable=True)
        if status >= 400:
            raise ProviderError(ProviderErrorCode.UNAVAILABLE, f"search provider returned HTTP {status}", retryable=status >= 500)
        parser = _ResultsParser()
        try:
            parser.feed(body)
        except Exception as error:
            raise ProviderError(ProviderErrorCode.INVALID_RESPONSE, "search provider returned malformed results") from error
        return [
            SearchResult(title=row["title"], url=self._destination(row["url"]), snippet=row["snippet"], provider_metadata={"provider": "duckduckgo"})
            for row in parser.rows[:query.limit]
            if self._destination(row["url"])
        ]

    @staticmethod
    def _destination(value: str) -> str:
        """Normalize a DuckDuckGo redirect without changing source content."""
        resolved = urljoin("https://duckduckgo.com", value)
        parsed = urlsplit(resolved)
        if parsed.hostname and parsed.hostname.endswith("duckduckgo.com"):
            destination = parse_qs(parsed.query).get("uddg", [None])[0]
            if destination:
                return unquote(destination)
        return resolved
