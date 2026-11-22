"""Bank Account and Bank Transaction Repositories."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.finance.models.bank import BankAccount, BankTransaction


class BankRepository:
    """Repository for Bank Accounts & Transactions with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_account_by_id(
        self, bank_account_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BankAccount | None:
        stmt = (
            select(BankAccount)
            .options(selectinload(BankAccount.transactions))
            .where(
                BankAccount.id == bank_account_id,
                BankAccount.tenant_id == tenant_id,
                BankAccount.organization_id == org_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_accounts_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> Sequence[BankAccount]:
        stmt = (
            select(BankAccount)
            .options(selectinload(BankAccount.transactions))
            .where(
                BankAccount.tenant_id == tenant_id,
                BankAccount.organization_id == org_id,
            )
            .order_by(BankAccount.account_name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_accounts_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(BankAccount.id)).where(
            BankAccount.tenant_id == tenant_id,
            BankAccount.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create_account(self, account: BankAccount) -> BankAccount:
        self.session.add(account)
        await self.session.flush()
        return account

    async def create_transaction(self, tx: BankTransaction) -> BankTransaction:
        self.session.add(tx)
        await self.session.flush()
        return tx

    async def list_transactions_by_account(
        self,
        bank_account_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[BankTransaction]:
        stmt = (
            select(BankTransaction)
            .where(
                BankTransaction.bank_account_id == bank_account_id,
                BankTransaction.tenant_id == tenant_id,
                BankTransaction.organization_id == org_id,
            )
            .order_by(BankTransaction.transaction_date.desc(), BankTransaction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
