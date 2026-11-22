"""Work Calendar API endpoints."""

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
from app.modules.organization.schemas.calendar import (
    WorkCalendarBase,
    WorkCalendarCreate,
    WorkCalendarResponse,
    WorkCalendarUpdate,
    WorkingDayCreate,
    WorkingDayResponse,
)
from app.modules.organization.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendars", tags=["Calendar Management"])


@router.get(
    "/",
    response_model=list[WorkCalendarBase],
    status_code=status.HTTP_200_OK,
    summary="List Work Calendars",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CALENDARS_READ.value))],
)
async def list_calendars(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[WorkCalendarBase]:
    """Lists all work calendars in active organization."""
    service = CalendarService(db)
    cals = await service.list_calendars(tenant_id, org_id, is_active)
    return [
        WorkCalendarBase(
            code=c.code,
            name=c.name,
            description=c.description,
            time_zone=c.time_zone,
            is_default=c.is_default,
            standard_hours_per_day=c.standard_hours_per_day,
            is_active=c.is_active,
        )
        for c in cals
    ]


@router.post(
    "/",
    response_model=WorkCalendarResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Work Calendar",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CALENDARS_WRITE.value))],
)
async def create_calendar(
    req: WorkCalendarCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkCalendarResponse:
    """Creates a work calendar with shift/working day schedule."""
    service = CalendarService(db)
    cal = await service.create_calendar(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="CALENDAR_CREATED",
        description=f"Calendar '{cal.name}' ({cal.code}) created by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return cal


@router.get(
    "/{cal_id}",
    response_model=WorkCalendarResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Work Calendar Details",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CALENDARS_READ.value))],
)
async def get_calendar(
    cal_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> WorkCalendarResponse:
    """Retrieves work calendar with working days schedule."""
    service = CalendarService(db)
    return await service.get_calendar(cal_id, tenant_id, org_id)


@router.put(
    "/{cal_id}",
    response_model=WorkCalendarResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Work Calendar",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CALENDARS_WRITE.value))],
)
async def update_calendar(
    cal_id: uuid.UUID,
    req: WorkCalendarUpdate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> WorkCalendarResponse:
    """Updates work calendar metadata."""
    service = CalendarService(db)
    await service.update_calendar(cal_id, tenant_id, org_id, req)
    cal_res = await service.get_calendar(cal_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="CALENDAR_UPDATED",
        description=f"Calendar '{cal_res.name}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return cal_res


@router.put(
    "/{cal_id}/working-days",
    response_model=list[WorkingDayResponse],
    status_code=status.HTTP_200_OK,
    summary="Update Calendar Working Days",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CALENDARS_WRITE.value))],
)
async def update_calendar_working_days(
    cal_id: uuid.UUID,
    days: list[WorkingDayCreate],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[WorkingDayResponse]:
    """Updates the 7-day schedule for a calendar."""
    service = CalendarService(db)
    updated_days = await service.update_working_days(cal_id, tenant_id, org_id, days)

    await AuditService.log_security_event(
        session=db,
        event_type="CALENDAR_DAYS_UPDATED",
        description=f"Working days for calendar '{cal_id}' updated by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return [
        WorkingDayResponse(
            id=d.id,
            tenant_id=d.tenant_id,
            calendar_id=d.calendar_id,
            day_of_week=d.day_of_week,
            is_working_day=d.is_working_day,
            start_time=d.start_time,
            end_time=d.end_time,
            created_at=d.created_at,
        )
        for d in updated_days
    ]


@router.delete(
    "/{cal_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Work Calendar",
    dependencies=[Depends(require_permission(PermissionCode.ORGANIZATION_CALENDARS_WRITE.value))],
)
async def delete_calendar(
    cal_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft deletes a work calendar."""
    service = CalendarService(db)
    await service.delete_calendar(cal_id, tenant_id, org_id)

    await AuditService.log_security_event(
        session=db,
        event_type="CALENDAR_DELETED",
        description=f"Calendar '{cal_id}' deleted by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )
