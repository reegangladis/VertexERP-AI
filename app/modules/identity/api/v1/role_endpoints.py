"""Role, Permission, and RBAC assignment API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from app.core.exceptions import ConflictException, NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import (
    get_current_tenant_id,
    get_current_user,
    get_optional_redis,
    require_permission,
)
from app.modules.identity.services.rbac_service import RbacService
from app.modules.identity.models.role import Role, UserRole
from app.modules.identity.models.user import User
from app.modules.identity.repositories.role_repository import RoleRepository
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.role import (
    AssignRoleRequest,
    PermissionResponse,
    RoleCreateRequest,
    RoleResponse,
)

router = APIRouter(prefix="/roles", tags=["Role & RBAC Management"])


@router.get(
    "/permissions",
    response_model=list[PermissionResponse],
    status_code=status.HTTP_200_OK,
    summary="List All System Permissions",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_ROLES_READ.value))],
)
async def list_permissions(
    db: AsyncSession = Depends(get_db),
) -> list[PermissionResponse]:
    """Retrieves all standard fine-grained system permission codes."""
    role_repo = RoleRepository(db)
    perms = await role_repo.get_all_permissions()
    return [PermissionResponse.model_validate(p) for p in perms]


@router.get(
    "/",
    response_model=list[RoleResponse],
    status_code=status.HTTP_200_OK,
    summary="List Roles in Tenant",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_ROLES_READ.value))],
)
async def list_roles(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[RoleResponse]:
    """Lists all roles defined within the caller's tenant."""
    role_repo = RoleRepository(db)
    roles = await role_repo.list_roles_by_tenant(tenant_id)
    response_list: list[RoleResponse] = []
    for r in roles:
        perms = await role_repo.get_permissions_for_role(r.id)
        role_resp = RoleResponse(
            id=r.id,
            tenant_id=r.tenant_id,
            name=r.name,
            code=r.code,
            description=r.description,
            is_system_role=r.is_system_role,
            created_at=r.created_at,
            permissions=[PermissionResponse.model_validate(p) for p in perms],
        )
        response_list.append(role_resp)
    return response_list


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Role by ID",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_ROLES_READ.value))],
)
async def get_role_by_id(
    role_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """Retrieves a specific role and its granted permissions."""
    role_repo = RoleRepository(db)
    role = await role_repo.get_role_by_id(role_id, tenant_id=tenant_id)
    if not role:
        raise NotFoundException(f"Role '{role_id}' not found in this tenant")

    perms = await role_repo.get_permissions_for_role(role.id)
    return RoleResponse(
        id=role.id,
        tenant_id=role.tenant_id,
        name=role.name,
        code=role.code,
        description=role.description,
        is_system_role=role.is_system_role,
        created_at=role.created_at,
        permissions=[PermissionResponse.model_validate(p) for p in perms],
    )


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Custom Role in Tenant",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_ROLES_CREATE.value))],
)
async def create_role(
    req: RoleCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    """Creates a new custom role and associates specified permissions."""
    role_repo = RoleRepository(db)
    existing = await role_repo.get_role_by_code(req.code, tenant_id=tenant_id)
    if existing:
        raise ConflictException(f"Role code '{req.code}' already exists in this tenant")

    role = Role(
        tenant_id=tenant_id,
        name=req.name.strip(),
        code=req.code.strip(),
        description=req.description,
        is_system_role=False,
    )
    await role_repo.create_role(role)

    if req.permission_ids:
        await role_repo.assign_permissions_to_role(tenant_id, role.id, req.permission_ids)

    perms = await role_repo.get_permissions_for_role(role.id)

    await AuditService.log_security_event(
        session=db,
        event_type="ROLE_CREATED",
        description=f"Role {role.code} created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return RoleResponse(
        id=role.id,
        tenant_id=role.tenant_id,
        name=role.name,
        code=role.code,
        description=role.description,
        is_system_role=role.is_system_role,
        created_at=role.created_at,
        permissions=[PermissionResponse.model_validate(p) for p in perms],
    )


@router.post(
    "/assign",
    status_code=status.HTTP_200_OK,
    summary="Assign Role to User for Organization",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_ROLES_ASSIGN.value))],
)
async def assign_role_to_user(
    req: AssignRoleRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis | None = Depends(get_optional_redis),
) -> dict[str, str]:
    """Assigns an RBAC role to a user within an organization context."""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)

    # Validate target user belongs to tenant
    target_user = await user_repo.get_by_id(req.user_id, tenant_id=tenant_id)
    if not target_user:
        raise NotFoundException(f"User '{req.user_id}' not found in this tenant")

    # Validate role belongs to tenant
    role = await role_repo.get_role_by_id(req.role_id, tenant_id=tenant_id)
    if not role:
        raise NotFoundException(f"Role '{req.role_id}' not found in this tenant")

    user_role = UserRole(
        tenant_id=tenant_id,
        user_id=target_user.id,
        role_id=role.id,
        organization_id=req.organization_id,
        branch_id=req.branch_id,
        department_id=req.department_id,
    )
    await role_repo.assign_user_role(user_role)

    rbac_service = RbacService(db, redis=redis)
    await rbac_service.invalidate_user_cache(
        user_id=target_user.id,
        organization_id=req.organization_id,
        tenant_id=tenant_id,
    )

    await AuditService.log_security_event(
        session=db,
        event_type="ROLE_ASSIGNED",
        description=(
            f"Role {role.code} assigned to user {target_user.email} by {current_user.email}"
        ),
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return {"message": f"Role '{role.name}' successfully assigned to user"}
