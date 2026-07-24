"""Validated configuration via pydantic-settings.

Reads from environment variables (or a .env file), coerces types, and fails loudly at
startup if something required is missing or malformed.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./notes.db"
    api_key: str = "secret123"
    jwt_secret: str = "change-me-in-production-this-is-only-a-demo-secret"
    # Comma-separated origins in the env become a list; default allows a common dev port.
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
