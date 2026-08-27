"""Application-owned logging setup without secret or provider coupling."""

from __future__ import annotations

import logging
import os
import re
import traceback
from collections.abc import Iterable

from strategic_intelligence.config import Settings


_SECRET_ENV_NAME = re.compile(r"(?:API[_-]?KEY|AUTHORIZATION|COOKIE|PASSWORD|SECRET|TOKEN)$", re.IGNORECASE)
_BEARER_TOKEN = re.compile(r"(?i)(bearer\s+)[^\s,;]+")
_KEY_VALUE_SECRET = re.compile(r"(?i)\b(api[_-]?key|authorization|cookie|password|secret|token)\b\s*([=:])\s*([^\s,;]+)")


def configured_secret_values(environment: Iterable[tuple[str, str]] | None = None) -> tuple[str, ...]:
    """Return configured secret values without exposing their names to components."""

    values = os.environ.items() if environment is None else environment
    return tuple(value for name, value in values if _SECRET_ENV_NAME.search(name) and value)


def redact_secrets(message: str, secret_values: Iterable[str] = ()) -> str:
    """Redact configured values and credential-shaped log fragments deterministically."""

    redacted = message
    for value in sorted(set(secret_values), key=len, reverse=True):
        redacted = redacted.replace(value, "[REDACTED]")
    redacted = _BEARER_TOKEN.sub(r"\1[REDACTED]", redacted)
    return _KEY_VALUE_SECRET.sub(r"\1\2[REDACTED]", redacted)


class SecretRedactionFilter(logging.Filter):
    """Normalize a log record before handlers can format sensitive content."""

    def __init__(self, secret_values: Iterable[str] = ()) -> None:
        super().__init__()
        self._secret_values = tuple(secret_values)

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_secrets(record.getMessage(), self._secret_values)
        record.args = ()
        if record.exc_info:
            record.exc_text = redact_secrets("".join(traceback.format_exception(*record.exc_info)), self._secret_values)
        if record.stack_info:
            record.stack_info = redact_secrets(record.stack_info, self._secret_values)
        return True


def configure_logging(settings: Settings) -> None:
    """Configure the application logger once at the composition boundary."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    redaction = SecretRedactionFilter(configured_secret_values())
    for handler in logging.getLogger().handlers:
        handler.addFilter(redaction)
