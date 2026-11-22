"""Warehouse and Locations API Endpoints."""

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
from app.modules.inventory.models.warehouse import Location, Warehouse
from app.modules.inventory.repositories.warehouse_repository import (
    LocationRepository,
    WarehouseRepository,
)
from app.modules.inventory.schemas.warehouse import (
    LocationCreate,
    LocationResponse,
    WarehouseCreate,
    WarehouseListResponse,
    WarehouseResponse,
)

router = APIRouter(prefix="/inventory/warehouses", tags=["Inventory - Warehouses & Locations"])


@router.get(
    "/",
    response_model=WarehouseListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_WAREHOUSES_READ.value))],
)
async def list_warehouses(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WarehouseListResponse:
    repo = WarehouseRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_by_org(tenant_id, org_id)
    return WarehouseListResponse(
        items=[WarehouseResponse.model_validate(w) for w in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=WarehouseResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_WAREHOUSES_WRITE.value))],
)
async def create_warehouse(
    data: WarehouseCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WarehouseResponse:
    repo = WarehouseRepository(db)
    wh = Warehouse(
        tenant_id=tenant_id,
        organization_id=org_id,
        branch_id=data.branch_id,
        code=data.code.upper(),
        name=data.name,
        warehouse_type=data.warehouse_type,
        address=data.address,
        manager_id=data.manager_id,
        is_primary=data.is_primary,
        is_active=data.is_active,
    )
    await repo.create(wh)
    fresh_wh = await repo.get_by_id(wh.id, tenant_id, org_id)
    return WarehouseResponse.model_validate(fresh_wh)


@router.get(
    "/{warehouse_id}",
    response_model=WarehouseResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_WAREHOUSES_READ.value))],
)
async def get_warehouse(
    warehouse_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WarehouseResponse:
    repo = WarehouseRepository(db)
    wh = await repo.get_by_id(warehouse_id, tenant_id, org_id)
    if not wh:
        raise NotFoundException(f"Warehouse {warehouse_id} not found.")
    return WarehouseResponse.model_validate(wh)


@router.post(
    "/{warehouse_id}/locations",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_LOCATIONS_MANAGE.value))],
)
async def create_location(
    warehouse_id: uuid.UUID,
    data: LocationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    wh_repo = WarehouseRepository(db)
    wh = await wh_repo.get_by_id(warehouse_id, tenant_id, org_id)
    if not wh:
        raise NotFoundException(f"Warehouse {warehouse_id} not found.")

    loc_repo = LocationRepository(db)
    loc = Location(
        tenant_id=tenant_id,
        organization_id=org_id,
        warehouse_id=warehouse_id,
        code=data.code.upper(),
        name=data.name,
        aisle=data.aisle,
        rack=data.rack,
        shelf=data.shelf,
        bin=data.bin,
        location_type=data.location_type,
        max_weight=data.max_weight,
        max_volume=data.max_volume,
        is_active=data.is_active,
    )
    await loc_repo.create(loc)
    return LocationResponse.model_validate(loc)


@router.get(
    "/{warehouse_id}/locations",
    response_model=list[LocationResponse],
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_WAREHOUSES_READ.value))],
)
async def list_locations(
    warehouse_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[LocationResponse]:
    loc_repo = LocationRepository(db)
    items = await loc_repo.list_by_warehouse(warehouse_id, tenant_id, org_id)
    return [LocationResponse.model_validate(loc) for loc in items]
