import uuid

from app.models.scheduled_job import ScheduledJob
from app.repositories.scheduled_job import ScheduledJobRepository
from app.services.base import BaseService


class ScheduledJobService(BaseService[ScheduledJob, ScheduledJobRepository]):
    def __init__(self, repository: ScheduledJobRepository):
        super().__init__(repository)

    async def get_by_org(self, org_id: uuid.UUID) -> list[ScheduledJob]:
        return await self.repository.get_by_org_id(org_id)
