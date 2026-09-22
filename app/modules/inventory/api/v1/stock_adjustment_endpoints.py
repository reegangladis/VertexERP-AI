"""Stock Adjustments API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User
from app.modules.inventory.repositories.stock_adjustment_repository import StockAdjustmentRepository
from app.modules.inventory.schemas.stock_adjustment import (
    StockAdjustmentCreate,
    StockAdjustmentListResponse,
    StockAdjustmentResponse,
)
from app.modules.inventory.services.stock_adjustment_service import StockAdjustmentService

router = APIRouter(prefix="/inventory/adjustments", tags=["Inventory - Stock Adjustments"])


@router.get(
    "/",
    response_model=StockAdjustmentListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_READ.value))],
)
async def list_adjustments(
    status_filter: str | None = Query(None, alias="status"),
    warehouse_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentListResponse:
    repo = StockAdjustmentRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        status=status_filter,
        warehouse_id=warehouse_id,
        offset=offset,
        limit=page_size,
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter)
    return StockAdjustmentListResponse(
        items=[StockAdjustmentResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=StockAdjustmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_WRITE.value))],
)
async def create_adjustment(
    data: StockAdjustmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentResponse:
    service = StockAdjustmentService(db)
    adj = await service.create_adjustment(tenant_id, org_id, data, requested_by_id=current_user.id)
    return StockAdjustmentResponse.model_validate(adj)


@router.get(
    "/{adjustment_id}",
    response_model=StockAdjustmentResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_READ.value))],
)
async def get_adjustment(
    adjustment_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentResponse:
    repo = StockAdjustmentRepository(db)
    adj = await repo.get_by_id(adjustment_id, tenant_id, org_id)
    if not adj:
        raise NotFoundException(f"Stock Adjustment {adjustment_id} not found.")
    return StockAdjustmentResponse.model_validate(adj)


@router.post(
    "/{adjustment_id}/submit",
    response_model=StockAdjustmentResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_WRITE.value))],
)
async def submit_adjustment(
    adjustment_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentResponse:
    service = StockAdjustmentService(db)
    adj = await service.submit_adjustment(adjustment_id, tenant_id, org_id)
    return StockAdjustmentResponse.model_validate(adj)


@router.post(
    "/{adjustment_id}/approve",
    response_model=StockAdjustmentResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_APPROVE.value))],
)
async def approve_adjustment(
    adjustment_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentResponse:
    service = StockAdjustmentService(db)
    adj = await service.approve_adjustment(
        adjustment_id, tenant_id, org_id, approved_by_id=current_user.id
    )
    return StockAdjustmentResponse.model_validate(adj)


@router.post(
    "/{adjustment_id}/reject",
    response_model=StockAdjustmentResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_APPROVE.value))],
)
async def reject_adjustment(
    adjustment_id: uuid.UUID,
    body: dict | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentResponse:
    reason = body.get("reason") if body else None
    service = StockAdjustmentService(db)
    adj = await service.reject_adjustment(
        adjustment_id, tenant_id, org_id, rejected_by_id=current_user.id, reason=reason
    )
    return StockAdjustmentResponse.model_validate(adj)


@router.post(
    "/{adjustment_id}/post",
    response_model=StockAdjustmentResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_ADJUSTMENTS_POST.value))],
)
async def post_adjustment(
    adjustment_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockAdjustmentResponse:
    service = StockAdjustmentService(db)
    adj = await service.post_adjustment(
        adjustment_id, tenant_id, org_id, posted_by_id=current_user.id
    )
    return StockAdjustmentResponse.model_validate(adj)
