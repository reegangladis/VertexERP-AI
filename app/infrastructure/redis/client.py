"""Async Redis connection pool management and health monitoring."""

import time

from redis.asyncio import ConnectionPool, Redis

from app.core.config import settings
from app.core.constants import ServiceStatus
from app.core.logging import logger

# Global connection pool and client instances
_redis_pool: ConnectionPool | None = None
redis_client: Redis | None = None


async def init_redis_client() -> None:
    """Initializes the Redis connection pool during application startup."""
    global _redis_pool, redis_client
    if settings.REDIS_URL:
        logger.info(
            "Initializing Redis connection pool from REDIS_URL",
            pool_size=settings.REDIS_POOL_SIZE,
        )
        _redis_pool = ConnectionPool.from_url(
            settings.redis_url,
            max_connections=settings.REDIS_POOL_SIZE,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            decode_responses=True,
        )
    else:
        logger.info(
            "Initializing Redis connection pool",
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            pool_size=settings.REDIS_POOL_SIZE,
        )
        _redis_pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD or None,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_POOL_SIZE,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            decode_responses=True,
        )
    redis_client = Redis(connection_pool=_redis_pool)


async def close_redis_client() -> None:
    """Closes and disposes the Redis connection pool on application shutdown."""
    global _redis_pool, redis_client
    if redis_client:
        logger.info("Closing Redis client and connection pool")
        await redis_client.aclose()
        redis_client = None
    if _redis_pool:
        await _redis_pool.disconnect()
        _redis_pool = None


async def get_redis_client() -> Redis:
    """FastAPI dependency providing the shared active Redis client instance."""
    if redis_client is None:
        await init_redis_client()
    assert redis_client is not None
    return redis_client


async def check_redis_health() -> dict[str, object]:
    """Executes a PING command to assess Redis cluster responsiveness and latency."""
    start_time = time.perf_counter()
    try:
        client = await get_redis_client()
        pong = await client.ping()
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        if pong:
            return {
                "status": ServiceStatus.HEALTHY.value,
                "latency_ms": latency_ms,
                "message": "Redis cache is operational",
            }
        return {
            "status": ServiceStatus.UNHEALTHY.value,
            "latency_ms": latency_ms,
            "message": "Redis ping failed to return PONG",
        }
    except Exception as exc:
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.error("Redis health check failed", error=str(exc), latency_ms=latency_ms)
        return {
            "status": ServiceStatus.UNHEALTHY.value,
            "latency_ms": latency_ms,
            "error": str(exc),
        }
