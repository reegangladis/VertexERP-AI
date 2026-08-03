import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory_procurement_v11 import (
    BatchNumber,
    Brand,
    GoodsReceipt,
    GoodsReceiptItem,
    InventoryAdjustment,
    InventoryTransaction,
    Product,
    ProductCategory,
    ProductImage,
    ProductVariant,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseRequest,
    PurchaseRequestItem,
    SerialNumber,
    StockLevel,
    StockMovement,
    StockTransfer,
    StockTransferItem,
    Supplier,
    SupplierContact,
    SupplierQuotation,
    SupplierQuotationItem,
    UnitOfMeasure,
    Warehouse,
    WarehouseBin,
)
from app.repositories.base import BaseRepository


class ProductCategoryRepository(BaseRepository[ProductCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductCategory, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[ProductCategory]:
        stmt = select(ProductCategory).where(
            ProductCategory.organization_id == org_id, ProductCategory.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class BrandRepository(BaseRepository[Brand]):
    def __init__(self, db: AsyncSession):
        super().__init__(Brand, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Brand]:
        stmt = select(Brand).where(
            Brand.organization_id == org_id, Brand.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class UnitOfMeasureRepository(BaseRepository[UnitOfMeasure]):
    def __init__(self, db: AsyncSession):
        super().__init__(UnitOfMeasure, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[UnitOfMeasure]:
        stmt = select(UnitOfMeasure).where(
            UnitOfMeasure.organization_id == org_id, UnitOfMeasure.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def find_by_sku(self, org_id: uuid.UUID, sku: str) -> Product | None:
        stmt = select(Product).where(
            Product.organization_id == org_id, Product.sku == sku, Product.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_barcode(self, org_id: uuid.UUID, barcode: str) -> Product | None:
        stmt = select(Product).where(
            Product.organization_id == org_id, Product.barcode == barcode, Product.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[Product]:
        stmt = select(Product).where(
            Product.organization_id == org_id, Product.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, db: AsyncSession):
        super().__init__(Warehouse, db)

    async def find_by_code(self, org_id: uuid.UUID, code: str) -> Warehouse | None:
        stmt = select(Warehouse).where(
            Warehouse.organization_id == org_id, Warehouse.warehouse_code == code, Warehouse.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[Warehouse]:
        stmt = select(Warehouse).where(
            Warehouse.organization_id == org_id, Warehouse.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class StockLevelRepository(BaseRepository[StockLevel]):
    def __init__(self, db: AsyncSession):
        super().__init__(StockLevel, db)

    async def get_by_warehouse_and_product(
        self, warehouse_id: uuid.UUID, product_id: uuid.UUID
    ) -> StockLevel | None:
        stmt = select(StockLevel).where(
            StockLevel.warehouse_id == warehouse_id,
            StockLevel.product_id == product_id,
            StockLevel.is_deleted == False,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_warehouse(self, warehouse_id: uuid.UUID) -> list[StockLevel]:
        stmt = select(StockLevel).where(
            StockLevel.warehouse_id == warehouse_id, StockLevel.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class StockTransferRepository(BaseRepository[StockTransfer]):
    def __init__(self, db: AsyncSession):
        super().__init__(StockTransfer, db)

    async def find_by_number(self, number: str) -> StockTransfer | None:
        stmt = select(StockTransfer).where(
            StockTransfer.transfer_number == number, StockTransfer.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class InventoryAdjustmentRepository(BaseRepository[InventoryAdjustment]):
    def __init__(self, db: AsyncSession):
        super().__init__(InventoryAdjustment, db)


class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession):
        super().__init__(Supplier, db)

    async def find_by_code(self, org_id: uuid.UUID, code: str) -> Supplier | None:
        stmt = select(Supplier).where(
            Supplier.organization_id == org_id, Supplier.supplier_code == code, Supplier.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[Supplier]:
        stmt = select(Supplier).where(
            Supplier.organization_id == org_id, Supplier.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(PurchaseOrder, db)

    async def get_with_items(self, po_id: uuid.UUID) -> PurchaseOrder | None:
        stmt = (
            select(PurchaseOrder)
            .options(selectinload(PurchaseOrder.items))
            .where(PurchaseOrder.id == po_id, PurchaseOrder.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_number(self, po_number: str) -> PurchaseOrder | None:
        stmt = select(PurchaseOrder).where(
            PurchaseOrder.purchase_order_number == po_number, PurchaseOrder.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class GoodsReceiptRepository(BaseRepository[GoodsReceipt]):
    def __init__(self, db: AsyncSession):
        super().__init__(GoodsReceipt, db)

    async def get_with_items(self, gr_id: uuid.UUID) -> GoodsReceipt | None:
        stmt = (
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.items))
            .where(GoodsReceipt.id == gr_id, GoodsReceipt.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()
