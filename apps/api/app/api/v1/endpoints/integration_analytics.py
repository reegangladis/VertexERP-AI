from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.integration_repository import IntegrationRepository
from app.services.api_gateway import ApiGatewayService
from app.schemas.integration import GatewayAnalyticsSummary

router = APIRouter()
gateway_service = ApiGatewayService()


@router.get("/summary", response_model=GatewayAnalyticsSummary)
async def get_gateway_analytics_summary():
    """Returns aggregated API Gateway and Integration platform metrics."""
    return gateway_service.get_analytics_summary()


@router.get("/metrics")
async def get_traffic_metrics():
    """Returns time-series traffic throughput metrics."""
    return {
        "time_series": [
            {"timestamp": "10:00", "requests": 1200, "errors": 4, "latency_ms": 12.1},
            {"timestamp": "10:05", "requests": 1450, "errors": 2, "latency_ms": 14.5},
            {"timestamp": "10:10", "requests": 1890, "errors": 8, "latency_ms": 18.2},
            {"timestamp": "10:15", "requests": 2100, "errors": 5, "latency_ms": 15.0},
            {"timestamp": "10:20", "requests": 1750, "errors": 3, "latency_ms": 13.8},
        ],
        "top_endpoints": [
            {"path": "/v1/erp/sync", "calls": 4500, "avg_latency_ms": 22.4},
            {"path": "/v1/crm/contacts", "calls": 3200, "avg_latency_ms": 11.2},
            {"path": "/v2/analytics/reports", "calls": 1800, "avg_latency_ms": 48.0},
        ],
    }


@router.get("/audit-logs")
async def get_integration_audit_logs(db: AsyncSession = Depends(get_db)):
    """List integration admin security audit logs."""
    repo = IntegrationRepository(db)
    return await repo.list_audit_logs()
