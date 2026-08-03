import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.business_unit import BusinessUnit
from app.repositories.base import BaseRepository


class BusinessUnitRepository(BaseRepository[BusinessUnit]):
    def __init__(self, db: AsyncSession):
        super().__init__(BusinessUnit, db)

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> BusinessUnit | None:
        stmt = select(BusinessUnit).where(
            BusinessUnit.organization_id == org_id,
            BusinessUnit.code == code,
            BusinessUnit.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_org(self, org_id: uuid.UUID) -> list[BusinessUnit]:
        stmt = select(BusinessUnit).where(
            BusinessUnit.organization_id == org_id,
            BusinessUnit.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_descendants(self, business_unit_id: uuid.UUID) -> set[uuid.UUID]:
        """Returns all descendant Business Unit IDs to prevent circular hierarchy."""
        descendants = set()
        to_process = [business_unit_id]

        while to_process:
            curr_id = to_process.pop()
            stmt = select(BusinessUnit.id).where(
                BusinessUnit.parent_business_unit_id == curr_id,
                BusinessUnit.is_deleted == False,
            )
            res = await self.db.execute(stmt)
            child_ids = res.scalars().all()
            for cid in child_ids:
                if cid not in descendants:
                    descendants.add(cid)
                    to_process.append(cid)

        return descendants
