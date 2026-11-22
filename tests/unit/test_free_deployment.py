"""Unit and configuration tests for VertexERP AI V2 Free Deployment Mode ($0/mo Stack)."""

from pathlib import Path
import pytest
from pydantic import ValidationError

from app.core.config import AppSettings
from app.core.constants import Environment


def test_free_deployment_mode_configuration_valid():
    """Verifies that free mode configuration instantiates properly with cloud provider URLs."""
    free_settings = AppSettings(
        APP_NAME="VertexERP-AI-V2",
        APP_ENV=Environment.FREE,
        DEPLOYMENT_MODE="free",
        WORKER_MODE="embedded",
        DATABASE_URL="postgresql://postgres.myprojectref:StrongDbPass12345@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        REDIS_URL="rediss://default:UpstashSecurePassword123@us1-active-panda-12345.upstash.io:6379",
        JWT_SECRET_KEY="high_entropy_secure_jwt_secret_key_free_mode_32_chars!",
        INTEGRATION_SIGNING_SECRET="high_entropy_secure_integration_secret_free_mode_32_chars!",
        ALLOWED_ORIGINS=["https://vertexerp-demo.vercel.app"],
        ALLOWED_HOSTS=["vertexerp-api-free.onrender.com"],
        AI_DEFAULT_PROVIDER="mock",
        DEBUG=False,
    )
    assert free_settings.APP_ENV == Environment.FREE
    assert free_settings.DEPLOYMENT_MODE == "free"
    assert free_settings.WORKER_MODE == "embedded"
    assert "postgresql+asyncpg://" in free_settings.async_database_url
    assert "aws-0-us-east-1.pooler.supabase.com" in free_settings.async_database_url
    assert free_settings.redis_url.startswith("rediss://")


def test_supabase_database_url_normalization():
    """Verifies that both postgres:// and postgresql:// Supabase formats are normalized to asyncpg."""
    # Format 1: Direct Connection
    settings_direct = AppSettings(
        DATABASE_URL="postgres://postgres:MySecurePass@db.myprojectref.supabase.co:5432/postgres",
        JWT_SECRET_KEY="valid_secure_jwt_secret_key_for_testing_purposes_123456!",
    )
    assert settings_direct.async_database_url.startswith("postgresql+asyncpg://postgres:MySecurePass@db.myprojectref.supabase.co:5432/postgres")
    assert settings_direct.sync_database_url.startswith("postgresql://postgres:MySecurePass@db.myprojectref.supabase.co:5432/postgres")

    # Format 2: Connection Pooler (Transaction Mode)
    settings_pooler = AppSettings(
        DATABASE_URL="postgresql://postgres.myref:MySecurePass@aws-0-eu-central-1.pooler.supabase.com:6543/postgres",
        JWT_SECRET_KEY="valid_secure_jwt_secret_key_for_testing_purposes_123456!",
    )
    assert settings_pooler.async_database_url.startswith("postgresql+asyncpg://postgres.myref:MySecurePass@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")


def test_upstash_redis_url_handling():
    """Verifies that Upstash rediss:// TLS connection strings are preserved."""
    settings_upstash = AppSettings(
        REDIS_URL="rediss://default:upstash_secret_token_123@eu1-fast-tiger-32145.upstash.io:6379",
        JWT_SECRET_KEY="valid_secure_jwt_secret_key_for_testing_purposes_123456!",
    )
    assert settings_upstash.redis_url == "rediss://default:upstash_secret_token_123@eu1-fast-tiger-32145.upstash.io:6379"


def test_redis_url_empty_and_normalization():
    """Verifies that empty, whitespace, and missing-scheme REDIS_URL values are handled safely."""
    # Empty string falls back to host/port
    settings_empty = AppSettings(
        REDIS_URL="",
        JWT_SECRET_KEY="valid_secure_jwt_secret_key_for_testing_purposes_123456!",
    )
    assert settings_empty.redis_url.startswith("redis://")

    # Whitespace falls back to host/port
    settings_ws = AppSettings(
        REDIS_URL="   ",
        JWT_SECRET_KEY="valid_secure_jwt_secret_key_for_testing_purposes_123456!",
    )
    assert settings_ws.redis_url.startswith("redis://")

    # Host/port without scheme gets redis:// prefix added
    settings_noscheme = AppSettings(
        REDIS_URL="upstash-redis-node:6379",
        JWT_SECRET_KEY="valid_secure_jwt_secret_key_for_testing_purposes_123456!",
    )
    assert settings_noscheme.redis_url == "redis://upstash-redis-node:6379"


def test_free_mode_insecure_jwt_fails_closed():
    """Verifies that default dev JWT secrets fail closed even in free mode."""
    with pytest.raises(ValidationError, match="Insecure default or placeholder JWT_SECRET_KEY"):
        AppSettings(
            APP_ENV=Environment.FREE,
            DEPLOYMENT_MODE="free",
            JWT_SECRET_KEY="dev_insecure_secret_key_change_in_production_min_32_chars_long!",
            DATABASE_URL="postgresql://postgres.myref:pass@aws-0.pooler.supabase.com:6543/postgres",
            REDIS_URL="rediss://default:pass@upstash.io:6379",
            ALLOWED_ORIGINS=["https://demo.vercel.app"],
        )


def test_free_mode_wildcard_cors_fails_closed():
    """Verifies that wildcard CORS origins are strictly forbidden in free deployment mode."""
    with pytest.raises(ValidationError, match="Wildcard CORS origins"):
        AppSettings(
            APP_ENV=Environment.FREE,
            DEPLOYMENT_MODE="free",
            JWT_SECRET_KEY="valid_strong_unique_jwt_secret_key_32_chars_long!",
            DATABASE_URL="postgresql://postgres.myref:pass@aws-0.pooler.supabase.com:6543/postgres",
            REDIS_URL="rediss://default:pass@upstash.io:6379",
            ALLOWED_ORIGINS=["*"],
        )


def test_free_mode_placeholder_database_url_fails_closed():
    """Verifies that placeholder database credentials fail validation in free deployment mode."""
    with pytest.raises(ValidationError, match="Placeholder DATABASE_URL"):
        AppSettings(
            APP_ENV=Environment.FREE,
            DEPLOYMENT_MODE="free",
            JWT_SECRET_KEY="valid_strong_unique_jwt_secret_key_32_chars_long!",
            DATABASE_URL="postgresql://postgres.myref:REPLACE_WITH_PASSWORD@aws-0.pooler.supabase.com:6543/postgres",
            REDIS_URL="rediss://default:pass@upstash.io:6379",
            ALLOWED_ORIGINS=["https://demo.vercel.app"],
        )


def test_render_free_blueprint_file_structure():
    """Verifies that render.free.yaml exists and is configured for $0 free tier without paid resources."""
    root = Path(__file__).resolve().parents[2]
    free_blueprint = root / "render.free.yaml"
    assert free_blueprint.exists(), "render.free.yaml must exist in repository root"

    content = free_blueprint.read_text(encoding="utf-8")
    assert "vertexerp-api-free" in content
    assert "plan: free" in content
    assert "DEPLOYMENT_MODE" in content
    assert "WORKER_MODE" in content
    assert "DATABASE_URL" in content
    assert "REDIS_URL" in content

    # Crucial constraint: Free blueprint must NOT provision paid Render databases or background worker services
    assert "type: worker" not in content, "render.free.yaml must not provision a separate paid worker service"
    assert "vertexerp-postgres" not in content, "render.free.yaml must not provision Render PostgreSQL"


def test_render_production_blueprint_remains_intact():
    """Verifies that render.yaml (production blueprint) is unaltered and retains full enterprise stack."""
    root = Path(__file__).resolve().parents[2]
    prod_blueprint = root / "render.yaml"
    assert prod_blueprint.exists(), "render.yaml must remain in repository root"

    content = prod_blueprint.read_text(encoding="utf-8")
    assert "vertexerp-postgres" in content
    assert "vertexerp-redis" in content
    assert "vertexerp-api" in content
    assert "vertexerp-worker" in content


def test_free_deployment_with_production_app_env():
    """Verifies that free mode functions correctly when Render/Cloud injects APP_ENV=production."""
    free_prod_settings = AppSettings(
        APP_NAME="VertexERP-AI-V2",
        APP_ENV=Environment.PRODUCTION,
        DEPLOYMENT_MODE="free",
        WORKER_MODE="embedded",
        DATABASE_URL="postgresql://postgres.myprojectref:StrongDbPass12345@aws-0-us-east-1.pooler.supabase.com:6543/postgres",
        REDIS_URL="rediss://default:UpstashSecurePassword123@us1-active-panda-12345.upstash.io:6379",
        JWT_SECRET_KEY="high_entropy_secure_jwt_secret_key_free_mode_32_chars!",
        INTEGRATION_SIGNING_SECRET="high_entropy_secure_integration_secret_free_mode_32_chars!",
        ALLOWED_ORIGINS=["https://vertexerp-demo.vercel.app"],
        ALLOWED_HOSTS=["vertexerp-api-free.onrender.com"],
        AI_DEFAULT_PROVIDER="mock",
        AI_DEFAULT_MODEL="mock-gpt-4o",
        DEBUG=False,
    )
    assert free_prod_settings.APP_ENV == Environment.PRODUCTION
    assert free_prod_settings.DEPLOYMENT_MODE == "free"
    assert free_prod_settings.AI_DEFAULT_PROVIDER == "mock"
    assert free_prod_settings.DEBUG is False

