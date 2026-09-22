"""Analytics Domain Schemas Package."""

from app.modules.analytics.schemas.aggregation import (
    AnalyticsFilterParams,
    ChartDatasetResponse,
    DimensionalBucket,
    TimeSeriesPoint,
)
from app.modules.analytics.schemas.dashboard import (
    DashboardCreate,
    DashboardResponse,
    DashboardUpdate,
    DashboardWidgetCreate,
    DashboardWidgetResponse,
)
from app.modules.analytics.schemas.kpi import (
    KPIDefinitionCreate,
    KPIDefinitionResponse,
    KPIDefinitionUpdate,
    MetricCardData,
)
from app.modules.analytics.schemas.report import (
    AnalyticsReportCreate,
    AnalyticsReportResponse,
    ReportExecutionRequest,
    ReportExecutionResponse,
)

__all__ = [
    "KPIDefinitionCreate",
    "KPIDefinitionResponse",
    "KPIDefinitionUpdate",
    "MetricCardData",
    "AnalyticsFilterParams",
    "TimeSeriesPoint",
    "DimensionalBucket",
    "ChartDatasetResponse",
    "DashboardCreate",
    "DashboardResponse",
    "DashboardUpdate",
    "DashboardWidgetCreate",
    "DashboardWidgetResponse",
    "AnalyticsReportCreate",
    "AnalyticsReportResponse",
    "ReportExecutionRequest",
    "ReportExecutionResponse",
]
