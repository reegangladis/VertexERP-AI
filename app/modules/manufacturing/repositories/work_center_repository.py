"""Repository for Work Centers and Machines."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.manufacturing.models.work_center import Machine, WorkCenter


class WorkCenterRepository:
    """Database repository for WorkCenter and Machine entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_work_center(self, work_center: WorkCenter) -> WorkCenter:
        self.session.add(work_center)
        await self.session.flush()
        return work_center

    async def get_work_center_by_id(
        self, work_center_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> WorkCenter | None:
        stmt = (
            select(WorkCenter)
            .where(
                WorkCenter.id == work_center_id,
                WorkCenter.tenant_id == tenant_id,
                WorkCenter.organization_id == org_id,
            )
            .options(selectinload(WorkCenter.machines))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_work_center_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> WorkCenter | None:
        stmt = select(WorkCenter).where(
            WorkCenter.code == code,
            WorkCenter.tenant_id == tenant_id,
            WorkCenter.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_work_centers(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        work_center_type: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[WorkCenter], int]:
        query = select(WorkCenter).where(
            WorkCenter.tenant_id == tenant_id,
            WorkCenter.organization_id == org_id,
        )
        if work_center_type:
            query = query.where(WorkCenter.work_center_type == work_center_type)
        if status:
            query = query.where(WorkCenter.status == status)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            query.options(selectinload(WorkCenter.machines))
            .order_by(WorkCenter.code)
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    # Machine methods
    async def create_machine(self, machine: Machine) -> Machine:
        self.session.add(machine)
        await self.session.flush()
        return machine

    async def get_machine_by_id(
        self, machine_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Machine | None:
        stmt = select(Machine).where(
            Machine.id == machine_id,
            Machine.tenant_id == tenant_id,
            Machine.organization_id == org_id,
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_machines(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        work_center_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Machine]:
        stmt = select(Machine).where(
            Machine.tenant_id == tenant_id,
            Machine.organization_id == org_id,
        )
        if work_center_id:
            stmt = stmt.where(Machine.work_center_id == work_center_id)
        stmt = stmt.order_by(Machine.code).offset(offset).limit(limit)
        res = await self.session.execute(stmt)
        return res.scalars().all()

