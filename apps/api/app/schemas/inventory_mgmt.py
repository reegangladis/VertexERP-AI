import uuid
from datetime import date

from pydantic import BaseModel


class InventoryBaseModel(BaseModel):
    class Config:
        from_attributes = True


# 1. Product Master & Category
class ProductCategoryCreate(InventoryBaseModel):
    name: str
    code: str
    description: str | None = None
    parent_id: uuid.UUID | None = None


class ProductCategoryResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: str | None = None
    parent_id: uuid.UUID | None = None


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
    brand_id: uuid.UUID | None = None
    unit_id: uuid.UUID
    name: str
    sku: str
    barcode: str | None = None
    qr_code: str | None = None
    description: str | None = None
    status: str = "active"
    safety_stock: int = 0
    reorder_level: int = 0
    tags: list[str] | None = None


class ProductUpdate(InventoryBaseModel):
    name: str | None = None
    status: str | None = None
    safety_stock: int | None = None
    reorder_level: int | None = None


class ProductResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    category_id: uuid.UUID
    brand_id: uuid.UUID | None = None
    unit_id: uuid.UUID
    name: str
    sku: str
    barcode: str | None = None
    qr_code: str | None = None
    description: str | None = None
    status: str
    safety_stock: int
    reorder_level: int
    tags: dict | None = None


class ProductVariantCreate(InventoryBaseModel):
    product_id: uuid.UUID
    sku: str
    options: dict | None = None


class ProductVariantResponse(InventoryBaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    options: dict | None = None


# 2. Warehouse Layout
class WarehouseCreate(InventoryBaseModel):
    name: str
    code: str
    address: str | None = None
    capacity_cubic_meters: float | None = None
    manager_id: uuid.UUID | None = None


class WarehouseResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    address: str | None = None
    capacity_cubic_meters: float | None = None
    manager_id: uuid.UUID | None = None


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
    warehouse_bin_id: uuid.UUID | None = None
    available: int
    reserved: int
    on_hand: int


# 3. Suppliers
class SupplierContactCreate(InventoryBaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None


class SupplierContactResponse(InventoryBaseModel):
    id: uuid.UUID
    supplier_id: uuid.UUID
    first_name: str
    last_name: str
    email: str
    phone: str | None = None


class SupplierCreate(InventoryBaseModel):
    name: str
    code: str
    gst_vat: str | None = None
    payment_terms: str | None = None
    rating: float | None = 5.0
    contacts: list[SupplierContactCreate] | None = None


class SupplierResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    gst_vat: str | None = None
    payment_terms: str | None = None
    rating: float | None = None


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
    items: list[PurchaseOrderItemCreate]


class PurchaseOrderUpdate(InventoryBaseModel):
    status: str
    approved_by_id: uuid.UUID | None = None


class PurchaseOrderResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    supplier_id: uuid.UUID
    po_number: str
    status: str
    total_amount: float
    approved_by_id: uuid.UUID | None = None


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
    from_bin_id: uuid.UUID | None = None
    to_bin_id: uuid.UUID | None = None
    quantity: int


class StockMovementResponse(InventoryBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    from_bin_id: uuid.UUID | None = None
    to_bin_id: uuid.UUID | None = None
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
    items: list[InterWarehouseTransferItemCreate]


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
    approved_by_id: uuid.UUID | None = None
    items: list[InterWarehouseTransferItemResponse] | None = None


class InventorySummaryResponse(InventoryBaseModel):
    total_products: int
    total_warehouses: int
    total_stock_on_hand: int
    low_stock_count: int
    out_of_stock_count: int
    pending_purchase_orders: int
    completed_transfers: int
