"""Central logging configuration."""

from __future__ import annotations

import logging
import sys
import warnings

from app.core.config import get_settings
from app.core.logging.formatters import JSONFormatter
from app.core.logging.handlers import DailyNamedFileHandler, cleanup_old_daily_logs


def setup_logging() -> None:
    """
    Configure application-wide logging.

    - Console (stdout): optional, enabled by default in development
    - File: daily ``logs/RPS_YYYY-MM-DD.log`` with append mode
    """
    settings = get_settings()
    formatter = JSONFormatter()
    level = settings.log_level.upper()

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)

    if settings.log_to_console:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        root.addHandler(console)

    if settings.log_to_file:
        file_handler = DailyNamedFileHandler(
            log_dir=settings.log_path,
            prefix=settings.log_file_prefix,
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

        error_file_handler = DailyNamedFileHandler(
            log_dir=settings.log_path,
            prefix=settings.log_error_file_prefix,
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        root.addHandler(error_file_handler)

        deleted_count = cleanup_old_daily_logs(
            log_dir=settings.log_path,
            retention_days=settings.log_retention_days,
            prefixes=(settings.log_file_prefix, settings.log_error_file_prefix),
        )
    else:
        deleted_count = 0

    # Route Python warnings through the logging system.
    logging.captureWarnings(True)
    warnings.filterwarnings("default")

    # Align framework loggers with the root configuration.
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"):
        framework_logger = logging.getLogger(logger_name)
        framework_logger.handlers.clear()
        framework_logger.propagate = True

    logging.getLogger("app").info(
        "logging initialized",
        extra={
            "event": "logging.startup",
            "log_dir": str(settings.log_path),
            "log_file_prefix": settings.log_file_prefix,
            "log_error_file_prefix": settings.log_error_file_prefix,
            "log_retention_days": settings.log_retention_days,
            "log_to_console": settings.log_to_console,
            "log_to_file": settings.log_to_file,
            "deleted_log_files": deleted_count,
        },
    )
