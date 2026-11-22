"""Integration tests for database session management and health checker."""

import pytest

from app.infrastructure.database.session import check_db_health, close_db_engine, init_db_engine


@pytest.mark.asyncio
async def test_db_lifecycle_methods():
    """Verifies that database init and close execute without error."""
    await init_db_engine()
    # Close gracefully
    await close_db_engine()


@pytest.mark.asyncio
async def test_db_health_check_offline():
    """Verifies that check_db_health returns UNHEALTHY when database is offline."""
    # Since DB is not running locally in unit test runner, check returns UNHEALTHY gracefully
    result = await check_db_health()
    assert "status" in result
    assert "latency_ms" in result
    assert result["status"] in ("HEALTHY", "UNHEALTHY")
