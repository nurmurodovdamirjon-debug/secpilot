from functools import lru_cache
from typing import Literal
from urllib.parse import urlparse

from pydantic import Field, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: Literal["development", "test", "staging", "production"] = "development"
    APP_NAME: str = "SecPilot Defense"
    APP_VERSION: str = "0.1.0"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_BASE_URL: str = "http://api:8000"
    API_SECRET_KEY: str = "change-me"
    API_CONNECT_TIMEOUT_SECONDS: float = Field(default=5.0, gt=0)
    API_READ_TIMEOUT_SECONDS: float = Field(default=30.0, gt=0)
    API_RETRY_ATTEMPTS: int = Field(default=3, ge=1)
    API_RETRY_BACKOFF_SECONDS: float = Field(default=0.25, ge=0)
    API_CIRCUIT_FAILURE_THRESHOLD: int = Field(default=5, ge=1)
    API_CIRCUIT_RESET_SECONDS: float = Field(default=30.0, gt=0)
    JWT_SECRET_KEY: str = "change-me"

    BOT_TOKEN: str = "change-me"
    BOT_ADMIN_IDS: str = ""

    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "secpilot"
    POSTGRES_USER: str = "secpilot"
    POSTGRES_PASSWORD: str = "change-me"
    DATABASE_URL: str = "postgresql+psycopg://secpilot:change-me@postgres:5432/secpilot"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://redis:6379/0"

    QUEUE_BACKEND: Literal["celery"] = "celery"
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGS: bool = True
    METRICS_ENABLED: bool = True

    ALLOWED_TARGETS: str = Field(default="", description="Comma-separated defensive target whitelist.")
    POLICY_FAIL_CLOSED: bool = True
    AUTO_BLOCK_ENABLED: bool = False
    AUTO_BLOCK_MAX_ACTIONS_PER_10M: int = 10
    DEFAULT_TEMP_BLOCK_SECONDS: int = 3600
    INTEL_TIMEOUT_SECONDS: float = 5.0
    INTEL_RATE_LIMIT_PER_MINUTE: int = 30
    MONITORING_INTERVAL_SECONDS: int = 300

    HONEYPOT_ENABLED: bool = True
    CANARY_BASE_URL: str = "https://token.example.uz"
    PDF_REPORT_ENABLED: bool = True
    REPORT_TZ: str = "Asia/Tashkent"

    CLOUDFLARE_ENABLED: bool = False
    CLOUDFLARE_API_TOKEN: str = ""
    CLOUDFLARE_ZONE_ID: str = ""
    ABUSEIPDB_ENABLED: bool = False
    ABUSEIPDB_API_KEY: str = ""
    VIRUSTOTAL_ENABLED: bool = False
    VIRUSTOTAL_API_KEY: str = ""

    @computed_field
    @property
    def bot_admin_id_set(self) -> set[int]:
        return _parse_int_csv(self.BOT_ADMIN_IDS)

    @computed_field
    @property
    def allowed_target_set(self) -> set[str]:
        return _parse_str_csv(self.ALLOWED_TARGETS)

    @model_validator(mode="after")
    def validate_production_environment(self) -> "Settings":
        if self.APP_ENV not in {"production", "staging"}:
            return self

        if self.API_SECRET_KEY == "change-me":
            raise ValueError("API_SECRET_KEY must be changed outside development.")
        if self.JWT_SECRET_KEY == "change-me":
            raise ValueError("JWT_SECRET_KEY must be changed outside development.")
        if self.BOT_TOKEN == "change-me":
            raise ValueError("BOT_TOKEN must be changed outside development.")
        if not self.BOT_ADMIN_IDS.strip():
            raise ValueError("BOT_ADMIN_IDS must contain at least one admin outside development.")

        hostname = (urlparse(self.API_BASE_URL).hostname or "").lower()
        if hostname in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("API_BASE_URL must use the docker compose service name, for example http://api:8000.")
        return self


def _parse_int_csv(value: str) -> set[int]:
    ids: set[int] = set()
    for raw_item in value.split(","):
        item = raw_item.strip()
        if item:
            ids.add(int(item))
    return ids


def _parse_str_csv(value: str) -> set[str]:
    return {item.strip().lower() for item in value.split(",") if item.strip()}


@lru_cache
def get_settings() -> Settings:
    return Settings()
