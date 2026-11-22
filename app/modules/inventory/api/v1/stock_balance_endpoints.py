"""Stock Balances and Real-Time Valuation API Endpoints."""

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
from app.modules.inventory.repositories.stock_balance_repository import StockBalanceRepository
from app.modules.inventory.schemas.stock_balance import (
    StockBalanceListResponse,
    StockBalanceResponse,
    StockValuationSummary,
)

router = APIRouter(tags=["Inventory - Stock Balances"])


@router.get(
    "/inventory/balances",
    response_model=StockBalanceListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
@router.get(
    "/inventory/balances/",
    response_model=StockBalanceListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
@router.get(
    "/inventory/ledger/balances",
    response_model=StockBalanceListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
@router.get(
    "/inventory/ledger/balances/",
    response_model=StockBalanceListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def list_stock_balances(
    product_id: uuid.UUID | None = None,
    warehouse_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockBalanceListResponse:
    repo = StockBalanceRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        product_id=product_id,
        warehouse_id=warehouse_id,
        offset=offset,
        limit=page_size,
    )
    # Total count approximation / valuation
    val_data = await repo.get_total_valuation(tenant_id, org_id, warehouse_id=warehouse_id)
    return StockBalanceListResponse(
        items=[StockBalanceResponse.model_validate(b) for b in items],
        total=val_data["total_items"],
        page=page,
        page_size=page_size,
    )


@router.get(
    "/inventory/balances/valuation",
    response_model=StockValuationSummary,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def get_valuation_summary(
    warehouse_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockValuationSummary:
    repo = StockBalanceRepository(db)
    summary = await repo.get_total_valuation(tenant_id, org_id, warehouse_id=warehouse_id)
    return StockValuationSummary(
        total_items=summary["total_items"],
        total_quantity_on_hand=summary["total_quantity_on_hand"],
        total_valuation=summary["total_valuation"],
    )
