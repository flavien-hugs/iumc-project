from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://iumc:iumc@localhost:5432/iumc"
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "change-me-in-env"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expires_minutes: int = 15
    jwt_refresh_token_expires_days: int = 7

    cors_allow_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://localhost:3001",
    ]

    storage_backend: str = "local"
    storage_local_path: str = "/data/media"
    max_upload_mb: int = 10

    # SMTP optionnel : sans hôte configuré, les e-mails sont journalisés (dev).
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@iumc.ci"

    # Base des liens envoyés par e-mail (réinitialisation de mot de passe).
    admin_base_url: str = "http://localhost:3001"


@lru_cache
def get_settings() -> Settings:
    return Settings()
