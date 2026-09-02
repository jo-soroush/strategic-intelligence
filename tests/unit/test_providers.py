import json
import socket

import pytest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from strategic_intelligence.application.strategic_analysis import StrategicAnalysisService
from strategic_intelligence.config import DEFAULT_GEMINI_MODEL, Settings
from strategic_intelligence.providers.contracts import (
    LLMRequest,
    ProviderError,
    ProviderErrorCode,
    SearchQuery,
    SearchResult,
    StructuredOutputFailureReason,
)
from strategic_intelligence.providers.brave import BraveSearchAdapter
from strategic_intelligence.providers.factory import build_providers
from strategic_intelligence.providers.fakes import FakeLLMProvider, FakeSearchProvider
from strategic_intelligence.providers.ollama import OllamaAdapter
from strategic_intelligence.providers.gemini import GeminiAdapter, GeminiSchemaProjectionError, project_gemini_response_json_schema
from strategic_intelligence.providers.search import DuckDuckGoSearchAdapter


class Response(BaseModel):
    answer: str


class LimitedResponse(BaseModel):
    text: str = Field(max_length=2_000)


class StrictResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    answer: str


def _settings(monkeypatch, **values: str) -> Settings:
    for name in ("LLM_PROVIDER", "LLM_MODEL", "LLM_TIMEOUT_SECONDS", "OLLAMA_BASE_URL", "SEARCH_PROVIDER", "CLOUD_PROVIDERS_ENABLED", "BRAVE_SEARCH_API_KEY", "GEMINI_API_KEY"):
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

    class HttpResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"response":"ok"}'

    monkeypatch.setattr(
        "strategic_intelligence.providers.ollama.open_external_request",
        lambda request, *, timeout: captured.append(request.full_url) or HttpResponse(),
    )
    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", lambda *args, **kwargs: pytest.fail("remote request bypassed C14"))

    response = OllamaAdapter("https://remote.example", "remote", 1, allow_remote=True).generate(LLMRequest("prompt"))

    assert response.text == "ok"
    assert captured == ["https://remote.example/api/generate"]


def test_cloud_selection_is_rejected_without_explicit_enablement(monkeypatch) -> None:
    with pytest.raises(ProviderError) as error:
        build_providers(_settings(monkeypatch, LLM_PROVIDER="hosted"))
    assert error.value.code is ProviderErrorCode.CONFIGURATION_INVALID


def test_factory_routes_opt_in_gemini_without_fallback(monkeypatch) -> None:
    provider = build_providers(_settings(monkeypatch, LLM_PROVIDER="gemini", CLOUD_PROVIDERS_ENABLED="true", GEMINI_API_KEY="test-secret", SEARCH_PROVIDER="fake")).llm
    assert isinstance(provider, GeminiAdapter)
    assert provider._model == DEFAULT_GEMINI_MODEL


def test_gemini_missing_key_fails_safely(monkeypatch) -> None:
    provider = build_providers(_settings(monkeypatch, LLM_PROVIDER="gemini", CLOUD_PROVIDERS_ENABLED="true", SEARCH_PROVIDER="fake")).llm
    with pytest.raises(ProviderError) as error:
        provider.generate(LLMRequest("prompt"))
    assert error.value.code is ProviderErrorCode.AUTHENTICATION_FAILED
    assert "GEMINI_API_KEY" not in str(error.value)


def test_gemini_text_and_structured_calls_use_c14_and_parse(monkeypatch) -> None:
    calls: list[str] = []
    payloads: list[dict] = []
    class HttpResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"candidates":[{"content":{"parts":[{"text":"{\\\"answer\\\":\\\"READY\\\"}"}]}}]}'
    def open_request(request, *, timeout):
        calls.append(request.full_url)
        payloads.append(json.loads(request.data.decode("utf-8")))
        return HttpResponse()

    monkeypatch.setattr("strategic_intelligence.providers.gemini.open_external_request", open_request)
    adapter = GeminiAdapter("gemini-secret", DEFAULT_GEMINI_MODEL, 1)
    assert adapter.generate_structured(LLMRequest("prompt"), Response).answer == "READY"
    assert calls == [f"https://generativelanguage.googleapis.com/v1beta/models/{DEFAULT_GEMINI_MODEL}:generateContent"]
    assert not {"temperature", "top_p", "top_k"} & set(payloads[0].get("generationConfig", {}))
    assert all(content.get("role") != "model" for content in payloads[0]["contents"])


def test_gemini_structured_request_projects_unsupported_text_limits(monkeypatch) -> None:
    payloads: list[dict] = []
    class HttpResponse:
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b'{"candidates":[{"content":{"parts":[{"text":"{\\"text\\":\\"ok\\"}"}]}}]}'

    def open_request(request, *, timeout):
        payloads.append(json.loads(request.data.decode("utf-8")))
        return HttpResponse()

    monkeypatch.setattr("strategic_intelligence.providers.gemini.open_external_request", open_request)
    assert GeminiAdapter("gemini-secret", DEFAULT_GEMINI_MODEL, 1).generate_structured(LLMRequest("prompt"), LimitedResponse).text == "ok"
    schema = payloads[0]["generationConfig"]["responseJsonSchema"]
    assert "maxLength" not in schema["properties"]["text"]
    assert LimitedResponse.model_validate({"text": "x" * 2_000}).text
    with pytest.raises(ValidationError):
        LimitedResponse.model_validate({"text": "x" * 2_001})


def _schema_keywords(value: object) -> set[str]:
    if isinstance(value, dict):
        return set(value) | set().union(*(_schema_keywords(child) for child in value.values()))
    if isinstance(value, list):
        return set().union(*(_schema_keywords(child) for child in value)) if value else set()
    return set()


def test_gemini_projector_preserves_supported_c15_structure_without_mutating_source() -> None:
    raw = StrategicAnalysisService._semantic_schema_for({"CLAIM_1": "one", "CLAIM_2": "two"}).model_json_schema()
    raw_copy = json.loads(json.dumps(raw))

    projected = project_gemini_response_json_schema(raw)

    assert raw == raw_copy
    assert {"minLength", "maxLength", "default"} <= _schema_keywords(raw)
    assert not {"minLength", "maxLength", "default"} & _schema_keywords(projected)
    assert "$defs" in projected and "$ref" in _schema_keywords(projected)
    assert "required" in _schema_keywords(projected)
    assert "enum" in _schema_keywords(projected)
    assert "minItems" in _schema_keywords(projected)
    assert "anyOf" in _schema_keywords(projected)
    assert projected["properties"]["fact_selections"]["type"] == "array"


def test_gemini_projector_preserves_collection_bounds_and_translates_singleton_alias_constraint() -> None:
    raw = {
        "type": "object",
        "properties": {
            "minLength": {"type": "string", "minLength": 1, "maxLength": 2},
            "values": {"type": "array", "items": {"const": "CLAIM_1", "type": "string"}, "minItems": 1, "maxItems": 2},
            "nullable": {"anyOf": [{"type": "string"}, {"type": "null"}], "default": None},
        },
        "required": ["minLength", "values"],
        "additionalProperties": False,
    }

    projected = project_gemini_response_json_schema(raw)

    assert "minLength" in projected["properties"]
    assert projected["properties"]["values"]["minItems"] == 1
    assert projected["properties"]["values"]["maxItems"] == 2
    assert projected["properties"]["values"]["items"]["enum"] == ["CLAIM_1"]
    assert "const" not in _schema_keywords(projected)
    assert projected["properties"]["nullable"]["anyOf"][1] == {"type": "null"}
    assert "default" not in _schema_keywords(projected)


@pytest.mark.parametrize("schema", [
    {"type": "object", "patternProperties": {}},
    {"type": "object", "properties": []},
    {"type": "object", "required": [1]},
    {"type": "array", "items": []},
    {"type": "array", "items": "not-a-schema"},
])
def test_gemini_projector_fails_closed_for_unknown_or_malformed_schema(schema) -> None:
    with pytest.raises(GeminiSchemaProjectionError):
        project_gemini_response_json_schema(schema)


def test_gemini_projector_preserves_a_valid_object_items_schema() -> None:
    raw = {"type": "array", "items": {"type": "string", "minLength": 1}}

    assert project_gemini_response_json_schema(raw) == {
        "type": "array", "items": {"type": "string"},
    }


def test_gemini_adapter_fails_closed_before_transport_for_an_unsupported_schema_keyword(monkeypatch) -> None:
    monkeypatch.setattr(Response, "model_json_schema", classmethod(lambda cls: {"type": "object", "patternProperties": {}}))
    monkeypatch.setattr(
        "strategic_intelligence.providers.gemini.open_external_request",
        lambda *args, **kwargs: pytest.fail("unsupported schema must not reach transport"),
    )

    with pytest.raises(ProviderError) as error:
        GeminiAdapter("gemini-secret", DEFAULT_GEMINI_MODEL, 1).generate_structured(LLMRequest("prompt"), Response)

    assert error.value.code is ProviderErrorCode.CONFIGURATION_INVALID
    assert error.value.structured_output_failure_reason is StructuredOutputFailureReason.DYNAMIC_SCHEMA_GENERATION_FAILED


def test_gemini_schema_generation_failure_has_safe_bounded_taxonomy(monkeypatch) -> None:
    monkeypatch.setattr(Response, "model_json_schema", classmethod(lambda cls: (_ for _ in ()).throw(RuntimeError("schema secret"))))
    monkeypatch.setattr(
        "strategic_intelligence.providers.gemini.open_external_request",
        lambda *args, **kwargs: pytest.fail("schema generation failure must not reach transport"),
    )

    with pytest.raises(ProviderError) as error:
        GeminiAdapter("gemini-secret", DEFAULT_GEMINI_MODEL, 1).generate_structured(LLMRequest("prompt"), Response)

    assert error.value.code is ProviderErrorCode.CONFIGURATION_INVALID
    assert error.value.retryable is False
    assert error.value.structured_output_failure_reason is StructuredOutputFailureReason.DYNAMIC_SCHEMA_GENERATION_FAILED
    assert "schema secret" not in str(error.value)


@pytest.mark.parametrize(
    ("response_text", "reason"),
    [
        ("{not-json", StructuredOutputFailureReason.INNER_JSON_DECODE_FAILED),
        ('{"answer": []}', StructuredOutputFailureReason.PYDANTIC_VALIDATION_FAILED),
    ],
)
def test_gemini_structured_output_failures_keep_code_retry_and_safe_reason(monkeypatch, response_text, reason) -> None:
    adapter = GeminiAdapter("gemini-secret", DEFAULT_GEMINI_MODEL, 1)
    monkeypatch.setattr(adapter, "_request", lambda request, schema: response_text)

    with pytest.raises(ProviderError) as error:
        adapter.generate_structured(LLMRequest("prompt"), Response)

    assert error.value.code is ProviderErrorCode.STRUCTURED_OUTPUT_INVALID
    assert error.value.retryable is False
    assert error.value.structured_output_failure_reason is reason
    assert response_text not in str(error.value)


def test_application_draft_validation_remains_authoritative_after_projection() -> None:
    schema = StrategicAnalysisService._semantic_schema_for({"CLAIM_1": "one"})
    assert schema.model_validate({"strategic_signals": [{
        "text": "x" * 2_000, "type": "INFERENCE", "related_claim_ids": ["CLAIM_1"],
    }]})
    assert schema.model_validate({"strategic_signals": [{
        "text": "x" * 2_001, "type": "INFERENCE", "related_claim_ids": ["CLAIM_1"],
    }]}).strategic_signals == []
    for payload in (
        {"strategic_signals": [{"text": "signal", "type": "INFERENCE", "related_claim_ids": ["CLAIM_2"]}]},
        {"strategic_signals": [{"text": "signal", "type": "FACT", "related_claim_ids": ["CLAIM_1"]}]},
        {"strategic_signals": [{"text": "signal", "type": "INFERENCE", "related_claim_ids": ["CLAIM_1"], "extra": "x"}]},
    ):
        with pytest.raises(ValidationError):
            schema.model_validate(payload)
    with pytest.raises(ValidationError):
        StrictResponse.model_validate({})


@pytest.mark.parametrize(("status", "code"), [(401, ProviderErrorCode.AUTHENTICATION_FAILED), (429, ProviderErrorCode.RATE_LIMITED), (500, ProviderErrorCode.UNAVAILABLE)])
def test_gemini_http_errors_are_typed_and_secret_safe(monkeypatch, status, code) -> None:
    from urllib.error import HTTPError
    key = "gemini-secret"
    monkeypatch.setattr("strategic_intelligence.providers.gemini.open_external_request", lambda *args, **kwargs: (_ for _ in ()).throw(HTTPError("https://generativelanguage.googleapis.com", status, "failure", None, None)))
    with pytest.raises(ProviderError) as error:
        GeminiAdapter(key, DEFAULT_GEMINI_MODEL, 1).generate(LLMRequest("prompt"))
    assert error.value.code is code
    assert key not in str(error.value)


def test_unknown_search_provider_is_rejected_without_fallback(monkeypatch) -> None:
    with pytest.raises(ProviderError):
        build_providers(_settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="hosted-search"))


def test_factory_selects_isolated_search_adapter(monkeypatch) -> None:
    assert isinstance(build_providers(_settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="duckduckgo")).search, DuckDuckGoSearchAdapter)


def test_factory_selects_brave_search_adapter_without_a_fallback(monkeypatch) -> None:
    providers = build_providers(_settings(
        monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="brave", BRAVE_SEARCH_API_KEY="test-key",
    ))
    assert isinstance(providers.search, BraveSearchAdapter)


def test_brave_requires_an_environment_supplied_key_without_leaking_configuration(monkeypatch) -> None:
    key = "brave-secret-key"
    settings = _settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="brave", BRAVE_SEARCH_API_KEY=key)
    assert key not in repr(settings)
    provider = build_providers(_settings(monkeypatch, LLM_PROVIDER="fake", SEARCH_PROVIDER="brave")).search
    with pytest.raises(ProviderError) as error:
        provider.search(SearchQuery("example"))
    assert error.value.code is ProviderErrorCode.AUTHENTICATION_FAILED
    assert "BRAVE_SEARCH_API_KEY" not in str(error.value)


def test_brave_results_are_normalized_at_the_c05_provider_boundary(monkeypatch) -> None:
    captured: dict[str, str | None] = {}

    class HttpResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"web":{"results":[{"title":" Example report ","url":"https://example.test/report","description":" Public summary "}]}}'

    def opener(request, *, timeout):
        captured["url"] = request.full_url
        captured["token"] = request.get_header("X-subscription-token")
        return HttpResponse()

    monkeypatch.setattr("strategic_intelligence.providers.brave.open_external_request", opener)
    result = BraveSearchAdapter("test-key").search(SearchQuery("example", limit=1))

    assert result == [SearchResult(
        title="Example report", url="https://example.test/report", snippet="Public summary", provider_metadata={"provider": "brave"},
    )]
    assert captured["url"] == "https://api.search.brave.com/res/v1/web/search?q=example&count=1"
    assert captured["token"] == "test-key"


def test_brave_zero_results_are_not_treated_as_a_provider_failure(monkeypatch) -> None:
    class HttpResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"web":{"results":[]}}'

    monkeypatch.setattr("strategic_intelligence.providers.brave.open_external_request", lambda *args, **kwargs: HttpResponse())
    assert BraveSearchAdapter("test-key").search(SearchQuery("example")) == []


@pytest.mark.parametrize(
    ("status", "code", "retryable"),
    [
        (401, ProviderErrorCode.AUTHENTICATION_FAILED, False),
        (429, ProviderErrorCode.RATE_LIMITED, True),
        (500, ProviderErrorCode.UNAVAILABLE, True),
    ],
)
def test_brave_http_failures_are_typed_and_do_not_leak_the_api_key(monkeypatch, status, code, retryable) -> None:
    from urllib.error import HTTPError

    key = "brave-secret-key"
    monkeypatch.setattr(
        "strategic_intelligence.providers.brave.open_external_request",
        lambda *args, **kwargs: (_ for _ in ()).throw(HTTPError("https://api.search.brave.com", status, "failure", None, None)),
    )
    with pytest.raises(ProviderError) as error:
        BraveSearchAdapter(key).search(SearchQuery("example"))
    assert error.value.code is code
    assert error.value.retryable is retryable
    assert key not in str(error.value)


@pytest.mark.parametrize(
    "failure,code",
    [
        (TimeoutError(), ProviderErrorCode.TIMEOUT),
        (socket.gaierror(), ProviderErrorCode.UNAVAILABLE),
    ],
)
def test_brave_timeout_and_network_failures_are_typed(monkeypatch, failure, code) -> None:
    from urllib.error import URLError

    raised = URLError(failure) if isinstance(failure, socket.gaierror) else failure
    monkeypatch.setattr(
        "strategic_intelligence.providers.brave.open_external_request",
        lambda *args, **kwargs: (_ for _ in ()).throw(raised),
    )
    with pytest.raises(ProviderError) as error:
        BraveSearchAdapter("test-key").search(SearchQuery("example"))
    assert error.value.code is code
    assert error.value.retryable


def test_brave_malformed_response_is_typed_without_exposing_the_api_key(monkeypatch) -> None:
    class HttpResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"web":{"results":[{"title":"missing url"}]}}'

    key = "brave-secret-key"
    monkeypatch.setattr("strategic_intelligence.providers.brave.open_external_request", lambda *args, **kwargs: HttpResponse())
    with pytest.raises(ProviderError) as error:
        BraveSearchAdapter(key).search(SearchQuery("example"))
    assert error.value.code is ProviderErrorCode.INVALID_RESPONSE
    assert key not in str(error.value)


def test_duckduckgo_html_results_are_normalized_without_becoming_evidence(monkeypatch) -> None:
    class HttpResponse:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'<a class="result-link" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.test%2Freport">Example report</a><td class="result-snippet">Public summary</td>'

    monkeypatch.setattr("strategic_intelligence.providers.search.open_external_url", lambda *args, **kwargs: HttpResponse())
    result = DuckDuckGoSearchAdapter().search(SearchQuery("example", limit=1))
    assert result == [SearchResult(title="Example report", url="https://example.test/report", snippet="Public summary", provider_metadata={"provider": "duckduckgo"})]


def test_duckduckgo_challenge_is_a_typed_error_not_an_empty_result(monkeypatch) -> None:
    class HttpResponse:
        status = 202

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b"challenge"

    monkeypatch.setattr("strategic_intelligence.providers.search.open_external_url", lambda *args, **kwargs: HttpResponse())
    with pytest.raises(ProviderError) as error:
        DuckDuckGoSearchAdapter().search(SearchQuery("example"))
    assert error.value.code is ProviderErrorCode.RATE_LIMITED
    assert error.value.retryable


def test_ollama_timeout_is_normalized_without_secret_leakage(monkeypatch) -> None:
    def timed_out(*args, **kwargs):
        raise TimeoutError
    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", timed_out)
    with pytest.raises(ProviderError) as error:
        OllamaAdapter("http://127.0.0.1:11434", "local", 1).generate(LLMRequest("prompt"))
    assert error.value.code is ProviderErrorCode.TIMEOUT
    assert "127.0.0.1" not in str(error.value)


def test_ollama_structured_output_requests_schema_without_reasoning(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class HttpResponse:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self):
            return b'{"response":"{\\"answer\\":\\"READY\\"}"}'

    def opener(request, *, timeout):
        captured.update(json.loads(request.data.decode()))
        return HttpResponse()

    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", opener)
    response = OllamaAdapter("http://127.0.0.1:11434", "local", 1).generate_structured(LLMRequest("prompt"), Response)
    assert response.answer == "READY"
    assert captured["think"] is False
    assert isinstance(captured["format"], dict)


def test_ollama_unavailable_is_normalized_and_retryable(monkeypatch) -> None:
    from urllib.error import URLError
    monkeypatch.setattr("strategic_intelligence.providers.ollama.urlopen", lambda *args, **kwargs: (_ for _ in ()).throw(URLError(socket.gaierror())))
    with pytest.raises(ProviderError) as error:
        OllamaAdapter("http://127.0.0.1:11434", "local", 1).generate(LLMRequest("prompt"))
    assert error.value.code is ProviderErrorCode.UNAVAILABLE
    assert error.value.retryable
