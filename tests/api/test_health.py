"""API tests for Kubernetes health, liveness, and readiness probes."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_probe(async_client: AsyncClient):
    """Verifies that /health/live returns 200 OK and status ALIVE."""
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ALIVE"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_startup_probe(async_client: AsyncClient):
    """Verifies that /health/startup returns 200 OK and status STARTED."""
    response = await async_client.get("/health/startup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "STARTED"


@pytest.mark.asyncio
async def test_app_info(async_client: AsyncClient):
    """Verifies that /health/info returns application metadata."""
    response = await async_client.get("/health/info")
    assert response.status_code == 200
    data = response.json()
    assert data["app_name"] == "VertexERP-AI-V2"
    assert data["version"] == "2.0.0"
    assert data["status"] == "OPERATIONAL"


@pytest.mark.asyncio
async def test_readiness_probe_healthy(
    async_client: AsyncClient, mock_db_health_healthy, mock_redis_health_healthy
):
    """Verifies that /health/ready returns 200 OK when DB and Redis are healthy."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["checks"]["database"]["status"] == "HEALTHY"
    assert data["checks"]["redis"]["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_readiness_probe_db_unhealthy(
    async_client: AsyncClient, mock_db_health_unhealthy, mock_redis_health_healthy
):
    """Verifies that /health/ready returns 503 when PostgreSQL is down."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "UNHEALTHY"
    assert data["checks"]["database"]["status"] == "UNHEALTHY"
    assert data["checks"]["redis"]["status"] == "HEALTHY"


@pytest.mark.asyncio
async def test_readiness_probe_redis_unhealthy(
    async_client: AsyncClient, mock_db_health_healthy, mock_redis_health_unhealthy
):
    """Verifies that /health/ready returns 503 when Redis is down."""
    response = await async_client.get("/health/ready")
    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "UNHEALTHY"
    assert data["checks"]["database"]["status"] == "HEALTHY"
    assert data["checks"]["redis"]["status"] == "UNHEALTHY"


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Verifies root endpoint returns basic application status."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "VertexERP-AI-V2"
    assert data["version"] == "2.0.0"
