"""Production Orders and Shop-Floor Work Orders API Endpoints."""

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
from app.modules.manufacturing.repositories.production_order_repository import (
    ProductionOrderRepository,
)
from app.modules.manufacturing.schemas.production_order import (
    MaterialConsumptionCreate,
    MaterialConsumptionRead,
    ProductionOrderCreate,
    ProductionOrderRead,
    ProductionOutputCreate,
    ProductionOutputRead,
    ProductionScrapCreate,
    ProductionScrapRead,
    WorkOrderRead,
    WorkOrderUpdateStatus,
)
from app.modules.manufacturing.services.production_service import ProductionService

router = APIRouter(tags=["Manufacturing - Production & Work Orders"])


class ProductionOrderListResponse(BaseModel):
    items: list[ProductionOrderRead]
    total: int
    page: int
    page_size: int


class WorkOrderListResponse(BaseModel):
    items: list[WorkOrderRead]
    total: int
    page: int
    page_size: int


@router.get(
    "/orders",
    response_model=ProductionOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_READ.value))],
)
@router.get(
    "/production-orders",
    response_model=ProductionOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_READ.value))],
)
async def list_production_orders(
    product_id: uuid.UUID | None = None,
    order_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderListResponse:
    repo = ProductionOrderRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_orders(
        tenant_id,
        org_id,
        product_id=product_id,
        status=order_status,
        offset=offset,
        limit=page_size,
    )
    return ProductionOrderListResponse(
        items=[ProductionOrderRead.model_validate(o) for o in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/orders",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_WRITE.value))],
)
@router.post(
    "/production-orders",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_WRITE.value))],
)
async def create_production_order(
    data: ProductionOrderCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderRead:
    service = ProductionService(db)
    order = await service.create_production_order(tenant_id, org_id, data, created_by_id=user_id)
    return ProductionOrderRead.model_validate(order)


@router.get(
    "/orders/{order_id}",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_READ.value))],
)
@router.get(
    "/production-orders/{order_id}",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_READ.value))],
)
async def get_production_order(
    order_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderRead:
    repo = ProductionOrderRepository(db)
    order = await repo.get_order_by_id(order_id, tenant_id, org_id)
    if not order:
        raise NotFoundException(f"Production Order {order_id} not found.")
    return ProductionOrderRead.model_validate(order)


@router.post(
    "/orders/{order_id}/confirm",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_WRITE.value))],
)
@router.post(
    "/production-orders/{order_id}/confirm",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_WRITE.value))],
)
async def confirm_production_order(
    order_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderRead:
    service = ProductionService(db)
    order = await service.confirm_production_order(order_id, tenant_id, org_id)
    return ProductionOrderRead.model_validate(order)


@router.post(
    "/orders/{order_id}/start",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/start",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
async def start_production_order(
    order_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderRead:
    service = ProductionService(db)
    order = await service.start_production_order(order_id, tenant_id, org_id)
    return ProductionOrderRead.model_validate(order)


@router.post(
    "/orders/{order_id}/complete",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/complete",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
async def complete_production_order(
    order_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderRead:
    service = ProductionService(db)
    order = await service.complete_production_order(order_id, tenant_id, org_id)
    return ProductionOrderRead.model_validate(order)


@router.post(
    "/orders/{order_id}/cancel",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_WRITE.value))],
)
@router.post(
    "/production-orders/{order_id}/cancel",
    response_model=ProductionOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_WRITE.value))],
)
async def cancel_production_order(
    order_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOrderRead:
    service = ProductionService(db)
    order = await service.cancel_production_order(order_id, tenant_id, org_id)
    return ProductionOrderRead.model_validate(order)


@router.post(
    "/orders/{order_id}/consume",
    response_model=MaterialConsumptionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/orders/{order_id}/consume-materials",
    response_model=MaterialConsumptionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/consume",
    response_model=MaterialConsumptionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/consume-materials",
    response_model=MaterialConsumptionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
async def consume_material(
    order_id: uuid.UUID,
    data: MaterialConsumptionCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> MaterialConsumptionRead:
    service = ProductionService(db)
    cons = await service.record_material_consumption(
        order_id, tenant_id, org_id, data, consumed_by_id=user_id
    )
    return MaterialConsumptionRead.model_validate(cons)


@router.post(
    "/orders/{order_id}/produce",
    response_model=ProductionOutputRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/orders/{order_id}/record-output",
    response_model=ProductionOutputRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/produce",
    response_model=ProductionOutputRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/record-output",
    response_model=ProductionOutputRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
async def produce_output(
    order_id: uuid.UUID,
    data: ProductionOutputCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionOutputRead:
    service = ProductionService(db)
    output = await service.record_production_output(
        order_id, tenant_id, org_id, data, created_by_id=user_id
    )
    return ProductionOutputRead.model_validate(output)


@router.post(
    "/orders/{order_id}/scrap",
    response_model=ProductionScrapRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/orders/{order_id}/record-scrap",
    response_model=ProductionScrapRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/scrap",
    response_model=ProductionScrapRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
@router.post(
    "/production-orders/{order_id}/record-scrap",
    response_model=ProductionScrapRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
async def record_scrap(
    order_id: uuid.UUID,
    data: ProductionScrapCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> ProductionScrapRead:
    service = ProductionService(db)
    scrap = await service.record_production_scrap(
        order_id, tenant_id, org_id, data, recorded_by_id=user_id
    )
    return ProductionScrapRead.model_validate(scrap)


@router.get(
    "/work-orders",
    response_model=WorkOrderListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_READ.value))],
)
async def list_work_orders(
    production_order_id: uuid.UUID | None = None,
    work_center_id: uuid.UUID | None = None,
    wo_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkOrderListResponse:
    repo = ProductionOrderRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_work_orders(
        tenant_id,
        org_id,
        production_order_id=production_order_id,
        work_center_id=work_center_id,
        status=wo_status,
        offset=offset,
        limit=page_size,
    )
    return WorkOrderListResponse(
        items=[WorkOrderRead.model_validate(w) for w in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/work-orders/{work_order_id}/status",
    response_model=WorkOrderRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ORDERS_EXECUTE.value))],
)
async def update_work_order_status(
    work_order_id: uuid.UUID,
    data: WorkOrderUpdateStatus,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkOrderRead:
    service = ProductionService(db)
    wo = await service.update_work_order_status(work_order_id, tenant_id, org_id, data)
    return WorkOrderRead.model_validate(wo)
