"""Repository for Quality Inspections."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.manufacturing.models.quality import QualityInspection


class QualityRepository:
    """Database repository for Quality Inspection records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_inspection(self, inspection: QualityInspection) -> QualityInspection:
        self.session.add(inspection)
        await self.session.flush()
        return inspection

    async def get_inspection_by_id(
        self, inspection_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> QualityInspection | None:
        stmt = select(QualityInspection).where(
            QualityInspection.id == inspection_id,
            QualityInspection.tenant_id == tenant_id,
            QualityInspection.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_inspections(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        production_order_id: uuid.UUID | None = None,
        result: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[QualityInspection], int]:
        query = select(QualityInspection).where(
            QualityInspection.tenant_id == tenant_id,
            QualityInspection.organization_id == org_id,
        )
        if production_order_id:
            query = query.where(QualityInspection.production_order_id == production_order_id)
        if result:
            query = query.where(QualityInspection.result == result)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = query.order_by(QualityInspection.inspection_date.desc()).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all(), total
