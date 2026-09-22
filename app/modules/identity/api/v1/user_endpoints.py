"""User management API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException
from app.core.permissions import PermissionCode
from app.core.security import hash_password
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.role import UserRole
from app.modules.identity.models.user import User
from app.modules.identity.models.user_credential import UserCredential
from app.modules.identity.repositories.role_repository import RoleRepository
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.user import UserCreateRequest, UserResponse, UserUpdateRequest
from app.modules.identity.services.auth_service import AuthService
from app.modules.organization.services.organization_service import OrganizationService

router = APIRouter(prefix="/users", tags=["User Management"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Authenticated User Profile",
)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Returns the authenticated user's profile details."""
    return UserResponse.model_validate(current_user)


@router.patch(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Authenticated User Profile",
)
async def update_my_profile(
    req: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Updates profile attributes of the authenticated user."""
    if req.full_name is not None:
        current_user.full_name = req.full_name.strip()
    if req.phone_number is not None:
        current_user.phone_number = req.phone_number
    if req.avatar_url is not None:
        current_user.avatar_url = req.avatar_url

    await db.flush()
    return UserResponse.model_validate(current_user)


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List Users in Tenant",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_USERS_READ.value))],
)
async def list_users(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[UserResponse]:
    """Lists all users belonging to the caller's tenant."""
    user_repo = UserRepository(db)
    users = await user_repo.list_by_tenant(tenant_id)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User by ID",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_USERS_READ.value))],
)
async def get_user_by_id(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Retrieves a specific user enforcing tenant boundary isolation."""
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id, tenant_id=tenant_id)
    if not user:
        raise NotFoundException(f"User '{user_id}' not found in this tenant")
    return UserResponse.model_validate(user)


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create User in Tenant",
    dependencies=[Depends(require_permission(PermissionCode.IDENTITY_USERS_CREATE.value))],
)
async def create_user(
    req: UserCreateRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Provisions a new user, credential, and organization membership within the tenant."""
    AuthService.validate_password_strength(req.password)

    user_repo = UserRepository(db)
    email_clean = req.email.lower().strip()
    existing = await user_repo.get_by_email(email_clean, tenant_id=tenant_id)
    if existing:
        raise ConflictException(f"User with email '{email_clean}' already exists in this tenant")

    user = User(
        tenant_id=tenant_id,
        email=email_clean,
        full_name=req.full_name.strip(),
        phone_number=req.phone_number,
        is_active=True,
        is_verified=True,
        default_organization_id=org_id,
        created_by_id=current_user.id,
    )
    await user_repo.create(user)

    import secrets

    password_hash = hash_password(req.password)
    creds = UserCredential(
        tenant_id=tenant_id,
        user_id=user.id,
        password_hash=password_hash,
        salt=secrets.token_hex(16),
    )
    await user_repo.create_credentials(creds)

    # Add default org membership
    org_service = OrganizationService(db)
    await org_service.add_membership(
        tenant_id=tenant_id,
        user_id=user.id,
        org_id=org_id,
        is_default=True,
    )

    # Assign roles if provided
    if req.role_ids:
        role_repo = RoleRepository(db)
        for role_id in req.role_ids:
            role = await role_repo.get_role_by_id(role_id, tenant_id=tenant_id)
            if role:
                user_role = UserRole(
                    tenant_id=tenant_id,
                    user_id=user.id,
                    role_id=role.id,
                    organization_id=org_id,
                )
                await role_repo.assign_user_role(user_role)

    await AuditService.log_security_event(
        session=db,
        event_type="USER_CREATED",
        description=f"User {user.email} created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=user.id,
    )

    return UserResponse.model_validate(user)
