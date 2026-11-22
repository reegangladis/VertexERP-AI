"""Vendor Bill (AP) Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.finance.models.bill import Bill


class BillRepository:
    """Repository for AP Bills with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, bill_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Bill | None:
        stmt = (
            select(Bill)
            .options(selectinload(Bill.lines))
            .where(
                Bill.id == bill_id,
                Bill.tenant_id == tenant_id,
                Bill.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, bill_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Bill | None:
        stmt = (
            select(Bill)
            .options(selectinload(Bill.lines))
            .where(
                Bill.bill_number == bill_number,
                Bill.tenant_id == tenant_id,
                Bill.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        vendor_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Bill]:
        stmt = (
            select(Bill)
            .options(selectinload(Bill.lines))
            .where(
                Bill.tenant_id == tenant_id,
                Bill.organization_id == org_id,
            )
        )
        if vendor_id:
            stmt = stmt.where(Bill.vendor_id == vendor_id)
        if status:
            stmt = stmt.where(Bill.status == status.upper())

        stmt = (
            stmt.order_by(Bill.bill_date.desc(), Bill.created_at.desc()).offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        vendor_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(Bill.id)).where(
            Bill.tenant_id == tenant_id,
            Bill.organization_id == org_id,
        )
        if vendor_id:
            stmt = stmt.where(Bill.vendor_id == vendor_id)
        if status:
            stmt = stmt.where(Bill.status == status.upper())

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, bill: Bill) -> Bill:
        self.session.add(bill)
        await self.session.flush()
        return bill
