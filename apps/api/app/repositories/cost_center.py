import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost_center import CostCenter
from app.repositories.base import BaseRepository


class CostCenterRepository(BaseRepository[CostCenter]):
    def __init__(self, db: AsyncSession):
        super().__init__(CostCenter, db)

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> CostCenter | None:
        stmt = select(CostCenter).where(
            CostCenter.organization_id == org_id,
            CostCenter.code == code,
            CostCenter.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
