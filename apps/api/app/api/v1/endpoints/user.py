import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_current_user, get_db_session
from app.models.user import User
from app.repositories.role import RoleRepository
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserWithRolesResponse
from app.services.user import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db_session)) -> UserService:
    return UserService(UserRepository(db), RoleRepository(db))


@router.post("", response_model=UserWithRolesResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(PermissionChecker("users.create")),
    service: UserService = Depends(get_user_service),
):
    return await service.create_user(data)


@router.get("", response_model=list[UserWithRolesResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=UserWithRolesResponse)
async def get_user(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    return await service.get_user_with_roles(id)


@router.patch("/{id}", response_model=UserWithRolesResponse)
async def update_user(
    id: uuid.UUID,
    data: UserUpdate,
    current_user: User = Depends(PermissionChecker("users.update")),
    service: UserService = Depends(get_user_service),
):
    return await service.update_user(id, data)


@router.delete("/{id}", response_model=UserResponse)
async def delete_user(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("user.delete")),
    service: UserService = Depends(get_user_service),
):
    user = await service.delete(id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.post("/{id}/roles/{role_id}", response_model=UserWithRolesResponse)
async def assign_user_role(
    id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("role.assign")),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_with_roles(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    existing_roles = [r.id for r in user.roles]
    if role_id not in existing_roles:
        existing_roles.append(role_id)
    return await service.user_repo.assign_roles(user, existing_roles)


@router.delete("/{id}/roles/{role_id}", response_model=UserWithRolesResponse)
async def remove_user_role(
    id: uuid.UUID,
    role_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("role.assign")),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_with_roles(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    new_roles = [r.id for r in user.roles if r.id != role_id]
    return await service.user_repo.assign_roles(user, new_roles)


@router.get("/{id}/roles")
async def get_user_roles(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    user = await service.get_user_with_roles(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user.roles
