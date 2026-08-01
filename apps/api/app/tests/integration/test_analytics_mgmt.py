import pytest
import uuid
from unittest.mock import MagicMock, AsyncMock
from httpx import AsyncClient
from app.main import app
from app.core.dependencies import get_current_user, get_db_session

def make_mock_result():
    res = MagicMock()
    res.scalars.return_value.all.return_value = []
    res.scalar.return_value = 0
    return res

@pytest.fixture(autouse=True)
def setup_auth_and_db_overrides(mock_db_session: MagicMock):
    current_u = MagicMock()
    current_u.organization_id = uuid.uuid4()
    current_u.id = uuid.uuid4()

    async def override_get_current_user():
        return current_u

    async def override_get_db_session():
        yield mock_db_session

    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_db_session] = override_get_db_session
    yield
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(get_db_session, None)

@pytest.mark.asyncio
async def test_executive_dashboard_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())

    response = await client.get("/api/v1/analytics/dashboards/executive")
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "net_profit" in data
    assert data["total_revenue"] > 0


@pytest.mark.asyncio
async def test_hr_analytics_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())
    response = await client.get("/api/v1/analytics/hr")
    assert response.status_code == 200
    data = response.json()
    assert "total_employees" in data
    assert "attendance_rate_percent" in data


@pytest.mark.asyncio
async def test_crm_analytics_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())
    response = await client.get("/api/v1/analytics/crm")
    assert response.status_code == 200
    data = response.json()
    assert "total_leads" in data
    assert "sales_pipeline_value" in data


@pytest.mark.asyncio
async def test_inventory_analytics_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())
    response = await client.get("/api/v1/analytics/inventory")
    assert response.status_code == 200
    data = response.json()
    assert "total_stock_value" in data
    assert "inventory_turnover_ratio" in data


@pytest.mark.asyncio
async def test_finance_analytics_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())
    response = await client.get("/api/v1/analytics/finance")
    assert response.status_code == 200
    data = response.json()
    assert "budget_utilization_percent" in data
    assert "net_income" in data


@pytest.mark.asyncio
async def test_manufacturing_analytics_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())
    response = await client.get("/api/v1/analytics/manufacturing")
    assert response.status_code == 200
    data = response.json()
    assert "overall_equipment_effectiveness_percent" in data
    assert "production_efficiency_percent" in data


@pytest.mark.asyncio
async def test_report_execution_and_export_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())
    exec_payload = {
        "domain": "FINANCE",
        "page": 1,
        "page_size": 20
    }
    res_exec = await client.post("/api/v1/analytics/reports/execute", json=exec_payload)
    assert res_exec.status_code == 200
    exec_data = res_exec.json()
    assert exec_data["domain"] == "FINANCE"
    assert len(exec_data["data"]) > 0

    export_payload = {
        "report_name": "Executive Profitability",
        "export_format": "CSV",
        "dataset": exec_data["data"],
        "columns": exec_data["columns"]
    }
    res_export = await client.post("/api/v1/analytics/export", json=export_payload)
    assert res_export.status_code == 200
    export_data = res_export.json()
    assert export_data["export_format"] == "CSV"
    assert len(export_data["content_base64"]) > 0


@pytest.mark.asyncio
async def test_analytics_search_endpoint(client: AsyncClient, mock_db_session: MagicMock):
    mock_db_session.execute = AsyncMock(side_effect=lambda *args, **kwargs: make_mock_result())

    response = await client.get("/api/v1/analytics/search", params={"q": "Executive"})
    assert response.status_code == 200
    data = response.json()
    assert "dashboards" in data
    assert "reports" in data
    assert "kpis" in data

