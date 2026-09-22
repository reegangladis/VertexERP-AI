"""Centralized Router for the Analytics & Reporting Domain."""

from fastapi import APIRouter

from app.modules.analytics.api.chart_endpoints import router as chart_router
from app.modules.analytics.api.dashboard_endpoints import router as dashboard_router
from app.modules.analytics.api.kpi_endpoints import router as kpi_router
from app.modules.analytics.api.report_endpoints import router as report_router

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics & Intelligence Domain"])

analytics_router.include_router(kpi_router)
analytics_router.include_router(dashboard_router)
analytics_router.include_router(chart_router)
analytics_router.include_router(report_router)
