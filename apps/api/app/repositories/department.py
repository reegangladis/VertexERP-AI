import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.repositories.base import BaseRepository


class DepartmentRepository(BaseRepository[Department]):
    def __init__(self, db: AsyncSession):
        super().__init__(Department, db)

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Department | None:
        stmt = select(Department).where(
            Department.organization_id == org_id,
            Department.code == code,
            Department.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_by_org(self, org_id: uuid.UUID) -> list[Department]:
        stmt = select(Department).where(
            Department.organization_id == org_id,
            Department.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_descendants(self, department_id: uuid.UUID) -> set[uuid.UUID]:
        """Returns all descendant department IDs to prevent circular assignment."""
        descendants = set()
        to_process = [department_id]

        while to_process:
            curr_id = to_process.pop()
            stmt = select(Department.id).where(
                Department.parent_department_id == curr_id,
                Department.is_deleted == False,
            )
            res = await self.db.execute(stmt)
            child_ids = res.scalars().all()
            for cid in child_ids:
                if cid not in descendants:
                    descendants.add(cid)
                    to_process.append(cid)

        return descendants
