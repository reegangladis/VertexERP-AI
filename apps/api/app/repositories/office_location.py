import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.office_location import OfficeLocation
from app.repositories.base import BaseRepository


class OfficeLocationRepository(BaseRepository[OfficeLocation]):
    def __init__(self, db: AsyncSession):
        super().__init__(OfficeLocation, db)

    async def get_all_by_org(self, org_id: uuid.UUID) -> list[OfficeLocation]:
        stmt = select(OfficeLocation).where(
            OfficeLocation.organization_id == org_id,
            OfficeLocation.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
