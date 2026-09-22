"""Repository for Bills of Materials (BOM), Versions, and Components."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.manufacturing.models.bom import BillOfMaterial, BOMComponent, BOMVersion


class BOMRepository:
    """Database repository for BillOfMaterial, BOMVersion, and BOMComponent entities."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_bom(self, bom: BillOfMaterial) -> BillOfMaterial:
        self.session.add(bom)
        await self.session.flush()
        return bom

    async def get_bom_by_id(
        self, bom_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BillOfMaterial | None:
        stmt = (
            select(BillOfMaterial)
            .where(
                BillOfMaterial.id == bom_id,
                BillOfMaterial.tenant_id == tenant_id,
                BillOfMaterial.organization_id == org_id,
            )
            .options(selectinload(BillOfMaterial.versions).selectinload(BOMVersion.components))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def get_default_bom_by_product(
        self, product_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BillOfMaterial | None:
        stmt = (
            select(BillOfMaterial)
            .where(
                BillOfMaterial.product_id == product_id,
                BillOfMaterial.tenant_id == tenant_id,
                BillOfMaterial.organization_id == org_id,
                BillOfMaterial.is_default.is_(True),
                BillOfMaterial.status == "ACTIVE",
            )
            .options(selectinload(BillOfMaterial.versions).selectinload(BOMVersion.components))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_boms(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        product_id: uuid.UUID | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[BillOfMaterial], int]:
        query = select(BillOfMaterial).where(
            BillOfMaterial.tenant_id == tenant_id,
            BillOfMaterial.organization_id == org_id,
        )
        if product_id:
            query = query.where(BillOfMaterial.product_id == product_id)
        if status:
            query = query.where(BillOfMaterial.status == status)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_res = await self.session.execute(count_stmt)
        total = total_res.scalar_one()

        stmt = (
            query.options(selectinload(BillOfMaterial.versions).selectinload(BOMVersion.components))
            .order_by(BillOfMaterial.code)
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all(), total

    async def get_version_by_id(
        self, version_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> BOMVersion | None:
        stmt = (
            select(BOMVersion)
            .where(
                BOMVersion.id == version_id,
                BOMVersion.tenant_id == tenant_id,
                BOMVersion.organization_id == org_id,
            )
            .options(selectinload(BOMVersion.components))
        )
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def create_version(self, version: BOMVersion) -> BOMVersion:
        self.session.add(version)
        await self.session.flush()
        return version

    async def create_component(self, component: "BOMComponent") -> "BOMComponent":
        self.session.add(component)
        await self.session.flush()
        return component

