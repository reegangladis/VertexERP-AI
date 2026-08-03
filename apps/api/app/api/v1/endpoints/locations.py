import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.location import LocationRepository
from app.schemas.location import LocationCreate, LocationResponse, LocationUpdate
from app.services.location_service import LocationService

router = APIRouter()


def get_location_service(
    db: AsyncSession = Depends(get_db_session),
) -> LocationService:
    return LocationService(LocationRepository(db))


@router.post("", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    service: LocationService = Depends(get_location_service),
):
    return await service.create(data)


@router.get("", response_model=list[LocationResponse])
async def list_locations(
    organization_id: uuid.UUID | None = None,
    service: LocationService = Depends(get_location_service),
):
    if organization_id:
        return await service.get_by_org(organization_id)
    items, _ = await service.get_multi()
    return items


@router.get("/{id}", response_model=LocationResponse)
async def get_location(
    id: uuid.UUID,
    service: LocationService = Depends(get_location_service),
):
    loc = await service.get(id)
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return loc


@router.put("/{id}", response_model=LocationResponse)
async def update_location(
    id: uuid.UUID,
    data: LocationUpdate,
    service: LocationService = Depends(get_location_service),
):
    loc = await service.update(id, data)
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return loc


@router.delete("/{id}", response_model=LocationResponse)
async def delete_location(
    id: uuid.UUID,
    service: LocationService = Depends(get_location_service),
):
    loc = await service.delete(id)
    if not loc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Location not found"
        )
    return loc
