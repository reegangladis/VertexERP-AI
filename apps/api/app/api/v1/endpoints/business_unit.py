import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.business_unit import BusinessUnitRepository
from app.schemas.business_unit import (
    BusinessUnitCreate,
    BusinessUnitResponse,
    BusinessUnitTreeNode,
    BusinessUnitUpdate,
)
from app.services.business_unit import BusinessUnitService

router = APIRouter()


def get_business_unit_service(db: AsyncSession = Depends(get_db_session)) -> BusinessUnitService:
    return BusinessUnitService(BusinessUnitRepository(db))


@router.post("", response_model=BusinessUnitResponse, status_code=status.HTTP_201_CREATED)
async def create_business_unit(
    data: BusinessUnitCreate,
    current_user: User = Depends(PermissionChecker("business_unit.manage")),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    return await service.create_business_unit(data)


@router.get("", response_model=list[BusinessUnitResponse])
async def list_business_units(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("business_unit.read")),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/tree", response_model=list[BusinessUnitTreeNode])
async def get_business_unit_tree(
    org_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("business_unit.read")),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    target_org_id = org_id or current_user.organization_id
    if not target_org_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Organization ID required"
        )
    return await service.get_business_unit_tree(target_org_id)


@router.get("/{id}", response_model=BusinessUnitResponse)
async def get_business_unit(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("business_unit.read")),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    item = await service.get(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business unit not found"
        )
    return item


@router.patch("/{id}", response_model=BusinessUnitResponse)
async def update_business_unit(
    id: uuid.UUID,
    data: BusinessUnitUpdate,
    current_user: User = Depends(PermissionChecker("business_unit.manage")),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    return await service.update_business_unit(id, data)


@router.delete("/{id}", response_model=BusinessUnitResponse)
async def delete_business_unit(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("business_unit.manage")),
    service: BusinessUnitService = Depends(get_business_unit_service),
):
    item = await service.delete(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business unit not found"
        )
    return item
