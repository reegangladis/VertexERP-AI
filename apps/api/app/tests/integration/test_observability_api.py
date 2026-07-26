import uuid
import pytest
from datetime import datetime, UTC
from fastapi import status
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from app.models.observability import SystemMetric, ApplicationLog, DashboardConfig


@pytest.mark.asyncio
async def test_observability_health_endpoint(client: AsyncClient, mock_db_session):
    """Verifies access and schema responses for system health diagnostics endpoint."""
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.organization_id = uuid.uuid4()
    mock_user.status = "active"
    
    mock_role = AsyncMock()
    mock_role.name = "Super Admin"
    mock_user.roles = [mock_role]

    mock_health = {
        "status": "healthy",
        "version": "1.2.0",
        "timestamp": "2026-07-26T12:00:00Z",
        "uptime_ratio_percent": 99.98,
        "services": []
    }

    with patch("app.core.dependencies.oauth2_scheme", return_value="mocked_token"), \
         patch("app.core.dependencies.decode_token", return_value=str(mock_user.id)), \
         patch("app.repositories.user.UserRepository.get", return_value=mock_user), \
         patch("app.core.dependencies.get_current_tenant_id", return_value=mock_user.organization_id), \
         patch("app.services.observability_service.ObservabilityService.get_system_health", return_value=mock_health):

        headers = {"Authorization": "Bearer mocked_token"}
        response = await client.get("/api/v1/observability/health", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert "services" in payload["data"]


@pytest.mark.asyncio
async def test_record_and_query_metrics(client: AsyncClient, mock_db_session):
    """Verifies submitting a performance metric and retrieving aggregated timeseries."""
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.organization_id = uuid.uuid4()
    mock_user.status = "active"
    
    mock_role = AsyncMock()
    mock_role.name = "Super Admin"
    mock_user.roles = [mock_role]

    mock_metric = SystemMetric(
        id=uuid.uuid4(),
        organization_id=mock_user.organization_id,
        metric_name="cpu_usage",
        metric_type="gauge",
        value=45.5,
        labels={"host": "host-1"},
        created_at=datetime.now(UTC)
    )

    with patch("app.core.dependencies.oauth2_scheme", return_value="mocked_token"), \
         patch("app.core.dependencies.decode_token", return_value=str(mock_user.id)), \
         patch("app.repositories.user.UserRepository.get", return_value=mock_user), \
         patch("app.core.dependencies.get_current_tenant_id", return_value=mock_user.organization_id), \
         patch("app.services.observability_service.ObservabilityService.record_metric", return_value=mock_metric), \
         patch("app.services.observability_service.ObservabilityService.get_system_metrics", return_value=[mock_metric]):

        headers = {"Authorization": "Bearer mocked_token"}
        payload = {
            "metric_name": "cpu_usage",
            "metric_type": "gauge",
            "value": 45.5,
            "labels": {"host": "host-1"}
        }

        # 1. Test POST submit metric
        response = await client.post("/api/v1/observability/metrics", json=payload, headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        post_payload = response.json()
        assert post_payload["success"] is True
        assert post_payload["data"]["metric_name"] == "cpu_usage"

        # 2. Test GET query metrics
        response = await client.get("/api/v1/observability/metrics?metric_name=cpu_usage", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        get_payload = response.json()
        assert get_payload["success"] is True
        assert isinstance(get_payload["data"], list)


@pytest.mark.asyncio
async def test_query_logs(client: AsyncClient, mock_db_session):
    """Verifies structured logs search filters logic."""
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.organization_id = uuid.uuid4()
    mock_user.status = "active"
    
    mock_role = AsyncMock()
    mock_role.name = "Super Admin"
    mock_user.roles = [mock_role]

    with patch("app.core.dependencies.oauth2_scheme", return_value="mocked_token"), \
         patch("app.core.dependencies.decode_token", return_value=str(mock_user.id)), \
         patch("app.repositories.user.UserRepository.get", return_value=mock_user), \
         patch("app.core.dependencies.get_current_tenant_id", return_value=mock_user.organization_id), \
         patch("app.services.observability_service.ObservabilityService.search_logs", return_value=([], 0)):

        headers = {"Authorization": "Bearer mocked_token"}
        response = await client.get("/api/v1/observability/logs?service_name=rest-api&log_level=ERROR", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert "logs" in payload["data"]


@pytest.mark.asyncio
async def test_dashboard_config_endpoint(client: AsyncClient, mock_db_session):
    """Verifies fetching dashboard custom layout config grids."""
    mock_user = AsyncMock()
    mock_user.id = uuid.uuid4()
    mock_user.organization_id = uuid.uuid4()
    mock_user.status = "active"
    
    mock_role = AsyncMock()
    mock_role.name = "Super Admin"
    mock_user.roles = [mock_role]

    with patch("app.core.dependencies.oauth2_scheme", return_value="mocked_token"), \
         patch("app.core.dependencies.decode_token", return_value=str(mock_user.id)), \
         patch("app.repositories.user.UserRepository.get", return_value=mock_user), \
         patch("app.core.dependencies.get_current_tenant_id", return_value=mock_user.organization_id), \
         patch("app.services.observability_service.ObservabilityService.get_dashboard_config", return_value=None):

        headers = {"Authorization": "Bearer mocked_token"}
        response = await client.get("/api/v1/observability/dashboards/operations", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        payload = response.json()
        assert payload["success"] is True
        assert payload["data"]["dashboard_type"] == "operations"
