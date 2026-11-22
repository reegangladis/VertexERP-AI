"""Cost Center API endpoints."""

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
from app.modules.organization.schemas.cost_center import (
    CostCenterCreate,
    CostCenterResponse,
    CostCenterUpdate,
)
from app.modules.organization.services.cost_center_service import CostCenterService

router = APIRouter(prefix="/cost-centers", tags=["Cost Center Management"])


@router.get(
    "/",
    response_model=list[CostCenterResponse],
    status_code=status.HTTP_200_OK,
    summary="List Cost Centers",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_COST_CENTERS_READ.value))],
)
async def list_cost_centers(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[CostCenterResponse]:
    """Lists all cost centers in active organization."""
    service = CostCenterService(db)
    ccs = await service.list_cost_centers(tenant_id, org_id, is_active)
    return [CostCenterResponse.model_validate(c) for c in ccs]


@router.post(
    "/",
    response_model=CostCenterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Cost Center",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_COST_CENTERS_WRITE.value))
    ],
)
async def create_cost_center(
    req: CostCenterCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CostCenterResponse:
    """Creates a cost center within the active organization."""
    service = CostCenterService(db)
    cc = await service.create_cost_center(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="COST_CENTER_CREATED",
        description=f"Cost center '{cc.name}' ({cc.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return CostCenterResponse.model_validate(cc)


@router.get(
    "/{cc_id}",
    response_model=CostCenterResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Cost Center Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_COST_CENTERS_READ.value))],
)
async def get_cost_center(
    cc_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> CostCenterResponse:
    """Retrieves cost center details enforcing tenant and org isolation."""
    service = CostCenterService(db)
    cc = await service.get_cost_center(cc_id, tenant_id, org_id)
    return CostCenterResponse.model_validate(cc)


@router.put(
    "/{cc_id}",
    response_model=CostCenterResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Cost Center",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_COST_CENTERS_WRITE.value))
    ],
)
async def update_cost_center(
    cc_id: uuid.UUID,
    req: CostCenterUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CostCenterResponse:
    """Updates cost center properties."""
    service = CostCenterService(db)
    cc = await service.update_cost_center(cc_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="COST_CENTER_UPDATED",
        description=f"Cost center '{cc.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return CostCenterResponse.model_validate(cc)


@router.delete(
    "/{cc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Cost Center",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_COST_CENTERS_WRITE.value))
    ],
)
async def delete_cost_center(
    cc_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a cost center."""
    service = CostCenterService(db)
    await service.delete_cost_center(cc_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="COST_CENTER_DELETED",
        description=f"Cost center '{cc_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
