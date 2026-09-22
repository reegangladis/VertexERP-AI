"""Location API endpoints."""

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
from app.modules.organization.schemas.location import (
    LocationCreate,
    LocationResponse,
    LocationUpdate,
)
from app.modules.organization.services.location_service import LocationService

router = APIRouter(prefix="/locations", tags=["Location Management"])


@router.get(
    "/",
    response_model=list[LocationResponse],
    status_code=status.HTTP_200_OK,
    summary="List Locations",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_LOCATIONS_READ.value))],
)
async def list_locations(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[LocationResponse]:
    """Lists all physical facility locations in active organization."""
    service = LocationService(db)
    locs = await service.list_locations(tenant_id, org_id, is_active)
    return [LocationResponse.model_validate(loc) for loc in locs]


@router.post(
    "/",
    response_model=LocationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Location",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_LOCATIONS_WRITE.value))],
)
async def create_location(
    req: LocationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    """Creates a location within the active organization."""
    service = LocationService(db)
    loc = await service.create_location(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="LOCATION_CREATED",
        description=f"Location '{loc.name}' ({loc.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return LocationResponse.model_validate(loc)


@router.get(
    "/{loc_id}",
    response_model=LocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Location Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_LOCATIONS_READ.value))],
)
async def get_location(
    loc_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    """Retrieves location details enforcing tenant and org isolation."""
    service = LocationService(db)
    loc = await service.get_location(loc_id, tenant_id, org_id)
    return LocationResponse.model_validate(loc)


@router.put(
    "/{loc_id}",
    response_model=LocationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Location",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_LOCATIONS_WRITE.value))],
)
async def update_location(
    loc_id: uuid.UUID,
    req: LocationUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LocationResponse:
    """Updates location properties."""
    service = LocationService(db)
    loc = await service.update_location(loc_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="LOCATION_UPDATED",
        description=f"Location '{loc.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return LocationResponse.model_validate(loc)


@router.delete(
    "/{loc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Location",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_LOCATIONS_WRITE.value))],
)
async def delete_location(
    loc_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a location."""
    service = LocationService(db)
    await service.delete_location(loc_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="LOCATION_DELETED",
        description=f"Location '{loc_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
