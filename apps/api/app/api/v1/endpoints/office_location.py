import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.office_location import OfficeLocationRepository
from app.schemas.office_location import OfficeLocationCreate, OfficeLocationResponse, OfficeLocationUpdate
from app.services.office_location import OfficeLocationService

router = APIRouter()


def get_office_location_service(db: AsyncSession = Depends(get_db_session)) -> OfficeLocationService:
    return OfficeLocationService(OfficeLocationRepository(db))


@router.post("", response_model=OfficeLocationResponse, status_code=status.HTTP_201_CREATED)
async def create_office_location(
    data: OfficeLocationCreate,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: OfficeLocationService = Depends(get_office_location_service),
):
    return await service.create(data.model_dump())


@router.get("", response_model=list[OfficeLocationResponse])
async def list_office_locations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: OfficeLocationService = Depends(get_office_location_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=OfficeLocationResponse)
async def get_office_location(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: OfficeLocationService = Depends(get_office_location_service),
):
    item = await service.get(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Office location not found"
        )
    return item


@router.patch("/{id}", response_model=OfficeLocationResponse)
async def update_office_location(
    id: uuid.UUID,
    data: OfficeLocationUpdate,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: OfficeLocationService = Depends(get_office_location_service),
):
    item = await service.get(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Office location not found"
        )
    return await service.update(id, data.model_dump(exclude_unset=True))


@router.delete("/{id}", response_model=OfficeLocationResponse)
async def delete_office_location(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: OfficeLocationService = Depends(get_office_location_service),
):
    item = await service.delete(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Office location not found"
        )
    return item
