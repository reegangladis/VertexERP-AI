import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.scheduled_job import ScheduledJob
from app.repositories.base import BaseRepository


class ScheduledJobRepository(BaseRepository[ScheduledJob]):
    def __init__(self, db: AsyncSession):
        super().__init__(ScheduledJob, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> list[ScheduledJob]:
        stmt = select(ScheduledJob).where(
            ScheduledJob.organization_id == org_id, ScheduledJob.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
