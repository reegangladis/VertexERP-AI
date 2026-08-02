import asyncio
import json
import logging
from typing import Any

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """Redis Service acts as connection manager and caching client."""

    def __init__(self) -> None:
        self.pool: ConnectionPool | None = None
        self.client: redis.Redis | None = None

    def initialize(self) -> None:
        """Initializes the Redis connection pool and client."""
        if not self.pool:
            self.pool = ConnectionPool.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
            )
            self.client = redis.Redis(connection_pool=self.pool)
            logger.info("Redis connection pool and client initialized successfully.")

    async def close(self) -> None:
        """Closes the Redis client and connection pool."""
        if self.client:
            await self.client.aclose()
        if self.pool:
            await self.pool.disconnect()
        self.client = None
        self.pool = None
        logger.info("Redis connection pool and client closed.")

    async def ping(self) -> bool:
        """Performs a health check ping to the Redis server."""
        if not self.client:
            self.initialize()
        try:
            # Check ping with timeout settings
            await asyncio.wait_for(self.client.ping(), timeout=settings.REDIS_TIMEOUT)
            return True
        except Exception as e:
            logger.error(f"Redis healthcheck ping failed: {e}")
            return False

    async def get(self, key: str) -> Any:
        """Retrieves a key and deserializes JSON payload."""
        if not self.client:
            self.initialize()
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Failed to retrieve key '{key}' from Redis cache: {e}")
            return None

    async def set(
        self, key: str, value: Any, expire_seconds: int | None = None
    ) -> bool:
        """Serializes and saves a key/value payload to Redis."""
        if not self.client:
            self.initialize()
        try:
            serialized_value = json.dumps(value)
            await self.client.set(key, serialized_value, ex=expire_seconds)
            return True
        except Exception as e:
            logger.error(f"Failed to set key '{key}' in Redis cache: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Deletes a key from Redis."""
        if not self.client:
            self.initialize()
        try:
            result = await self.client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to delete key '{key}' from Redis cache: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """Checks if a key exists in Redis."""
        if not self.client:
            self.initialize()
        try:
            return await self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check existence for key '{key}': {e}")
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """Sets an expiration time on a key in Redis."""
        if not self.client:
            self.initialize()
        try:
            return await self.client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Failed to apply expiration on key '{key}': {e}")
            return False

    async def flush(self) -> bool:
        """Flushes the database keys."""
        if not self.client:
            self.initialize()
        try:
            await self.client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Failed to flush Redis database: {e}")
            return False


# Singleton instances for global import
_redis_service = RedisService()


def get_redis_service() -> RedisService:
    """Returns the global RedisService instance."""
    return _redis_service


async def check_redis_health() -> bool:
    """Verifies connection to the Redis server. Backward compatible helper."""
    return await _redis_service.ping()
