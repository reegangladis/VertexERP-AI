"""Holiday API endpoints."""

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
from app.modules.organization.schemas.holiday import (
    HolidayCreate,
    HolidayResponse,
    HolidayUpdate,
)
from app.modules.organization.services.holiday_service import HolidayService

router = APIRouter(prefix="/holidays", tags=["Holiday Management"])


@router.get(
    "/",
    response_model=list[HolidayResponse],
    status_code=status.HTTP_200_OK,
    summary="List Holidays",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_HOLIDAYS_READ.value))],
)
async def list_holidays(
    year: int | None = None,
    calendar_id: uuid.UUID | None = None,
    branch_id: uuid.UUID | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[HolidayResponse]:
    """Lists holidays in active organization with optional year/branch/calendar filters."""
    service = HolidayService(db)
    holidays = await service.list_holidays(tenant_id, org_id, year, calendar_id, branch_id)
    return [HolidayResponse.model_validate(h) for h in holidays]


@router.post(
    "/",
    response_model=HolidayResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Holiday",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_HOLIDAYS_WRITE.value))],
)
async def create_holiday(
    req: HolidayCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HolidayResponse:
    """Creates a holiday for the organization."""
    service = HolidayService(db)
    holiday = await service.create_holiday(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HOLIDAY_CREATED",
        description=(
            f"Holiday '{holiday.name}' ({holiday.holiday_date}) created by {current_user.email}"
        ),
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return HolidayResponse.model_validate(holiday)


@router.get(
    "/{holiday_id}",
    response_model=HolidayResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Holiday Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_HOLIDAYS_READ.value))],
)
async def get_holiday(
    holiday_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> HolidayResponse:
    """Retrieves holiday details enforcing tenant and org isolation."""
    service = HolidayService(db)
    holiday = await service.get_holiday(holiday_id, tenant_id, org_id)
    return HolidayResponse.model_validate(holiday)


@router.put(
    "/{holiday_id}",
    response_model=HolidayResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Holiday",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_HOLIDAYS_WRITE.value))],
)
async def update_holiday(
    holiday_id: uuid.UUID,
    req: HolidayUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HolidayResponse:
    """Updates holiday properties."""
    service = HolidayService(db)
    holiday = await service.update_holiday(holiday_id, tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HOLIDAY_UPDATED",
        description=f"Holiday '{holiday.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return HolidayResponse.model_validate(holiday)


@router.delete(
    "/{holiday_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Holiday",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_HOLIDAYS_WRITE.value))],
)
async def delete_holiday(
    holiday_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a holiday."""
    service = HolidayService(db)
    await service.delete_holiday(holiday_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="HOLIDAY_DELETED",
        description=f"Holiday '{holiday_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
