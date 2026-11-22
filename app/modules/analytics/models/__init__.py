"""Analytics Domain ORM Models Package."""

from app.modules.analytics.models.dashboard import Dashboard, DashboardWidget
from app.modules.analytics.models.kpi import KPIDefinition, KPISnapshot
from app.modules.analytics.models.report import AnalyticsReport, ReportExecution

__all__ = [
    "KPIDefinition",
    "KPISnapshot",
    "Dashboard",
    "DashboardWidget",
    "AnalyticsReport",
    "ReportExecution",
]
