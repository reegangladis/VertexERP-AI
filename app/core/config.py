"""Application configuration and strict environment variable validation."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import Environment, LogLevel


class AppSettings(BaseSettings):
    """Centralized, type-safe settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application Info
    APP_NAME: str = "VertexERP-AI-V2"
    APP_ENV: Environment = Environment.DEVELOPMENT
    DEPLOYMENT_MODE: str = "development"
    WORKER_MODE: str = "auto"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # Server Network
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & CORS
    ALLOWED_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"]
    )
    ALLOWED_HOSTS: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "testserver"]
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = Field(
        default="dev_insecure_secret_key_change_in_production_min_32_chars_long!",
        min_length=32,
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    INTEGRATION_SIGNING_SECRET: str = "vertexerp_integration_default_secret_key_v2"

    # PostgreSQL Relational Persistence (PostgreSQL 16)
    DATABASE_URL: str | None = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_USER: str = "postgres"
    DATABASE_PASSWORD: str = "postgres"
    DATABASE_NAME: str = "vertexerp_v2"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # Redis Distributed Cache & Broker
    REDIS_URL: str | None = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    REDIS_POOL_SIZE: int = 50
    REDIS_SOCKET_TIMEOUT: float = 5.0

    # Logging & Observability
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_JSON_FORMAT: bool = True

    # AI Platform & Gateway Settings
    AI_DEFAULT_PROVIDER: str = "mock"
    AI_DEFAULT_MODEL: str = "mock-gpt-4o"
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    AI_REQUEST_TIMEOUT_SECONDS: float = 30.0
    AI_ENABLE_TELEMETRY: bool = True

    # S3 / MinIO object storage
    STORAGE_ENDPOINT_URL: str = "http://localhost:9000"
    STORAGE_PUBLIC_ENDPOINT_URL: str = "http://localhost:9000"
    STORAGE_ACCESS_KEY: str = "minioadmin"
    STORAGE_SECRET_KEY: str = "minioadmin"
    STORAGE_BUCKET_NAME: str = "vertexerp-vault"

    # Computed Database URLs
    @property
    def async_database_url(self) -> str:
        """Constructs asyncpg connection string, normalizing cloud PostgreSQL connection URLs."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        """Constructs sync psycopg connection string for Alembic CLI / engine bindings."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL.strip()
            if url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql+asyncpg://", "postgresql://", 1)
            if url.startswith("postgres://"):
                return url.replace("postgres://", "postgresql://", 1)
            return url
        return (
            f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    @property
    def redis_url(self) -> str:
        """Constructs Redis connection URL, prioritizing REDIS_URL if provided."""
        if self.REDIS_URL:
            return self.REDIS_URL.strip()
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Rate Limiting & Abuse Prevention (Defaults relaxed for test suites; production invariants enforce strict limits)
    RATE_LIMIT_AUTH_PER_MINUTE: int = 500
    RATE_LIMIT_AI_PER_MINUTE: int = 300
    RATE_LIMIT_DEFAULT_PER_MINUTE: int = 1000

    @field_validator("DATABASE_PORT", "REDIS_PORT", "PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError(f"Port must be between 1 and 65535, received: {v}")
        return v

    @model_validator(mode="after")
    def validate_production_invariants(self) -> "AppSettings":
        """Fails closed if insecure defaults are used in production or free cloud environments."""
        is_cloud_env = self.APP_ENV in (Environment.PRODUCTION, Environment.STAGING, Environment.FREE) or self.DEPLOYMENT_MODE.lower() in ("production", "staging", "free")

        if is_cloud_env and self.APP_ENV != Environment.TESTING:
            if "dev_insecure_secret_key" in self.JWT_SECRET_KEY or "REPLACE_WITH" in self.JWT_SECRET_KEY:
                raise ValueError(
                    f"Insecure default or placeholder JWT_SECRET_KEY cannot be used in {self.APP_ENV.value.upper()} / {self.DEPLOYMENT_MODE.upper()} mode!"
                )
            if "*" in self.ALLOWED_ORIGINS:
                raise ValueError(
                    "Wildcard CORS origins ('*') are strictly prohibited in non-development environments!"
                )
            if self.DATABASE_URL:
                if "REPLACE_WITH" in self.DATABASE_URL:
                    raise ValueError(
                        f"Placeholder DATABASE_URL cannot be used in {self.APP_ENV.value.upper()}!"
                    )
            else:
                if "REPLACE_WITH" in self.DATABASE_PASSWORD:
                    raise ValueError(
                        f"Placeholder DATABASE_PASSWORD cannot be used in {self.APP_ENV.value.upper()}!"
                    )
            if self.REDIS_URL and "REPLACE_WITH" in self.REDIS_URL:
                raise ValueError(
                    f"Placeholder REDIS_URL cannot be used in {self.APP_ENV.value.upper()}!"
                )
            if "REPLACE_WITH" in self.STORAGE_SECRET_KEY:
                raise ValueError(
                    f"Placeholder STORAGE_SECRET_KEY cannot be used in {self.APP_ENV.value.upper()}!"
                )
            if (
                "REPLACE_WITH" in self.INTEGRATION_SIGNING_SECRET
                or (self.INTEGRATION_SIGNING_SECRET == "vertexerp_integration_default_secret_key_v2" and self.APP_ENV == Environment.PRODUCTION)
            ):
                raise ValueError(
                    f"Default/placeholder INTEGRATION_SIGNING_SECRET cannot be used in "
                    f"{self.APP_ENV.value.upper()}!"
                )

            if self.AI_DEFAULT_PROVIDER.lower() in {"openai", "anthropic", "gemini"}:
                provider_keys = {
                    "openai": self.OPENAI_API_KEY,
                    "anthropic": self.ANTHROPIC_API_KEY,
                    "gemini": self.GEMINI_API_KEY,
                }
                provider_key = provider_keys[self.AI_DEFAULT_PROVIDER.lower()]
                if not provider_key or "REPLACE_WITH" in provider_key:
                    raise ValueError(
                        f"API key for configured AI provider '{self.AI_DEFAULT_PROVIDER}' "
                        f"is required in {self.APP_ENV.value.upper()}"
                    )

        if self.APP_ENV == Environment.PRODUCTION:
            if self.DEBUG:
                raise ValueError("DEBUG mode must be set to false in PRODUCTION!")
            if not self.DATABASE_URL and self.DATABASE_PASSWORD in ("postgres", "password", "root", "admin", "123456"):
                raise ValueError("Insecure default DATABASE_PASSWORD cannot be used in PRODUCTION!")
            secret_values = [
                self.JWT_SECRET_KEY,
                self.INTEGRATION_SIGNING_SECRET,
                self.STORAGE_SECRET_KEY,
            ]
            if not self.DATABASE_URL:
                secret_values.append(self.DATABASE_PASSWORD)
            else:
                secret_values.append(self.DATABASE_URL)
            if any("REPLACE_WITH" in value or "dev_insecure" in value for value in secret_values):
                raise ValueError("Production secrets must be replaced with unique high-entropy values")
            if self.INTEGRATION_SIGNING_SECRET == "vertexerp_integration_default_secret_key_v2":
                raise ValueError("Default integration signing secret cannot be used in PRODUCTION")
            if self.DEPLOYMENT_MODE.lower() == "production" and self.AI_DEFAULT_PROVIDER.lower() == "mock":
                raise ValueError("Mock AI provider cannot be the default in PRODUCTION")
            provider_keys = {
                "openai": self.OPENAI_API_KEY,
                "anthropic": self.ANTHROPIC_API_KEY,
                "gemini": self.GEMINI_API_KEY,
            }
            if self.AI_DEFAULT_PROVIDER.lower() in provider_keys and not provider_keys[self.AI_DEFAULT_PROVIDER.lower()]:
                raise ValueError(
                    f"API key for configured AI provider '{self.AI_DEFAULT_PROVIDER}' is required in PRODUCTION"
                )
        return self


# Global cached settings instance
settings = AppSettings()
