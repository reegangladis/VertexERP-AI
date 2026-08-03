import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.reporting_structure import ReportingStructureRepository
from app.schemas.reporting_structure import (
    ReportingStructureCreate,
    ReportingStructureResponse,
    ReportingStructureUpdate,
)
from app.services.reporting_structure import ReportingStructureService

router = APIRouter()


def get_reporting_service(db: AsyncSession = Depends(get_db_session)) -> ReportingStructureService:
    return ReportingStructureService(ReportingStructureRepository(db))


@router.post("", response_model=ReportingStructureResponse, status_code=status.HTTP_201_CREATED)
async def create_reporting_relation(
    data: ReportingStructureCreate,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: ReportingStructureService = Depends(get_reporting_service),
):
    return await service.create_reporting_relation(data)


@router.get("", response_model=list[ReportingStructureResponse])
async def list_reporting_structures(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: ReportingStructureService = Depends(get_reporting_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=ReportingStructureResponse)
async def get_reporting_relation(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ReportingStructureService = Depends(get_reporting_service),
):
    item = await service.get(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reporting relation not found"
        )
    return item


@router.delete("/{id}", response_model=ReportingStructureResponse)
async def delete_reporting_relation(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("organization.write")),
    service: ReportingStructureService = Depends(get_reporting_service),
):
    item = await service.delete(id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reporting relation not found"
        )
    return item
