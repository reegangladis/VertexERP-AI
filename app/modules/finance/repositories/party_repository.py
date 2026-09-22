"""Customer and Vendor Party Repositories."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.finance.models.party import CustomerParty, VendorParty


class CustomerPartyRepository:
    """Repository for Financial Customers with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, customer_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> CustomerParty | None:
        stmt = select(CustomerParty).where(
            CustomerParty.id == customer_id,
            CustomerParty.tenant_id == tenant_id,
            CustomerParty.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> CustomerParty | None:
        stmt = select(CustomerParty).where(
            CustomerParty.code == code.upper(),
            CustomerParty.tenant_id == tenant_id,
            CustomerParty.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> Sequence[CustomerParty]:
        stmt = (
            select(CustomerParty)
            .where(
                CustomerParty.tenant_id == tenant_id,
                CustomerParty.organization_id == org_id,
            )
            .order_by(CustomerParty.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(CustomerParty.id)).where(
            CustomerParty.tenant_id == tenant_id,
            CustomerParty.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, customer: CustomerParty) -> CustomerParty:
        self.session.add(customer)
        await self.session.flush()
        return customer


class VendorPartyRepository:
    """Repository for Financial Vendors with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, vendor_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> VendorParty | None:
        stmt = select(VendorParty).where(
            VendorParty.id == vendor_id,
            VendorParty.tenant_id == tenant_id,
            VendorParty.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> VendorParty | None:
        stmt = select(VendorParty).where(
            VendorParty.code == code.upper(),
            VendorParty.tenant_id == tenant_id,
            VendorParty.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 50
    ) -> Sequence[VendorParty]:
        stmt = (
            select(VendorParty)
            .where(
                VendorParty.tenant_id == tenant_id,
                VendorParty.organization_id == org_id,
            )
            .order_by(VendorParty.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(VendorParty.id)).where(
            VendorParty.tenant_id == tenant_id,
            VendorParty.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, vendor: VendorParty) -> VendorParty:
        self.session.add(vendor)
        await self.session.flush()
        return vendor
