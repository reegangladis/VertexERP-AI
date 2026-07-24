import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.database.connection import get_db as _get_db
from app.database.redis import RedisService, get_redis_service


def get_settings() -> Settings:
    """Dependency provider returning the application settings."""
    return settings


async def get_db_session() -> AsyncGenerator[AsyncSession]:
    """Dependency provider for obtaining an asynchronous database session.

    Delegates to the database connection manager.
    """
    async for session in _get_db():
        yield session


async def get_redis() -> AsyncGenerator[RedisService]:
    """Dependency provider for obtaining the Redis cache service."""
    yield get_redis_service()


def get_logger(name: str):
    """Dependency generator that provides a configured logger instance for a given name."""

    def _logger_dependency() -> logging.Logger:
        return logging.getLogger(name)

    return _logger_dependency
