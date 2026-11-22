"""Attendance and Shifts service."""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, NotFoundException, ValidationException
from app.modules.hr.models.attendance import (
    AttendanceRecord,
    AttendanceRegularization,
    Shift,
    ShiftAssignment,
)
from app.modules.hr.repositories.attendance_repository import AttendanceRepository
from app.modules.hr.repositories.employee_repository import EmployeeRepository
from app.modules.hr.schemas.attendance import (
    AttendanceClockIn,
    AttendanceClockOut,
    RegularizationCreate,
    RegularizationReviewRequest,
    ShiftAssignmentCreate,
    ShiftCreate,
)


class AttendanceService:
    """Business service for Shifts and Clock-in/out Attendance tracking."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.att_repo = AttendanceRepository(session)
        self.emp_repo = EmployeeRepository(session)

    async def _ensure_employee(
        self, employee_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> None:
        emp = await self.emp_repo.get_by_id(employee_id, tenant_id, org_id)
        if not emp:
            raise NotFoundException(f"Employee '{employee_id}' not found")

    # Shifts
    async def create_shift(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: ShiftCreate
    ) -> Shift:
        existing = await self.att_repo.get_shift_by_code(data.code, tenant_id, org_id)
        if existing:
            raise ConflictException(f"Shift with code '{data.code}' already exists")
        shift = Shift(
            tenant_id=tenant_id,
            organization_id=org_id,
            code=data.code,
            name=data.name,
            start_time=data.start_time,
            end_time=data.end_time,
            break_duration_minutes=data.break_duration_minutes,
            grace_period_minutes=data.grace_period_minutes,
            is_night_shift=data.is_night_shift,
            is_active=data.is_active,
        )
        return await self.att_repo.create_shift(shift)

    async def list_shifts(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Shift]:
        return await self.att_repo.list_shifts(tenant_id, org_id, is_active)

    async def assign_shift(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: ShiftAssignmentCreate
    ) -> ShiftAssignment:
        await self._ensure_employee(data.employee_id, tenant_id, org_id)
        shift = await self.att_repo.get_shift(data.shift_id, tenant_id, org_id)
        if not shift:
            raise NotFoundException(f"Shift '{data.shift_id}' not found")

        assignment = ShiftAssignment(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            shift_id=data.shift_id,
            start_date=data.start_date,
            end_date=data.end_date,
            is_active=data.is_active,
        )
        return await self.att_repo.create_assignment(assignment)

    # Attendance Clock In / Out
    async def clock_in(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: AttendanceClockIn
    ) -> AttendanceRecord:
        await self._ensure_employee(data.employee_id, tenant_id, org_id)
        existing = await self.att_repo.get_record_by_date(
            data.employee_id, data.work_date, tenant_id, org_id
        )
        if existing and existing.check_in_time:
            raise ConflictException(f"Employee already clocked in for {data.work_date}")

        # Determine shift assignment
        shift_assign = await self.att_repo.get_active_assignment(
            data.employee_id, data.work_date, tenant_id, org_id
        )
        shift_id = shift_assign.shift_id if shift_assign else None

        status = "PRESENT"
        if existing:
            existing.check_in_time = data.check_in_time
            existing.check_in_ip = data.check_in_ip
            existing.check_in_latitude = data.check_in_latitude
            existing.check_in_longitude = data.check_in_longitude
            existing.shift_id = shift_id
            existing.status = status
            return await self.att_repo.update_record(existing)

        record = AttendanceRecord(
            tenant_id=tenant_id,
            organization_id=org_id,
            employee_id=data.employee_id,
            shift_id=shift_id,
            work_date=data.work_date,
            check_in_time=data.check_in_time,
            check_in_ip=data.check_in_ip,
            check_in_latitude=data.check_in_latitude,
            check_in_longitude=data.check_in_longitude,
            status=status,
            verification_method=data.verification_method,
        )
        return await self.att_repo.create_record(record)

    async def clock_out(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: AttendanceClockOut
    ) -> AttendanceRecord:
        await self._ensure_employee(data.employee_id, tenant_id, org_id)
        record = await self.att_repo.get_record_by_date(
            data.employee_id, data.work_date, tenant_id, org_id
        )
        if not record or not record.check_in_time:
            raise ValidationException(
                f"Cannot clock out: No clock-in record found for {data.work_date}"
            )

        record.check_out_time = data.check_out_time
        record.check_out_ip = data.check_out_ip
        record.check_out_latitude = data.check_out_latitude
        record.check_out_longitude = data.check_out_longitude

        # Calculate worked hours with timezone safety
        in_time = record.check_in_time
        if in_time.tzinfo is None:
            in_time = in_time.replace(tzinfo=UTC)
        out_time = data.check_out_time
        if out_time.tzinfo is None:
            out_time = out_time.replace(tzinfo=UTC)

        duration_seconds = max(0.0, (out_time - in_time).total_seconds())
        total_hours = round(duration_seconds / 3600.0, 2)

        # Standard 8-hour benchmark
        regular_hours = min(8.0, total_hours)
        overtime_hours = max(0.0, total_hours - 8.0)

        record.regular_hours = regular_hours
        record.overtime_hours = overtime_hours
        if overtime_hours > 0:
            record.status = "OVERTIME"
        elif total_hours < 4.0:
            record.status = "HALF_DAY"

        return await self.att_repo.update_record(record)

    async def list_records(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[AttendanceRecord]:
        return await self.att_repo.list_records(
            tenant_id, org_id, employee_id, start_date, end_date
        )

    # Regularization
    async def request_regularization(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, data: RegularizationCreate
    ) -> AttendanceRegularization:
        await self._ensure_employee(data.employee_id, tenant_id, org_id)
        record = await self.att_repo.get_record(data.attendance_record_id, tenant_id, org_id)
        if not record:
            raise NotFoundException(f"Attendance record '{data.attendance_record_id}' not found")

        reg = AttendanceRegularization(
            tenant_id=tenant_id,
            organization_id=org_id,
            attendance_record_id=data.attendance_record_id,
            employee_id=data.employee_id,
            requested_check_in=data.requested_check_in,
            requested_check_out=data.requested_check_out,
            reason=data.reason,
            status="PENDING",
        )
        return await self.att_repo.create_regularization(reg)

    async def review_regularization(
        self,
        reg_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        data: RegularizationReviewRequest,
    ) -> AttendanceRegularization:
        reg = await self.att_repo.get_regularization(reg_id, tenant_id, org_id)
        if not reg:
            raise NotFoundException(f"Regularization request '{reg_id}' not found")

        reg.status = data.status
        reg.approver_id = user_id
        reg.approved_at = datetime.now(UTC)
        reg.remarks = data.remarks

        if data.status == "APPROVED":
            record = await self.att_repo.get_record(reg.attendance_record_id, tenant_id, org_id)
            if record:
                if reg.requested_check_in:
                    record.check_in_time = reg.requested_check_in
                if reg.requested_check_out:
                    record.check_out_time = reg.requested_check_out
                record.status = "PRESENT"
                await self.att_repo.update_record(record)

        await self.session.flush()
        return reg

    async def list_regularizations(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, employee_id: uuid.UUID | None = None
    ) -> Sequence[AttendanceRegularization]:
        return await self.att_repo.list_regularizations(tenant_id, org_id, employee_id)
