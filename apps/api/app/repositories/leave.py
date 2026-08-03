import uuid
from datetime import date
from typing import Sequence
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.leave_v6 import (
    CompOff,
    HolidayCalendar,
    HolidayEvent,
    LeaveAccrual,
    LeaveApproval,
    LeaveBalance,
    LeavePolicy,
    LeavePolicyAssignment,
    LeaveRequest,
    LeaveType,
)


class LeaveTypeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, leave_type: LeaveType) -> LeaveType:
        self.db.add(leave_type)
        await self.db.commit()
        await self.db.refresh(leave_type)
        return leave_type

    async def get_by_id(self, leave_type_id: uuid.UUID) -> LeaveType | None:
        stmt = select(LeaveType).where(
            and_(LeaveType.id == leave_type_id, LeaveType.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> LeaveType | None:
        stmt = select(LeaveType).where(
            and_(
                LeaveType.organization_id == org_id,
                LeaveType.code == code,
                LeaveType.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[LeaveType]:
        stmt = (
            select(LeaveType)
            .where(and_(LeaveType.organization_id == org_id, LeaveType.is_deleted == False))
            .order_by(LeaveType.name.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, leave_type: LeaveType) -> LeaveType:
        await self.db.commit()
        await self.db.refresh(leave_type)
        return leave_type

    async def delete(self, leave_type_id: uuid.UUID) -> LeaveType | None:
        leave_type = await self.get_by_id(leave_type_id)
        if leave_type:
            leave_type.is_deleted = True
            await self.db.commit()
        return leave_type


class LeavePolicyRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, policy: LeavePolicy) -> LeavePolicy:
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def get_by_id(self, policy_id: uuid.UUID) -> LeavePolicy | None:
        stmt = select(LeavePolicy).where(
            and_(LeavePolicy.id == policy_id, LeavePolicy.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list(self, org_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[LeavePolicy]:
        stmt = (
            select(LeavePolicy)
            .where(and_(LeavePolicy.organization_id == org_id, LeavePolicy.is_deleted == False))
            .order_by(LeavePolicy.name.asc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, policy: LeavePolicy) -> LeavePolicy:
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def delete(self, policy_id: uuid.UUID) -> LeavePolicy | None:
        policy = await self.get_by_id(policy_id)
        if policy:
            policy.is_deleted = True
            await self.db.commit()
        return policy


class LeaveBalanceRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, balance: LeaveBalance) -> LeaveBalance:
        self.db.add(balance)
        await self.db.commit()
        await self.db.refresh(balance)
        return balance

    async def get_by_id(self, balance_id: uuid.UUID) -> LeaveBalance | None:
        stmt = select(LeaveBalance).where(
            and_(LeaveBalance.id == balance_id, LeaveBalance.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_employee_and_type(
        self, employee_id: uuid.UUID, leave_type_id: uuid.UUID
    ) -> LeaveBalance | None:
        stmt = select(LeaveBalance).where(
            and_(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.leave_type_id == leave_type_id,
                LeaveBalance.is_deleted == False,
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[LeaveBalance]:
        stmt = (
            select(LeaveBalance)
            .where(and_(LeaveBalance.employee_id == employee_id, LeaveBalance.is_deleted == False))
            .order_by(LeaveBalance.created_at.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, balance: LeaveBalance) -> LeaveBalance:
        await self.db.commit()
        await self.db.refresh(balance)
        return balance


class LeaveRequestRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, request: LeaveRequest) -> LeaveRequest:
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def get_by_id(self, request_id: uuid.UUID) -> LeaveRequest | None:
        stmt = (
            select(LeaveRequest)
            .options(selectinload(LeaveRequest.approvals))
            .where(and_(LeaveRequest.id == request_id, LeaveRequest.is_deleted == False))
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def check_overlapping(
        self, employee_id: uuid.UUID, start_date: date, end_date: date
    ) -> bool:
        stmt = select(LeaveRequest).where(
            and_(
                LeaveRequest.employee_id == employee_id,
                LeaveRequest.status.in_(["Pending", "Approved"]),
                LeaveRequest.is_deleted == False,
                or_(
                    and_(LeaveRequest.start_date <= start_date, LeaveRequest.end_date >= start_date),
                    and_(LeaveRequest.start_date <= end_date, LeaveRequest.end_date >= end_date),
                    and_(LeaveRequest.start_date >= start_date, LeaveRequest.end_date <= end_date),
                ),
            )
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def list(
        self,
        employee_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[LeaveRequest]:
        conditions = [LeaveRequest.is_deleted == False]
        if employee_id:
            conditions.append(LeaveRequest.employee_id == employee_id)
        if status:
            conditions.append(LeaveRequest.status == status)

        stmt = (
            select(LeaveRequest)
            .options(selectinload(LeaveRequest.approvals))
            .where(and_(*conditions))
            .order_by(LeaveRequest.applied_at.desc())
            .offset(skip)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def update(self, request: LeaveRequest) -> LeaveRequest:
        await self.db.commit()
        await self.db.refresh(request)
        return request


class LeaveApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, approval: LeaveApproval) -> LeaveApproval:
        self.db.add(approval)
        await self.db.commit()
        await self.db.refresh(approval)
        return approval

    async def update(self, approval: LeaveApproval) -> LeaveApproval:
        await self.db.commit()
        await self.db.refresh(approval)
        return approval


class LeaveAccrualRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, accrual: LeaveAccrual) -> LeaveAccrual:
        self.db.add(accrual)
        await self.db.commit()
        await self.db.refresh(accrual)
        return accrual


class CompOffRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, comp_off: CompOff) -> CompOff:
        self.db.add(comp_off)
        await self.db.commit()
        await self.db.refresh(comp_off)
        return comp_off

    async def get_by_id(self, comp_off_id: uuid.UUID) -> CompOff | None:
        stmt = select(CompOff).where(
            and_(CompOff.id == comp_off_id, CompOff.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_by_employee(self, employee_id: uuid.UUID) -> Sequence[CompOff]:
        stmt = (
            select(CompOff)
            .where(and_(CompOff.employee_id == employee_id, CompOff.is_deleted == False))
            .order_by(CompOff.earned_date.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def delete(self, comp_off_id: uuid.UUID) -> CompOff | None:
        comp_off = await self.get_by_id(comp_off_id)
        if comp_off:
            comp_off.is_deleted = True
            await self.db.commit()
        return comp_off


class HolidayCalendarRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_calendar(self, calendar: HolidayCalendar) -> HolidayCalendar:
        self.db.add(calendar)
        await self.db.commit()
        await self.db.refresh(calendar)
        return calendar

    async def get_calendar_by_id(self, calendar_id: uuid.UUID) -> HolidayCalendar | None:
        stmt = select(HolidayCalendar).where(
            and_(HolidayCalendar.id == calendar_id, HolidayCalendar.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_calendars(self, org_id: uuid.UUID) -> Sequence[HolidayCalendar]:
        stmt = (
            select(HolidayCalendar)
            .where(and_(HolidayCalendar.organization_id == org_id, HolidayCalendar.is_deleted == False))
            .order_by(HolidayCalendar.year.desc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def create_event(self, event: HolidayEvent) -> HolidayEvent:
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def list_events_for_calendar(self, calendar_id: uuid.UUID) -> Sequence[HolidayEvent]:
        stmt = (
            select(HolidayEvent)
            .where(and_(HolidayEvent.calendar_id == calendar_id, HolidayEvent.is_deleted == False))
            .order_by(HolidayEvent.holiday_date.asc())
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def list_events_between(
        self, org_id: uuid.UUID, start_date: date, end_date: date
    ) -> Sequence[HolidayEvent]:
        stmt = (
            select(HolidayEvent)
            .join(HolidayCalendar, HolidayEvent.calendar_id == HolidayCalendar.id)
            .where(
                and_(
                    HolidayCalendar.organization_id == org_id,
                    HolidayEvent.holiday_date >= start_date,
                    HolidayEvent.holiday_date <= end_date,
                    HolidayEvent.is_deleted == False,
                )
            )
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()
