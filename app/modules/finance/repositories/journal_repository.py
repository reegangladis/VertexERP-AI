"""Journal Entry and General Ledger Repositories."""

import uuid
from collections.abc import Sequence
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.finance.models.journal import GeneralLedger, JournalEntry


class JournalRepository:
    """Repository for double-entry Journal Entries with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, entry_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JournalEntry | None:
        stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(
                JournalEntry.id == entry_id,
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_number(
        self, entry_number: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> JournalEntry | None:
        stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(
                JournalEntry.entry_number == entry_number,
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(
                JournalEntry.tenant_id == tenant_id,
                JournalEntry.organization_id == org_id,
            )
        )
        if status:
            stmt = stmt.where(JournalEntry.status == status.upper())

        stmt = (
            stmt.order_by(JournalEntry.posting_date.desc(), JournalEntry.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        status: str | None = None,
    ) -> int:
        stmt = select(func.count(JournalEntry.id)).where(
            JournalEntry.tenant_id == tenant_id,
            JournalEntry.organization_id == org_id,
        )
        if status:
            stmt = stmt.where(JournalEntry.status == status.upper())

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, entry: JournalEntry) -> JournalEntry:
        self.session.add(entry)
        await self.session.flush()
        return entry


class GeneralLedgerRepository:
    """Repository for General Ledger transactions with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def record_gl_posting(self, gl_entry: GeneralLedger) -> GeneralLedger:
        self.session.add(gl_entry)
        await self.session.flush()
        return gl_entry

    async def list_by_journal(
        self,
        journal_entry_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Sequence[GeneralLedger]:
        stmt = (
            select(GeneralLedger)
            .where(
                GeneralLedger.journal_entry_id == journal_entry_id,
                GeneralLedger.tenant_id == tenant_id,
                GeneralLedger.organization_id == org_id,
            )
            .order_by(GeneralLedger.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_account(
        self,
        account_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        start_date: date | None = None,
        end_date: date | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[GeneralLedger]:
        stmt = select(GeneralLedger).where(
            GeneralLedger.account_id == account_id,
            GeneralLedger.tenant_id == tenant_id,
            GeneralLedger.organization_id == org_id,
        )
        if start_date:
            stmt = stmt.where(GeneralLedger.posting_date >= start_date)
        if end_date:
            stmt = stmt.where(GeneralLedger.posting_date <= end_date)

        stmt = (
            stmt.order_by(GeneralLedger.posting_date.asc(), GeneralLedger.created_at.asc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_account_totals(
        self,
        account_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        as_of_date: date | None = None,
    ) -> tuple[float, float]:
        stmt = select(
            func.coalesce(func.sum(GeneralLedger.debit), 0),
            func.coalesce(func.sum(GeneralLedger.credit), 0),
        ).where(
            GeneralLedger.account_id == account_id,
            GeneralLedger.tenant_id == tenant_id,
            GeneralLedger.organization_id == org_id,
        )
        if as_of_date:
            stmt = stmt.where(GeneralLedger.posting_date <= as_of_date)

        result = await self.session.execute(stmt)
        row = result.one()
        return float(row[0]), float(row[1])

    async def get_all_account_balances(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        as_of_date: date | None = None,
    ) -> Sequence[tuple[uuid.UUID, float, float]]:
        stmt = select(
            GeneralLedger.account_id,
            func.coalesce(func.sum(GeneralLedger.debit), 0),
            func.coalesce(func.sum(GeneralLedger.credit), 0),
        ).where(
            GeneralLedger.tenant_id == tenant_id,
            GeneralLedger.organization_id == org_id,
        )
        if as_of_date:
            stmt = stmt.where(GeneralLedger.posting_date <= as_of_date)

        stmt = stmt.group_by(GeneralLedger.account_id)
        result = await self.session.execute(stmt)
        return result.all()
