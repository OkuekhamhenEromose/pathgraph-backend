"""
Centralized configuration using Pydantic Settings.
Fails fast on startup if required environment variables are missing.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # CognoDB
    cognodb_uri: str
    cognodb_username: str = "cognodb"
    cognodb_password: str

    # App
    app_name: str = "PathGraph"
    app_env: str = "development"
    log_level: str = "INFO"

    # CORS
    frontend_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()
