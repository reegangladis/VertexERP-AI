import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> list[AuditLog]:
        stmt = select(AuditLog).where(
            AuditLog.organization_id == org_id, AuditLog.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
