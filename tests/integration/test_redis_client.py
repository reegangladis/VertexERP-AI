"""Integration tests for Redis client management and health checker."""

import pytest

from app.infrastructure.redis.client import (
    check_redis_health,
    close_redis_client,
    get_redis_client,
    init_redis_client,
)


@pytest.mark.asyncio
async def test_redis_lifecycle_methods():
    """Verifies that Redis init, get, and close execute cleanly."""
    await init_redis_client()
    client = await get_redis_client()
    assert client is not None
    await close_redis_client()


@pytest.mark.asyncio
async def test_redis_health_check_offline():
    """Verifies that check_redis_health returns structured status when Redis is offline."""
    result = await check_redis_health()
    assert "status" in result
    assert "latency_ms" in result
    assert result["status"] in ("HEALTHY", "UNHEALTHY")
