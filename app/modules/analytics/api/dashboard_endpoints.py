"""Analytics Dashboards API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.analytics.schemas.dashboard import (
    DashboardCreate,
    DashboardResponse,
)
from app.modules.analytics.services.dashboard_service import DashboardService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(tags=["Analytics - Dashboards"])


class DashboardListResponse(BaseModel):
    items: list[DashboardResponse]
    total: int


@router.get(
    "/dashboards",
    response_model=DashboardListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_DASHBOARDS_READ.value))],
)
async def list_dashboards(
    category: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> DashboardListResponse:
    """List available dashboards."""
    service = DashboardService(db)
    items = await service.list_dashboards(tenant_id, org_id, category=category)
    return DashboardListResponse(
        items=[DashboardResponse.model_validate(d) for d in items],
        total=len(items),
    )


@router.get(
    "/dashboards/{code}",
    response_model=DashboardResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_DASHBOARDS_READ.value))],
)
async def get_dashboard(
    code: str,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """Fetch single dashboard with widgets."""
    service = DashboardService(db)
    dash = await service.get_dashboard_by_code(tenant_id, org_id, code.upper())
    if not dash:
        raise NotFoundException(f"Dashboard '{code}' not found.")
    return DashboardResponse.model_validate(dash)


@router.post(
    "/dashboards",
    response_model=DashboardResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.ANALYTICS_DASHBOARDS_MANAGE.value))],
)
async def create_dashboard(
    data: DashboardCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """Create a new custom dashboard."""
    service = DashboardService(db)
    dash = await service.create_dashboard(tenant_id, org_id, data, user_id=user_id)
    return DashboardResponse.model_validate(dash)
