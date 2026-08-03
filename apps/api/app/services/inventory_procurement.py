import uuid
from datetime import UTC, date, datetime
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.inventory_procurement import (
    BrandRepository,
    GoodsReceiptRepository,
    InventoryAdjustmentRepository,
    ProductCategoryRepository,
    ProductRepository,
    PurchaseOrderRepository,
    StockLevelRepository,
    StockTransferRepository,
    SupplierRepository,
    UnitOfMeasureRepository,
    WarehouseRepository,
)
from app.schemas.inventory_procurement import (
    GoodsReceiptCreate,
    InventoryDashboardSummary,
    ProductCreate,
    ProductUpdate,
    PurchaseOrderCreate,
    StockAdjustmentPayload,
    StockTransferCreatePayload,
    SupplierCreate,
    WarehouseCreate,
)


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)

    async def create_product(self, payload: ProductCreate):
        dup_sku = await self.product_repo.find_by_sku(payload.organization_id, payload.sku)
        if dup_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SKU '{payload.sku}' already exists in this organization.",
            )

        if payload.barcode:
            dup_barcode = await self.product_repo.find_by_barcode(payload.organization_id, payload.barcode)
            if dup_barcode:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Barcode '{payload.barcode}' already exists in this organization.",
                )

        return await self.product_repo.create(payload.model_dump())


class WarehouseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.warehouse_repo = WarehouseRepository(db)

    async def create_warehouse(self, payload: WarehouseCreate):
        dup = await self.warehouse_repo.find_by_code(payload.organization_id, payload.warehouse_code)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Warehouse code '{payload.warehouse_code}' already exists.",
            )
        return await self.warehouse_repo.create(payload.model_dump())


class StockService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.stock_repo = StockLevelRepository(db)
        self.product_repo = ProductRepository(db)
        self.warehouse_repo = WarehouseRepository(db)
        self.adj_repo = InventoryAdjustmentRepository(db)
        self.transfer_repo = StockTransferRepository(db)

    async def adjust_stock(self, payload: StockAdjustmentPayload, user_id: uuid.UUID | None = None):
        stock = await self.stock_repo.get_by_warehouse_and_product(payload.warehouse_id, payload.product_id)
        old_qty = stock.available_quantity if stock else 0.0

        if stock:
            await self.stock_repo.update(stock.id, {"available_quantity": payload.new_quantity})
        else:
            stock = await self.stock_repo.create(
                {
                    "warehouse_id": payload.warehouse_id,
                    "product_id": payload.product_id,
                    "available_quantity": payload.new_quantity,
                    "reserved_quantity": 0.0,
                    "damaged_quantity": 0.0,
                    "reorder_quantity": 10.0,
                }
            )

        adj_number = f"ADJ-{uuid.uuid4().hex[:6].upper()}"
        await self.adj_repo.create(
            {
                "adjustment_number": adj_number,
                "warehouse_id": payload.warehouse_id,
                "product_id": payload.product_id,
                "old_quantity": old_qty,
                "new_quantity": payload.new_quantity,
                "adjustment_reason": payload.adjustment_reason,
                "adjusted_by": user_id,
            }
        )
        return await self.stock_repo.get_by_warehouse_and_product(payload.warehouse_id, payload.product_id)

    async def transfer_stock(self, payload: StockTransferCreatePayload):
        if payload.from_warehouse_id == payload.to_warehouse_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and Destination warehouse cannot be the same.",
            )

        src_stock = await self.stock_repo.get_by_warehouse_and_product(payload.from_warehouse_id, payload.product_id)
        if not src_stock or src_stock.available_quantity < payload.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient stock in source warehouse for transfer.",
            )

        # Deduct from Source Warehouse
        await self.stock_repo.update(
            src_stock.id, {"available_quantity": src_stock.available_quantity - payload.quantity}
        )

        # Add to Destination Warehouse
        dest_stock = await self.stock_repo.get_by_warehouse_and_product(payload.to_warehouse_id, payload.product_id)
        if dest_stock:
            await self.stock_repo.update(
                dest_stock.id, {"available_quantity": dest_stock.available_quantity + payload.quantity}
            )
        else:
            await self.stock_repo.create(
                {
                    "warehouse_id": payload.to_warehouse_id,
                    "product_id": payload.product_id,
                    "available_quantity": payload.quantity,
                    "reserved_quantity": 0.0,
                    "damaged_quantity": 0.0,
                    "reorder_quantity": 10.0,
                }
            )

        dup = await self.transfer_repo.find_by_number(payload.transfer_number)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transfer number '{payload.transfer_number}' already exists.",
            )

        transfer = await self.transfer_repo.create(
            {
                "transfer_number": payload.transfer_number,
                "from_warehouse_id": payload.from_warehouse_id,
                "to_warehouse_id": payload.to_warehouse_id,
                "transfer_date": payload.transfer_date,
                "status": "Completed",
            }
        )
        return transfer


class PurchaseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.po_repo = PurchaseOrderRepository(db)
        self.supplier_repo = SupplierRepository(db)
        self.gr_repo = GoodsReceiptRepository(db)
        self.stock_repo = StockLevelRepository(db)

    async def create_purchase_order(self, payload: PurchaseOrderCreate):
        supplier = await self.supplier_repo.get(payload.supplier_id)
        if not supplier:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

        dup = await self.po_repo.find_by_number(payload.purchase_order_number)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Purchase order number '{payload.purchase_order_number}' already exists.",
            )

        subtotal = 0.0
        tax = 0.0
        calculated_items = []
        for item in payload.items:
            item_subtotal = item.quantity * item.unit_price
            item_total = item_subtotal + item.tax_amount
            subtotal += item_subtotal
            tax += item.tax_amount
            calculated_items.append(
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "tax_amount": item.tax_amount,
                    "total_price": item_total,
                }
            )

        grand_total = max(0.0, (subtotal + tax) - payload.discount)

        po = await self.po_repo.create(
            {
                "supplier_id": payload.supplier_id,
                "purchase_order_number": payload.purchase_order_number,
                "order_date": payload.order_date,
                "expected_delivery": payload.expected_delivery,
                "subtotal": subtotal,
                "tax": tax,
                "discount": payload.discount,
                "grand_total": grand_total,
                "status": payload.status,
            }
        )
        return await self.po_repo.get_with_items(po.id)

    async def receive_goods(self, payload: GoodsReceiptCreate, user_id: uuid.UUID | None = None):
        po = await self.po_repo.get(payload.purchase_order_id)
        if not po:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase Order not found")

        gr = await self.gr_repo.create(
            {
                "purchase_order_id": payload.purchase_order_id,
                "receipt_number": payload.receipt_number,
                "receipt_date": payload.receipt_date,
                "received_by": user_id,
                "status": "Received",
            }
        )

        for item in payload.items:
            stock = await self.stock_repo.get_by_warehouse_and_product(item.warehouse_id, item.product_id)
            if stock:
                await self.stock_repo.update(
                    stock.id, {"available_quantity": stock.available_quantity + item.received_quantity}
                )
            else:
                await self.stock_repo.create(
                    {
                        "warehouse_id": item.warehouse_id,
                        "product_id": item.product_id,
                        "available_quantity": item.received_quantity,
                        "reserved_quantity": 0.0,
                        "damaged_quantity": 0.0,
                        "reorder_quantity": 10.0,
                    }
                )

        await self.po_repo.update(po.id, {"status": "Received"})
        return await self.gr_repo.get_with_items(gr.id)


class SupplierService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.supplier_repo = SupplierRepository(db)

    async def create_supplier(self, payload: SupplierCreate):
        dup = await self.supplier_repo.find_by_code(payload.organization_id, payload.supplier_code)
        if dup:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supplier code '{payload.supplier_code}' already exists.",
            )
        return await self.supplier_repo.create(payload.model_dump())


class InventoryReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.product_repo = ProductRepository(db)
        self.warehouse_repo = WarehouseRepository(db)
        self.stock_repo = StockLevelRepository(db)
        self.supplier_repo = SupplierRepository(db)
        self.po_repo = PurchaseOrderRepository(db)
        self.gr_repo = GoodsReceiptRepository(db)

    async def get_dashboard_summary(self, org_id: uuid.UUID) -> InventoryDashboardSummary:
        products = await self.product_repo.get_by_org(org_id)
        warehouses = await self.warehouse_repo.get_by_org(org_id)
        suppliers = await self.supplier_repo.get_by_org(org_id)

        all_stocks = await self.stock_repo.get_all()
        stock_val = sum(s.available_quantity * (next((p.cost_price for p in products if p.id == s.product_id), 0.0)) for s in all_stocks)
        low_stock = len([s for s in all_stocks if s.available_quantity <= s.reorder_quantity and s.available_quantity > 0])
        out_of_stock = len([s for s in all_stocks if s.available_quantity == 0])

        pos = await self.po_repo.get_all()
        pending_pos = len([p for p in pos if p.status in ("Draft", "Approved", "Sent")])

        receipts = await self.gr_repo.get_all()

        return InventoryDashboardSummary(
            total_products=len(products),
            total_warehouses=len(warehouses),
            total_suppliers=len(suppliers),
            total_stock_value=round(stock_val, 2),
            low_stock_count=low_stock,
            out_of_stock_count=out_of_stock,
            pending_purchase_orders=pending_pos,
            total_goods_received=len(receipts),
        )
