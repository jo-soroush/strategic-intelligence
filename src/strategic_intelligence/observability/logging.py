"""Application-owned logging setup without secret or provider coupling."""

from __future__ import annotations

import logging

from strategic_intelligence.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure the application logger once at the composition boundary."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
