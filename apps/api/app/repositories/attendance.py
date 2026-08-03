import uuid
from datetime import date, datetime
from typing import Sequence
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

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


class AttendanceRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, record: AttendanceRecord) -> AttendanceRecord:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_by_id(self, record_id: uuid.UUID) -> AttendanceRecord | None:
        stmt = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.id == record_id,
                AttendanceRecord.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_active_by_employee_and_date(
        self, employee_id: uuid.UUID, attendance_date: date
    ) -> AttendanceRecord | None:
        stmt = select(AttendanceRecord).where(
            and_(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.attendance_date == attendance_date,
                AttendanceRecord.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        employee_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[AttendanceRecord]:
        conditions = [AttendanceRecord.is_deleted == False]
        if employee_id:
            conditions.append(AttendanceRecord.employee_id == employee_id)
        if start_date:
            conditions.append(AttendanceRecord.attendance_date >= start_date)
        if end_date:
            conditions.append(AttendanceRecord.attendance_date <= end_date)
        if status:
            conditions.append(AttendanceRecord.status == status)

        stmt = (
            select(AttendanceRecord)
            .where(and_(*conditions))
            .order_by(AttendanceRecord.attendance_date.desc(), AttendanceRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, record: AttendanceRecord) -> AttendanceRecord:
        await self.db.commit()
        await self.db.refresh(record)
        return record


class ShiftRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, shift: Shift) -> Shift:
        self.db.add(shift)
        await self.db.commit()
        await self.db.refresh(shift)
        return shift

    async def get_by_id(self, shift_id: uuid.UUID) -> Shift | None:
        stmt = select(Shift).where(
            and_(Shift.id == shift_id, Shift.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Shift | None:
        stmt = select(Shift).where(
            and_(
                Shift.organization_id == org_id,
                Shift.code == code,
                Shift.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[Shift]:
        stmt = (
            select(Shift)
            .where(and_(Shift.organization_id == org_id, Shift.is_deleted == False))
            .order_by(Shift.name.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, shift: Shift) -> Shift:
        await self.db.commit()
        await self.db.refresh(shift)
        return shift

    async def delete(self, shift_id: uuid.UUID) -> Shift | None:
        shift = await self.get_by_id(shift_id)
        if shift:
            shift.is_deleted = True
            await self.db.commit()
        return shift


class ShiftAssignmentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, assignment: EmployeeShiftAssignment) -> EmployeeShiftAssignment:
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        return assignment

    async def get_by_employee_and_date(
        self, employee_id: uuid.UUID, target_date: date
    ) -> EmployeeShiftAssignment | None:
        stmt = (
            select(EmployeeShiftAssignment)
            .where(
                and_(
                    EmployeeShiftAssignment.employee_id == employee_id,
                    EmployeeShiftAssignment.effective_from <= target_date,
                    EmployeeShiftAssignment.is_deleted == False,
                )
            )
            .order_by(EmployeeShiftAssignment.effective_from.desc())
        )
        res = await self.db.execute(stmt)
        assignments = res.scalars().all()
        for assign in assignments:
            if assign.effective_to is None or assign.effective_to >= target_date:
                return assign
        return None

    async def list(
        self, employee_id: uuid.UUID | None = None, skip: int = 0, limit: int = 100
    ) -> Sequence[EmployeeShiftAssignment]:
        conditions = [EmployeeShiftAssignment.is_deleted == False]
        if employee_id:
            conditions.append(EmployeeShiftAssignment.employee_id == employee_id)
        stmt = (
            select(EmployeeShiftAssignment)
            .where(and_(*conditions))
            .order_by(EmployeeShiftAssignment.effective_from.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class AttendanceCorrectionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, correction: AttendanceCorrection) -> AttendanceCorrection:
        self.db.add(correction)
        await self.db.commit()
        await self.db.refresh(correction)
        return correction

    async def get_by_id(self, correction_id: uuid.UUID) -> AttendanceCorrection | None:
        stmt = select(AttendanceCorrection).where(
            and_(
                AttendanceCorrection.id == correction_id,
                AttendanceCorrection.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        requested_by: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[AttendanceCorrection]:
        conditions = [AttendanceCorrection.is_deleted == False]
        if requested_by:
            conditions.append(AttendanceCorrection.requested_by == requested_by)
        if status:
            conditions.append(AttendanceCorrection.status == status)

        stmt = (
            select(AttendanceCorrection)
            .where(and_(*conditions))
            .order_by(AttendanceCorrection.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, correction: AttendanceCorrection) -> AttendanceCorrection:
        await self.db.commit()
        await self.db.refresh(correction)
        return correction


class OvertimeRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, record: OvertimeRecord) -> OvertimeRecord:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_by_id(self, record_id: uuid.UUID) -> OvertimeRecord | None:
        stmt = select(OvertimeRecord).where(
            and_(
                OvertimeRecord.id == record_id,
                OvertimeRecord.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(
        self,
        employee_id: uuid.UUID | None = None,
        approved: bool | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[OvertimeRecord]:
        conditions = [OvertimeRecord.is_deleted == False]
        if employee_id:
            conditions.append(OvertimeRecord.employee_id == employee_id)
        if approved is not None:
            conditions.append(OvertimeRecord.approved == approved)

        stmt = (
            select(OvertimeRecord)
            .where(and_(*conditions))
            .order_by(OvertimeRecord.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, record: OvertimeRecord) -> OvertimeRecord:
        await self.db.commit()
        await self.db.refresh(record)
        return record


class WorkScheduleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, schedule: WorkSchedule) -> WorkSchedule:
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule

    async def get_by_id(self, schedule_id: uuid.UUID) -> WorkSchedule | None:
        stmt = select(WorkSchedule).where(
            and_(WorkSchedule.id == schedule_id, WorkSchedule.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[WorkSchedule]:
        stmt = (
            select(WorkSchedule)
            .where(and_(WorkSchedule.organization_id == org_id, WorkSchedule.is_deleted == False))
            .order_by(WorkSchedule.name.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class AttendanceDeviceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, device: AttendanceDevice) -> AttendanceDevice:
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        return device

    async def get_by_id(self, device_id: uuid.UUID) -> AttendanceDevice | None:
        stmt = select(AttendanceDevice).where(
            and_(
                AttendanceDevice.id == device_id,
                AttendanceDevice.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[AttendanceDevice]:
        stmt = (
            select(AttendanceDevice)
            .where(and_(AttendanceDevice.organization_id == org_id, AttendanceDevice.is_deleted == False))
            .order_by(AttendanceDevice.device_name.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


class BreakRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, record: BreakRecord) -> BreakRecord:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def list_by_attendance(self, attendance_record_id: uuid.UUID) -> Sequence[BreakRecord]:
        stmt = select(BreakRecord).where(
            and_(
                BreakRecord.attendance_record_id == attendance_record_id,
                BreakRecord.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()


# Backward compatibility aliases
WorkShiftRepository = ShiftRepository
OvertimeRequestRepository = OvertimeRecordRepository
