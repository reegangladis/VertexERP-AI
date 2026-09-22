"""Units of Measure API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)
from app.modules.inventory.models.uom import UnitOfMeasure
from app.modules.inventory.repositories.uom_repository import UomRepository
from app.modules.inventory.schemas.uom import (
    UomCreate,
    UomListResponse,
    UomResponse,
)

router = APIRouter(prefix="/inventory/uom", tags=["Inventory - Units of Measure"])


@router.get(
    "/",
    response_model=UomListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def list_uom(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> UomListResponse:
    repo = UomRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_by_org(tenant_id, org_id)
    return UomListResponse(
        items=[UomResponse.model_validate(u) for u in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=UomResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_UOM_MANAGE.value))],
)
async def create_uom(
    data: UomCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> UomResponse:
    repo = UomRepository(db)
    uom = UnitOfMeasure(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code.upper(),
        name=data.name,
        category=data.category,
        is_base_unit=data.is_base_unit,
        conversion_factor=data.conversion_factor,
        base_unit_id=data.base_unit_id,
        is_active=data.is_active,
    )
    await repo.create(uom)
    return UomResponse.model_validate(uom)


@router.get(
    "/{uom_id}",
    response_model=UomResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def get_uom(
    uom_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> UomResponse:
    repo = UomRepository(db)
    uom = await repo.get_by_id(uom_id, tenant_id, org_id)
    if not uom:
        raise NotFoundException(f"Unit of Measure {uom_id} not found.")
    return UomResponse.model_validate(uom)
