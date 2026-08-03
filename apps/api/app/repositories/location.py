import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.location import Location
from app.repositories.base import BaseRepository


class LocationRepository(BaseRepository[Location]):
    def __init__(self, db: AsyncSession):
        super().__init__(Location, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> list[Location]:
        stmt = select(Location).where(
            Location.organization_id == org_id, Location.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
