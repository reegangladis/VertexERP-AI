"""Analytics Charting and Aggregation Endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.analytics.schemas.aggregation import AnalyticsFilterParams, ChartDatasetResponse
from app.modules.analytics.services.aggregation_service import AggregationService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(tags=["Analytics - Chart Datasets"])


@router.post(
    "/charts/financial-trend",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_FINANCE_READ.value))],
)
async def get_financial_trend_chart(
    params: AnalyticsFilterParams,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ChartDatasetResponse:
    """Revenue vs Expenses time-series chart dataset."""
    service = AggregationService(db)
    return await service.get_financial_trend(tenant_id, org_id, params)


@router.post(
    "/charts/sales-pipeline",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_SALES_READ.value))],
)
@router.post(
    "/charts/sales-pipeline-distribution",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,

    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_SALES_READ.value))],
)
async def get_sales_pipeline_chart(
    params: AnalyticsFilterParams,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ChartDatasetResponse:
    """Sales opportunity stage breakdown chart dataset."""
    service = AggregationService(db)
    return await service.get_sales_pipeline_distribution(tenant_id, org_id, params)


@router.get(
    "/charts/inventory-warehouses",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_INVENTORY_READ.value))],
)
@router.get(
    "/charts/inventory-by-warehouse",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,

    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_INVENTORY_READ.value))],
)
async def get_inventory_warehouses_chart(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ChartDatasetResponse:
    """Inventory valuation by warehouse chart dataset."""
    service = AggregationService(db)
    return await service.get_inventory_warehouse_breakdown(tenant_id, org_id)


@router.post(
    "/charts/manufacturing-trend",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_MFG_READ.value))],
)
@router.post(
    "/charts/mfg-fpy-trend",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,

    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_MFG_READ.value))],
)
async def get_manufacturing_trend_chart(
    params: AnalyticsFilterParams,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ChartDatasetResponse:
    """Manufacturing output and scrap loss trend chart dataset."""
    service = AggregationService(db)
    return await service.get_manufacturing_output_trend(tenant_id, org_id, params)


@router.get(
    "/charts/hr-headcount",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_HR_READ.value))],
)
@router.get(
    "/charts/hr-headcount-by-dept",
    response_model=ChartDatasetResponse,
    status_code=status.HTTP_200_OK,

    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_HR_READ.value))],
)
async def get_hr_headcount_chart(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ChartDatasetResponse:
    """Headcount distribution by department chart dataset."""
    service = AggregationService(db)
    return await service.get_hr_department_headcount(tenant_id, org_id)
