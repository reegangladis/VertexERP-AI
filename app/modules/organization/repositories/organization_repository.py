"""Repositories for Organization and Tenant persistence."""

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.organization.models.organization import Organization, TenantMembership
from app.modules.organization.models.tenant import Tenant


class OrganizationRepository:
    """Data access repository for Organizations and Tenants."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_tenant_by_id(self, tenant_id: uuid.UUID) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.id == tenant_id, Tenant.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tenant_by_slug(self, slug: str) -> Tenant | None:
        stmt = select(Tenant).where(Tenant.slug == slug, Tenant.is_deleted.is_(False))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_tenant(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        await self.session.flush()
        return tenant

    async def get_org_by_id(self, org_id: uuid.UUID, tenant_id: uuid.UUID) -> Organization | None:
        stmt = select(Organization).where(
            Organization.id == org_id,
            Organization.tenant_id == tenant_id,
            Organization.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_orgs_by_tenant(self, tenant_id: uuid.UUID) -> Sequence[Organization]:
        stmt = (
            select(Organization)
            .where(Organization.tenant_id == tenant_id, Organization.is_deleted.is_(False))
            .order_by(Organization.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_org(self, org: Organization) -> Organization:
        self.session.add(org)
        await self.session.flush()
        return org


class MembershipRepository:
    """Data access repository for Tenant Memberships."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_membership(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> TenantMembership | None:
        stmt = select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == user_id,
            TenantMembership.organization_id == org_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_memberships(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[TenantMembership]:
        stmt = select(TenantMembership).where(
            TenantMembership.tenant_id == tenant_id,
            TenantMembership.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create_membership(self, membership: TenantMembership) -> TenantMembership:
        self.session.add(membership)
        await self.session.flush()
        return membership
