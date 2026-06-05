from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root (parent of ``app/``)
PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "school-management-api"
    app_env: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = Field(..., description="SQLAlchemy database URL")

    jwt_secret_key: str = Field(..., min_length=16)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    password_hash_scheme: str = "argon2"
    log_level: str = "INFO"
    log_dir: str = Field(
        default=str(PROJECT_ROOT / "logs"),
        description="Directory for daily log files",
    )
    log_file_prefix: str = Field(
        default="RPS",
        description="Daily log file prefix, e.g. RPS_2026-05-27.log",
    )
    log_error_file_prefix: str = Field(
        default="RPS_ERROR",
        description="Daily ERROR log file prefix, e.g. RPS_ERROR_2026-05-27.log",
    )
    log_retention_days: int = Field(
        default=30,
        ge=0,
        description="Delete log files older than this many days (0 disables cleanup)",
    )
    log_to_console: bool = Field(
        default=True,
        description="Emit logs to stdout (recommended in development)",
    )
    log_to_file: bool = Field(
        default=True,
        description="Emit logs to daily files under log_dir",
    )

    seed_on_startup: bool = Field(
        default=False,
        description="Run default seed only when explicitly enabled",
    )

    cors_origins: str = "http://localhost:3000"

    upload_dir: str = Field(
        default=str(PROJECT_ROOT / "uploads"),
        description="Directory for admission document uploads",
    )
    max_upload_size_mb: int = Field(default=5, description="Max upload file size in MB")
    allowed_upload_extensions: str = Field(
        default="pdf,jpg,jpeg,png",
        description="Comma-separated allowed file extensions",
    )

    @field_validator("database_url", "jwt_secret_key")
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Required setting cannot be empty")
        return value.strip()

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def upload_path(self) -> Path:
        """Resolved upload directory path."""
        return Path(self.upload_dir)

    @property
    def log_path(self) -> Path:
        """Resolved log directory path."""
        return Path(self.log_dir)

    @property
    def allowed_extensions(self) -> set[str]:
        """Lowercase extensions including dot prefix."""
        return {f".{ext.strip().lower().lstrip('.')}" for ext in self.allowed_upload_extensions.split(",")}


@lru_cache
def get_settings() -> Settings:
    return Settings()
