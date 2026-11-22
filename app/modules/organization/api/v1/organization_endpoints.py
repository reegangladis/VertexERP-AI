"""Organization and Tenant Membership API endpoints."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import (
    get_current_tenant_id,
    get_current_user,
    get_current_user_claims,
    require_permission,
)
from app.modules.identity.models.user import User
from app.modules.identity.repositories.role_repository import RoleRepository
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.auth import TokenResponse
from app.modules.identity.services.jwt_service import JwtService
from app.modules.identity.services.rbac_service import RbacService
from app.modules.organization.schemas.organization import (
    AddMemberRequest,
    OrganizationCreate,
    OrganizationResponse,
    TenantMembershipResponse,
)
from app.modules.organization.services.organization_service import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Organization Management"])


@router.get(
    "/",
    response_model=list[OrganizationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organizations in Tenant",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_READ.value))],
)
async def list_organizations(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[OrganizationResponse]:
    """Lists all organizations under the caller's tenant."""
    org_service = OrganizationService(db)
    orgs = await org_service.list_organizations(tenant_id)
    return [OrganizationResponse.model_validate(o) for o in orgs]


@router.post(
    "/",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Organization in Tenant",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CREATE.value))],
)
async def create_organization(
    req: OrganizationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Creates a new operational organization or subsidiary within the tenant."""
    org_service = OrganizationService(db)
    org = await org_service.create_organization(tenant_id, req)

    # Automatically add creator as member
    await org_service.add_membership(tenant_id, current_user.id, org.id, is_default=False)

    await AuditService.log_security_event(
        session=db,
        event_type="ORGANIZATION_CREATED",
        description=f"Organization '{org.name}' created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return OrganizationResponse.model_validate(org)


@router.get(
    "/{org_id}",
    response_model=OrganizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Organization Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_READ.value))],
)
async def get_organization_by_id(
    org_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> OrganizationResponse:
    """Retrieves organization details enforcing tenant isolation."""
    org_service = OrganizationService(db)
    org = await org_service.get_organization(tenant_id, org_id)
    return OrganizationResponse.model_validate(org)


@router.post(
    "/{org_id}/switch",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Switch Active Organization Context",
)
async def switch_organization(
    org_id: uuid.UUID,
    claims: dict[str, Any] = Depends(get_current_user_claims),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Switches active organization context.
    Verifies user has active membership in the target organization and issues a refreshed token.
    """
    tenant_id = current_user.tenant_id
    org_service = OrganizationService(db)

    # Validate membership in target org
    await org_service.verify_membership(tenant_id, current_user.id, org_id)

    # Resolve roles and permissions in the target organization
    rbac_service = RbacService(db)
    roles, permissions = await rbac_service.get_user_roles_and_permissions(current_user.id, org_id)

    session_id = uuid.UUID(claims["session_id"]) if claims.get("session_id") else uuid.uuid4()

    access_token, token_jti, expires_in = JwtService.create_access_token(
        user_id=current_user.id,
        tenant_id=tenant_id,
        organization_id=org_id,
        roles=roles,
        permissions=permissions,
        session_id=session_id,
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user_id=current_user.id,
        tenant_id=tenant_id,
        organization_id=org_id,
        roles=roles,
        permissions=permissions,
    )


@router.post(
    "/{org_id}/members",
    response_model=TenantMembershipResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Member to Organization",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_MEMBERS_MANAGE.value))],
)
async def add_organization_member(
    org_id: uuid.UUID,
    req: AddMemberRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TenantMembershipResponse:
    """Grants a user membership into an organization within the tenant."""
    user_repo = UserRepository(db)
    target_user = await user_repo.get_by_id(req.user_id, tenant_id=tenant_id)
    if not target_user:
        raise NotFoundException(f"User '{req.user_id}' not found in this tenant")

    org_service = OrganizationService(db)
    membership = await org_service.add_membership(
        tenant_id=tenant_id,
        user_id=req.user_id,
        org_id=org_id,
        is_default=req.is_default,
    )

    # Assign optional roles
    if req.role_ids:
        role_repo = RoleRepository(db)
        from app.modules.identity.models.role import UserRole

        for role_id in req.role_ids:
            role = await role_repo.get_role_by_id(role_id, tenant_id=tenant_id)
            if role:
                user_role = UserRole(
                    tenant_id=tenant_id,
                    user_id=target_user.id,
                    role_id=role.id,
                    organization_id=org_id,
                )
                await role_repo.assign_user_role(user_role)

    await AuditService.log_security_event(
        session=db,
        event_type="MEMBER_ADDED",
        description=(
            f"User {target_user.email} added to organization '{org_id}' by {current_user.email}"
        ),
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return TenantMembershipResponse.model_validate(membership)


@router.get(
    "/{org_id}/members",
    response_model=list[TenantMembershipResponse],
    status_code=status.HTTP_200_OK,
    summary="List Organization Members",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_READ.value))],
)
async def list_organization_members(
    org_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TenantMembershipResponse]:
    """Lists memberships for the organization."""
    org_service = OrganizationService(db)
    await org_service.get_organization(tenant_id, org_id)
    memberships = await org_service.get_user_memberships(tenant_id, current_user.id)
    return [
        TenantMembershipResponse.model_validate(m)
        for m in memberships
        if m.organization_id == org_id
    ]
