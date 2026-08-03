import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.integration_observability_v16 import (
    APIKey,
    BackupJob,
    DeploymentHistory,
    EventBus,
    Notification,
    SecurityAudit,
    ServiceHealth,
    SystemMetric,
    Webhook,
)
from app.repositories.base import BaseRepository


class APIKeyRepository(BaseRepository[APIKey]):
    def __init__(self, db: AsyncSession):
        super().__init__(APIKey, db)

    async def find_by_key(self, api_key: str) -> APIKey | None:
        stmt = select(APIKey).where(APIKey.api_key == api_key, APIKey.is_deleted == False)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[APIKey]:
        stmt = select(APIKey).where(
            APIKey.organization_id == org_id, APIKey.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class WebhookRepository(BaseRepository[Webhook]):
    def __init__(self, db: AsyncSession):
        super().__init__(Webhook, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Webhook]:
        stmt = select(Webhook).where(
            Webhook.organization_id == org_id, Webhook.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class EventBusRepository(BaseRepository[EventBus]):
    def __init__(self, db: AsyncSession):
        super().__init__(EventBus, db)


class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, db: AsyncSession):
        super().__init__(Notification, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Notification]:
        stmt = select(Notification).where(
            Notification.organization_id == org_id, Notification.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ServiceHealthRepository(BaseRepository[ServiceHealth]):
    def __init__(self, db: AsyncSession):
        super().__init__(ServiceHealth, db)


class SystemMetricRepository(BaseRepository[SystemMetric]):
    def __init__(self, db: AsyncSession):
        super().__init__(SystemMetric, db)


class DeploymentHistoryRepository(BaseRepository[DeploymentHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(DeploymentHistory, db)


class BackupJobRepository(BaseRepository[BackupJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(BackupJob, db)


class SecurityAuditRepository(BaseRepository[SecurityAudit]):
    def __init__(self, db: AsyncSession):
        super().__init__(SecurityAudit, db)
