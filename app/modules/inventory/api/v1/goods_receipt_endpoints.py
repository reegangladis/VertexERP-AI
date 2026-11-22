"""Goods Receipts (GRN) API Endpoints."""

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
from app.modules.inventory.repositories.goods_receipt_repository import GoodsReceiptRepository
from app.modules.inventory.schemas.goods_receipt import (
    GoodsReceiptCreate,
    GoodsReceiptListResponse,
    GoodsReceiptResponse,
)
from app.modules.inventory.services.goods_receipt_service import GoodsReceiptService

router = APIRouter(prefix="/inventory/receipts", tags=["Inventory - Goods Receipts"])


@router.get(
    "/",
    response_model=GoodsReceiptListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_RECEIPTS_READ.value))],
)
async def list_receipts(
    status_filter: str | None = Query(None, alias="status"),
    supplier_id: uuid.UUID | None = None,
    purchase_order_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> GoodsReceiptListResponse:
    repo = GoodsReceiptRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        status=status_filter,
        supplier_id=supplier_id,
        purchase_order_id=purchase_order_id,
        offset=offset,
        limit=page_size,
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter)
    return GoodsReceiptListResponse(
        items=[GoodsReceiptResponse.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=GoodsReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_RECEIPTS_WRITE.value))],
)
async def create_receipt(
    data: GoodsReceiptCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoodsReceiptResponse:
    service = GoodsReceiptService(db)
    gr = await service.create_goods_receipt(tenant_id, org_id, data, received_by_id=current_user.id)
    return GoodsReceiptResponse.model_validate(gr)


@router.get(
    "/{receipt_id}",
    response_model=GoodsReceiptResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_RECEIPTS_READ.value))],
)
async def get_receipt(
    receipt_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> GoodsReceiptResponse:
    repo = GoodsReceiptRepository(db)
    gr = await repo.get_by_id(receipt_id, tenant_id, org_id)
    if not gr:
        raise NotFoundException(f"Goods Receipt {receipt_id} not found.")
    return GoodsReceiptResponse.model_validate(gr)


@router.post(
    "/{receipt_id}/post",
    response_model=GoodsReceiptResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_RECEIPTS_POST.value))],
)
async def post_receipt(
    receipt_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoodsReceiptResponse:
    service = GoodsReceiptService(db)
    gr = await service.post_goods_receipt(
        receipt_id, tenant_id, org_id, posted_by_id=current_user.id
    )
    return GoodsReceiptResponse.model_validate(gr)
