import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.designation import Designation
from app.repositories.base import BaseRepository


class DesignationRepository(BaseRepository[Designation]):
    def __init__(self, db: AsyncSession):
        super().__init__(Designation, db)

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Designation | None:
        stmt = select(Designation).where(
            Designation.organization_id == org_id,
            Designation.code == code,
            Designation.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
