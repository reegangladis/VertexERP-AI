import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

class InventoryBaseModel(BaseModel):
    class Config:
        from_attributes = True

# 1. Product Master & Category
class ProductCategoryCreate(InventoryBaseModel):
    name: str
    code: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

class ProductCategoryResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None

class BrandCreate(InventoryBaseModel):
    name: str
    code: str

class BrandResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str

class UnitCreate(InventoryBaseModel):
    name: str
    code: str

class UnitResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str

class ProductCreate(InventoryBaseModel):
    category_id: uuid.UUID
    brand_id: Optional[uuid.UUID] = None
    unit_id: uuid.UUID
    name: str
    sku: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    safety_stock: int = 0
    reorder_level: int = 0
    tags: Optional[List[str]] = None

class ProductUpdate(InventoryBaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    safety_stock: Optional[int] = None
    reorder_level: Optional[int] = None

class ProductResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    category_id: uuid.UUID
    brand_id: Optional[uuid.UUID] = None
    unit_id: uuid.UUID
    name: str
    sku: str
    barcode: Optional[str] = None
    qr_code: Optional[str] = None
    description: Optional[str] = None
    status: str
    safety_stock: int
    reorder_level: int
    tags: Optional[dict] = None

class ProductVariantCreate(InventoryBaseModel):
    product_id: uuid.UUID
    sku: str
    options: Optional[dict] = None

class ProductVariantResponse(InventoryBaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    options: Optional[dict] = None

# 2. Warehouse Layout
class WarehouseCreate(InventoryBaseModel):
    name: str
    code: str
    address: Optional[str] = None
    capacity_cubic_meters: Optional[float] = None
    manager_id: Optional[uuid.UUID] = None

class WarehouseResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    address: Optional[str] = None
    capacity_cubic_meters: Optional[float] = None
    manager_id: Optional[uuid.UUID] = None

class WarehouseBinCreate(InventoryBaseModel):
    warehouse_id: uuid.UUID
    zone: str
    rack: str
    shelf: str
    bin_code: str

class WarehouseBinResponse(InventoryBaseModel):
    id: uuid.UUID
    warehouse_id: uuid.UUID
    zone: str
    rack: str
    shelf: str
    bin_code: str

class StockLevelResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    warehouse_bin_id: Optional[uuid.UUID] = None
    available: int
    reserved: int
    on_hand: int

# 3. Suppliers
class SupplierContactCreate(InventoryBaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

class SupplierContactResponse(InventoryBaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None

class SupplierCreate(InventoryBaseModel):
    name: str
    code: str
    gst_vat: Optional[str] = None
    payment_terms: Optional[str] = None
    rating: Optional[float] = 5.0
    contacts: Optional[List[SupplierContactCreate]] = None

class SupplierResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    gst_vat: Optional[str] = None
    payment_terms: Optional[str] = None
    rating: Optional[float] = None

# 4. Procurement & Purchase
class PurchaseOrderItemCreate(InventoryBaseModel):
    product_id: uuid.UUID
    quantity: int
    unit_price: float

class PurchaseOrderItemResponse(InventoryBaseModel):
    id: uuid.UUID
    purchase_order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    unit_price: float

class PurchaseOrderCreate(InventoryBaseModel):
    supplier_id: uuid.UUID
    po_number: str
    items: List[PurchaseOrderItemCreate]

class PurchaseOrderUpdate(InventoryBaseModel):
    status: str
    approved_by_id: Optional[uuid.UUID] = None

class PurchaseOrderResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    supplier_id: uuid.UUID
    po_number: str
    status: str
    total_amount: float
    approved_by_id: Optional[uuid.UUID] = None

class GoodsReceiptResponse(InventoryBaseModel):
    id: uuid.UUID
    purchase_order_id: uuid.UUID
    grn_number: str
    received_by_id: uuid.UUID
    received_date: date

# 5. Transfers & Adjustments
class StockTransferCreate(InventoryBaseModel):
    product_id: uuid.UUID
    warehouse_id: uuid.UUID
    from_bin_id: Optional[uuid.UUID] = None
    to_bin_id: Optional[uuid.UUID] = None
    quantity: int

class StockMovementResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    from_bin_id: Optional[uuid.UUID] = None
    to_bin_id: Optional[uuid.UUID] = None
    quantity: int

class InventoryAdjustmentCreate(InventoryBaseModel):
    warehouse_id: uuid.UUID
    status: str = "pending"

class InventoryAdjustmentResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    warehouse_id: uuid.UUID
    adjusted_by_id: uuid.UUID
    status: str

class InventoryCountCreate(InventoryBaseModel):
    warehouse_id: uuid.UUID

class InventoryCountResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    warehouse_id: uuid.UUID
    status: str

# 6. Inter-Warehouse Transfers & Telemetry
class InterWarehouseTransferItemCreate(InventoryBaseModel):
    product_id: uuid.UUID
    quantity: int

class InterWarehouseTransferCreate(InventoryBaseModel):
    source_warehouse_id: uuid.UUID
    target_warehouse_id: uuid.UUID
    items: List[InterWarehouseTransferItemCreate]

class InterWarehouseTransferItemResponse(InventoryBaseModel):
    id: uuid.UUID
    stock_transfer_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int

class InterWarehouseTransferResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    transfer_number: str
    source_warehouse_id: uuid.UUID
    target_warehouse_id: uuid.UUID
    status: str
    requested_by_id: uuid.UUID
    approved_by_id: Optional[uuid.UUID] = None
    items: Optional[List[InterWarehouseTransferItemResponse]] = None

class InventorySummaryResponse(InventoryBaseModel):
    total_products: int
    total_warehouses: int
    total_stock_on_hand: int
    low_stock_count: int
    out_of_stock_count: int
    pending_purchase_orders: int
    completed_transfers: int
