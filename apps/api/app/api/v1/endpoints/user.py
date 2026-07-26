import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session, get_current_user, PermissionChecker
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.auth import UserResponse, SessionResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response
from app.models.user import User

router = APIRouter()

# Services
async def get_user_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.user import UserRepository, PasswordHistoryRepository
    from app.services.user import UserService
    return UserService(UserRepository(db), PasswordHistoryRepository(db))

async def get_session_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.session import SessionRepository, TrustedDeviceRepository
    from app.services.session import SessionService
    return SessionService(SessionRepository(db), TrustedDeviceRepository(db))

@router.get("", response_model=APIResponse[list[UserResponse]])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
    sort: str | None = None,
    current_user: User = Depends(PermissionChecker("users.read")),
    user_service = Depends(get_user_service)
):
    # Enforce Tenant Isolation
    filters = {"organization_id": current_user.organization_id}
    if status:
        filters["status"] = status

    sort_list = [sort] if sort else None
    
    users, total = await user_service.get_multi(
        skip=skip,
        limit=limit,
        filters=filters,
        sort=sort_list
    )
    
    data = [UserResponse.model_validate(u) for u in users]
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Users listed successfully",
        data=data,
        meta={"total": total, "skip": skip, "limit": limit}
    )

@router.post("", response_model=APIResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    current_user: User = Depends(PermissionChecker("users.create")),
    user_service = Depends(get_user_service),
    db: AsyncSession = Depends(get_db_session)
):
    # Tenant boundary
    user_in = {
        "first_name": payload.first_name,
        "last_name": payload.last_name,
        "username": payload.username,
        "email": payload.email,
        "password": payload.password,
        "organization_id": current_user.organization_id,
        "status": "active"
    }
    
    # Assign Roles
    from app.repositories.role import RoleRepository
    role_repo = RoleRepository(db)
    roles_list = []
    for r_name in payload.role_names:
        r = await role_repo.get_by_name(r_name)
        if r:
            roles_list.append(r)

    user = await user_service.create_user(user_in)
    user.roles = roles_list
    await db.commit()
    await db.refresh(user)

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="User created successfully",
        data=UserResponse.model_validate(user)
    )

@router.get("/{user_id}", response_model=APIResponse[UserResponse])
async def get_user(
    user_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("users.read")),
    user_service = Depends(get_user_service)
):
    user = await user_service.get(user_id)
    if not user or user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User details retrieved",
        data=UserResponse.model_validate(user)
    )

@router.put("/{user_id}", response_model=APIResponse[UserResponse])
async def update_user(
    user_id: uuid.UUID,
    payload: UserUpdate,
    current_user: User = Depends(PermissionChecker("users.update")),
    user_service = Depends(get_user_service),
    db: AsyncSession = Depends(get_db_session)
):
    user = await user_service.get(user_id)
    if not user or user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = payload.model_dump(exclude_unset=True)
    role_names = update_data.pop("role_names", None)
    
    updated_user = await user_service.update(user_id, update_data)

    if role_names is not None:
        from app.repositories.role import RoleRepository
        role_repo = RoleRepository(db)
        roles_list = []
        for r_name in role_names:
            r = await role_repo.get_by_name(r_name)
            if r:
                roles_list.append(r)
        updated_user.roles = roles_list
        await db.commit()
        await db.refresh(updated_user)

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User details updated successfully",
        data=UserResponse.model_validate(updated_user)
    )

@router.delete("/{user_id}")
async def delete_user(
    user_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("users.delete")),
    user_service = Depends(get_user_service)
):
    user = await user_service.get(user_id)
    if not user or user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    await user_service.delete(user_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User soft-deleted successfully"
    )

# Sessions management endpoints
@router.get("/{user_id}/sessions", response_model=APIResponse[list[SessionResponse]])
async def get_user_sessions(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session_service = Depends(get_session_service)
):
    if user_id != current_user.id and not any(r.name == "Super Admin" for r in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to view this user's sessions")
        
    sessions = await session_service.get_active_by_user(user_id)
    data = [SessionResponse.model_validate(s) for s in sessions]
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="User sessions retrieved",
        data=data
    )

@router.delete("/{user_id}/sessions")
async def terminate_all_sessions(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session_service = Depends(get_session_service)
):
    if user_id != current_user.id and not any(r.name == "Super Admin" for r in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to terminate this user's sessions")
        
    await session_service.revoke_all_user_sessions(user_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="All sessions terminated successfully"
    )
