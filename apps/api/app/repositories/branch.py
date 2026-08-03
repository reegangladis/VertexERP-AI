import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.branch import Branch
from app.repositories.base import BaseRepository


class BranchRepository(BaseRepository[Branch]):
    def __init__(self, db: AsyncSession):
        super().__init__(Branch, db)

    async def get_by_org_id(self, org_id: uuid.UUID) -> list[Branch]:
        stmt = select(Branch).where(
            Branch.organization_id == org_id, Branch.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
