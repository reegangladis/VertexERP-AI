import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.permission import PermissionRepository
from app.schemas.permission import (
    PermissionCreate,
    PermissionResponse,
    PermissionUpdate,
)
from app.services.permission_service import PermissionService

router = APIRouter()


def get_permission_service(
    db: AsyncSession = Depends(get_db_session),
) -> PermissionService:
    return PermissionService(PermissionRepository(db))


@router.post("", response_model=PermissionResponse, status_code=status.HTTP_201_CREATED)
async def create_permission(
    data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
):
    existing = await service.get_by_code(data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Permission code '{data.code}' already exists",
        )
    return await service.create(data)


@router.get("", response_model=list[PermissionResponse])
async def list_permissions(
    skip: int = 0,
    limit: int = 100,
    service: PermissionService = Depends(get_permission_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=PermissionResponse)
async def get_permission(
    id: uuid.UUID,
    service: PermissionService = Depends(get_permission_service),
):
    perm = await service.get(id)
    if not perm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return perm


@router.put("/{id}", response_model=PermissionResponse)
async def update_permission(
    id: uuid.UUID,
    data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
):
    perm = await service.update(id, data)
    if not perm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return perm


@router.delete("/{id}", response_model=PermissionResponse)
async def delete_permission(
    id: uuid.UUID,
    service: PermissionService = Depends(get_permission_service),
):
    perm = await service.delete(id)
    if not perm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Permission not found"
        )
    return perm
