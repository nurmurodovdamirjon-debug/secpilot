import logging
import sys
from typing import Any

import structlog

from src.core.config import Settings


SENSITIVE_KEYS = {"token", "password", "secret", "api_key", "authorization"}


def mask_secrets(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Mask obvious secrets before logs leave the process."""
    for key, value in list(event_dict.items()):
        if any(sensitive in key.lower() for sensitive in SENSITIVE_KEYS) and value:
            event_dict[key] = "***masked***"
    return event_dict


def configure_logging(settings: Settings) -> None:
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    )
    processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        mask_secrets,
    ]
    if settings.STRUCTURED_LOGS:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        ),
        cache_logger_on_first_use=True,
    )
