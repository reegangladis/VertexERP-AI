import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.designation import DesignationRepository
from app.schemas.designation import DesignationCreate, DesignationResponse, DesignationUpdate
from app.services.designation import DesignationService

router = APIRouter()


def get_designation_service(db: AsyncSession = Depends(get_db_session)) -> DesignationService:
    return DesignationService(DesignationRepository(db))


@router.post("", response_model=DesignationResponse, status_code=status.HTTP_201_CREATED)
async def create_designation(
    data: DesignationCreate,
    current_user: User = Depends(PermissionChecker("designation.create")),
    service: DesignationService = Depends(get_designation_service),
):
    return await service.create_designation(data)


@router.get("", response_model=list[DesignationResponse])
async def list_designations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(PermissionChecker("designation.read")),
    service: DesignationService = Depends(get_designation_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=DesignationResponse)
async def get_designation(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("designation.read")),
    service: DesignationService = Depends(get_designation_service),
):
    item = await service.get(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found"
        )
    return item


@router.patch("/{id}", response_model=DesignationResponse)
async def update_designation(
    id: uuid.UUID,
    data: DesignationUpdate,
    current_user: User = Depends(PermissionChecker("designation.update")),
    service: DesignationService = Depends(get_designation_service),
):
    return await service.update_designation(id, data)


@router.delete("/{id}", response_model=DesignationResponse)
async def delete_designation(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("designation.delete")),
    service: DesignationService = Depends(get_designation_service),
):
    item = await service.delete(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Designation not found"
        )
    return item
