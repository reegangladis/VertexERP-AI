import uuid
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.attendance import (
    AttendanceCorrectionRepository,
    AttendanceDeviceRepository,
    AttendanceRecordRepository,
    BreakRecordRepository,
    OvertimeRecordRepository,
    ShiftAssignmentRepository,
    ShiftRepository,
    WorkScheduleRepository,
)
from app.schemas.attendance import (
    AttendanceCorrectionApproveRequest,
    AttendanceCorrectionCreate,
    AttendanceCorrectionResponse,
    AttendanceDashboardSummary,
    AttendanceDeviceCreate,
    AttendanceDeviceResponse,
    AttendanceRecordResponse,
    AttendanceRecordUpdate,
    CheckInRequest,
    CheckOutRequest,
    EmployeeShiftAssignmentCreate,
    EmployeeShiftAssignmentResponse,
    OvertimeApproveRequest,
    OvertimeRecordCreate,
    OvertimeRecordResponse,
    ShiftCreate,
    ShiftResponse,
    ShiftUpdate,
    WorkScheduleCreate,
    WorkScheduleResponse,
)
from app.services.attendance import AttendanceService

router = APIRouter()


def get_attendance_service(db: AsyncSession = Depends(get_db_session)) -> AttendanceService:
    return AttendanceService(
        record_repo=AttendanceRecordRepository(db),
        shift_repo=ShiftRepository(db),
        assignment_repo=ShiftAssignmentRepository(db),
        correction_repo=AttendanceCorrectionRepository(db),
        overtime_repo=OvertimeRecordRepository(db),
        device_repo=AttendanceDeviceRepository(db),
        schedule_repo=WorkScheduleRepository(db),
        break_repo=BreakRecordRepository(db),
    )


# --- Attendance Core ---
@router.post("/attendance/check-in", response_model=AttendanceRecordResponse, status_code=status.HTTP_201_CREATED)
async def check_in(
    payload: CheckInRequest,
    current_user: User = Depends(PermissionChecker("attendance.checkin")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.check_in(payload)


@router.post("/attendance/check-out", response_model=AttendanceRecordResponse)
async def check_out(
    payload: CheckOutRequest,
    current_user: User = Depends(PermissionChecker("attendance.checkout")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.check_out(payload)


@router.get("/attendance", response_model=list[AttendanceRecordResponse])
async def list_attendance(
    employee_id: uuid.UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    attendance_status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_attendance(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date,
        status_filter=attendance_status,
        skip=skip,
        limit=limit,
    )


@router.get("/attendance/dashboard-summary", response_model=AttendanceDashboardSummary)
async def get_dashboard_summary(
    org_id: uuid.UUID = Query(...),
    target_date: date | None = Query(None),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.get_dashboard_summary(org_id, target_date)


@router.get("/attendance/{id}", response_model=AttendanceRecordResponse)
async def get_attendance_record(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.get_attendance(id)


@router.patch("/attendance/{id}", response_model=AttendanceRecordResponse)
async def update_attendance_record(
    id: uuid.UUID,
    payload: AttendanceRecordUpdate,
    current_user: User = Depends(PermissionChecker("attendance.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.update_attendance(id, payload)


# --- Attendance Corrections ---
@router.post("/attendance/corrections", response_model=AttendanceCorrectionResponse, status_code=status.HTTP_201_CREATED)
async def create_correction(
    payload: AttendanceCorrectionCreate,
    current_user: User = Depends(PermissionChecker("attendance.checkin")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.create_correction(payload)


@router.get("/attendance/corrections", response_model=list[AttendanceCorrectionResponse])
async def list_corrections(
    requested_by: uuid.UUID | None = Query(None),
    correction_status: str | None = Query(None),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_corrections(requested_by=requested_by, status_filter=correction_status)


@router.post("/attendance/corrections/{id}/approve", response_model=AttendanceCorrectionResponse)
async def approve_correction(
    id: uuid.UUID,
    payload: AttendanceCorrectionApproveRequest,
    current_user: User = Depends(PermissionChecker("attendance.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.approve_correction(id, payload)


@router.post("/attendance/corrections/{id}/reject", response_model=AttendanceCorrectionResponse)
async def reject_correction(
    id: uuid.UUID,
    payload: AttendanceCorrectionApproveRequest,
    current_user: User = Depends(PermissionChecker("attendance.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.reject_correction(id, payload)


# --- Shifts ---
@router.post("/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    payload: ShiftCreate,
    current_user: User = Depends(PermissionChecker("shift.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.create_shift(payload)


@router.get("/shifts", response_model=list[ShiftResponse])
async def list_shifts(
    org_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_shifts(org_id, skip=skip, limit=limit)


@router.get("/shifts/{id}", response_model=ShiftResponse)
async def get_shift(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.get_shift(id)


@router.patch("/shifts/{id}", response_model=ShiftResponse)
async def update_shift(
    id: uuid.UUID,
    payload: ShiftUpdate,
    current_user: User = Depends(PermissionChecker("shift.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.update_shift(id, payload)


@router.delete("/shifts/{id}", response_model=ShiftResponse)
async def delete_shift(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("shift.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.delete_shift(id)


# --- Work Schedules ---
@router.post("/work-schedules", response_model=WorkScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_work_schedule(
    payload: WorkScheduleCreate,
    current_user: User = Depends(PermissionChecker("schedule.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.create_schedule(payload)


@router.get("/work-schedules", response_model=list[WorkScheduleResponse])
async def list_work_schedules(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_schedules(org_id)


# --- Shift Assignments ---
@router.post("/shift-assignments", response_model=EmployeeShiftAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_shift(
    payload: EmployeeShiftAssignmentCreate,
    current_user: User = Depends(PermissionChecker("shift.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.assign_shift(payload)


@router.get("/shift-assignments", response_model=list[EmployeeShiftAssignmentResponse])
async def list_assignments(
    employee_id: uuid.UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_assignments(employee_id, skip=skip, limit=limit)


# --- Overtime ---
@router.post("/overtime", response_model=OvertimeRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_overtime_record(
    payload: OvertimeRecordCreate,
    current_user: User = Depends(PermissionChecker("overtime.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.create_overtime_record(payload)


@router.get("/overtime", response_model=list[OvertimeRecordResponse])
async def list_overtime_records(
    employee_id: uuid.UUID | None = Query(None),
    approved: bool | None = Query(None),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_overtime_records(employee_id=employee_id, approved=approved)


@router.post("/overtime/{id}/approve", response_model=OvertimeRecordResponse)
async def approve_overtime(
    id: uuid.UUID,
    payload: OvertimeApproveRequest,
    current_user: User = Depends(PermissionChecker("overtime.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.approve_overtime(id, payload)


# --- Attendance Devices ---
@router.post("/attendance-devices", response_model=AttendanceDeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_attendance_device(
    payload: AttendanceDeviceCreate,
    current_user: User = Depends(PermissionChecker("attendance.manage")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.create_device(payload)


@router.get("/attendance-devices", response_model=list[AttendanceDeviceResponse])
async def list_attendance_devices(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("attendance.read")),
    service: AttendanceService = Depends(get_attendance_service),
):
    return await service.list_devices(org_id)
