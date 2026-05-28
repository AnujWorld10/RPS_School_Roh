"""Structured log formatters."""

from __future__ import annotations

import json
import logging
import traceback
from datetime import UTC, datetime
from typing import Any


class JSONFormatter(logging.Formatter):
    """Emit one JSON object per log line with request and source context."""

    _EXTRA_FIELDS = (
        "request_id",
        "method",
        "path",
        "endpoint",
        "status_code",
        "duration_ms",
        "client_ip",
        "user_id",
        "error_code",
        "event",
        "response_size",
    )

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC)
            .isoformat()
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "file": record.filename,
            "line": record.lineno,
            "function": record.funcName,
        }

        for key in self._EXTRA_FIELDS:
            if hasattr(record, key):
                value = getattr(record, key)
                if value is not None:
                    payload[key] = value

        if record.exc_info:
            payload["exception_type"] = record.exc_info[0].__name__ if record.exc_info[0] else None
            payload["exception"] = self.formatException(record.exc_info)
            payload["traceback"] = "".join(traceback.format_exception(*record.exc_info)).strip()

        return json.dumps(payload, default=str)
