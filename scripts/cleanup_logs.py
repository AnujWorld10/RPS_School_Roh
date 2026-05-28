"""Delete old daily logs using application settings."""

from app.core.config import get_settings
from app.core.logging.handlers import cleanup_old_daily_logs


def main() -> None:
    settings = get_settings()
    deleted = cleanup_old_daily_logs(
        log_dir=settings.log_path,
        retention_days=settings.log_retention_days,
        prefixes=(settings.log_file_prefix, settings.log_error_file_prefix),
    )
    print(
        f"Deleted {deleted} log files older than "
        f"{settings.log_retention_days} days from {settings.log_path}",
    )


if __name__ == "__main__":
    main()
