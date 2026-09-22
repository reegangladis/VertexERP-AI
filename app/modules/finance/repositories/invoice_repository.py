"""Invoice (AR) Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.finance.models.invoice import Invoice


class InvoiceRepository:
    """Repository for AR Invoices with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, invoice_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Invoice | None:
        stmt = (
            select(Invoice)
            .options(selectinload(Invoice.lines))
            .where(
                Invoice.id == invoice_id,
                Invoice.tenant_id == tenant_id,
                Invoice.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, invoice_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Invoice | None:
        stmt = (
            select(Invoice)
            .options(selectinload(Invoice.lines))
            .where(
                Invoice.invoice_number == invoice_number,
                Invoice.tenant_id == tenant_id,
                Invoice.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        customer_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Invoice]:
        stmt = (
            select(Invoice)
            .options(selectinload(Invoice.lines))
            .where(
                Invoice.tenant_id == tenant_id,
                Invoice.organization_id == org_id,
            )
        )
        if customer_id:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if status:
            stmt = stmt.where(Invoice.status == status.upper())

        stmt = (
            stmt.order_by(Invoice.issue_date.desc(), Invoice.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        customer_id: uuid.UUID | None = None,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(Invoice.id)).where(
            Invoice.tenant_id == tenant_id,
            Invoice.organization_id == org_id,
        )
        if customer_id:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if status:
            stmt = stmt.where(Invoice.status == status.upper())

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, invoice: Invoice) -> Invoice:
        self.session.add(invoice)
        await self.session.flush()
        return invoice
