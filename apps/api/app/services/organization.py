import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.base import BaseService
from app.models.organization import Organization, TenantSetting
from app.models.security_setting import SecuritySetting
from app.repositories.organization import OrganizationRepository, TenantSettingRepository, SecuritySettingRepository

class OrganizationService(BaseService[Organization, OrganizationRepository]):
    def __init__(
        self,
        repository: OrganizationRepository,
        tenant_repo: TenantSettingRepository,
        security_repo: SecuritySettingRepository
    ):
        super().__init__(repository)
        self.tenant_repo = tenant_repo
        self.security_repo = security_repo

    async def get_by_slug(self, slug: str) -> Organization | None:
        return await self.repository.get_by_slug(slug)

    async def create_organization(
        self,
        org_name: str,
        slug: str,
        email: str | None = None,
        industry: str | None = None,
        company_size: str | None = None,
        country: str | None = None,
    ) -> Organization:
        # Create Organization
        org_data: dict = {
            "name": org_name,
            "slug": slug,
            "status": "active",
        }
        if email:
            org_data["email"] = email
        if industry:
            org_data["industry"] = industry
        if company_size:
            org_data["company_size"] = company_size
        if country:
            org_data["country"] = country

        org = await self.repository.create(org_data)

        # Create Tenant Settings default
        await self.tenant_repo.create({
            "organization_id": org.id,
            "currency": "USD",
            "locale": "en_US"
        })

        # Create Security Settings default
        await self.security_repo.create({
            "organization_id": org.id,
            "password_min_length": 8,
            "password_require_uppercase": True,
            "password_require_lowercase": True,
            "password_require_numbers": True,
            "password_require_special": True,
            "password_expiry_days": 90,
            "session_idle_timeout_minutes": 30,
            "max_concurrent_sessions": 5,
            "account_lockout_threshold": 5,
            "account_lockout_duration_minutes": 15
        })

        return org


class TenantSettingService(BaseService[TenantSetting, TenantSettingRepository]):
    def __init__(self, repository: TenantSettingRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> TenantSetting | None:
        return await self.repository.get_by_org_id(org_id)


class SecuritySettingService(BaseService[SecuritySetting, SecuritySettingRepository]):
    def __init__(self, repository: SecuritySettingRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> SecuritySetting | None:
        return await self.repository.get_by_org_id(org_id)
