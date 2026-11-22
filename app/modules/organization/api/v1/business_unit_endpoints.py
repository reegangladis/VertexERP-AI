"""Business Unit API endpoints."""

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
from app.modules.organization.schemas.business_unit import (
    BusinessUnitCreate,
    BusinessUnitResponse,
    BusinessUnitUpdate,
)
from app.modules.organization.services.business_unit_service import BusinessUnitService

router = APIRouter(prefix="/business-units", tags=["Business Unit Management"])


@router.get(
    "/",
    response_model=list[BusinessUnitResponse],
    status_code=status.HTTP_200_OK,
    summary="List Business Units",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_BUSINESS_UNITS_READ.value))
    ],
)
async def list_business_units(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[BusinessUnitResponse]:
    """Lists all business units in active organization."""
    service = BusinessUnitService(db)
    bus = await service.list_business_units(tenant_id, org_id, is_active)
    return [BusinessUnitResponse.model_validate(b) for b in bus]


@router.post(
    "/",
    response_model=BusinessUnitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Business Unit",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_BUSINESS_UNITS_WRITE.value))
    ],
)
async def create_business_unit(
    req: BusinessUnitCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessUnitResponse:
    """Creates a business unit within the active organization."""
    service = BusinessUnitService(db)
    bu = await service.create_business_unit(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="BUSINESS_UNIT_CREATED",
        description=f"Business unit '{bu.name}' ({bu.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return BusinessUnitResponse.model_validate(bu)


@router.get(
    "/{bu_id}",
    response_model=BusinessUnitResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Business Unit Details",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_BUSINESS_UNITS_READ.value))
    ],
)
async def get_business_unit(
    bu_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BusinessUnitResponse:
    """Retrieves business unit details enforcing tenant and org isolation."""
    service = BusinessUnitService(db)
    bu = await service.get_business_unit(bu_id, tenant_id, org_id)
    return BusinessUnitResponse.model_validate(bu)


@router.put(
    "/{bu_id}",
    response_model=BusinessUnitResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Business Unit",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_BUSINESS_UNITS_WRITE.value))
    ],
)
async def update_business_unit(
    bu_id: uuid.UUID,
    req: BusinessUnitUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessUnitResponse:
    """Updates business unit properties."""
    service = BusinessUnitService(db)
    bu = await service.update_business_unit(bu_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="BUSINESS_UNIT_UPDATED",
        description=f"Business unit '{bu.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return BusinessUnitResponse.model_validate(bu)


@router.delete(
    "/{bu_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Business Unit",
    dependencies=[
        Depends(require_permission(PermissionCode.ORGANIZATION_BUSINESS_UNITS_WRITE.value))
    ],
)
async def delete_business_unit(
    bu_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a business unit."""
    service = BusinessUnitService(db)
    await service.delete_business_unit(bu_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="BUSINESS_UNIT_DELETED",
        description=f"Business unit '{bu_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
