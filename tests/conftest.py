"""Global Pytest Fixtures and Test Environment Setup."""

import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import fakeredis.aioredis
import pytest
from httpx import ASGITransport, AsyncClient
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.compiler import compiles

# Set environment to testing before importing app
os.environ["APP_ENV"] = "testing"
os.environ["DEBUG"] = "true"
os.environ["JWT_SECRET_KEY"] = "test_super_secret_key_minimum_32_characters_long_for_tests!"


# SQLite Compilation Hooks for PostgreSQL Dialect Types
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"


@compiles(INET, "sqlite")
def compile_inet_sqlite(type_, compiler, **kw):
    return "VARCHAR(45)"


@compiles(Vector, "sqlite")
def compile_vector_sqlite(type_, compiler, **kw):
    return "TEXT"


import app.infrastructure.database.models  # noqa: F401, E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.session import get_db  # noqa: E402
from app.infrastructure.redis.client import get_redis_client  # noqa: E402
from app.main import create_app  # noqa: E402
from app.modules.identity.api.dependencies import get_optional_redis  # noqa: E402


@pytest.fixture(scope="session")
def app_instance():
    """Provides a fresh FastAPI test application instance."""
    return create_app()


@pytest.fixture
async def test_db_engine():
    """Provides an in-memory SQLite database engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provides an isolated AsyncSession for database operations during tests."""
    session_factory = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def redis_mock():
    """Provides an in-memory FakeRedis instance for caching and revocation testing."""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield fake_redis
    await fake_redis.aclose()


@pytest.fixture
async def async_client(
    app_instance, db_session: AsyncSession, redis_mock
) -> AsyncGenerator[AsyncClient, None]:
    """Provides an asynchronous HTTP client with DB and Redis dependencies overridden."""

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    async def override_get_redis():
        return redis_mock

    app_instance.dependency_overrides[get_db] = override_get_db
    app_instance.dependency_overrides[get_redis_client] = override_get_redis
    app_instance.dependency_overrides[get_optional_redis] = override_get_redis

    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

    app_instance.dependency_overrides.clear()


@pytest.fixture
def mock_db_health_healthy():
    """Mocks check_db_health returning a healthy status."""
    with patch("app.api.v1.health.check_db_health", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "status": "HEALTHY",
            "latency_ms": 1.25,
            "message": "PostgreSQL database is operational",
        }
        yield mock


@pytest.fixture
def mock_db_health_unhealthy():
    """Mocks check_db_health returning an unhealthy status."""
    with patch("app.api.v1.health.check_db_health", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "status": "UNHEALTHY",
            "latency_ms": 50.0,
            "error": "Connection to PostgreSQL refused",
        }
        yield mock


@pytest.fixture
def mock_redis_health_healthy():
    """Mocks check_redis_health returning a healthy status."""
    with patch("app.api.v1.health.check_redis_health", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "status": "HEALTHY",
            "latency_ms": 0.45,
            "message": "Redis cache is operational",
        }
        yield mock


@pytest.fixture
def mock_redis_health_unhealthy():
    """Mocks check_redis_health returning an unhealthy status."""
    with patch("app.api.v1.health.check_redis_health", new_callable=AsyncMock) as mock:
        mock.return_value = {
            "status": "UNHEALTHY",
            "latency_ms": 10.0,
            "error": "Redis cluster unreachable",
        }
        yield mock
