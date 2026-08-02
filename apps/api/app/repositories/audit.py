import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.models.login_history import LoginHistory
from app.repositories.base import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: AsyncSession):
        super().__init__(AuditLog, db)

    async def get_by_org(self, organization_id: uuid.UUID) -> list[AuditLog]:
        stmt = (
            select(AuditLog)
            .where(
                AuditLog.organization_id == organization_id,
                AuditLog.is_deleted == False,
            )
            .order_by(AuditLog.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class LoginHistoryRepository(BaseRepository[LoginHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(LoginHistory, db)

    async def get_by_user(self, user_id: uuid.UUID) -> list[LoginHistory]:
        stmt = (
            select(LoginHistory)
            .where(LoginHistory.user_id == user_id, LoginHistory.is_deleted == False)
            .order_by(LoginHistory.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
