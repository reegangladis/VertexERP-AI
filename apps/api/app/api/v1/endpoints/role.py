import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session, get_current_user, PermissionChecker
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleAssignPermissions
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response
from app.models.user import User

router = APIRouter()

# Services
async def get_role_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.role import RoleRepository
    from app.repositories.permission import PermissionRepository
    from app.services.role import RoleService
    return RoleService(RoleRepository(db), PermissionRepository(db))

@router.get("", response_model=APIResponse[list[RoleResponse]])
async def list_roles(
    current_user: User = Depends(PermissionChecker("roles.read")),
    role_service = Depends(get_role_service)
):
    roles = await role_service.get_roles_by_org(current_user.organization_id)
    data = [RoleResponse.model_validate(r) for r in roles]
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Roles retrieved successfully",
        data=data
    )

@router.post("", response_model=APIResponse[RoleResponse], status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: RoleCreate,
    current_user: User = Depends(PermissionChecker("roles.manage")),
    role_service = Depends(get_role_service)
):
    role_in = {
        "name": payload.name,
        "description": payload.description,
        "organization_id": current_user.organization_id
    }
    
    # Check if role name already exists
    existing = await role_service.get_by_name(payload.name)
    if existing:
         raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Role name already exists")

    role = await role_service.create(role_in)
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Role created successfully",
        data=RoleResponse.model_validate(role)
    )

@router.put("/{role_id}", response_model=APIResponse[RoleResponse])
async def update_role(
    role_id: uuid.UUID,
    payload: RoleUpdate,
    current_user: User = Depends(PermissionChecker("roles.manage")),
    role_service = Depends(get_role_service)
):
    role = await role_service.get(role_id)
    if not role or (role.organization_id and role.organization_id != current_user.organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
    updated = await role_service.update(role_id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Role updated successfully",
        data=RoleResponse.model_validate(updated)
    )

@router.delete("/{role_id}")
async def delete_role(
    role_id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("roles.manage")),
    role_service = Depends(get_role_service)
):
    role = await role_service.get(role_id)
    if not role or (role.organization_id and role.organization_id != current_user.organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
    await role_service.delete(role_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Role deleted successfully"
    )

@router.post("/{role_id}/permissions", response_model=APIResponse[RoleResponse])
async def assign_permissions(
    role_id: uuid.UUID,
    payload: RoleAssignPermissions,
    current_user: User = Depends(PermissionChecker("roles.manage")),
    role_service = Depends(get_role_service)
):
    role = await role_service.get(role_id)
    if not role or (role.organization_id and role.organization_id != current_user.organization_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
    updated = await role_service.assign_permissions_to_role(role_id, payload.permissions)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Permissions assigned to role successfully",
        data=RoleResponse.model_validate(updated)
    )
