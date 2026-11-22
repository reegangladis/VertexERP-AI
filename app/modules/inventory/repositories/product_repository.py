"""Product Repository."""

import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.models.product import Product


class ProductRepository:
    """Repository for Product / SKU Master with strict multi-tenant isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(
        self, product_id: uuid.UUID, tenant_id: uuid.UUID, org_id: uuid.UUID
    ) -> Product | None:
        stmt = select(Product).where(
            Product.id == product_id,
            Product.tenant_id == tenant_id,
            Product.organization_id == org_id,
            Product.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_sku(self, sku: str, tenant_id: uuid.UUID, org_id: uuid.UUID) -> Product | None:
        stmt = select(Product).where(
            Product.sku == sku.upper(),
            Product.tenant_id == tenant_id,
            Product.organization_id == org_id,
            Product.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> Sequence[Product]:
        stmt = select(Product).where(
            Product.tenant_id == tenant_id,
            Product.organization_id == org_id,
            Product.is_deleted.is_(False),
        )
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if search:
            stmt = stmt.where(
                (Product.name.ilike(f"%{search}%"))
                | (Product.sku.ilike(f"%{search}%"))
                | (Product.barcode.ilike(f"%{search}%"))
            )
        stmt = stmt.order_by(Product.name).offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_org(
        self,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        category_id: uuid.UUID | None = None,
        search: str | None = None,
    ) -> int:
        stmt = select(func.count(Product.id)).where(
            Product.tenant_id == tenant_id,
            Product.organization_id == org_id,
            Product.is_deleted.is_(False),
        )
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if search:
            stmt = stmt.where(
                (Product.name.ilike(f"%{search}%"))
                | (Product.sku.ilike(f"%{search}%"))
                | (Product.barcode.ilike(f"%{search}%"))
            )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def create(self, product: Product) -> Product:
        self.session.add(product)
        await self.session.flush()
        return product
