"""Attendance and Shifts repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.attendance import (
    AttendanceRecord,
    AttendanceRegularization,
    Shift,
    ShiftAssignment,
)


class AttendanceRepository:
    """Repository for Shifts, Shift Assignments, Attendance, and Regularization."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Shifts
    async def get_shift(
        self, shift_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Shift | None:
        stmt = select(Shift).where(
            Shift.id == shift_id,
            Shift.tenant_id == tenant_id,
            Shift.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_shift_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Shift | None:
        stmt = select(Shift).where(
            Shift.code == code,
            Shift.tenant_id == tenant_id,
            Shift.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_shifts(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[Shift]:
        stmt = select(Shift).where(
            Shift.tenant_id == tenant_id,
            Shift.organization_id == org_id,
        )
        if is_active is not None:
            stmt = stmt.where(Shift.is_active.is_(is_active))
        stmt = stmt.order_by(Shift.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_shift(self, shift: Shift) -> Shift:
        self.session.add(shift)
        await self.session.flush()
        return shift

    async def update_shift(self, shift: Shift) -> Shift:
        shift.updated_at = datetime.now(UTC)
        shift.version += 1
        await self.session.flush()
        return shift

    # Shift Assignment
    async def get_active_assignment(
        self, employee_id: uuid.UUID, work_date: date, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ShiftAssignment | None:
        stmt = (
            select(ShiftAssignment)
            .where(
                ShiftAssignment.employee_id == employee_id,
                ShiftAssignment.tenant_id == tenant_id,
                ShiftAssignment.organization_id == org_id,
                ShiftAssignment.start_date <= work_date,
                (ShiftAssignment.end_date.is_(None)) | (ShiftAssignment.end_date >= work_date),
                ShiftAssignment.is_active.is_(True),
            )
            .order_by(ShiftAssignment.start_date.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create_assignment(self, assignment: ShiftAssignment) -> ShiftAssignment:
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    # Attendance Records
    async def get_record(
        self, record_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> AttendanceRecord | None:
        stmt = select(AttendanceRecord).where(
            AttendanceRecord.id == record_id,
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_record_by_date(
        self, employee_id: uuid.UUID, work_date: date, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> AttendanceRecord | None:
        stmt = select(AttendanceRecord).where(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.work_date == work_date,
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_records(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> Sequence[AttendanceRecord]:
        stmt = select(AttendanceRecord).where(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.organization_id == org_id,
        )
        if employee_id is not None:
            stmt = stmt.where(AttendanceRecord.employee_id == employee_id)
        if start_date is not None:
            stmt = stmt.where(AttendanceRecord.work_date >= start_date)
        if end_date is not None:
            stmt = stmt.where(AttendanceRecord.work_date <= end_date)
        stmt = stmt.order_by(AttendanceRecord.work_date.desc(), AttendanceRecord.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_record(self, record: AttendanceRecord) -> AttendanceRecord:
        self.session.add(record)
        await self.session.flush()
        return record

    async def update_record(self, record: AttendanceRecord) -> AttendanceRecord:
        record.updated_at = datetime.now(UTC)
        record.version += 1
        await self.session.flush()
        return record

    # Regularization
    async def get_regularization(
        self, reg_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> AttendanceRegularization | None:
        stmt = select(AttendanceRegularization).where(
            AttendanceRegularization.id == reg_id,
            AttendanceRegularization.tenant_id == tenant_id,
            AttendanceRegularization.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_regularization(
        self, reg: AttendanceRegularization
    ) -> AttendanceRegularization:
        self.session.add(reg)
        await self.session.flush()
        return reg

    async def list_regularizations(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, employee_id: uuid.UUID | None = None
    ) -> Sequence[AttendanceRegularization]:
        stmt = select(AttendanceRegularization).where(
            AttendanceRegularization.tenant_id == tenant_id,
            AttendanceRegularization.organization_id == org_id,
        )
        if employee_id is not None:
            stmt = stmt.where(AttendanceRegularization.employee_id == employee_id)
        stmt = stmt.order_by(AttendanceRegularization.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()
