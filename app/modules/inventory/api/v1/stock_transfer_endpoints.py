"""Stock Transfer API Endpoints."""

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
from app.modules.inventory.repositories.stock_transfer_repository import StockTransferRepository
from app.modules.inventory.schemas.stock_transfer import (
    StockTransferCreate,
    StockTransferListResponse,
    StockTransferResponse,
)
from app.modules.inventory.services.stock_transfer_service import StockTransferService

router = APIRouter(prefix="/inventory/transfers", tags=["Inventory - Stock Transfers"])


@router.get(
    "/",
    response_model=StockTransferListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_READ.value))],
)
async def list_transfers(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockTransferListResponse:
    repo = StockTransferRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id, org_id, status=status_filter, offset=offset, limit=page_size
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter)
    return StockTransferListResponse(
        items=[StockTransferResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=StockTransferResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_WRITE.value))],
)
async def create_transfer(
    data: StockTransferCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockTransferResponse:
    service = StockTransferService(db)
    transfer = await service.create_transfer(tenant_id, org_id, data, created_by_id=current_user.id)
    return StockTransferResponse.model_validate(transfer)


@router.get(
    "/{transfer_id}",
    response_model=StockTransferResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_READ.value))],
)
async def get_transfer(
    transfer_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> StockTransferResponse:
    repo = StockTransferRepository(db)
    transfer = await repo.get_by_id(transfer_id, tenant_id, org_id)
    if not transfer:
        raise NotFoundException(f"Stock Transfer {transfer_id} not found.")
    return StockTransferResponse.model_validate(transfer)


@router.post(
    "/{transfer_id}/ship",
    response_model=StockTransferResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_EXECUTE.value))],
)
@router.post(
    "/{transfer_id}/dispatch",
    response_model=StockTransferResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_EXECUTE.value))],
)
async def ship_transfer(
    transfer_id: uuid.UUID,
    body: dict | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockTransferResponse:
    service = StockTransferService(db)
    transfer = await service.ship_transfer(transfer_id, tenant_id, org_id, user_id=current_user.id)
    return StockTransferResponse.model_validate(transfer)


@router.post(
    "/{transfer_id}/complete",
    response_model=StockTransferResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_EXECUTE.value))],
)
@router.post(
    "/{transfer_id}/receive",
    response_model=StockTransferResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_TRANSFERS_EXECUTE.value))],
)
async def complete_transfer(
    transfer_id: uuid.UUID,
    body: dict | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StockTransferResponse:
    service = StockTransferService(db)
    transfer = await service.complete_transfer(
        transfer_id, tenant_id, org_id, user_id=current_user.id
    )
    return StockTransferResponse.model_validate(transfer)
