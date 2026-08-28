import socket

import pytest
from pydantic import BaseModel

from strategic_intelligence.config import Settings
from strategic_intelligence.providers.contracts import LLMRequest, ProviderError, ProviderErrorCode, SearchQuery, SearchResult
from strategic_intelligence.providers.factory import build_providers
from strategic_intelligence.providers.fakes import FakeLLMProvider, FakeSearchProvider
from strategic_intelligence.providers.ollama import OllamaAdapter
from strategic_intelligence.providers.search import DuckDuckGoSearchAdapter


class Response(BaseModel):
    answer: str


def _settings(monkeypatch, **values: str) -> Settings:
    for name in ("LLM_PROVIDER", "LLM_MODEL", "LLM_TIMEOUT_SECONDS", "OLLAMA_BASE_URL", "SEARCH_PROVIDER", "CLOUD_PROVIDERS_ENABLED"):
        monkeypatch.delenv(name, raising=False)
    for name, value in values.items():
        monkeypatch.setenv(name, value)
    return Settings.from_environment()


def test_fake_providers_are_deterministic_and_application_owned() -> None:
    llm = FakeLLMProvider('{"answer":"ok"}')
    assert llm.generate_structured(LLMRequest("hello"), Response).answer == "ok"
    search = FakeSearchProvider([SearchResult("A", "https://example.test"), SearchResult("B", "https://two.test")])
    assert len(search.search(SearchQuery("example", limit=1))) == 1


def test_factory_selects_explicit_fake_providers(monkeypatch) -> None:
    providers = build_providers(_settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="fake"))
    assert providers.llm.generate(LLMRequest("x")).provider == "fake"


def test_default_settings_construct_local_ollama_provider_without_network(monkeypatch) -> None:
    providers = build_providers(_settings(monkeypatch))
    assert isinstance(providers.llm, OllamaAdapter)
    assert _settings(monkeypatch).ollama_base_url == "http://127.0.0.1:11434"


def test_ollama_base_url_rejects_non_http_scheme(monkeypatch) -> None:
    with pytest.raises(ValueError, match="OLLAMA_BASE_URL"):
        _settings(monkeypatch, OLLAMA_BASE_URL="file:///tmp/ollama")


def test_remote_ollama_requires_explicit_enablement(monkeypatch) -> None:
    with pytest.raises(ValueError, match="CLOUD_PROVIDERS_ENABLED"):
        _settings(monkeypatch, OLLAMA_BASE_URL="https://remote.example")
    settings = _settings(monkeypatch, OLLAMA_BASE_URL="https://remote.example", CLOUD_PROVIDERS_ENABLED="true")
    assert isinstance(build_providers(settings).llm, OllamaAdapter)


def test_enabled_remote_ollama_uses_the_c14_external_request_boundary(monkeypatch) -> None:
    captured: list[str] = []

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"response":"ok"}'

    monkeypatch.setattr(
        "strategic_intelligence.providers.ollama.open_external_request",
        lambda request, *, timeout: captured.append(request.full_url) or Response(),
    )
    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", lambda *args, **kwargs: pytest.fail("remote request bypassed C14"))

    response = OllamaAdapter("https://remote.example", "remote", 1, allow_remote=True).generate(LLMRequest("prompt"))

    assert response.text == "ok"
    assert captured == ["https://remote.example/api/generate"]


def test_cloud_selection_is_rejected_without_explicit_enablement(monkeypatch) -> None:
    with pytest.raises(ProviderError) as error:
        build_providers(_settings(monkeypatch, LLM_PROVIDER="hosted"))
    assert error.value.code is ProviderErrorCode.CONFIGURATION_INVALID


def test_unknown_search_provider_is_rejected_without_fallback(monkeypatch) -> None:
    with pytest.raises(ProviderError):
        build_providers(_settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="hosted-search"))


def test_factory_selects_isolated_search_adapter(monkeypatch) -> None:
    assert isinstance(build_providers(_settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="duckduckgo")).search, DuckDuckGoSearchAdapter)


def test_ollama_timeout_is_normalized_without_secret_leakage(monkeypatch) -> None:
    def timed_out(*args, **kwargs):
        raise TimeoutError
    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", timed_out)
    with pytest.raises(ProviderError) as error:
        OllamaAdapter("http://127.0.0.1:11434", "local", 1).generate(LLMRequest("prompt"))
    assert error.value.code is ProviderErrorCode.TIMEOUT
    assert "127.0.0.1" not in str(error.value)


def test_ollama_unavailable_is_normalized_and_retryable(monkeypatch) -> None:
    from urllib.error import URLError
    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(URLError(socket.gaierror())))
    with pytest.raises(ProviderError) as error:
        OllamaAdapter("http://127.0.0.1:11434", "local", 1).generate(LLMRequest("prompt"))
    assert error.value.code is ProviderErrorCode.UNAVAILABLE
    assert error.value.retryable
