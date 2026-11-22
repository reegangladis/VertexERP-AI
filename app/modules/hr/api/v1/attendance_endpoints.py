"""Attendance, Shifts, and Regularization API endpoints."""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.hr.schemas.attendance import (
    AttendanceClockIn,
    AttendanceClockOut,
    AttendanceRecordResponse,
    RegularizationCreate,
    RegularizationResponse,
    RegularizationReviewRequest,
    ShiftAssignmentCreate,
    ShiftAssignmentResponse,
    ShiftCreate,
    ShiftResponse,
)
from app.modules.hr.services.attendance_service import AttendanceService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user,
    require_permission,
)
from app.modules.identity.models.user import User

router = APIRouter(prefix="/attendance", tags=["HR Attendance & Shifts"])


# --------------------------------------------------------------------------
# Shifts
# --------------------------------------------------------------------------
@router.post(
    "/shifts",
    response_model=ShiftResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Shift",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_WRITE.value))],
)
async def create_shift(
    req: ShiftCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShiftResponse:
    """Creates a work shift."""
    service = AttendanceService(db)
    shift = await service.create_shift(tenant_id, org_id, req)
    return ShiftResponse.model_validate(shift)


@router.get(
    "/shifts",
    response_model=list[ShiftResponse],
    status_code=status.HTTP_200_OK,
    summary="List Shifts",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_READ.value))],
)
async def list_shifts(
    is_active: bool | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[ShiftResponse]:
    """Lists available shifts."""
    service = AttendanceService(db)
    shifts = await service.list_shifts(tenant_id, org_id, is_active)
    return [ShiftResponse.model_validate(s) for s in shifts]


@router.post(
    "/shifts/assign",
    response_model=ShiftAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign Shift to Employee",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_WRITE.value))],
)
async def assign_shift(
    req: ShiftAssignmentCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShiftAssignmentResponse:
    """Assigns shift roster to an employee."""
    service = AttendanceService(db)
    assignment = await service.assign_shift(tenant_id, org_id, req)
    return ShiftAssignmentResponse.model_validate(assignment)


# --------------------------------------------------------------------------
# Clock-In / Clock-Out
# --------------------------------------------------------------------------
@router.post(
    "/clock-in",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Employee Clock-In",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_WRITE.value))],
)
async def clock_in(
    req: AttendanceClockIn,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceRecordResponse:
    """Records clock-in punch timestamp with optional IP/GPS metadata."""
    service = AttendanceService(db)
    record = await service.clock_in(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_CLOCK_IN",
        description=f"Clock-in for employee '{record.employee_id}' on {record.work_date} by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return AttendanceRecordResponse.model_validate(record)


@router.post(
    "/clock-out",
    response_model=AttendanceRecordResponse,
    status_code=status.HTTP_200_OK,
    summary="Employee Clock-Out",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_WRITE.value))],
)
async def clock_out(
    req: AttendanceClockOut,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> AttendanceRecordResponse:
    """Records clock-out punch timestamp and computes worked hours."""
    service = AttendanceService(db)
    record = await service.clock_out(tenant_id, org_id, req)

    await AuditService.log_security_event(
        session=db,
        event_type="HR_CLOCK_OUT",
        description=f"Clock-out for employee '{record.employee_id}' on {record.work_date} ({record.regular_hours} hrs worked) by {current_user.email}",
        severity="INFO",
        tenant_id=tenant_id,
        user_id=current_user.id,
    )

    return AttendanceRecordResponse.model_validate(record)


@router.get(
    "/records",
    response_model=list[AttendanceRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="List Attendance Records",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_READ.value))],
)
async def list_attendance_records(
    employee_id: uuid.UUID | None = None,
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> list[AttendanceRecordResponse]:
    """Lists attendance logs."""
    service = AttendanceService(db)
    records = await service.list_records(tenant_id, org_id, employee_id, start_date, end_date)
    return [AttendanceRecordResponse.model_validate(r) for r in records]


# --------------------------------------------------------------------------
# Regularization
# --------------------------------------------------------------------------
@router.post(
    "/regularizations",
    response_model=RegularizationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Request Attendance Regularization",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_WRITE.value))],
)
async def request_regularization(
    req: RegularizationCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RegularizationResponse:
    """Submits regularization application for missed punches."""
    service = AttendanceService(db)
    reg = await service.request_regularization(tenant_id, org_id, req)
    return RegularizationResponse.model_validate(reg)


@router.put(
    "/regularizations/{reg_id}/review",
    response_model=RegularizationResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve or Reject Regularization",
    dependencies=[Depends(require_permission(PermissionCode.HR_ATTENDANCE_APPROVE.value))],
)
async def review_regularization(
    reg_id: uuid.UUID,
    req: RegularizationReviewRequest,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RegularizationResponse:
    """Manager approval or rejection of attendance regularization."""
    service = AttendanceService(db)
    reg = await service.review_regularization(reg_id, tenant_id, org_id, current_user.id, req)
    return RegularizationResponse.model_validate(reg)
