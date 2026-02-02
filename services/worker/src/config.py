"""Worker service configuration using flat Pydantic settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Flat settings structure for environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="WORKER_",
        env_nested_delimiter="__",
        case_sensitive=False,
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Redis settings - maps to WORKER_REDIS__HOST, WORKER_REDIS__PORT, etc.
    redis__host: str = Field(default="localhost")
    redis__port: int = Field(default=6379)
    redis__database: int = Field(default=1, description="Queue database")
    redis__cache_database: int = Field(default=0, description="Cache database")
    redis__password: str | None = Field(default=None)

    # API Client settings - maps to WORKER_API_CLIENT__WORKOUT_API_URL, etc.
    api_client__workout_api_url: str = Field(default="http://localhost:8000")
    api_client__ai_coach_url: str = Field(default="http://localhost:8001")
    api_client__timeout: int = Field(default=30)

    # Worker settings - maps to WORKER_WORKER__MAX_JOBS, etc.
    worker__max_jobs: int = Field(default=10)
    worker__job_timeout: int = Field(default=300)
    worker__health_port: int = Field(default=8002)

    # Schedule settings - maps to WORKER_SCHEDULE__ENABLE_HOURLY_REFRESH, etc.
    schedule__enable_hourly_refresh: bool = Field(default=True)
    schedule__enable_daily_warmup: bool = Field(default=True)
    schedule__enable_weekly_cleanup: bool = Field(default=True)
    schedule__warmup_hour: int = Field(default=6, description="UTC hour for daily warmup")
    schedule__cleanup_day_of_week: int = Field(default=6, description="0=Monday, 6=Sunday")
    schedule__cleanup_hour: int = Field(default=2, description="UTC hour for weekly cleanup")

    # Refresh settings - maps to WORKER_REFRESH__CONCURRENCY, etc.
    refresh__concurrency: int = Field(default=5)
    refresh__idempotency_ttl: int = Field(default=3600)
    refresh__retry_delay: int = Field(default=5)
    refresh__max_retries: int = Field(default=3)

    @property
    def redis_queue_url(self) -> str:
        """Redis URL for Arq job queue (DB 1)."""
        if self.redis__password:
            return f"redis://:{self.redis__password}@{self.redis__host}:{self.redis__port}/{self.redis__database}"
        return f"redis://{self.redis__host}:{self.redis__port}/{self.redis__database}"

    @property
    def redis_cache_url(self) -> str:
        """Redis URL for cache and idempotency (DB 0)."""
        if self.redis__password:
            return f"redis://:{self.redis__password}@{self.redis__host}:{self.redis__port}/{self.redis__cache_database}"
        return f"redis://{self.redis__host}:{self.redis__port}/{self.redis__cache_database}"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
