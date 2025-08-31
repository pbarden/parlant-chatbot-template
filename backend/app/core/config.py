from __future__ import annotations
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env", env_file_encoding="utf-8")

    ENV: str = "dev"  # dev|stage|prod
    DEBUG: bool = False

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "YOUR_COMPANY Chat Platform"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] | None = None

    # Database
    SQLALCHEMY_DATABASE_URI: str

    # Parlant server base URL (per-tenant override allowed)
    PARLANT_BASE_URL: AnyUrl | None = None

    # OpenAI default key (per-tenant override stored in DB; this is fallback)
    OPENAI_API_KEY: str | None = None

    # Signing secrets for public session tokens
    PUBLIC_TOKEN_SECRET: str

    # Request timeout
    HTTP_CLIENT_TIMEOUT_S: float = 35.0

    # Metrics
    PROMETHEUS_ENABLED: bool = True

settings = Settings()  # type: ignore