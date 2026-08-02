import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# --- KPI Schemas ---


class KPICreate(BaseModel):
    code: str = Field(..., max_length=100)
    name: str = Field(..., max_length=255)
    category: str = Field(
        ..., description="EXECUTIVE, HR, CRM, INVENTORY, FINANCE, MANUFACTURING, CUSTOM"
    )
    scope: str = Field("GLOBAL", description="GLOBAL, ORGANIZATION, DEPARTMENT, BRANCH")
    department_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    metric_unit: str = Field("USD", max_length=50)
    target_value: float = 0.0
    warning_threshold: float | None = None
    critical_threshold: float | None = None
    calculation_formula: str | None = None


class KPIResponse(KPICreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    ml_anomaly_score: float | None = 0.0
    target_forecast_value: float | None = None
    created_at: datetime
    updated_at: datetime


class KPIValueCreate(BaseModel):
    kpi_id: uuid.UUID
    actual_value: float
    target_value: float
    period_start: date
    period_end: date


class KPIValueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kpi_id: uuid.UUID
    organization_id: uuid.UUID
    actual_value: float
    target_value: float
    trend_direction: str  # UP, DOWN, STABLE
    trend_percentage: float
    period_start: date
    period_end: date
    created_at: datetime


class KPITrendResponse(BaseModel):
    kpi_id: uuid.UUID
    kpi_name: str
    metric_unit: str
    current_value: float
    target_value: float
    achievement_rate_percent: float
    trend_direction: str
    trend_percentage: float
    history: list[KPIValueResponse] = []


# --- Widget Schemas ---


class AnalyticsWidgetCreate(BaseModel):
    title: str = Field(..., max_length=255)
    widget_type: str = Field(
        ..., description="BAR, LINE, PIE, AREA, SCATTER, TABLE, KPI_CARD, HEATMAP"
    )
    chart_config: dict[str, Any] | None = None
    data_source: str = Field(
        ..., description="HR, CRM, INVENTORY, FINANCE, MANUFACTURING, CUSTOM"
    )
    query_config: dict[str, Any] | None = None
    refresh_interval_seconds: int = 300
    grid_position: dict[str, Any] | None = None


class AnalyticsWidgetResponse(AnalyticsWidgetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dashboard_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Dashboard Schemas ---


class AnalyticsDashboardCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: str | None = None
    scope: str = Field(
        "EXECUTIVE", description="GLOBAL, EXECUTIVE, DEPARTMENT, BRANCH, CUSTOM"
    )
    department_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    is_default: bool = False
    is_public: bool = True
    theme_config: dict[str, Any] | None = None
    ai_forecast_enabled: bool = False
    widgets: list[AnalyticsWidgetCreate] = []


class AnalyticsDashboardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    title: str
    description: str | None = None
    scope: str
    department_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    created_by: uuid.UUID | None = None
    is_default: bool
    is_public: bool
    theme_config: dict[str, Any] | None = None
    ai_forecast_enabled: bool
    predictive_metadata: dict[str, Any] | None = None
    widgets: list[AnalyticsWidgetResponse] = []
    created_at: datetime
    updated_at: datetime


class DashboardLayoutUpdate(BaseModel):
    layout_data: dict[str, Any]


# --- Report Schemas ---


class ReportCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    report_category: str = Field(
        "CUSTOM",
        description="EXECUTIVE, HR, CRM, INVENTORY, FINANCE, MANUFACTURING, CUSTOM",
    )
    dataset_query: dict[str, Any] | None = None
    columns_config: dict[str, Any] | None = None
    filters_config: dict[str, Any] | None = None
    is_template: bool = False


class ReportResponse(ReportCreate):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    created_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class SavedReportCreate(BaseModel):
    report_id: uuid.UUID
    title: str = Field(..., max_length=255)
    parameters: dict[str, Any] | None = None


class SavedReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    report_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    parameters: dict[str, Any] | None = None
    execution_count: int
    last_executed_at: datetime | None = None
    created_at: datetime


class ReportTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    name: str
    category: str
    template_schema: dict[str, Any]
    is_system: bool
    created_at: datetime


# --- Execution & Export Schemas ---


class ReportExecuteRequest(BaseModel):
    report_id: uuid.UUID | None = None
    domain: str = Field(
        "FINANCE", description="HR, CRM, INVENTORY, FINANCE, MANUFACTURING"
    )
    organization_id: uuid.UUID | None = None
    branch_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    filters: dict[str, Any] | None = None
    columns: list[str] | None = None
    page: int = 1
    page_size: int = 50


class ReportExecuteResponse(BaseModel):
    report_title: str
    domain: str
    total_records: int
    page: int
    page_size: int
    columns: list[str]
    data: list[dict[str, Any]]
    summary_kpis: dict[str, Any] = {}


class ExportRequest(BaseModel):
    report_name: str
    export_format: str = Field("CSV", description="CSV, JSON, PDF")
    dataset: list[dict[str, Any]]
    columns: list[str]


class ExportResponse(BaseModel):
    filename: str
    export_format: str
    content_base64: str
    download_url: str


class SearchAnalyticsResponse(BaseModel):
    dashboards: list[AnalyticsDashboardResponse] = []
    reports: list[ReportResponse] = []
    kpis: list[KPIResponse] = []
    saved_reports: list[SavedReportResponse] = []


# --- Domain Aggregation Responses ---


class ExecutiveAnalyticsResponse(BaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin_percent: float
    total_employees: int
    total_customers: int
    total_inventory_value: float
    overall_oee_percent: float
    revenue_growth_yoy_percent: float
    operating_cash_flow: float
    kpis: list[KPITrendResponse] = []
    monthly_financial_trend: list[dict[str, Any]] = []
    department_performance: list[dict[str, Any]] = []


class HRAnalyticsResponse(BaseModel):
    total_employees: int
    active_employees: int
    headcount_growth_percent: float
    attendance_rate_percent: float
    average_leave_days: float
    training_completion_rate: float
    top_performer_count: int
    department_headcount_breakdown: list[dict[str, Any]] = []
    monthly_attendance_trend: list[dict[str, Any]] = []
    leave_category_distribution: list[dict[str, Any]] = []


class CRMAnalyticsResponse(BaseModel):
    total_leads: int
    converted_leads: int
    lead_conversion_rate_percent: float
    sales_pipeline_value: float
    active_deals_count: int
    win_rate_percent: float
    top_customer_revenue: float
    lead_funnel_stages: list[dict[str, Any]] = []
    sales_pipeline_by_stage: list[dict[str, Any]] = []
    revenue_by_top_customers: list[dict[str, Any]] = []


class InventoryAnalyticsResponse(BaseModel):
    total_stock_value: float
    total_products_count: int
    inventory_turnover_ratio: float
    average_warehouse_utilization_percent: float
    average_supplier_rating: float
    purchase_orders_total_value: float
    stock_aging_breakdown: list[dict[str, Any]] = []
    warehouse_capacity_utilization: list[dict[str, Any]] = []
    purchase_trends: list[dict[str, Any]] = []


class FinanceAnalyticsResponse(BaseModel):
    total_revenue: float
    total_expenses: float
    net_income: float
    budget_utilization_percent: float
    operating_cash_flow: float
    accounts_receivable: float
    accounts_payable: float
    revenue_vs_expenses_trend: list[dict[str, Any]] = []
    budget_vs_actual_by_category: list[dict[str, Any]] = []
    ar_ap_aging_summary: list[dict[str, Any]] = []


class ManufacturingAnalyticsResponse(BaseModel):
    overall_equipment_effectiveness_percent: float
    production_efficiency_percent: float
    quality_pass_rate_percent: float
    total_downtime_hours: float
    open_maintenance_tickets: int
    active_production_orders: int
    machine_utilization_breakdown: list[dict[str, Any]] = []
    quality_inspections_summary: list[dict[str, Any]] = []
    maintenance_metrics: list[dict[str, Any]] = []
