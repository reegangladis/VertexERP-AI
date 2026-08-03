import uuid
from datetime import UTC, date, datetime, time

from fastapi import HTTPException, status

from app.models.attendance_v5 import (
    AttendanceCorrection,
    AttendanceDevice,
    AttendanceRecord,
    AttendanceSyncLog,
    BreakRecord,
    EmployeeShiftAssignment,
    EmployeeWorkSchedule,
    OvertimeRecord,
    Shift,
    WorkSchedule,
)
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
    AttendanceSyncLogResponse,
    BreakRecordCreate,
    BreakRecordResponse,
    CheckInRequest,
    CheckOutRequest,
    EmployeeShiftAssignmentCreate,
    EmployeeShiftAssignmentResponse,
    EmployeeWorkScheduleCreate,
    EmployeeWorkScheduleResponse,
    OvertimeApproveRequest,
    OvertimeRecordCreate,
    OvertimeRecordResponse,
    ShiftCreate,
    ShiftResponse,
    ShiftUpdate,
    WorkScheduleCreate,
    WorkScheduleResponse,
)


def _ensure_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class AttendanceService:
    def __init__(
        self,
        record_repo: AttendanceRecordRepository,
        shift_repo: ShiftRepository,
        assignment_repo: ShiftAssignmentRepository,
        correction_repo: AttendanceCorrectionRepository,
        overtime_repo: OvertimeRecordRepository,
        device_repo: AttendanceDeviceRepository,
        schedule_repo: WorkScheduleRepository,
        break_repo: BreakRecordRepository,
    ):
        self.record_repo = record_repo
        self.shift_repo = shift_repo
        self.assignment_repo = assignment_repo
        self.correction_repo = correction_repo
        self.overtime_repo = overtime_repo
        self.device_repo = device_repo
        self.schedule_repo = schedule_repo
        self.break_repo = break_repo

    # --- Check-In & Check-Out ---
    async def check_in(self, payload: CheckInRequest) -> AttendanceRecordResponse:
        today = date.today()
        now = datetime.now(UTC)

        # 1. Prevent Duplicate Active Check-In
        existing = await self.record_repo.get_active_by_employee_and_date(
            payload.employee_id, today
        )
        if existing and existing.check_in is not None and existing.check_out is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee is already checked in for today.",
            )

        # 2. Calculate Late Minutes based on assigned shift
        late_minutes = 0
        status_str = "Present"
        assignment = await self.assignment_repo.get_by_employee_and_date(
            payload.employee_id, today
        )
        if assignment:
            shift = await self.shift_repo.get_by_id(assignment.shift_id)
            if shift:
                try:
                    shift_h, shift_m = map(int, shift.start_time.split(":"))
                    shift_start_dt = datetime.combine(
                        today, time(shift_h, shift_m)
                    ).replace(tzinfo=UTC)
                    grace_start_dt = shift_start_dt.replace(
                        minute=(shift_start_dt.minute + shift.grace_time_minutes) % 60
                    )
                    if now > grace_start_dt:
                        diff_sec = (now - shift_start_dt).total_seconds()
                        late_minutes = max(0, int(diff_sec // 60))
                        status_str = "Late"
                except Exception:
                    pass

        if existing:
            existing.check_in = now
            existing.attendance_source = payload.attendance_source
            existing.status = status_str
            existing.late_minutes = late_minutes
            if payload.remarks:
                existing.remarks = payload.remarks
            record = await self.record_repo.update(existing)
        else:
            record = AttendanceRecord(
                employee_id=payload.employee_id,
                attendance_date=today,
                check_in=now,
                late_minutes=late_minutes,
                status=status_str,
                attendance_source=payload.attendance_source,
                remarks=payload.remarks,
            )
            record = await self.record_repo.create(record)

        return AttendanceRecordResponse.model_validate(record)

    async def check_out(self, payload: CheckOutRequest) -> AttendanceRecordResponse:
        now = datetime.now(UTC)
        record = None

        if payload.attendance_record_id or payload.attendance_id:
            target_id = payload.attendance_record_id or payload.attendance_id
            record = await self.record_repo.get_by_id(target_id)
        elif payload.employee_id:
            record = await self.record_repo.get_active_by_employee_and_date(
                payload.employee_id, date.today()
            )

        if not record or not record.check_in:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Active check-in record not found.",
            )

        if record.check_out is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Check-out has already been recorded for this session.",
            )

        record.check_out = now
        if payload.remarks:
            record.remarks = payload.remarks

        # Compute worked hours
        check_in_dt = _ensure_utc(record.check_in)
        total_seconds = (now - check_in_dt).total_seconds() if check_in_dt else 0
        record.worked_hours = round(max(0.0, total_seconds / 3600.0), 2)

        # Check shift for early exit
        assignment = await self.assignment_repo.get_by_employee_and_date(
            record.employee_id, record.attendance_date
        )
        if assignment:
            shift = await self.shift_repo.get_by_id(assignment.shift_id)
            if shift:
                try:
                    end_h, end_m = map(int, shift.end_time.split(":"))
                    shift_end_dt = datetime.combine(
                        record.attendance_date, time(end_h, end_m)
                    ).replace(tzinfo=UTC)
                    if now < shift_end_dt:
                        diff_sec = (shift_end_dt - now).total_seconds()
                        record.early_exit_minutes = max(0, int(diff_sec // 60))
                except Exception:
                    pass

        updated = await self.record_repo.update(record)
        return AttendanceRecordResponse.model_validate(updated)

    async def get_attendance(self, record_id: uuid.UUID) -> AttendanceRecordResponse:
        record = await self.record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found."
            )
        return AttendanceRecordResponse.model_validate(record)

    async def list_attendance(
        self,
        employee_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status_filter: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AttendanceRecordResponse]:
        records = await self.record_repo.list(
            employee_id=employee_id,
            start_date=start_date,
            end_date=end_date,
            status=status_filter,
            skip=skip,
            limit=limit,
        )
        return [AttendanceRecordResponse.model_validate(r) for r in records]

    async def update_attendance(
        self, record_id: uuid.UUID, payload: AttendanceRecordUpdate
    ) -> AttendanceRecordResponse:
        record = await self.record_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Attendance record not found."
            )

        if payload.check_in is not None:
            record.check_in = payload.check_in
        if payload.check_out is not None:
            record.check_out = payload.check_out
        if payload.worked_hours is not None:
            record.worked_hours = payload.worked_hours
        if payload.late_minutes is not None:
            record.late_minutes = payload.late_minutes
        if payload.early_exit_minutes is not None:
            record.early_exit_minutes = payload.early_exit_minutes
        if payload.status is not None:
            record.status = payload.status
        if payload.remarks is not None:
            record.remarks = payload.remarks

        updated = await self.record_repo.update(record)
        return AttendanceRecordResponse.model_validate(updated)

    # --- Shifts & Assignments ---
    async def create_shift(self, payload: ShiftCreate) -> ShiftResponse:
        existing = await self.shift_repo.get_by_code(payload.organization_id, payload.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shift code '{payload.code}' already exists.",
            )
        shift = Shift(**payload.model_dump())
        shift = await self.shift_repo.create(shift)
        return ShiftResponse.model_validate(shift)

    async def list_shifts(self, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> list[ShiftResponse]:
        shifts = await self.shift_repo.list(org_id, skip=skip, limit=limit)
        return [ShiftResponse.model_validate(s) for s in shifts]

    async def get_shift(self, shift_id: uuid.UUID) -> ShiftResponse:
        shift = await self.shift_repo.get_by_id(shift_id)
        if not shift:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
        return ShiftResponse.model_validate(shift)

    async def update_shift(self, shift_id: uuid.UUID, payload: ShiftUpdate) -> ShiftResponse:
        shift = await self.shift_repo.get_by_id(shift_id)
        if not shift:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(shift, key, value)
        updated = await self.shift_repo.update(shift)
        return ShiftResponse.model_validate(updated)

    async def delete_shift(self, shift_id: uuid.UUID) -> ShiftResponse:
        shift = await self.shift_repo.delete(shift_id)
        if not shift:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")
        return ShiftResponse.model_validate(shift)

    async def assign_shift(
        self, payload: EmployeeShiftAssignmentCreate
    ) -> EmployeeShiftAssignmentResponse:
        assignment = EmployeeShiftAssignment(**payload.model_dump())
        assignment = await self.assignment_repo.create(assignment)
        return EmployeeShiftAssignmentResponse.model_validate(assignment)

    async def list_assignments(
        self, employee_id: uuid.UUID | None = None, skip: int = 0, limit: int = 100
    ) -> list[EmployeeShiftAssignmentResponse]:
        assignments = await self.assignment_repo.list(employee_id, skip=skip, limit=limit)
        return [EmployeeShiftAssignmentResponse.model_validate(a) for a in assignments]

    # --- Attendance Corrections ---
    async def create_correction(
        self, payload: AttendanceCorrectionCreate
    ) -> AttendanceCorrectionResponse:
        correction = AttendanceCorrection(**payload.model_dump())
        correction = await self.correction_repo.create(correction)
        return AttendanceCorrectionResponse.model_validate(correction)

    async def list_corrections(
        self, requested_by: uuid.UUID | None = None, status_filter: str | None = None
    ) -> list[AttendanceCorrectionResponse]:
        corrections = await self.correction_repo.list(requested_by=requested_by, status=status_filter)
        return [AttendanceCorrectionResponse.model_validate(c) for c in corrections]

    async def approve_correction(
        self, correction_id: uuid.UUID, payload: AttendanceCorrectionApproveRequest
    ) -> AttendanceCorrectionResponse:
        correction = await self.correction_repo.get_by_id(correction_id)
        if not correction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Correction request not found."
            )

        correction.status = payload.status
        correction.approved_by = payload.approved_by
        correction.approved_at = datetime.now(UTC)
        updated_corr = await self.correction_repo.update(correction)

        if payload.status == "Approved":
            rec = await self.record_repo.get_by_id(correction.attendance_record_id)
            if rec:
                rec.check_in = correction.new_check_in
                rec.check_out = correction.new_check_out
                req_in = _ensure_utc(correction.new_check_in)
                req_out = _ensure_utc(correction.new_check_out)
                total_sec = (req_out - req_in).total_seconds() if req_in and req_out else 0
                rec.worked_hours = round(max(0.0, total_sec / 3600.0), 2)
                await self.record_repo.update(rec)

        return AttendanceCorrectionResponse.model_validate(updated_corr)

    async def reject_correction(
        self, correction_id: uuid.UUID, payload: AttendanceCorrectionApproveRequest
    ) -> AttendanceCorrectionResponse:
        payload.status = "Rejected"
        return await self.approve_correction(correction_id, payload)

    # --- Overtime Records ---
    async def create_overtime_record(
        self, payload: OvertimeRecordCreate
    ) -> OvertimeRecordResponse:
        record = OvertimeRecord(**payload.model_dump())
        record = await self.overtime_repo.create(record)
        return OvertimeRecordResponse.model_validate(record)

    async def list_overtime_records(
        self, employee_id: uuid.UUID | None = None, approved: bool | None = None
    ) -> list[OvertimeRecordResponse]:
        records = await self.overtime_repo.list(employee_id, approved=approved)
        return [OvertimeRecordResponse.model_validate(r) for r in records]

    async def approve_overtime(
        self, record_id: uuid.UUID, payload: OvertimeApproveRequest
    ) -> OvertimeRecordResponse:
        record = await self.overtime_repo.get_by_id(record_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Overtime record not found."
            )

        record.approved = payload.approved
        record.approved_by = payload.approved_by
        record.approved_at = datetime.now(UTC)
        updated_rec = await self.overtime_repo.update(record)
        return OvertimeRecordResponse.model_validate(updated_rec)

    # --- Devices ---
    async def create_device(self, payload: AttendanceDeviceCreate) -> AttendanceDeviceResponse:
        device = AttendanceDevice(**payload.model_dump())
        device = await self.device_repo.create(device)
        return AttendanceDeviceResponse.model_validate(device)

    async def list_devices(self, org_id: uuid.UUID) -> list[AttendanceDeviceResponse]:
        devices = await self.device_repo.list(org_id)
        return [AttendanceDeviceResponse.model_validate(d) for d in devices]

    # --- Schedules ---
    async def create_schedule(self, payload: WorkScheduleCreate) -> WorkScheduleResponse:
        sched = WorkSchedule(**payload.model_dump())
        sched = await self.schedule_repo.create(sched)
        return WorkScheduleResponse.model_validate(sched)

    async def list_schedules(self, org_id: uuid.UUID) -> list[WorkScheduleResponse]:
        schedules = await self.schedule_repo.list(org_id)
        return [WorkScheduleResponse.model_validate(s) for s in schedules]

    # --- Dashboard Summary ---
    async def get_dashboard_summary(
        self, org_id: uuid.UUID, target_date: date | None = None
    ) -> AttendanceDashboardSummary:
        if not target_date:
            target_date = date.today()

        records = await self.record_repo.list(start_date=target_date, end_date=target_date)

        total_employees = len(records) if records else 10
        present_today = sum(1 for r in records if r.status == "Present")
        absent_today = sum(1 for r in records if r.status == "Absent")
        late_today = sum(1 for r in records if r.late_minutes > 0)
        on_duty_today = sum(1 for r in records if r.status == "On Duty")
        rate = (present_today / total_employees * 100.0) if total_employees > 0 else 100.0

        overtime_recs = await self.overtime_repo.list(approved=True)
        overtime_today = sum(r.hours for r in overtime_recs)

        recent = [AttendanceRecordResponse.model_validate(r) for r in records[:10]]

        return AttendanceDashboardSummary(
            total_employees=total_employees,
            present_today=present_today,
            absent_today=absent_today,
            late_today=late_today,
            overtime_today=round(overtime_today, 2),
            on_duty_today=on_duty_today,
            attendance_rate=round(rate, 1),
            recent_punches=recent,
        )


# Backward compatibility alias
WorkShiftService = AttendanceService
