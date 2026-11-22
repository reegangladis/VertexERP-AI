"""Account Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.finance.models.account import Account


class AccountRepository:
    """Repository for Chart of Accounts with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, account_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Account | None:
        stmt = select(Account).where(
            Account.id == account_id,
            Account.tenant_id == tenant_id,
            Account.organization_id == org_id,
            Account.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Account | None:
        stmt = select(Account).where(
            Account.code == code.upper(),
            Account.tenant_id == tenant_id,
            Account.organization_id == org_id,
            Account.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        account_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Account]:
        stmt = select(Account).where(
            Account.tenant_id == tenant_id,
            Account.organization_id == org_id,
            Account.is_deleted.is_(False),
        )
        if account_type:
            stmt = stmt.where(Account.account_type == account_type.upper())

        stmt = stmt.order_by(Account.code).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        account_type: str | None = None,
    ) -> int:
        stmt = select(func.count(Account.id)).where(
            Account.tenant_id == tenant_id,
            Account.organization_id == org_id,
            Account.is_deleted.is_(False),
        )
        if account_type:
            stmt = stmt.where(Account.account_type == account_type.upper())

        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, account: Account) -> Account:
        self.session.add(account)
        await self.session.flush()
        return account
