"""Manufacturing Routing API Endpoints."""

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
    require_permission,
)
from app.modules.manufacturing.repositories.routing_repository import RoutingRepository
from app.modules.manufacturing.schemas.routing import (
    RoutingCreate,
    RoutingOperationCreate,
    RoutingOperationRead,
    RoutingRead,
)
from app.modules.manufacturing.services.routing_service import RoutingService

router = APIRouter(tags=["Manufacturing - Routings"])


class RoutingListResponse(BaseModel):
    items: list[RoutingRead]
    total: int
    page: int
    page_size: int


@router.get(
    "/routings",
    response_model=RoutingListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ROUTINGS_READ.value))],
)
async def list_routings(
    product_id: uuid.UUID | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> RoutingListResponse:
    repo = RoutingRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_routings(
        tenant_id, org_id, product_id=product_id, offset=offset, limit=page_size
    )
    return RoutingListResponse(
        items=[RoutingRead.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/routings",
    response_model=RoutingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ROUTINGS_WRITE.value))],
)
async def create_routing(
    data: RoutingCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> RoutingRead:
    service = RoutingService(db)
    routing = await service.create_routing(tenant_id, org_id, data)
    return RoutingRead.model_validate(routing)


@router.get(
    "/routings/{routing_id}",
    response_model=RoutingRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ROUTINGS_READ.value))],
)
async def get_routing(
    routing_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> RoutingRead:
    repo = RoutingRepository(db)
    routing = await repo.get_routing_by_id(routing_id, tenant_id, org_id)
    if not routing:
        raise NotFoundException(f"Routing {routing_id} not found.")
    return RoutingRead.model_validate(routing)


@router.post(
    "/routing-operations",
    response_model=RoutingOperationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_ROUTINGS_WRITE.value))],
)
async def create_routing_operation(
    data: RoutingOperationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> RoutingOperationRead:
    service = RoutingService(db)
    op = await service.add_operation(tenant_id, org_id, data)
    return RoutingOperationRead.model_validate(op)

