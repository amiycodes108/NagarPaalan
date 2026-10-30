"""NAGARPAALAN AI — Structured JSON logging configuration.

Configures Python's stdlib logging with structured JSON output
using python-json-logger for production-grade log aggregation.
"""

from __future__ import annotations

import logging
import sys
from datetime import datetime, timezone

from pythonjsonlogger.json import JsonFormatter


class NagarpaalanJsonFormatter(JsonFormatter):
    """Custom JSON formatter that adds standard fields to every log record."""

    def add_fields(
        self,
        log_record: dict,
        record: logging.LogRecord,
        message_dict: dict,
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = (
            datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        )
        log_record["level"] = record.levelname.upper()
        log_record["logger"] = record.name
        log_record["module"] = record.module
        if record.exc_info and not log_record.get("exc_info"):
            log_record["exc_info"] = self.formatException(record.exc_info)


def setup_logging(log_level: str = "INFO") -> None:
    """Configure the root logger with structured JSON output.

    Args:
        log_level: The minimum log level to capture (e.g. "DEBUG", "INFO").
    """
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = NagarpaalanJsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s",
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    # Clear any existing handlers to avoid duplicate output
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(numeric_level)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if numeric_level <= logging.DEBUG else logging.WARNING
    )
