"""Branch API endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User
from app.modules.organization.schemas.branch import BranchCreate, BranchResponse, BranchUpdate
from app.modules.organization.services.branch_service import BranchService

router = APIRouter(prefix="/branches", tags=["Branch Management"])


@router.get(
    "/",
    response_model=list[BranchResponse],
    status_code=status.HTTP_200_OK,
    summary="List Branches in Organization",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_BRANCHES_READ.value))],
)
async def list_branches(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[BranchResponse]:
    """Lists all physical branches within the active organization."""
    service = BranchService(db)
    branches = await service.list_branches(tenant_id, org_id, is_active)
    return [BranchResponse.model_validate(b) for b in branches]


@router.post(
    "/",
    response_model=BranchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Branch",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_BRANCHES_WRITE.value))],
)
async def create_branch(
    req: BranchCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BranchResponse:
    """Creates a new branch office under the active organization."""
    service = BranchService(db)
    branch = await service.create_branch(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="BRANCH_CREATED",
        description=f"Branch '{branch.name}' ({branch.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return BranchResponse.model_validate(branch)


@router.get(
    "/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Branch Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_BRANCHES_READ.value))],
)
async def get_branch(
    branch_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BranchResponse:
    """Retrieves specific branch details enforcing tenant and org isolation."""
    service = BranchService(db)
    branch = await service.get_branch(branch_id, tenant_id, org_id)
    return BranchResponse.model_validate(branch)


@router.put(
    "/{branch_id}",
    response_model=BranchResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Branch",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_BRANCHES_WRITE.value))],
)
async def update_branch(
    branch_id: uuid.UUID,
    req: BranchUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BranchResponse:
    """Updates branch properties."""
    service = BranchService(db)
    branch = await service.update_branch(branch_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="BRANCH_UPDATED",
        description=f"Branch '{branch.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return BranchResponse.model_validate(branch)


@router.delete(
    "/{branch_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Branch",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_BRANCHES_WRITE.value))],
)
async def delete_branch(
    branch_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a branch."""
    service = BranchService(db)
    await service.delete_branch(branch_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="BRANCH_DELETED",
        description=f"Branch '{branch_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
