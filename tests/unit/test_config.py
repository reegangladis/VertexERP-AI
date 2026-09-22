"""Unit tests for application configuration and environment validation."""

import pytest
from pydantic import ValidationError

from app.core.config import AppSettings
from app.core.constants import Environment


def test_default_settings_instantiation():
    """Verifies that default settings load with expected defaults."""
    settings = AppSettings()
    assert settings.APP_NAME == "VertexERP-AI-V2"
    assert settings.PORT == 8000
    assert "postgresql+asyncpg" in settings.async_database_url
    assert "redis://" in settings.redis_url


def test_invalid_port_validation():
    """Verifies that invalid port numbers raise validation errors."""
    with pytest.raises(ValidationError):
        AppSettings(PORT=70000)


def test_production_secret_fail_closed():
    """Verifies that default insecure JWT secrets are rejected in production."""
    with pytest.raises(ValidationError, match="Insecure default"):
        AppSettings(
            APP_ENV=Environment.PRODUCTION,
            JWT_SECRET_KEY="dev_insecure_secret_key_change_in_production_min_32_chars_long!",
        )


def test_production_wildcard_cors_fail_closed():
    """Verifies that wildcard CORS origins are rejected in production."""
    with pytest.raises(ValidationError, match="Wildcard CORS origins"):
        AppSettings(
            APP_ENV=Environment.PRODUCTION,
            JWT_SECRET_KEY="production_valid_secure_secret_key_min_32_chars_long!",
            ALLOWED_ORIGINS=["*"],
        )


def test_production_debug_mode_fail_closed():
    """Verifies that DEBUG=True is rejected in production."""
    with pytest.raises(ValidationError, match="DEBUG mode must be set to false"):
        AppSettings(
            APP_ENV=Environment.PRODUCTION,
            JWT_SECRET_KEY="production_valid_secure_secret_key_min_32_chars_long!",
            INTEGRATION_SIGNING_SECRET="production_valid_integration_signing_secret_min_32_chars!",
            DEBUG=True,
        )


def test_valid_production_settings():
    """Verifies that properly configured production settings pass validation."""
    prod_settings = AppSettings(
        APP_ENV=Environment.PRODUCTION,
        JWT_SECRET_KEY="valid_strong_production_jwt_signing_key_secret_1234567890!",
        INTEGRATION_SIGNING_SECRET="valid_production_integration_signing_secret_1234567890!",
        DATABASE_PASSWORD="strong_production_database_password_998877!",
        STORAGE_SECRET_KEY="strong_production_storage_secret_1234567890!",
        ALLOWED_ORIGINS=["https://app.vertexerp.io"],
        AI_DEFAULT_PROVIDER="openai",
        OPENAI_API_KEY="sk-test-production-placeholder-value",
        DEBUG=False,
    )
    assert prod_settings.APP_ENV == Environment.PRODUCTION
    assert prod_settings.DEBUG is False

def test_staging_placeholder_secrets_fail_closed():
    """Staging must not start with placeholder credentials."""
    with pytest.raises(ValidationError, match="DATABASE_PASSWORD"):
        AppSettings(
            APP_ENV=Environment.STAGING,
            JWT_SECRET_KEY="valid_staging_jwt_signing_secret_1234567890!",
            INTEGRATION_SIGNING_SECRET="valid_staging_integration_secret_1234567890!",
            DATABASE_PASSWORD="REPLACE_WITH_SECURE_STAGING_DATABASE_PASSWORD",
            STORAGE_SECRET_KEY="valid_staging_storage_secret_1234567890!",
            ALLOWED_ORIGINS=["https://staging.example.com"],
            AI_DEFAULT_PROVIDER="mock",
        )


def test_staging_real_secrets_with_mock_ai_are_allowed():
    """Staging may intentionally use mock AI, but secrets must be real."""
    staging_settings = AppSettings(
        APP_ENV=Environment.STAGING,
        JWT_SECRET_KEY="valid_staging_jwt_signing_secret_1234567890!",
        INTEGRATION_SIGNING_SECRET="valid_staging_integration_secret_1234567890!",
        DATABASE_PASSWORD="strong_staging_database_password_123456!",
        STORAGE_SECRET_KEY="strong_staging_storage_secret_1234567890!",
        ALLOWED_ORIGINS=["https://staging.example.com"],
        AI_DEFAULT_PROVIDER="mock",
    )
    assert staging_settings.APP_ENV == Environment.STAGING
