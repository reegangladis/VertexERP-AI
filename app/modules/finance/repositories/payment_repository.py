"""Payment and Allocation Repositories."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.finance.models.payment import Payment, PaymentAllocation


class PaymentRepository:
    """Repository for Payments & Allocations with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, payment_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Payment | None:
        stmt = (
            select(Payment)
            .options(selectinload(Payment.allocations))
            .where(
                Payment.id == payment_id,
                Payment.tenant_id == tenant_id,
                Payment.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, payment_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Payment | None:
        stmt = (
            select(Payment)
            .options(selectinload(Payment.allocations))
            .where(
                Payment.payment_number == payment_number,
                Payment.tenant_id == tenant_id,
                Payment.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        payment_type: str | None = None,
        partner_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Payment]:
        stmt = (
            select(Payment)
            .options(selectinload(Payment.allocations))
            .where(
                Payment.tenant_id == tenant_id,
                Payment.organization_id == org_id,
            )
        )
        if payment_type:
            stmt = stmt.where(Payment.payment_type == payment_type.upper())
        if partner_id:
            stmt = stmt.where(Payment.partner_id == partner_id)
        if status:
            stmt = stmt.where(Payment.status == status.upper())

        stmt = (
            stmt.order_by(Payment.payment_date.desc(), Payment.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        payment_type: str | None = None,
        partner_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(Payment.id)).where(
            Payment.tenant_id == tenant_id,
            Payment.organization_id == org_id,
        )
        if payment_type:
            stmt = stmt.where(Payment.payment_type == payment_type.upper())
        if partner_id:
            stmt = stmt.where(Payment.partner_id == partner_id)
        if status:
            stmt = stmt.where(Payment.status == status.upper())

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, payment: Payment) -> Payment:
        self.session.add(payment)
        await self.session.flush()
        return payment

    async def create_allocation(self, allocation: PaymentAllocation) -> PaymentAllocation:
        self.session.add(allocation)
        await self.session.flush()
        return allocation
