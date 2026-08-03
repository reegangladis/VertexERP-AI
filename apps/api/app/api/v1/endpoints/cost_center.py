import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.cost_center import CostCenterRepository
from app.schemas.cost_center import CostCenterCreate, CostCenterResponse, CostCenterUpdate
from app.services.cost_center import CostCenterService

router = APIRouter()


def get_cost_center_service(db: AsyncSession = Depends(get_db_session)) -> CostCenterService:
    return CostCenterService(CostCenterRepository(db))


@router.post("", response_model=CostCenterResponse, status_code=status.HTTP_201_CREATED)
async def create_cost_center(
    data: CostCenterCreate,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: CostCenterService = Depends(get_cost_center_service),
):
    return await service.create_cost_center(data)


@router.get("", response_model=list[CostCenterResponse])
async def list_cost_centers(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: CostCenterService = Depends(get_cost_center_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=CostCenterResponse)
async def get_cost_center(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CostCenterService = Depends(get_cost_center_service),
):
    item = await service.get(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cost center not found"
        )
    return item


@router.patch("/{id}", response_model=CostCenterResponse)
async def update_cost_center(
    id: uuid.UUID,
    data: CostCenterUpdate,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: CostCenterService = Depends(get_cost_center_service),
):
    return await service.update_cost_center(id, data)


@router.delete("/{id}", response_model=CostCenterResponse)
async def delete_cost_center(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: CostCenterService = Depends(get_cost_center_service),
):
    item = await service.delete(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cost center not found"
        )
    return item
