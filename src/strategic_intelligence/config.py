"""Centralized, non-secret application settings for the local foundation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit


_VALID_LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"})


def _relative_directory(name: str, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{name} must be a relative path inside the project")
    return path


def _http_base_url(name: str, value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.query or parsed.fragment:
        raise ValueError(f"{name} must be an absolute http(s) base URL without query or fragment")
    return value.rstrip("/")


@dataclass(frozen=True)
class Settings:
    """Settings read at the application boundary, never by business components."""

    environment: str
    log_level: str
    data_dir: Path
    log_dir: Path
    llm_provider: str
    llm_model: str
    llm_timeout_seconds: float
    ollama_base_url: str
    search_provider: str
    cloud_providers_enabled: bool

    @property
    def database_path(self) -> Path:
        """Configured local SQLite location; infrastructure resolves it."""
        return self.data_dir / "strategic_intelligence.db"

    @property
    def artifact_root(self) -> Path:
        """Configured root for case-owned local artifacts."""
        return self.data_dir / "cases"

    @classmethod
    def from_environment(cls) -> "Settings":
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        if log_level not in _VALID_LOG_LEVELS:
            raise ValueError(f"LOG_LEVEL must be one of {sorted(_VALID_LOG_LEVELS)}")

        return cls(
            environment=os.getenv("APP_ENV", "development"),
            log_level=log_level,
            data_dir=_relative_directory("DATA_DIR", os.getenv("DATA_DIR", "data")),
            log_dir=_relative_directory("LOG_DIR", os.getenv("LOG_DIR", "logs")),
            llm_provider=os.getenv("LLM_PROVIDER", "ollama").lower(),
            llm_model=os.getenv("LLM_MODEL", "llama3.2"),
            llm_timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "30")),
            ollama_base_url=_http_base_url("OLLAMA_BASE_URL", os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")),
            search_provider=os.getenv("SEARCH_PROVIDER", "fake").lower(),
            cloud_providers_enabled=os.getenv("CLOUD_PROVIDERS_ENABLED", "false").lower() == "true",
        )
