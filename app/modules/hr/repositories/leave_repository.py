"""Leave repository."""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.hr.models.leave import (
    LeaveBalance,
    LeavePolicy,
    LeaveRequest,
    LeaveType,
)


class LeaveRepository:
    """Repository for Leave Types, Policies, Balances, and Requests."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Leave Types
    async def get_type(
        self, type_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> LeaveType | None:
        stmt = select(LeaveType).where(
            LeaveType.id == type_id,
            LeaveType.tenant_id == tenant_id,
            LeaveType.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_type_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> LeaveType | None:
        stmt = select(LeaveType).where(
            LeaveType.code == code,
            LeaveType.tenant_id == tenant_id,
            LeaveType.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_types(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, is_active: bool | None = None
    ) -> Sequence[LeaveType]:
        stmt = select(LeaveType).where(
            LeaveType.tenant_id == tenant_id,
            LeaveType.organization_id == org_id,
        )
        if is_active is not None:
            stmt = stmt.where(LeaveType.is_active.is_(is_active))
        stmt = stmt.order_by(LeaveType.name.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_type(self, leave_type: LeaveType) -> LeaveType:
        self.session.add(leave_type)
        await self.session.flush()
        return leave_type

    # Policy
    async def get_policy(
        self, leave_type_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> LeavePolicy | None:
        stmt = select(LeavePolicy).where(
            LeavePolicy.leave_type_id == leave_type_id,
            LeavePolicy.tenant_id == tenant_id,
            LeavePolicy.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_policy(self, policy: LeavePolicy) -> LeavePolicy:
        self.session.add(policy)
        await self.session.flush()
        return policy

    # Balance
    async def get_balance(
        self,
        employee_id: uuid.UUID,
        leave_type_id: uuid.UUID,
        fiscal_year: int,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> LeaveBalance | None:
        stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.leave_type_id == leave_type_id,
            LeaveBalance.fiscal_year == fiscal_year,
            LeaveBalance.tenant_id == tenant_id,
            LeaveBalance.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_balances_for_employee(
        self, employee_id: uuid.UUID, fiscal_year: int, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Sequence[LeaveBalance]:
        stmt = select(LeaveBalance).where(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.fiscal_year == fiscal_year,
            LeaveBalance.tenant_id == tenant_id,
            LeaveBalance.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_balance(self, balance: LeaveBalance) -> LeaveBalance:
        self.session.add(balance)
        await self.session.flush()
        return balance

    async def update_balance(self, balance: LeaveBalance) -> LeaveBalance:
        balance.updated_at = datetime.now(UTC)
        await self.session.flush()
        return balance

    # Leave Requests
    async def get_request(
        self, request_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> LeaveRequest | None:
        stmt = select(LeaveRequest).where(
            LeaveRequest.id == request_id,
            LeaveRequest.tenant_id == tenant_id,
            LeaveRequest.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_requests(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        employee_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> Sequence[LeaveRequest]:
        stmt = select(LeaveRequest).where(
            LeaveRequest.tenant_id == tenant_id,
            LeaveRequest.organization_id == org_id,
        )
        if employee_id is not None:
            stmt = stmt.where(LeaveRequest.employee_id == employee_id)
        if status is not None:
            stmt = stmt.where(LeaveRequest.status == status)
        stmt = stmt.order_by(LeaveRequest.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_request(self, req: LeaveRequest) -> LeaveRequest:
        self.session.add(req)
        await self.session.flush()
        return req

    async def update_request(self, req: LeaveRequest) -> LeaveRequest:
        req.updated_at = datetime.now(UTC)
        req.version += 1
        await self.session.flush()
        return req
