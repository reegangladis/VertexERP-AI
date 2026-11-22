"""Organization and Tenant management service."""

import uuid
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictException, ForbiddenException, NotFoundException
from app.infrastructure.database.session import set_tenant_context
from app.modules.organization.models.organization import Organization, TenantMembership
from app.modules.organization.models.tenant import Tenant
from app.modules.organization.repositories.organization_repository import (
    MembershipRepository,
    OrganizationRepository,
)
from app.modules.organization.schemas.organization import OrganizationCreate


class OrganizationService:
    """Business logic for Tenant and Organization lifecycle and memberships."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.org_repo = OrganizationRepository(session)
        self.membership_repo = MembershipRepository(session)

    async def create_tenant_with_default_org(
        self,
        tenant_name: str,
        tenant_slug: str,
        org_name: str,
        legal_name: str,
        tax_identifier: str,
        base_currency: str = "USD",
        fiscal_year_start_month: int = 1,
    ) -> tuple[Tenant, Organization]:
        """Provisions a new Tenant and its initial primary Organization."""
        existing_tenant = await self.org_repo.get_tenant_by_slug(tenant_slug)
        if existing_tenant:
            raise ConflictException(f"Tenant slug '{tenant_slug}' is already registered")

        tenant = Tenant(
            name=tenant_name,
            slug=tenant_slug,
        )
        await self.org_repo.create_tenant(tenant)

        # Establish the tenant context before creating the first tenant-owned
        # organization; this is required when PostgreSQL RLS is enforced.
        await set_tenant_context(self.session, tenant.id)

        org = Organization(
            tenant_id=tenant.id,
            name=org_name,
            legal_name=legal_name,
            tax_identifier=tax_identifier,
            base_currency=base_currency,
            fiscal_year_start_month=fiscal_year_start_month,
        )
        await self.org_repo.create_org(org)

        return tenant, org

    async def create_organization(
        self, tenant_id: uuid.UUID, org_in: OrganizationCreate
    ) -> Organization:
        """Creates a new Organization inside an existing Tenant."""
        tenant = await self.org_repo.get_tenant_by_id(tenant_id)
        if not tenant:
            raise NotFoundException(f"Tenant '{tenant_id}' not found")

        org = Organization(
            tenant_id=tenant_id,
            name=org_in.name,
            legal_name=org_in.legal_name,
            tax_identifier=org_in.tax_identifier,
            base_currency=org_in.base_currency,
            fiscal_year_start_month=org_in.fiscal_year_start_month,
            website=org_in.website,
        )
        return await self.org_repo.create_org(org)

    async def get_organization(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> Organization:
        """Retrieves an organization ensuring tenant isolation."""
        org = await self.org_repo.get_org_by_id(org_id, tenant_id)
        if not org:
            raise NotFoundException(f"Organization '{org_id}' not found in this tenant")
        return org

    async def list_organizations(self, tenant_id: uuid.UUID) -> Sequence[Organization]:
        """Lists all active organizations within a tenant."""
        return await self.org_repo.list_orgs_by_tenant(tenant_id)

    async def add_membership(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        is_default: bool = False,
    ) -> TenantMembership:
        """Grants a user membership to an organization under a tenant."""
        org = await self.get_organization(tenant_id, org_id)
        existing = await self.membership_repo.get_membership(tenant_id, user_id, org.id)
        if existing:
            return existing

        membership = TenantMembership(
            tenant_id=tenant_id,
            user_id=user_id,
            organization_id=org_id,
            is_default=is_default,
        )
        return await self.membership_repo.create_membership(membership)

    async def get_user_memberships(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[TenantMembership]:
        """Lists all organizations a user has membership in."""
        return await self.membership_repo.list_user_memberships(tenant_id, user_id)

    async def verify_membership(
        self, tenant_id: uuid.UUID, user_id: uuid.UUID, org_id: uuid.UUID
    ) -> TenantMembership:
        """Verifies that the user belongs to the given organization."""
        membership = await self.membership_repo.get_membership(tenant_id, user_id, org_id)
        if not membership:
            raise ForbiddenException("User does not have access to this organization")
        return membership
