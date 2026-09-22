"""Designation API endpoints."""

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
from app.modules.organization.schemas.designation import (
    DesignationCreate,
    DesignationResponse,
    DesignationUpdate,
)
from app.modules.organization.services.designation_service import DesignationService

router = APIRouter(prefix="/designations", tags=["Designation Management"])


@router.get(
    "/",
    response_model=list[DesignationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Designations",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DESIGNATIONS_READ.value))],
)
async def list_designations(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[DesignationResponse]:
    """Lists all designations in active organization."""
    service = DesignationService(db)
    desigs = await service.list_designations(tenant_id, org_id, is_active)
    return [DesignationResponse.model_validate(d) for d in desigs]


@router.post(
    "/",
    response_model=DesignationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Designation",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_DESIGNATIONS_WRITE.value))
    ],
)
async def create_designation(
    req: DesignationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DesignationResponse:
    """Creates a designation within the active organization."""
    service = DesignationService(db)
    desig = await service.create_designation(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="DESIGNATION_CREATED",
        description=f"Designation '{desig.name}' ({desig.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return DesignationResponse.model_validate(desig)


@router.get(
    "/{desig_id}",
    response_model=DesignationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Designation Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_DESIGNATIONS_READ.value))],
)
async def get_designation(
    desig_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> DesignationResponse:
    """Retrieves designation details enforcing tenant and org isolation."""
    service = DesignationService(db)
    desig = await service.get_designation(desig_id, tenant_id, org_id)
    return DesignationResponse.model_validate(desig)


@router.put(
    "/{desig_id}",
    response_model=DesignationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Designation",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_DESIGNATIONS_WRITE.value))
    ],
)
async def update_designation(
    desig_id: uuid.UUID,
    req: DesignationUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DesignationResponse:
    """Updates designation properties."""
    service = DesignationService(db)
    desig = await service.update_designation(desig_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="DESIGNATION_UPDATED",
        description=f"Designation '{desig.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return DesignationResponse.model_validate(desig)


@router.delete(
    "/{desig_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Designation",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_DESIGNATIONS_WRITE.value))
    ],
)
async def delete_designation(
    desig_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a designation."""
    service = DesignationService(db)
    await service.delete_designation(desig_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="DESIGNATION_DELETED",
        description=f"Designation '{desig_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
