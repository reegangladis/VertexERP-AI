import pytest
import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.schemas.analytics import (
    AnalyticsDashboardCreate,
    AnalyticsWidgetCreate,
    KPICreate,
    KPIValueCreate,
    ReportExecuteRequest,
    ExportRequest,
)
from app.services.analytics_service import AnalyticsService
from app.models.analytics import AnalyticsDashboard, KPI, KPIValue


@pytest.mark.asyncio
async def test_executive_and_domain_analytics():
    mock_session = AsyncMock()
    service = AnalyticsService(mock_session)

    org_id = uuid.uuid4()

    mock_result = MagicMock()
    mock_result.scalar.return_value = 100
    mock_session.execute = AsyncMock(return_value=mock_result)

    # 1. Executive Analytics
    exec_res = await service.get_executive_analytics(org_id)
    assert exec_res.total_revenue > 0
    assert exec_res.profit_margin_percent > 0

    # 2. HR Analytics
    hr_res = await service.get_hr_analytics(org_id)
    assert hr_res.total_employees > 0
    assert len(hr_res.department_headcount_breakdown) > 0

    # 3. CRM Analytics
    crm_res = await service.get_crm_analytics(org_id)
    assert crm_res.sales_pipeline_value > 0
    assert len(crm_res.revenue_by_top_customers) > 0

    # 4. Inventory Analytics
    inv_res = await service.get_inventory_analytics(org_id)
    assert inv_res.total_stock_value > 0

    # 5. Finance Analytics
    fin_res = await service.get_finance_analytics(org_id)
    assert fin_res.total_revenue > 0

    # 6. Manufacturing Analytics
    mfg_res = await service.get_manufacturing_analytics(org_id)
    assert mfg_res.overall_equipment_effectiveness_percent > 0


@pytest.mark.asyncio
async def test_kpi_trend_and_history():
    mock_session = AsyncMock()
    service = AnalyticsService(mock_session)

    org_id = uuid.uuid4()
    kpi_id = uuid.uuid4()

    kpi = KPI(
        id=kpi_id,
        organization_id=org_id,
        code="KPI-REV-01",
        name="Monthly Revenue Target",
        category="EXECUTIVE",
        metric_unit="USD",
        target_value=1000000.0,
    )
    service.repo.get_kpi_by_id = AsyncMock(return_value=kpi)
    service.repo.get_kpi_values = AsyncMock(
        return_value=[
            KPIValue(
                id=uuid.uuid4(),
                kpi_id=kpi_id,
                organization_id=org_id,
                actual_value=1200000.0,
                target_value=1000000.0,
                trend_direction="UP",
                trend_percentage=20.0,
                period_start=date.today(),
                period_end=date.today(),
            )
        ]
    )

    trend = await service.get_kpi_trend(kpi_id, org_id)
    assert trend.kpi_name == "Monthly Revenue Target"
    assert trend.achievement_rate_percent == 120.0
    assert trend.trend_direction == "UP"


@pytest.mark.asyncio
async def test_report_execution_and_export():
    mock_session = AsyncMock()
    service = AnalyticsService(mock_session)

    org_id = uuid.uuid4()

    req = ReportExecuteRequest(
        domain="FINANCE",
        columns=["code", "name", "amount", "status"],
        page=1,
        page_size=5,
    )
    exec_res = await service.execute_report(org_id, req)
    assert exec_res.domain == "FINANCE"
    assert len(exec_res.data) > 0

    export_req = ExportRequest(
        report_name="Financial Revenue Summary",
        export_format="CSV",
        dataset=exec_res.data,
        columns=exec_res.columns,
    )
    exp_res = await service.export_report_data(export_req)
    assert exp_res.export_format == "CSV"
    assert exp_res.content_base64 is not None
