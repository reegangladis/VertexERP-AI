import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.inventory_product import ProductCategory, Brand, Unit, Product, ProductVariant, SerialNumber, BatchNumber
from app.models.inventory_warehouse import Warehouse, WarehouseBin, StockLevel
from app.models.inventory_supplier import Supplier, SupplierContact
from app.models.inventory_purchase import PurchaseRequest, PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from app.models.inventory_transaction import InventoryTransaction, StockMovement, InventoryAdjustment, InventoryCount

class ProductCategoryRepository(BaseRepository[ProductCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductCategory, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[ProductCategory]:
        stmt = select(ProductCategory).where(ProductCategory.organization_id == org_id, ProductCategory.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class BrandRepository(BaseRepository[Brand]):
    def __init__(self, db: AsyncSession):
        super().__init__(Brand, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Brand]:
        stmt = select(Brand).where(Brand.organization_id == org_id, Brand.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class UnitRepository(BaseRepository[Unit]):
    def __init__(self, db: AsyncSession):
        super().__init__(Unit, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Unit]:
        stmt = select(Unit).where(Unit.organization_id == org_id, Unit.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Product]:
        stmt = select(Product).where(Product.organization_id == org_id, Product.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class ProductVariantRepository(BaseRepository[ProductVariant]):
    def __init__(self, db: AsyncSession):
        super().__init__(ProductVariant, db)

class SerialNumberRepository(BaseRepository[SerialNumber]):
    def __init__(self, db: AsyncSession):
        super().__init__(SerialNumber, db)

class BatchNumberRepository(BaseRepository[BatchNumber]):
    def __init__(self, db: AsyncSession):
        super().__init__(BatchNumber, db)

class WarehouseRepository(BaseRepository[Warehouse]):
    def __init__(self, db: AsyncSession):
        super().__init__(Warehouse, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Warehouse]:
        stmt = select(Warehouse).where(Warehouse.organization_id == org_id, Warehouse.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class WarehouseBinRepository(BaseRepository[WarehouseBin]):
    def __init__(self, db: AsyncSession):
        super().__init__(WarehouseBin, db)

class StockLevelRepository(BaseRepository[StockLevel]):
    def __init__(self, db: AsyncSession):
        super().__init__(StockLevel, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[StockLevel]:
        stmt = select(StockLevel).where(StockLevel.organization_id == org_id, StockLevel.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class SupplierRepository(BaseRepository[Supplier]):
    def __init__(self, db: AsyncSession):
        super().__init__(Supplier, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Supplier]:
        stmt = select(Supplier).where(Supplier.organization_id == org_id, Supplier.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class SupplierContactRepository(BaseRepository[SupplierContact]):
    def __init__(self, db: AsyncSession):
        super().__init__(SupplierContact, db)

class PurchaseRequestRepository(BaseRepository[PurchaseRequest]):
    def __init__(self, db: AsyncSession):
        super().__init__(PurchaseRequest, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[PurchaseRequest]:
        stmt = select(PurchaseRequest).where(PurchaseRequest.organization_id == org_id, PurchaseRequest.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class PurchaseOrderRepository(BaseRepository[PurchaseOrder]):
    def __init__(self, db: AsyncSession):
        super().__init__(PurchaseOrder, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[PurchaseOrder]:
        stmt = select(PurchaseOrder).where(PurchaseOrder.organization_id == org_id, PurchaseOrder.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class PurchaseOrderItemRepository(BaseRepository[PurchaseOrderItem]):
    def __init__(self, db: AsyncSession):
        super().__init__(PurchaseOrderItem, db)

class GoodsReceiptRepository(BaseRepository[GoodsReceipt]):
    def __init__(self, db: AsyncSession):
        super().__init__(GoodsReceipt, db)

class InventoryTransactionRepository(BaseRepository[InventoryTransaction]):
    def __init__(self, db: AsyncSession):
        super().__init__(InventoryTransaction, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[InventoryTransaction]:
        stmt = select(InventoryTransaction).where(InventoryTransaction.organization_id == org_id, InventoryTransaction.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class StockMovementRepository(BaseRepository[StockMovement]):
    def __init__(self, db: AsyncSession):
        super().__init__(StockMovement, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[StockMovement]:
        stmt = select(StockMovement).where(StockMovement.organization_id == org_id, StockMovement.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class InventoryAdjustmentRepository(BaseRepository[InventoryAdjustment]):
    def __init__(self, db: AsyncSession):
        super().__init__(InventoryAdjustment, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[InventoryAdjustment]:
        stmt = select(InventoryAdjustment).where(InventoryAdjustment.organization_id == org_id, InventoryAdjustment.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

class InventoryCountRepository(BaseRepository[InventoryCount]):
    def __init__(self, db: AsyncSession):
        super().__init__(InventoryCount, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[InventoryCount]:
        stmt = select(InventoryCount).where(InventoryCount.organization_id == org_id, InventoryCount.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
