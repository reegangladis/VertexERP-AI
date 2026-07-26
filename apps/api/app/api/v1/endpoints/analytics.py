import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics import (
    AnalyticsDashboardCreate,
    AnalyticsDashboardResponse,
    AnalyticsWidgetCreate,
    AnalyticsWidgetResponse,
    KPICreate,
    KPIResponse,
    KPIValueCreate,
    KPIValueResponse,
    KPITrendResponse,
    ReportCreate,
    ReportResponse,
    SavedReportCreate,
    SavedReportResponse,
    ReportTemplateResponse,
    ReportExecuteRequest,
    ReportExecuteResponse,
    ExportRequest,
    ExportResponse,
    ExecutiveAnalyticsResponse,
    HRAnalyticsResponse,
    CRMAnalyticsResponse,
    InventoryAnalyticsResponse,
    FinanceAnalyticsResponse,
    ManufacturingAnalyticsResponse,
    SearchAnalyticsResponse,
)

router = APIRouter()

# Default test organization ID for dev/testing when tenant context header is omitted
DEFAULT_ORG_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
DEFAULT_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")


def get_analytics_service(session: AsyncSession = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(session)


# --- Executive & Domain Aggregation Dashboards ---

@router.get("/dashboards/executive", response_model=ExecutiveAnalyticsResponse)
async def get_executive_dashboard(
    branch_id: Optional[uuid.UUID] = None,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve Executive CEO Dashboard analytics summary."""
    return await service.get_executive_analytics(org_id, branch_id)


@router.get("/hr", response_model=HRAnalyticsResponse)
async def get_hr_analytics(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve HR Intelligence platform analytics."""
    return await service.get_hr_analytics(org_id)


@router.get("/crm", response_model=CRMAnalyticsResponse)
async def get_crm_analytics(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve CRM Intelligence platform analytics."""
    return await service.get_crm_analytics(org_id)


@router.get("/inventory", response_model=InventoryAnalyticsResponse)
async def get_inventory_analytics(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve Inventory & Warehouse platform analytics."""
    return await service.get_inventory_analytics(org_id)


@router.get("/finance", response_model=FinanceAnalyticsResponse)
async def get_finance_analytics(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve Finance & Accounting platform analytics."""
    return await service.get_finance_analytics(org_id)


@router.get("/manufacturing", response_model=ManufacturingAnalyticsResponse)
async def get_manufacturing_analytics(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve Manufacturing & Production platform analytics."""
    return await service.get_manufacturing_analytics(org_id)


# --- Dashboard & Widget Management ---

@router.get("/dashboards", response_model=List[AnalyticsDashboardResponse])
async def list_dashboards(
    scope: Optional[str] = Query(None, description="GLOBAL, EXECUTIVE, DEPARTMENT, BRANCH, CUSTOM"),
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """List analytics dashboards."""
    dashboards = await service.get_dashboards(org_id, scope)
    return [AnalyticsDashboardResponse.model_validate(d) for d in dashboards]


@router.post("/dashboards", response_model=AnalyticsDashboardResponse, status_code=status.HTTP_201_CREATED)
async def create_dashboard(
    data: AnalyticsDashboardCreate,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    user_id: uuid.UUID = DEFAULT_USER_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Create custom analytics dashboard with widgets."""
    dashboard = await service.create_dashboard(org_id, user_id, data)
    return AnalyticsDashboardResponse.model_validate(dashboard)


@router.get("/dashboards/{id}", response_model=AnalyticsDashboardResponse)
async def get_dashboard(
    id: uuid.UUID,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve analytics dashboard by ID."""
    dashboard = await service.get_dashboard_by_id(id, org_id)
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    return AnalyticsDashboardResponse.model_validate(dashboard)


@router.post("/dashboards/{id}/widgets", response_model=AnalyticsWidgetResponse, status_code=status.HTTP_201_CREATED)
async def add_widget(
    id: uuid.UUID,
    data: AnalyticsWidgetCreate,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Add visual widget to dashboard."""
    widget = await service.add_widget_to_dashboard(id, org_id, data)
    return AnalyticsWidgetResponse.model_validate(widget)


# --- KPI Builder & Trend Monitoring ---

@router.get("/kpis", response_model=List[KPIResponse])
async def list_kpis(
    category: Optional[str] = None,
    scope: Optional[str] = None,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """List enterprise Key Performance Indicators."""
    kpis = await service.get_kpis(org_id, category, scope)
    return [KPIResponse.model_validate(k) for k in kpis]


@router.post("/kpis", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    data: KPICreate,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Define new KPI in custom KPI builder."""
    kpi = await service.create_kpi(org_id, data)
    return KPIResponse.model_validate(kpi)


@router.post("/kpis/{id}/values", response_model=KPIValueResponse, status_code=status.HTTP_201_CREATED)
async def add_kpi_value(
    id: uuid.UUID,
    data: KPIValueCreate,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Log actual time-series value for a KPI."""
    if data.kpi_id != id:
        data.kpi_id = id
    val = await service.add_kpi_entry(org_id, data)
    return KPIValueResponse.model_validate(val)


@router.get("/kpis/{id}/trend", response_model=KPITrendResponse)
async def get_kpi_trend(
    id: uuid.UUID,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Retrieve KPI Target vs Actual trend and historical performance."""
    try:
        return await service.get_kpi_trend(id, org_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Report Builder, Execution & Saved Reports ---

@router.get("/reports", response_model=List[ReportResponse])
async def list_reports(
    category: Optional[str] = None,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """List analytics reports."""
    reports = await service.repo.get_reports(org_id, category)
    return [ReportResponse.model_validate(r) for r in reports]


@router.post("/reports", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    data: ReportCreate,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    user_id: uuid.UUID = DEFAULT_USER_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Create custom analytics report definition."""
    report = Report(
        organization_id=org_id,
        created_by=user_id,
        name=data.name,
        description=data.description,
        report_category=data.report_category,
        dataset_query=data.dataset_query,
        columns_config=data.columns_config,
        filters_config=data.filters_config,
        is_template=data.is_template,
    )
    res = await service.repo.create_report(report)
    return ReportResponse.model_validate(res)


@router.post("/reports/execute", response_model=ReportExecuteResponse)
async def execute_report(
    req: ReportExecuteRequest,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Execute dynamic analytics report query with filtering and pagination."""
    return await service.execute_report(org_id, req)


@router.get("/saved-reports", response_model=List[SavedReportResponse])
async def list_saved_reports(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    user_id: uuid.UUID = DEFAULT_USER_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """List user saved report snapshots."""
    saved = await service.repo.get_saved_reports(org_id, user_id)
    return [SavedReportResponse.model_validate(s) for s in saved]


@router.post("/saved-reports", response_model=SavedReportResponse, status_code=status.HTTP_201_CREATED)
async def create_saved_report(
    data: SavedReportCreate,
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    user_id: uuid.UUID = DEFAULT_USER_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Save report configuration snapshot."""
    saved = SavedReport(
        organization_id=org_id,
        report_id=data.report_id,
        user_id=user_id,
        title=data.title,
        parameters=data.parameters,
    )
    res = await service.repo.create_saved_report(saved)
    return SavedReportResponse.model_validate(res)


@router.get("/report-templates", response_model=List[ReportTemplateResponse])
async def list_report_templates(
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """List pre-packaged enterprise report templates."""
    templates = await service.repo.get_report_templates(org_id)
    return [ReportTemplateResponse.model_validate(t) for t in templates]


# --- Export & Unified Search ---

@router.post("/export", response_model=ExportResponse)
async def export_report_data(
    req: ExportRequest,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Export analytics dataset to CSV, JSON, or PDF preview."""
    return await service.export_report_data(req)


@router.get("/search", response_model=SearchAnalyticsResponse)
async def search_analytics(
    q: str = Query(..., min_length=1, description="Search query string"),
    org_id: uuid.UUID = DEFAULT_ORG_ID,
    service: AnalyticsService = Depends(get_analytics_service),
):
    """Unified search across dashboards, reports, KPIs, and saved analytics."""
    return await service.search_analytics(org_id, q)
