import uuid

from fastapi import HTTPException, status

from app.models.organization import (
    Organization,
    OrganizationMetadata,
    OrganizationSetting,
    TenantSetting,
)
from app.models.security_setting import SecuritySetting
from app.repositories.organization import (
    OrganizationMetadataRepository,
    OrganizationRepository,
    OrganizationSettingRepository,
    SecuritySettingRepository,
    TenantSettingRepository,
)
from app.schemas.org_metadata import OrganizationMetadataUpdate
from app.schemas.org_setting import OrganizationSettingUpdate
from app.schemas.organization import OrganizationCreate, OrganizationUpdate
from app.schemas.security_setting import SecuritySettingUpdate
from app.schemas.tenant_setting import TenantSettingUpdate
from app.services.base import BaseService


class OrganizationService(BaseService[Organization, OrganizationRepository]):
    def __init__(self, repository: OrganizationRepository):
        super().__init__(repository)

    async def create_organization(self, obj_in: OrganizationCreate) -> Organization:
        existing = await self.repository.get_by_slug(obj_in.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization with slug '{obj_in.slug}' already exists.",
            )
        return await self.repository.create(obj_in)

    async def get_by_slug(self, slug: str) -> Organization:
        org = await self.repository.get_by_slug(slug)
        if not org:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Organization with slug '{slug}' not found.",
            )
        return org


class TenantSettingService(BaseService[TenantSetting, TenantSettingRepository]):
    def __init__(self, repository: TenantSettingRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> TenantSetting:
        setting = await self.repository.get_by_org_id(org_id)
        if not setting:
            # Create default tenant setting if not exists
            setting = await self.repository.create(
                {"organization_id": org_id, "currency": "USD", "locale": "en_US"}
            )
        return setting

    async def update_by_org_id(
        self, org_id: uuid.UUID, obj_in: TenantSettingUpdate
    ) -> TenantSetting:
        setting = await self.get_by_org_id(org_id)
        return await self.repository.update(setting, obj_in)


class OrganizationSettingService(
    BaseService[OrganizationSetting, OrganizationSettingRepository]
):
    def __init__(self, repository: OrganizationSettingRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> OrganizationSetting:
        setting = await self.repository.get_by_org_id(org_id)
        if not setting:
            setting = await self.repository.create(
                {"organization_id": org_id, "default_currency": "USD", "timezone": "UTC"}
            )
        return setting

    async def update_by_org_id(
        self, org_id: uuid.UUID, obj_in: OrganizationSettingUpdate
    ) -> OrganizationSetting:
        setting = await self.get_by_org_id(org_id)
        return await self.repository.update(setting, obj_in)


class OrganizationMetadataService(
    BaseService[OrganizationMetadata, OrganizationMetadataRepository]
):
    def __init__(self, repository: OrganizationMetadataRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> OrganizationMetadata:
        meta = await self.repository.get_by_org_id(org_id)
        if not meta:
            meta = await self.repository.create({"organization_id": org_id})
        return meta

    async def update_by_org_id(
        self, org_id: uuid.UUID, obj_in: OrganizationMetadataUpdate
    ) -> OrganizationMetadata:
        meta = await self.get_by_org_id(org_id)
        return await self.repository.update(meta, obj_in)


class SecuritySettingService(
    BaseService[SecuritySetting, SecuritySettingRepository]
):
    def __init__(self, repository: SecuritySettingRepository):
        super().__init__(repository)

    async def get_by_org_id(self, org_id: uuid.UUID) -> SecuritySetting:
        setting = await self.repository.get_by_org_id(org_id)
        if not setting:
            setting = await self.repository.create({"organization_id": org_id})
        return setting

    async def update_by_org_id(
        self, org_id: uuid.UUID, obj_in: SecuritySettingUpdate
    ) -> SecuritySetting:
        setting = await self.get_by_org_id(org_id)
        return await self.repository.update(setting, obj_in)
