"""Custom logging handlers and maintenance helpers."""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path


class DailyNamedFileHandler(logging.Handler):
    """
    Append logs to ``{prefix}_YYYY-MM-DD.log`` inside ``log_dir``.

    Creates the directory and daily file automatically; switches files at day
    boundary without requiring process restart.
    """

    def __init__(self, log_dir: Path, prefix: str = "RPS") -> None:
        super().__init__()
        self.log_dir = log_dir
        self.prefix = prefix
        self._current_date: str | None = None
        self._stream = None
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def _path_for(self, date_str: str) -> Path:
        return self.log_dir / f"{self.prefix}_{date_str}.log"

    def _ensure_stream(self) -> None:
        today = datetime.now().strftime("%Y-%m-%d")
        if today == self._current_date and self._stream is not None:
            return
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        self._current_date = today
        path = self._path_for(today)
        self._stream = path.open("a", encoding="utf-8")

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self._ensure_stream()
            assert self._stream is not None
            self._stream.write(self.format(record) + "\n")
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        super().close()


def cleanup_old_daily_logs(
    log_dir: Path,
    retention_days: int,
    prefixes: tuple[str, ...],
) -> int:
    """
    Delete daily log files older than ``retention_days``.

    Only files matching ``<prefix>_YYYY-MM-DD.log`` are considered.
    Returns the number of deleted files.
    """
    if retention_days <= 0:
        return 0
    if not log_dir.exists():
        return 0

    cutoff_date = datetime.now(UTC).date() - timedelta(days=retention_days)
    deleted_count = 0

    for file_path in log_dir.glob("*.log"):
        for prefix in prefixes:
            expected_prefix = f"{prefix}_"
            if not file_path.name.startswith(expected_prefix):
                continue
            try:
                date_part = file_path.stem.removeprefix(expected_prefix)
                file_date = datetime.strptime(date_part, "%Y-%m-%d").date()  # noqa: DTZ007
            except ValueError:
                # Ignore logs that do not follow the expected naming pattern.
                continue
            if file_date < cutoff_date:
                file_path.unlink(missing_ok=True)
                deleted_count += 1
            break

    return deleted_count
