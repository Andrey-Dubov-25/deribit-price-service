from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Настройки приложения, читаются из переменных окружения и .env."""

    env: str = Field("local", alias="APP_ENV")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    fetch_interval_seconds: int = Field(60, alias="FETCH_INTERVAL_SECONDS")
    supported_tickers: list[str] = Field(..., alias="SUPPORTED_TICKERS")

    database_url: str = Field(..., alias="DATABASE_URL")

    celery_broker_url: str = Field(..., alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., alias="CELERY_RESULT_BACKEND")

    deribit_base_url: str = Field(..., alias="DERIBIT_BASE_URL")
    deribit_request_timeout: int = Field(10, alias="DERIBIT_REQUEST_TIMEOUT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache
def get_settings() -> AppSettings:
    """Вернуть кэшированный экземпляр настроек приложения."""
    return AppSettings()