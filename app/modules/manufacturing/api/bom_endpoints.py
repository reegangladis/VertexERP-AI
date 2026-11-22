"""Bills of Materials (BOM) API Endpoints."""

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
from app.modules.manufacturing.repositories.bom_repository import BOMRepository
from app.modules.manufacturing.schemas.bom import (
    BillOfMaterialCreate,
    BillOfMaterialRead,
    BOMComponentCreate,
    BOMComponentRead,
    BOMVersionCreate,
    BOMVersionRead,
)
from app.modules.manufacturing.services.bom_service import BOMService

router = APIRouter(tags=["Manufacturing - Bills of Materials (BOM)"])


class BOMListResponse(BaseModel):
    items: list[BillOfMaterialRead]
    total: int
    page: int
    page_size: int


@router.get(
    "/boms",
    response_model=BOMListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_BOM_READ.value))],
)
async def list_boms(
    product_id: uuid.UUID | None = None,
    bom_status: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BOMListResponse:
    repo = BOMRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_boms(
        tenant_id, org_id, product_id=product_id, status=bom_status, offset=offset, limit=page_size
    )
    return BOMListResponse(
        items=[BillOfMaterialRead.model_validate(b) for b in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/boms",
    response_model=BillOfMaterialRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_BOM_WRITE.value))],
)
async def create_bom(
    data: BillOfMaterialCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BillOfMaterialRead:
    service = BOMService(db)
    bom = await service.create_bom(tenant_id, org_id, data)
    return BillOfMaterialRead.model_validate(bom)


@router.get(
    "/boms/{bom_id}",
    response_model=BillOfMaterialRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_BOM_READ.value))],
)
async def get_bom(
    bom_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BillOfMaterialRead:
    repo = BOMRepository(db)
    bom = await repo.get_bom_by_id(bom_id, tenant_id, org_id)
    if not bom:
        raise NotFoundException(f"BOM {bom_id} not found.")
    return BillOfMaterialRead.model_validate(bom)


@router.post(
    "/boms/{bom_id}/versions",
    response_model=BOMVersionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_BOM_WRITE.value))],
)
async def add_bom_version(
    bom_id: uuid.UUID,
    data: BOMVersionCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BOMVersionRead:
    service = BOMService(db)
    version = await service.add_version(bom_id, tenant_id, org_id, data)
    return BOMVersionRead.model_validate(version)


@router.get(
    "/bom-versions/{version_id}/theoretical-cost",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_BOM_READ.value))],
)
async def get_bom_theoretical_cost(
    version_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = BOMService(db)
    cost = await service.calculate_bom_theoretical_cost(version_id, tenant_id, org_id)
    return {"bom_version_id": str(version_id), "theoretical_cost": str(cost)}


@router.post(
    "/bom-versions/{version_id}/components",
    response_model=BOMComponentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_BOM_WRITE.value))],
)
async def add_bom_component(
    version_id: uuid.UUID,
    data: BOMComponentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BOMComponentRead:
    service = BOMService(db)
    component = await service.add_component_to_version(version_id, tenant_id, org_id, data)
    return BOMComponentRead.model_validate(component)

