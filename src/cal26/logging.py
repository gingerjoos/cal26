"""Logging utilities for the Cal26 application."""

from __future__ import annotations

import json
import logging
import os
from contextvars import ContextVar, Token
from typing import Any, Dict

_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> Token[str]:
    """Bind the current request ID to the logging context."""
    return _request_id_ctx.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    """Reset the request ID context to the previous value."""
    _request_id_ctx.reset(token)


def get_request_id() -> str:
    """Return the current request ID or '-' if unset."""
    return _request_id_ctx.get()


class _RequestIdFilter(logging.Filter):
    """Inject the request ID into all log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class _JsonFormatter(logging.Formatter):
    """Format log records as JSON strings."""

    default_time_format = "%Y-%m-%dT%H:%M:%S"
    default_msec_format = "%s.%03dZ"

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)
        return json.dumps(log_record, ensure_ascii=False)


def configure_logging() -> None:
    """Configure structured logging for the application."""
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.addFilter(_RequestIdFilter())
    handler.setFormatter(_JsonFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]
    root_logger.propagate = False

    logging.captureWarnings(True)
