"""Quality Inspections API Endpoints."""

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
from app.modules.manufacturing.repositories.quality_repository import QualityRepository
from app.modules.manufacturing.schemas.quality import QualityInspectionCreate, QualityInspectionRead
from app.modules.manufacturing.services.quality_service import QualityService

router = APIRouter(tags=["Manufacturing - Quality Control"])


class QualityInspectionListResponse(BaseModel):
    items: list[QualityInspectionRead]
    total: int
    page: int
    page_size: int


@router.get(
    "/quality/inspections",
    response_model=QualityInspectionListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_QUALITY_READ.value))],
)
@router.get(
    "/quality-inspections",
    response_model=QualityInspectionListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_QUALITY_READ.value))],
)
async def list_quality_inspections(
    production_order_id: uuid.UUID | None = None,
    result: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> QualityInspectionListResponse:
    repo = QualityRepository(db)
    offset = (page - 1) * page_size
    items, total = await repo.list_inspections(
        tenant_id,
        org_id,
        production_order_id=production_order_id,
        result=result,
        offset=offset,
        limit=page_size,
    )
    return QualityInspectionListResponse(
        items=[QualityInspectionRead.model_validate(q) for q in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/quality/inspections",
    response_model=QualityInspectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_QUALITY_WRITE.value))],
)
@router.post(
    "/quality-inspections",
    response_model=QualityInspectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_QUALITY_WRITE.value))],
)
async def create_quality_inspection(
    data: QualityInspectionCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> QualityInspectionRead:
    service = QualityService(db)
    inspection = await service.create_inspection(tenant_id, org_id, data, inspector_id=user_id)
    return QualityInspectionRead.model_validate(inspection)


@router.get(
    "/quality/inspections/{inspection_id}",
    response_model=QualityInspectionRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_QUALITY_READ.value))],
)
@router.get(
    "/quality-inspections/{inspection_id}",
    response_model=QualityInspectionRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.MANUFACTURING_QUALITY_READ.value))],
)
async def get_quality_inspection(
    inspection_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> QualityInspectionRead:
    repo = QualityRepository(db)
    insp = await repo.get_inspection_by_id(inspection_id, tenant_id, org_id)
    if not insp:
        raise NotFoundException(f"Quality Inspection {inspection_id} not found.")
    return QualityInspectionRead.model_validate(insp)
