import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import KPICreate, KPIValueCreate, ReportExecuteRequest, ExportRequest


@pytest.mark.asyncio
async def test_kpi_trend_calculation_up():
    db_mock = AsyncMock()
    service = AnalyticsService(db_mock)
    org_id = uuid.uuid4()
    kpi_id = uuid.uuid4()

    # Mock KPI and history
    mock_kpi = MagicMock()
    mock_kpi.id = kpi_id
    mock_kpi.target_value = 100.0

    mock_history_entry = MagicMock()
    mock_history_entry.actual_value = 50.0  # Previous value was 50

    service.repo.get_kpi_by_id = AsyncMock(return_value=mock_kpi)
    service.repo.get_kpi_values = AsyncMock(return_value=[mock_history_entry])
    service.repo.add_kpi_value = AsyncMock(side_effect=lambda v: v)

    val_data = KPIValueCreate(
        kpi_id=kpi_id,
        actual_value=75.0,  # Current value is 75 -> 50% increase UP
        target_value=100.0,
        period_start="2026-07-01",
        period_end="2026-07-31",
    )

    res = await service.add_kpi_entry(org_id, val_data)
    assert res.trend_direction == "UP"
    assert res.trend_percentage == 50.0


@pytest.mark.asyncio
async def test_kpi_trend_calculation_down():
    db_mock = AsyncMock()
    service = AnalyticsService(db_mock)
    org_id = uuid.uuid4()
    kpi_id = uuid.uuid4()

    mock_kpi = MagicMock()
    mock_kpi.id = kpi_id
    mock_kpi.target_value = 100.0

    mock_history_entry = MagicMock()
    mock_history_entry.actual_value = 100.0

    service.repo.get_kpi_by_id = AsyncMock(return_value=mock_kpi)
    service.repo.get_kpi_values = AsyncMock(return_value=[mock_history_entry])
    service.repo.add_kpi_value = AsyncMock(side_effect=lambda v: v)

    val_data = KPIValueCreate(
        kpi_id=kpi_id,
        actual_value=80.0,  # Current value 80 -> 20% decrease DOWN
        target_value=100.0,
        period_start="2026-07-01",
        period_end="2026-07-31",
    )

    res = await service.add_kpi_entry(org_id, val_data)
    assert res.trend_direction == "DOWN"
    assert res.trend_percentage == -20.0


@pytest.mark.asyncio
async def test_executive_analytics_aggregation():
    db_mock = AsyncMock()
    service = AnalyticsService(db_mock)
    org_id = uuid.uuid4()

    service.repo.get_kpis = AsyncMock(return_value=[])

    res = await service.get_executive_analytics(org_id)
    assert res.total_revenue == 1060000.0
    assert res.total_expenses == 620000.0
    assert res.net_profit == 440000.0
    assert res.overall_oee_percent == 86.5
    assert len(res.monthly_financial_trend) == 6


@pytest.mark.asyncio
async def test_custom_report_execution_engine():
    db_mock = AsyncMock()
    service = AnalyticsService(db_mock)
    org_id = uuid.uuid4()

    req = ReportExecuteRequest(
        domain="FINANCE",
        page=1,
        page_size=10,
    )

    res = await service.execute_report(org_id, req)
    assert res.domain == "FINANCE"
    assert res.total_records == 4
    assert len(res.data) == 4
    assert "summary_kpis" in res.model_dump()


@pytest.mark.asyncio
async def test_export_report_csv_generation():
    db_mock = AsyncMock()
    service = AnalyticsService(db_mock)

    exp_req = ExportRequest(
        report_name="Financial Summary",
        export_format="CSV",
        dataset=[{"code": "FIN-01", "amount": 500.0}],
        columns=["code", "amount"],
    )

    res = await service.export_report_data(exp_req)
    assert res.export_format == "CSV"
    assert res.filename.startswith("financial_summary_")
    assert len(res.content_base64) > 0
