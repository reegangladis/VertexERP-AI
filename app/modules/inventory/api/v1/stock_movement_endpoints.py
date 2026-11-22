"""Stock Movement (Immutable Audit Ledger) API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)
from app.modules.inventory.repositories.stock_movement_repository import StockMovementRepository
from app.modules.inventory.schemas.stock_movement import (
    StockMovementListResponse,
    StockMovementResponse,
)

router = APIRouter(tags=["Inventory - Stock Movements Ledger"])


@router.get(
    "/inventory/movements",
    response_model=StockMovementListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_MOVEMENTS_READ.value))],
)
@router.get(
    "/inventory/movements/",
    response_model=StockMovementListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_MOVEMENTS_READ.value))],
)
@router.get(
    "/inventory/ledger/movements",
    response_model=StockMovementListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_MOVEMENTS_READ.value))],
)
@router.get(
    "/inventory/ledger/movements/",
    response_model=StockMovementListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_MOVEMENTS_READ.value))],
)
async def list_movements(
    movement_type: str | None = None,
    warehouse_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockMovementListResponse:
    repo = StockMovementRepository(db)
    offset = (page - 1) * page_size
    if product_id:
        items = await repo.list_by_product(
            tenant_id, org_id, product_id, warehouse_id=warehouse_id, offset=offset, limit=page_size
        )
    else:
        items = await repo.list_by_org(
            tenant_id,
            org_id,
            movement_type=movement_type,
            warehouse_id=warehouse_id,
            offset=offset,
            limit=page_size,
        )
    total = await repo.count_by_org(
        tenant_id, org_id, movement_type=movement_type, warehouse_id=warehouse_id
    )
    return StockMovementListResponse(
        items=[StockMovementResponse.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )
