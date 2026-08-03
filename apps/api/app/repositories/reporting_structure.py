import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reporting_structure import ReportingStructure
from app.repositories.base import BaseRepository


class ReportingStructureRepository(BaseRepository[ReportingStructure]):
    def __init__(self, db: AsyncSession):
        super().__init__(ReportingStructure, db)

    async def get_by_employee(self, org_id: uuid.UUID, employee_uuid: uuid.UUID) -> list[ReportingStructure]:
        stmt = select(ReportingStructure).where(
            ReportingStructure.organization_id == org_id,
            ReportingStructure.employee_uuid == employee_uuid,
            ReportingStructure.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
