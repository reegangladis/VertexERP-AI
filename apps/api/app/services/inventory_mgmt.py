import uuid
import csv
import io
from typing import List, Optional, Any, Dict
from sqlalchemy import select
from app.services.base import BaseService
from app.repositories.inventory_mgmt import (
    ProductCategoryRepository,
    BrandRepository,
    UnitRepository,
    ProductRepository,
    ProductVariantRepository,
    SerialNumberRepository,
    BatchNumberRepository,
    WarehouseRepository,
    WarehouseBinRepository,
    StockLevelRepository,
    SupplierRepository,
    SupplierContactRepository,
    PurchaseRequestRepository,
    PurchaseOrderRepository,
    PurchaseOrderItemRepository,
    GoodsReceiptRepository,
    InventoryTransactionRepository,
    StockMovementRepository,
    InventoryAdjustmentRepository,
    InventoryCountRepository,
)
from app.models.inventory_product import Product, ProductCategory, Brand, Unit
from app.models.inventory_warehouse import Warehouse, WarehouseBin, StockLevel
from app.models.inventory_supplier import Supplier, SupplierContact
from app.models.inventory_purchase import PurchaseOrder, PurchaseOrderItem, GoodsReceipt
from app.models.inventory_transaction import InventoryTransaction, StockMovement, InventoryAdjustment, InventoryCount

class InventoryServiceException(Exception):
    pass

class ProductService(BaseService[Product, ProductRepository]):
    def __init__(self, repository: ProductRepository, category_repo: ProductCategoryRepository, unit_repo: UnitRepository):
        super().__init__(repository)
        self.category_repo = category_repo
        self.unit_repo = unit_repo

    async def create_product(self, org_id: uuid.UUID, data: Dict[str, Any]) -> Product:
        sku = data.get("sku")
        if sku:
            stmt = select(Product).where(
                Product.organization_id == org_id,
                Product.sku == sku,
                Product.is_deleted == False
            )
            res = await self.repository.db.execute(stmt)
            if res.scalar_one_or_none():
                raise InventoryServiceException(f"SKU {sku} already exists under this organization.")

        payload = {
            "organization_id": org_id,
            **data
        }
        return await self.repository.create(payload)

    async def bulk_import_products_csv(self, org_id: uuid.UUID, file_content: bytes) -> int:
        stream = io.StringIO(file_content.decode("utf-8"))
        reader = csv.DictReader(stream)
        count = 0

        # Query a default category and unit to fall back to if none specified
        categories = await self.category_repo.get_by_org(org_id)
        units = await self.unit_repo.get_by_org(org_id)
        if not categories or not units:
            raise InventoryServiceException("Please seed ProductCategory and Unit records before running import.")

        default_cat = categories[0].id
        default_unit = units[0].id

        for row in reader:
            sku = row.get("sku")
            if not sku:
                continue

            stmt = select(Product).where(
                Product.organization_id == org_id,
                Product.sku == sku,
                Product.is_deleted == False
            )
            res = await self.repository.db.execute(stmt)
            if res.scalar_one_or_none():
                continue # Skip duplicates

            prod_dict = {
                "organization_id": org_id,
                "category_id": default_cat,
                "unit_id": default_unit,
                "name": row.get("name", "Product " + sku),
                "sku": sku,
                "barcode": row.get("barcode"),
                "status": row.get("status", "active"),
                "safety_stock": int(row.get("safety_stock", 10)),
                "reorder_level": int(row.get("reorder_level", 20)),
            }
            await self.repository.create(prod_dict)
            count += 1
        return count


class SupplierService(BaseService[Supplier, SupplierRepository]):
    def __init__(self, repository: SupplierRepository, contact_repo: SupplierContactRepository):
        super().__init__(repository)
        self.contact_repo = contact_repo

    async def bulk_import_suppliers_csv(self, org_id: uuid.UUID, file_content: bytes) -> int:
        stream = io.StringIO(file_content.decode("utf-8"))
        reader = csv.DictReader(stream)
        count = 0
        for row in reader:
            code = row.get("code")
            if not code:
                continue

            stmt = select(Supplier).where(
                Supplier.organization_id == org_id,
                Supplier.code == code,
                Supplier.is_deleted == False
            )
            res = await self.repository.db.execute(stmt)
            if res.scalar_one_or_none():
                continue # Skip duplicates

            supp_dict = {
                "organization_id": org_id,
                "name": row.get("name", "Supplier " + code),
                "code": code,
                "gst_vat": row.get("gst_vat"),
                "payment_terms": row.get("payment_terms", "Net 30"),
                "rating": float(row.get("rating", 5.0)),
            }
            await self.repository.create(supp_dict)
            count += 1
        return count


class StockMovementService(BaseService[StockMovement, StockMovementRepository]):
    def __init__(
        self,
        repository: StockMovementRepository,
        stock_level_repo: StockLevelRepository,
        transaction_repo: InventoryTransactionRepository
    ):
        super().__init__(repository)
        self.stock_level_repo = stock_level_repo
        self.transaction_repo = transaction_repo

    async def transfer_stock(
        self,
        org_id: uuid.UUID,
        product_id: uuid.UUID,
        warehouse_id: uuid.UUID,
        from_bin_id: Optional[uuid.UUID],
        to_bin_id: Optional[uuid.UUID],
        quantity: int
    ) -> StockMovement:
        if quantity <= 0:
            raise InventoryServiceException("Transfer quantity must be greater than 0.")

        # 1. Deduct from source bin level
        if from_bin_id:
            stmt = select(StockLevel).where(
                StockLevel.organization_id == org_id,
                StockLevel.product_id == product_id,
                StockLevel.warehouse_bin_id == from_bin_id,
                StockLevel.is_deleted == False
            )
            res = await self.stock_level_repo.db.execute(stmt)
            src_level = res.scalar_one_or_none()
            if not src_level or src_level.available < quantity:
                raise InventoryServiceException("Insufficient available stock in source bin.")
            
            src_level.available -= quantity
            src_level.on_hand -= quantity
            await self.stock_level_repo.update(src_level, {})

        # 2. Add to target bin level
        if to_bin_id:
            stmt = select(StockLevel).where(
                StockLevel.organization_id == org_id,
                StockLevel.product_id == product_id,
                StockLevel.warehouse_bin_id == to_bin_id,
                StockLevel.is_deleted == False
            )
            res = await self.stock_level_repo.db.execute(stmt)
            tgt_level = res.scalar_one_or_none()
            if not tgt_level:
                tgt_level = await self.stock_level_repo.create({
                    "organization_id": org_id,
                    "product_id": product_id,
                    "warehouse_id": warehouse_id,
                    "warehouse_bin_id": to_bin_id,
                    "available": quantity,
                    "on_hand": quantity,
                    "reserved": 0
                })
            else:
                tgt_level.available += quantity
                tgt_level.on_hand += quantity
                await self.stock_level_repo.update(tgt_level, {})

        # 3. Save physical stock movement
        movement = await self.repository.create({
            "organization_id": org_id,
            "product_id": product_id,
            "from_bin_id": from_bin_id,
            "to_bin_id": to_bin_id,
            "quantity": quantity
        })

        # 4. Save logical transaction ledger
        await self.transaction_repo.create({
            "organization_id": org_id,
            "product_id": product_id,
            "warehouse_id": warehouse_id,
            "type": "transfer",
            "quantity": quantity,
            "reference": f"Transfer {movement.id}"
        })

        return movement


class PurchaseOrderService(BaseService[PurchaseOrder, PurchaseOrderRepository]):
    def __init__(
        self,
        repository: PurchaseOrderRepository,
        grn_repo: GoodsReceiptRepository,
        stock_level_repo: StockLevelRepository,
        transaction_repo: InventoryTransactionRepository
    ):
        super().__init__(repository)
        self.grn_repo = grn_repo
        self.stock_level_repo = stock_level_repo
        self.transaction_repo = transaction_repo

    async def receive_goods(
        self,
        po_id: uuid.UUID,
        received_by_id: uuid.UUID,
        warehouse_id: uuid.UUID
    ) -> GoodsReceipt:
        po = await self.repository.get(po_id)
        if not po:
            raise InventoryServiceException("Purchase Order not found.")
        
        if po.status in ["received", "cancelled"]:
            raise InventoryServiceException(f"Cannot receive goods for PO with status {po.status}")

        # Update PO status
        po.status = "received"
        await self.repository.update(po, {})

        # Generate Goods Receipt Note (GRN)
        grn = await self.grn_repo.create({
            "purchase_order_id": po.id,
            "grn_number": f"GRN-{uuid.uuid4().hex[:8].upper()}",
            "received_by_id": received_by_id,
            "received_date": date.today()
        })

        # Fetch PO items and increment stock levels
        stmt = select(PurchaseOrderItem).where(
            PurchaseOrderItem.purchase_order_id == po.id,
            PurchaseOrderItem.is_deleted == False
        )
        res = await self.repository.db.execute(stmt)
        items = res.scalars().all()

        for item in items:
            # Query default bin for this warehouse
            stmt_bin = select(WarehouseBin).where(
                WarehouseBin.warehouse_id == warehouse_id,
                WarehouseBin.is_deleted == False
            )
            res_bin = await self.repository.db.execute(stmt_bin)
            w_bin = res_bin.scalars().first()
            bin_id = w_bin.id if w_bin else None

            # Increment stock levels
            stmt_lvl = select(StockLevel).where(
                StockLevel.organization_id == po.organization_id,
                StockLevel.product_id == item.product_id,
                StockLevel.warehouse_id == warehouse_id,
                StockLevel.warehouse_bin_id == bin_id,
                StockLevel.is_deleted == False
            )
            res_lvl = await self.stock_level_repo.db.execute(stmt_lvl)
            stock = res_lvl.scalar_one_or_none()
            if not stock:
                await self.stock_level_repo.create({
                    "organization_id": po.organization_id,
                    "product_id": item.product_id,
                    "warehouse_id": warehouse_id,
                    "warehouse_bin_id": bin_id,
                    "available": item.quantity,
                    "on_hand": item.quantity,
                    "reserved": 0
                })
            else:
                stock.available += item.quantity
                stock.on_hand += item.quantity
                await self.stock_level_repo.update(stock, {})

            # Log transaction
            await self.transaction_repo.create({
                "organization_id": po.organization_id,
                "product_id": item.product_id,
                "warehouse_id": warehouse_id,
                "type": "purchase",
                "quantity": item.quantity,
                "reference": grn.grn_number
            })

        return grn
