from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ignore vars like POSTGRES_* that the app doesn't use yet
    )

    app_name: str = "TenantShield"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    database_url: str = "postgresql+psycopg://tenantshield:change_me_locally@db:5432/tenantshield"
    database_app_url: str = "postgresql+psycopg://tenantshield_app:change_me_locally@db:5432/tenantshield"
    secret_key: str = "dev-only-change-me"


@lru_cache
def get_settings() -> Settings:
    return Settings()