"""Bounded retrieval of public HTML discovered by C07/C08 research."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum
from html.parser import HTMLParser
import re
from time import perf_counter
from typing import Protocol
from urllib.parse import urlsplit
from urllib.error import HTTPError, URLError
from urllib.request import Request

from strategic_intelligence.security import UnsafeExternalUrlError, open_external_request, validate_resolved_external_url


class _AuditObserver(Protocol):
    def record(self, event_type: str, component: str, status: str, *, target_id: str | None = None, metadata: dict[str, str | int | float | bool | None] | None = None): ...


class SourceAcquisitionFailure(str, Enum):
    SECURITY_REJECTED = "SECURITY_REJECTED"
    TIMEOUT = "TIMEOUT"
    HTTP_FAILURE = "HTTP_FAILURE"
    UNAVAILABLE = "UNAVAILABLE"
    UNSUPPORTED_CONTENT = "UNSUPPORTED_CONTENT"
    OVERSIZED_RESPONSE = "OVERSIZED_RESPONSE"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"


class SourceSuitability(str, Enum):
    """C07/C08 retention decision for already-acquired public page content."""

    SUBSTANTIVE = "SUBSTANTIVE"
    TITLE_ONLY = "TITLE_ONLY"
    BOILERPLATE_ONLY = "BOILERPLATE_ONLY"


@dataclass(frozen=True)
class PublicSourceContent:
    requested_url: str
    final_url: str
    title: str
    text: str
    publication_date: date | None


@dataclass(frozen=True)
class SourceAcquisitionResult:
    content: PublicSourceContent | None = None
    failure: SourceAcquisitionFailure | None = None


def assess_source_suitability(content: "PublicSourceContent") -> SourceSuitability:
    """Decide whether fetched public content can use a bounded C07/C08 slot.

    This is deliberately a content-usability floor, not C10 quality/freshness
    classification or C11 verification.  It rejects only obvious shells before
    they become RawFindings.
    """

    title = _normalized_words(content.title)
    text = _normalized_words(content.text)
    body = text[len(title):].strip() if title and text.startswith(title) else text
    if not body or len(body.split()) < 12:
        return SourceSuitability.TITLE_ONLY
    residual = body
    for phrase in _BOILERPLATE_PHRASES:
        residual = residual.replace(phrase, " ")
    if len(residual.split()) < 12:
        return SourceSuitability.BOILERPLATE_ONLY
    return SourceSuitability.SUBSTANTIVE


_BOILERPLATE_PHRASES = (
    "accept all cookies", "cookie settings", "privacy policy", "cookie policy",
    "consent preferences", "enable javascript", "access denied", "verify you are human",
    "checking your browser", "please wait while we verify", "sign in to continue",
)


def _normalized_words(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


class PublicSourceRetriever:
    """C14-protected, non-recursive acquisition of one public HTML page."""

    def __init__(self, *, timeout_seconds: float = 8.0, max_bytes: int = 1_000_000, audit: _AuditObserver | None = None) -> None:
        if timeout_seconds <= 0 or not 1 <= max_bytes <= 1_000_000:
            raise ValueError("source acquisition limits are invalid")
        self._timeout_seconds = timeout_seconds
        self._max_bytes = max_bytes
        self._audit = audit

    def retrieve(self, url: str) -> SourceAcquisitionResult:
        started = perf_counter()
        result = SourceAcquisitionResult()
        try:
            request = Request(url, headers={"Accept": "text/html,application/xhtml+xml", "User-Agent": "StrategicIntelligenceV1/1.0"})
            with open_external_request(request, timeout=self._timeout_seconds) as response:
                final_url = validate_resolved_external_url(response.geturl())
                content_type = response.headers.get_content_type().lower()
                if content_type not in {"text/html", "application/xhtml+xml"}:
                    result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.UNSUPPORTED_CONTENT)
                else:
                    payload = response.read(self._max_bytes + 1)
        except UnsafeExternalUrlError:
            result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.SECURITY_REJECTED)
        except TimeoutError:
            result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.TIMEOUT)
        except HTTPError:
            result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.HTTP_FAILURE)
        except URLError:
            result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.UNAVAILABLE)
        else:
            if result.failure is not None:
                pass
            elif len(payload) > self._max_bytes:
                result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.OVERSIZED_RESPONSE)
            else:
                try:
                    decoded = payload.decode("utf-8", errors="replace")
                    parser = _PublicHtmlParser()
                    parser.feed(decoded)
                    text = parser.text()
                except Exception:
                    result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.EXTRACTION_FAILED)
                else:
                    result = SourceAcquisitionResult(failure=SourceAcquisitionFailure.EXTRACTION_FAILED) if not text else SourceAcquisitionResult(content=PublicSourceContent(
                        requested_url=url, final_url=final_url, title=parser.title or final_url,
                        text=text, publication_date=_metadata_date(parser.metadata),
                    ))
        self._observe(url, result, started)
        return result

    def _observe(self, url: str, result: SourceAcquisitionResult, started: float) -> None:
        if self._audit is not None:
            self._audit.record("SOURCE_RETRIEVAL", "public_source", "SUCCESS" if result.content else result.failure.value, metadata={
                "domain": urlsplit(url).hostname or "", "duration_ms": int((perf_counter() - started) * 1000),
                "content_kind": "HTML" if result.content else None,
            })


class _PublicHtmlParser(HTMLParser):
    _VOID_ELEMENTS = frozenset({
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    })
    _IGNORED = frozenset({
        "script", "style", "noscript", "nav", "header", "footer", "svg",
        "form", "input", "select", "option", "button", "label", "textarea", "aside",
    })
    _IGNORED_CONTAINERS = _IGNORED - _VOID_ELEMENTS

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored = 0
        self._title = False
        self._title_parts: list[str] = []
        self._parts: list[str] = []
        self.metadata: dict[str, str] = {}

    @property
    def title(self) -> str:
        return " ".join(self._title_parts).strip()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lowered = tag.lower()
        if lowered in self._IGNORED_CONTAINERS:
            self._ignored += 1
        if lowered == "title":
            self._title = True
        if lowered == "meta":
            values = {key.lower(): value or "" for key, value in attrs}
            key = (values.get("property") or values.get("name") or "").lower()
            if key in {"datepublished", "datemodified", "article:published_time", "article:modified_time"}:
                self.metadata[key] = values.get("content", "")

    def handle_endtag(self, tag: str) -> None:
        lowered = tag.lower()
        if lowered in self._IGNORED_CONTAINERS and self._ignored:
            self._ignored -= 1
        if lowered == "title":
            self._title = False

    def handle_data(self, data: str) -> None:
        if self._title:
            self._title_parts.append(data)
        if not self._ignored:
            self._parts.append(data)

    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self._parts)).strip()[:50_000]


def _metadata_date(metadata: dict[str, str]) -> date | None:
    for key in ("article:published_time", "datepublished", "article:modified_time", "datemodified"):
        value = metadata.get(key, "")
        match = re.match(r"(\d{4}-\d{2}-\d{2})", value)
        if match:
            try:
                return date.fromisoformat(match.group(1))
            except ValueError:
                pass
    return None
