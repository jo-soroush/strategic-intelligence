"""Deterministic provider doubles for application tests."""

from __future__ import annotations

from dataclasses import dataclass, field

from strategic_intelligence.providers.contracts import LLMRequest, LLMResponse, SearchQuery, SearchResult


@dataclass
class FakeLLMProvider:
    response_text: str = "{}"
    calls: list[LLMRequest] = field(default_factory=list)

    def generate(self, request: LLMRequest) -> LLMResponse:
        self.calls.append(request)
        return LLMResponse(text=self.response_text, provider="fake", model=request.model or "fake")

    def generate_structured(self, request: LLMRequest, schema):
        return schema.model_validate_json(self.generate(request).text)


@dataclass
class FakeSearchProvider:
    results: list[SearchResult] = field(default_factory=list)
    calls: list[SearchQuery] = field(default_factory=list)

    def search(self, query: SearchQuery) -> list[SearchResult]:
        self.calls.append(query)
        return self.results[:query.limit]
