"""Material Requirements Planning (MRP) API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)
from app.modules.manufacturing.repositories.mrp_repository import MRPRepository
from app.modules.manufacturing.schemas.mrp import MRPRunRead, MRPRunTrigger
from app.modules.manufacturing.services.mrp_service import MRPService

router = APIRouter(tags=["Manufacturing - MRP Planning Engine"])


class MRPRunListResponse(BaseModel):
    items: list[MRPRunRead]
    total: int
    page: int
    page_size: int


@router.get(
    "/mrp/runs",
    response_model=MRPRunListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_MRP_RUN.value))],
)
async def list_mrp_runs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MRPRunListResponse:
    repo = MRPRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_runs(tenant_id, org_id, offset=offset, limit=page_size)
    return MRPRunListResponse(
        items=[MRPRunRead.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/mrp/runs/trigger",
    response_model=MRPRunRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_MRP_RUN.value))],
)
@router.post(
    "/mrp/runs",
    response_model=MRPRunRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_MRP_RUN.value))],
)
async def trigger_mrp_run(
    data: MRPRunTrigger,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MRPRunRead:
    service = MRPService(db)
    run = await service.run_mrp(tenant_id, org_id, planning_horizon_days=data.planning_horizon_days)
    return MRPRunRead.model_validate(run)


@router.get(
    "/mrp/runs/{run_id}",
    response_model=MRPRunRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_MRP_RUN.value))],
)
async def get_mrp_run(
    run_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> MRPRunRead:
    repo = MRPRepository(db)
    run = await repo.get_run_by_id(run_id, tenant_id, org_id)
    if not run:
        raise NotFoundException(f"MRP Run {run_id} not found.")
    return MRPRunRead.model_validate(run)


@router.post(
    "/mrp/planned-orders/{planned_order_id}/convert",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_MRP_RUN.value))],
)
async def convert_mrp_planned_order(
    planned_order_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = MRPService(db)
    return await service.convert_planned_order(planned_order_id, tenant_id, org_id, user_id=user_id)
