"""Tests for centralized logging."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from app.core.logging.formatters import JSONFormatter
from app.core.logging.handlers import DailyNamedFileHandler, cleanup_old_daily_logs


def test_daily_file_handler_creates_and_appends(tmp_path: Path) -> None:
    handler = DailyNamedFileHandler(log_dir=tmp_path, prefix="RPS")
    handler.setFormatter(logging.Formatter("%(message)s"))

    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="first line",
        args=(),
        exc_info=None,
    )
    handler.emit(record)
    handler.emit(record)
    handler.close()

    today = datetime.now().strftime("%Y-%m-%d")
    log_file = tmp_path / f"RPS_{today}.log"
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    assert lines[0] == "first line"


def test_json_formatter_includes_source_and_exception() -> None:
    formatter = JSONFormatter()
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        exc_info = sys.exc_info()

    record = logging.LogRecord(
        name="app.test",
        level=logging.ERROR,
        pathname=__file__,
        lineno=42,
        msg="failure",
        args=(),
        exc_info=exc_info,
        func="test_fn",
    )

    payload = json.loads(formatter.format(record))
    assert payload["level"] == "ERROR"
    assert payload["file"] == Path(__file__).name
    assert payload["line"] == 42
    assert payload["function"] == "test_fn"
    assert payload["exception_type"] == "ValueError"
    assert "traceback" in payload


def test_cleanup_old_daily_logs_deletes_old_files(tmp_path: Path) -> None:
    old_log = tmp_path / "RPS_2026-01-01.log"
    current_log = tmp_path / f"RPS_{datetime.now().strftime('%Y-%m-%d')}.log"
    error_log = tmp_path / "RPS_ERROR_2026-01-01.log"
    old_log.write_text("old", encoding="utf-8")
    current_log.write_text("today", encoding="utf-8")
    error_log.write_text("error-old", encoding="utf-8")

    deleted = cleanup_old_daily_logs(
        log_dir=tmp_path,
        retention_days=30,
        prefixes=("RPS", "RPS_ERROR"),
    )

    assert deleted >= 2
    assert not old_log.exists()
    assert not error_log.exists()
    assert current_log.exists()
