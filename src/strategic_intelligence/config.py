"""Centralized, non-secret application settings for the local foundation."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


_VALID_LOG_LEVELS = frozenset({"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"})


def _relative_directory(name: str, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{name} must be a relative path inside the project")
    return path


@dataclass(frozen=True)
class Settings:
    """Settings read at the application boundary, never by business components."""

    environment: str
    log_level: str
    data_dir: Path
    log_dir: Path

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
        )
