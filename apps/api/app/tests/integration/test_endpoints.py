from unittest.mock import patch

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_version_endpoint(client: AsyncClient):
    """Tests the version endpoint returns 200 and version data structure wrapped in APIResponse."""
    response = await client.get("/api/v1/version")
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["success"] is True
    assert "timestamp" in payload

    data = payload["data"]
    assert data["status"] == "active"
    assert data["version"] == "1.2.0"
    assert "environment" in data
    assert "timestamp" in data


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.health.check_redis_health")
async def test_health_endpoint_healthy(
    mock_redis, client: AsyncClient, mock_db_session
):
    """Tests the health endpoint returns 200 when database and Redis are operational."""
    mock_redis.return_value = True
    mock_db_session.execute.return_value = None

    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    payload = response.json()
    assert payload["success"] is True

    data = payload["data"]
    assert data["status"] == "healthy"
    assert data["services"]["database"] == "healthy"
    assert data["services"]["redis"] == "healthy"


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.health.check_redis_health")
async def test_health_endpoint_unhealthy_db(
    mock_redis, client: AsyncClient, mock_db_session
):
    """Tests health check returns 503 Service Unavailable when the database is offline."""
    mock_redis.return_value = True
    mock_db_session.execute.side_effect = Exception("DB Network down")

    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    payload = response.json()
    assert payload["success"] is False
    assert "message" in payload

    data = payload["data"]
    assert data["status"] == "unhealthy"
    assert data["services"]["database"] == "unhealthy"
    assert data["services"]["redis"] == "healthy"


@pytest.mark.asyncio
@patch("app.api.v1.endpoints.health.check_redis_health")
async def test_health_endpoint_unhealthy_redis(
    mock_redis, client: AsyncClient, mock_db_session
):
    """Tests health check returns 503 Service Unavailable when Redis is offline."""
    mock_redis.return_value = False
    mock_db_session.execute.return_value = None

    response = await client.get("/api/v1/health")
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    payload = response.json()
    assert payload["success"] is False

    data = payload["data"]
    assert data["status"] == "unhealthy"
    assert data["services"]["database"] == "healthy"
    assert data["services"]["redis"] == "unhealthy"
