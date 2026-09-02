from __future__ import annotations

from email.message import Message
from urllib.error import URLError

import pytest

from strategic_intelligence.application.source_acquisition import (
    _PublicHtmlParser, PublicSourceContent, PublicSourceRetriever, SourceAcquisitionFailure,
    SourceSuitability, assess_source_suitability,
)
from strategic_intelligence.security import UnsafeExternalUrlError


class _Response:
    def __init__(self, body: bytes, *, url: str = "https://public.example.test/article", content_type: str = "text/html") -> None:
        self._body = body
        self._url = url
        self.headers = Message()
        self.headers["Content-Type"] = content_type

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self) -> str:
        return self._url

    def read(self, amount: int) -> bytes:
        return self._body


def test_html_acquisition_extracts_content_and_machine_date(monkeypatch) -> None:
    response = _Response(b"<html><head><title>Public report</title><meta property='article:published_time' content='2026-08-20T12:00:00Z'></head><body><nav>menu</nav><main>Trusted public finding.</main><form>Phone personal data</form><script>secret()</script></body></html>")
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.open_external_request", lambda request, timeout: response)
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.validate_resolved_external_url", lambda value: value)

    result = PublicSourceRetriever().retrieve("https://public.example.test/article")

    assert result.failure is None
    assert result.content is not None
    assert result.content.title == "Public report"
    assert result.content.text == "Public report Trusted public finding."
    assert str(result.content.publication_date) == "2026-08-20"


@pytest.mark.parametrize("url", ["http://127.0.0.1/a", "http://localhost/a", "file:///tmp/a", "https://user:pass@example.test/a"])
def test_security_rejections_are_typed(monkeypatch, url: str) -> None:
    def reject(request, timeout):
        raise UnsafeExternalUrlError.__new__(UnsafeExternalUrlError)
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.open_external_request", reject)
    assert PublicSourceRetriever().retrieve(url).failure is SourceAcquisitionFailure.SECURITY_REJECTED


def test_bounds_content_type_and_network_failures_are_typed(monkeypatch) -> None:
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.validate_resolved_external_url", lambda value: value)
    retriever = PublicSourceRetriever(max_bytes=10)
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.open_external_request", lambda request, timeout: _Response(b"x" * 11))
    assert retriever.retrieve("https://public.example.test/a").failure is SourceAcquisitionFailure.OVERSIZED_RESPONSE
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.open_external_request", lambda request, timeout: _Response(b"pdf", content_type="application/pdf"))
    assert retriever.retrieve("https://public.example.test/a").failure is SourceAcquisitionFailure.UNSUPPORTED_CONTENT
    monkeypatch.setattr("strategic_intelligence.application.source_acquisition.open_external_request", lambda request, timeout: (_ for _ in ()).throw(URLError("offline")))
    assert retriever.retrieve("https://public.example.test/a").failure is SourceAcquisitionFailure.UNAVAILABLE


def test_source_suitability_rejects_title_and_cookie_shells_but_keeps_substantive_public_body() -> None:
    def content(text: str) -> PublicSourceContent:
        return PublicSourceContent(
            requested_url="https://public.example.test/report", final_url="https://public.example.test/report",
            title="Public report", text=text, publication_date=None,
        )

    assert assess_source_suitability(content("Public report")) is SourceSuitability.TITLE_ONLY
    assert assess_source_suitability(content(
        "Public report Accept all cookies Cookie settings Privacy policy Cookie policy Consent preferences Enable javascript Sign in to continue",
    )) is SourceSuitability.BOILERPLATE_ONLY
    assert assess_source_suitability(content(
        "Public report The organization describes its enterprise AI strategy, governed data foundation, delivery milestones, and measured operating outcomes for clients.",
    )) is SourceSuitability.SUBSTANTIVE


def test_ignored_void_input_does_not_suppress_later_main_content() -> None:
    parser = _PublicHtmlParser()

    parser.feed("<main>before</main><form><input name='x'></form><main>after meaningful content</main>")

    assert parser.text() == "before after meaningful content"


def test_multiple_ignored_void_inputs_and_self_closing_syntax_do_not_leak_state() -> None:
    parser = _PublicHtmlParser()

    parser.feed("<form><input name='a'><input name='b'/><button>ignored</button></form><main>kept after inputs</main>")

    assert parser.text() == "kept after inputs"


def test_nested_ignored_containers_and_script_style_stay_suppressed_after_void_handling() -> None:
    parser = _PublicHtmlParser()

    parser.feed("<header>header<nav>navigation</nav>still header</header><script>secret()</script><style>.private{display:none}</style><main>kept public content</main>")

    assert parser.text() == "kept public content"
