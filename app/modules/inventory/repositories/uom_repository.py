"""Unit of Measure and Category Repositories."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.category import ProductCategory
from app.modules.inventory.models.uom import UnitOfMeasure


class UomRepository:
    """Repository for Unit of Measure with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, uom_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> UnitOfMeasure | None:
        stmt = select(UnitOfMeasure).where(
            UnitOfMeasure.id == uom_id,
            UnitOfMeasure.tenant_id == tenant_id,
            UnitOfMeasure.organization_id == org_id,
            UnitOfMeasure.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> UnitOfMeasure | None:
        stmt = select(UnitOfMeasure).where(
            UnitOfMeasure.code == code.upper(),
            UnitOfMeasure.tenant_id == tenant_id,
            UnitOfMeasure.organization_id == org_id,
            UnitOfMeasure.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 100
    ) -> Sequence[UnitOfMeasure]:
        stmt = (
            select(UnitOfMeasure)
            .where(
                UnitOfMeasure.tenant_id == tenant_id,
                UnitOfMeasure.organization_id == org_id,
                UnitOfMeasure.is_deleted.is_(False),
            )
            .order_by(UnitOfMeasure.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(UnitOfMeasure.id)).where(
            UnitOfMeasure.tenant_id == tenant_id,
            UnitOfMeasure.organization_id == org_id,
            UnitOfMeasure.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, uom: UnitOfMeasure) -> UnitOfMeasure:
        self.session.add(uom)
        await self.session.flush()
        return uom


class CategoryRepository:
    """Repository for Product Category with multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, category_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductCategory | None:
        stmt = select(ProductCategory).where(
            ProductCategory.id == category_id,
            ProductCategory.tenant_id == tenant_id,
            ProductCategory.organization_id == org_id,
            ProductCategory.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_code(
        self, code: str, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> ProductCategory | None:
        stmt = select(ProductCategory).where(
            ProductCategory.code == code.upper(),
            ProductCategory.tenant_id == tenant_id,
            ProductCategory.organization_id == org_id,
            ProductCategory.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self, tenant_id: uuid.UUID, org_id: uuid.UUID, offset: int = 0, limit: int = 100
    ) -> Sequence[ProductCategory]:
        stmt = (
            select(ProductCategory)
            .where(
                ProductCategory.tenant_id == tenant_id,
                ProductCategory.organization_id == org_id,
                ProductCategory.is_deleted.is_(False),
            )
            .order_by(ProductCategory.name)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(self, tenant_id: uuid.UUID, org_id: uuid.UUID) -> int:
        stmt = select(func.count(ProductCategory.id)).where(
            ProductCategory.tenant_id == tenant_id,
            ProductCategory.organization_id == org_id,
            ProductCategory.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, category: ProductCategory) -> ProductCategory:
        self.session.add(category)
        await self.session.flush()
        return category
