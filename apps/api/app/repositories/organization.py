import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, TenantSetting
from app.models.security_setting import SecuritySetting
from app.repositories.base import BaseRepository


class OrganizationRepository(BaseRepository[Organization]):
    def __init__(self, db: AsyncSession):
        super().__init__(Organization, db)

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(Organization).where(
            Organization.slug == slug, Organization.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class TenantSettingRepository(BaseRepository[TenantSetting]):
    def __init__(self, db: AsyncSession):
        super().__init__(TenantSetting, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> TenantSetting | None:
        stmt = select(TenantSetting).where(
            TenantSetting.organization_id == org_id, TenantSetting.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class SecuritySettingRepository(BaseRepository[SecuritySetting]):
    def __init__(self, db: AsyncSession):
        super().__init__(SecuritySetting, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> SecuritySetting | None:
        stmt = select(SecuritySetting).where(
            SecuritySetting.organization_id == org_id,
            SecuritySetting.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
