"""Purchase Orders API Endpoints."""

import uuid

from fastapi import APIRouter, Body, Depends, Query, status
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
from app.modules.procurement.repositories.purchase_order_repository import PurchaseOrderRepository
from app.modules.procurement.schemas.purchase_order import (
    PurchaseOrderCancel,
    PurchaseOrderCreate,
    PurchaseOrderListResponse,
    PurchaseOrderResponse,
)
from app.modules.procurement.services.procurement_service import ProcurementService

router = APIRouter(tags=["Procurement - Purchase Orders"])


@router.get(
    "/procurement/purchase-orders",
    response_model=PurchaseOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_READ.value))],
)
@router.get(
    "/procurement/purchase-orders/",
    response_model=PurchaseOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_READ.value))],
)
@router.get(
    "/procurement/orders",
    response_model=PurchaseOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_READ.value))],
)
@router.get(
    "/procurement/orders/",
    response_model=PurchaseOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_READ.value))],
)
async def list_purchase_orders(
    status_filter: str | None = Query(None, alias="status"),
    supplier_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderListResponse:
    repo = PurchaseOrderRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id,
        org_id,
        status=status_filter,
        supplier_id=supplier_id,
        offset=offset,
        limit=page_size,
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter)
    return PurchaseOrderListResponse(
        items=[PurchaseOrderResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/procurement/purchase-orders",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_WRITE.value))],
)
@router.post(
    "/procurement/purchase-orders/",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_WRITE.value))],
)
@router.post(
    "/procurement/orders",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_WRITE.value))],
)
@router.post(
    "/procurement/orders/",
    response_model=PurchaseOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_WRITE.value))],
)
async def create_purchase_order(
    data: PurchaseOrderCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderResponse:
    service = ProcurementService(db)
    po = await service.create_purchase_order(tenant_id, org_id, data)
    return PurchaseOrderResponse.model_validate(po)


@router.get(
    "/procurement/purchase-orders/{po_id}",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_READ.value))],
)
@router.get(
    "/procurement/orders/{po_id}",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_READ.value))],
)
async def get_purchase_order(
    po_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderResponse:
    repo = PurchaseOrderRepository(db)
    po = await repo.get_by_id(po_id, tenant_id, org_id)
    if not po:
        raise NotFoundException(f"Purchase Order {po_id} not found.")
    return PurchaseOrderResponse.model_validate(po)


@router.post(
    "/procurement/purchase-orders/{po_id}/approve",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_APPROVE.value))],
)
@router.post(
    "/procurement/purchase-orders/{po_id}/confirm",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_APPROVE.value))],
)
@router.post(
    "/procurement/orders/{po_id}/approve",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_APPROVE.value))],
)
@router.post(
    "/procurement/orders/{po_id}/confirm",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_APPROVE.value))],
)
async def approve_purchase_order(
    po_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderResponse:
    service = ProcurementService(db)
    po = await service.approve_purchase_order(
        po_id, tenant_id, org_id, approved_by_id=current_user.id
    )
    return PurchaseOrderResponse.model_validate(po)


@router.post(
    "/procurement/purchase-orders/{po_id}/send",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_SEND.value))],
)
@router.post(
    "/procurement/purchase-orders/{po_id}/issue",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_SEND.value))],
)
@router.post(
    "/procurement/orders/{po_id}/send",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_SEND.value))],
)
@router.post(
    "/procurement/orders/{po_id}/issue",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_SEND.value))],
)
async def send_purchase_order(
    po_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderResponse:
    service = ProcurementService(db)
    po = await service.send_purchase_order(po_id, tenant_id, org_id)
    return PurchaseOrderResponse.model_validate(po)


@router.post(
    "/procurement/purchase-orders/{po_id}/cancel",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_WRITE.value))],
)
@router.post(
    "/procurement/orders/{po_id}/cancel",
    response_model=PurchaseOrderResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_ORDERS_WRITE.value))],
)
async def cancel_purchase_order(
    po_id: uuid.UUID,
    data: PurchaseOrderCancel | None = Body(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> PurchaseOrderResponse:
    service = ProcurementService(db)
    reason = data.reason if data and data.reason else ""
    po = await service.cancel_purchase_order(po_id, tenant_id, org_id, reason=reason)
    return PurchaseOrderResponse.model_validate(po)
