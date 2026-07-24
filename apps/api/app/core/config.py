import json
import os
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str = "VertexERP AI"
    ENVIRONMENT: Literal["development", "testing", "production"] = "development"
    API_V1_STR: str = "/api/v1"

    # CORS Settings (JSON string or comma-separated values)
    BACKEND_CORS_ORIGINS: list[str] | str = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str] | str:
        if isinstance(v, str):
            if not v:
                return []
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # PostgreSQL configuration
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "vertexerp_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 10

    @property
    def database_url_async(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_MAX_CONNECTIONS: int = 20
    REDIS_TIMEOUT: float = 5.0

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # Logging configuration
    LOG_DIR: str = "logs"
    LOG_LEVEL: str = "INFO"

    @property
    def log_dir_path(self) -> str:
        # Ensure log directory is relative to the apps/api folder if run locally,
        # but also resolved correctly.
        return os.path.abspath(self.LOG_DIR)


settings = Settings()
