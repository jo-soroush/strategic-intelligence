"""Explicit provider composition; no silent local-to-cloud fallback."""

from __future__ import annotations

from dataclasses import dataclass

from strategic_intelligence.config import Settings
from strategic_intelligence.providers.contracts import LLMProvider, ProviderError, ProviderErrorCode, SearchProvider
from strategic_intelligence.providers.fakes import FakeLLMProvider, FakeSearchProvider
from strategic_intelligence.providers.ollama import OllamaAdapter
from strategic_intelligence.providers.search import DuckDuckGoSearchAdapter


@dataclass(frozen=True)
class Providers:
    llm: LLMProvider
    search: SearchProvider


def build_providers(settings: Settings) -> Providers:
    if settings.llm_provider == "ollama":
        llm: LLMProvider = OllamaAdapter(settings.ollama_base_url, settings.llm_model, settings.llm_timeout_seconds, allow_remote=settings.cloud_providers_enabled)
    elif settings.llm_provider == "fake":
        llm = FakeLLMProvider()
    else:
        if not settings.cloud_providers_enabled:
            raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "cloud provider selection requires explicit enablement")
        raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "configured provider has no approved adapter")
    if settings.search_provider == "fake":
        search: SearchProvider = FakeSearchProvider()
    elif settings.search_provider == "duckduckgo":
        search = DuckDuckGoSearchAdapter()
    else:
        raise ProviderError(ProviderErrorCode.CONFIGURATION_INVALID, "configured search provider has no approved adapter")
    return Providers(llm=llm, search=search)
