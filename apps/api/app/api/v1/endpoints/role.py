import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.permission import PermissionRepository
from app.repositories.role import RoleRepository
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.role_service import RoleService

router = APIRouter()


def get_role_service(
    db: AsyncSession = Depends(get_db_session),
) -> RoleService:
    return RoleService(RoleRepository(db), PermissionRepository(db))


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    service: RoleService = Depends(get_role_service),
):
    return await service.create_role(data)


@router.get("", response_model=list[RoleResponse])
async def list_roles(
    organization_id: uuid.UUID | None = None,
    service: RoleService = Depends(get_role_service),
):
    if organization_id:
        return await service.get_by_org(organization_id)
    items, _ = await service.get_multi()
    return items


@router.get("/{id}", response_model=RoleResponse)
async def get_role(
    id: uuid.UUID,
    service: RoleService = Depends(get_role_service),
):
    role = await service.repository.get_with_permissions(id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role


@router.put("/{id}", response_model=RoleResponse)
async def update_role(
    id: uuid.UUID,
    data: RoleUpdate,
    service: RoleService = Depends(get_role_service),
):
    return await service.update_role(id, data)


@router.delete("/{id}", response_model=RoleResponse)
async def delete_role(
    id: uuid.UUID,
    service: RoleService = Depends(get_role_service),
):
    role = await service.delete(id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Role not found"
        )
    return role
