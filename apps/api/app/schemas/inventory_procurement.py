import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Product Category, Brand, & Unit Schemas ---
class ProductCategoryBase(BaseModel):
    category_name: str = Field(..., min_length=1, max_length=100)
    category_code: str = Field(..., min_length=1, max_length=50)
    description: str | None = Field(None, max_length=500)


class ProductCategoryCreate(ProductCategoryBase):
    organization_id: uuid.UUID


class ProductCategoryResponse(ProductCategoryBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrandBase(BaseModel):
    brand_name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class BrandCreate(BrandBase):
    organization_id: uuid.UUID


class BrandResponse(BrandBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UnitOfMeasureBase(BaseModel):
    unit_name: str = Field(..., min_length=1, max_length=50)
    unit_code: str = Field(..., min_length=1, max_length=20)


class UnitOfMeasureCreate(UnitOfMeasureBase):
    organization_id: uuid.UUID


class UnitOfMeasureResponse(UnitOfMeasureBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Product Schemas ---
class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    barcode: str | None = Field(None, max_length=100)
    product_name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    cost_price: float = Field(default=0.0, ge=0)
    selling_price: float = Field(default=0.0, ge=0)
    minimum_stock: float = Field(default=0.0, ge=0)
    maximum_stock: float = Field(default=10000.0, ge=0)
    reorder_level: float = Field(default=10.0, ge=0)
    track_inventory: bool = Field(default=True)
    track_serial: bool = Field(default=False)
    track_batch: bool = Field(default=False)
    status: str = Field(default="Active", max_length=50)


class ProductCreate(ProductBase):
    organization_id: uuid.UUID
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    unit_id: uuid.UUID | None = None


class ProductUpdate(BaseModel):
    sku: str | None = Field(None, min_length=1, max_length=100)
    barcode: str | None = Field(None, max_length=100)
    product_name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=2000)
    cost_price: float | None = Field(None, ge=0)
    selling_price: float | None = Field(None, ge=0)
    minimum_stock: float | None = Field(None, ge=0)
    maximum_stock: float | None = Field(None, ge=0)
    reorder_level: float | None = Field(None, ge=0)
    status: str | None = Field(None, max_length=50)


class ProductResponse(ProductBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    unit_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Warehouse & Stock Schemas ---
class WarehouseBase(BaseModel):
    warehouse_name: str = Field(..., min_length=1, max_length=255)
    warehouse_code: str = Field(..., min_length=1, max_length=50)
    status: str = Field(default="Active", max_length=50)


class WarehouseCreate(WarehouseBase):
    organization_id: uuid.UUID
    location_id: uuid.UUID | None = None
    manager_uuid: uuid.UUID | None = None


class WarehouseUpdate(BaseModel):
    warehouse_name: str | None = Field(None, min_length=1, max_length=255)
    warehouse_code: str | None = Field(None, min_length=1, max_length=50)
    status: str | None = Field(None, max_length=50)


class WarehouseResponse(WarehouseBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    location_id: uuid.UUID | None = None
    manager_uuid: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockLevelResponse(BaseModel):
    id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    available_quantity: float
    reserved_quantity: float
    damaged_quantity: float
    reorder_quantity: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StockAdjustmentPayload(BaseModel):
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    new_quantity: float = Field(..., ge=0)
    adjustment_reason: str = Field(..., min_length=1, max_length=500)


class StockTransferCreatePayload(BaseModel):
    transfer_number: str = Field(..., min_length=1, max_length=100)
    from_warehouse_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    transfer_date: date
    product_id: uuid.UUID
    quantity: float = Field(..., gt=0)


class StockTransferResponse(BaseModel):
    id: uuid.UUID
    transfer_number: str
    from_warehouse_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    transfer_date: date
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Supplier Schemas ---
class SupplierBase(BaseModel):
    supplier_code: str = Field(..., min_length=1, max_length=50)
    company_name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: str | None = Field(None, max_length=50)
    website: str | None = Field(None, max_length=255)
    tax_number: str | None = Field(None, max_length=50)
    payment_terms: str = Field(default="Net 30", max_length=100)
    status: str = Field(default="Active", max_length=50)


class SupplierCreate(SupplierBase):
    organization_id: uuid.UUID


class SupplierUpdate(BaseModel):
    company_name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=50)
    payment_terms: str | None = Field(None, max_length=100)
    status: str | None = Field(None, max_length=50)


class SupplierResponse(SupplierBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Purchase Order & Goods Receipt Schemas ---
class PurchaseOrderItemCreate(BaseModel):
    product_id: uuid.UUID
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    tax_amount: float = Field(default=0.0, ge=0)


class PurchaseOrderItemResponse(BaseModel):
    id: uuid.UUID
    purchase_order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: float
    unit_price: float
    tax_amount: float
    total_price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PurchaseOrderBase(BaseModel):
    purchase_order_number: str = Field(..., min_length=1, max_length=100)
    order_date: date
    expected_delivery: date
    discount: float = Field(default=0.0, ge=0)
    status: str = Field(default="Draft", max_length=50)


class PurchaseOrderCreate(PurchaseOrderBase):
    supplier_id: uuid.UUID
    items: list[PurchaseOrderItemCreate] = Field(..., min_length=1)


class PurchaseOrderResponse(PurchaseOrderBase):
    id: uuid.UUID
    supplier_id: uuid.UUID
    subtotal: float
    tax: float
    grand_total: float
    created_at: datetime
    updated_at: datetime
    items: list[PurchaseOrderItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptItemCreate(BaseModel):
    product_id: uuid.UUID
    received_quantity: float = Field(..., gt=0)
    warehouse_id: uuid.UUID


class GoodsReceiptItemResponse(BaseModel):
    id: uuid.UUID
    goods_receipt_id: uuid.UUID
    product_id: uuid.UUID
    received_quantity: float
    warehouse_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GoodsReceiptCreate(BaseModel):
    purchase_order_id: uuid.UUID
    receipt_number: str = Field(..., min_length=1, max_length=100)
    receipt_date: date
    items: list[GoodsReceiptItemCreate] = Field(..., min_length=1)


class GoodsReceiptResponse(BaseModel):
    id: uuid.UUID
    purchase_order_id: uuid.UUID
    receipt_number: str
    receipt_date: date
    status: str
    created_at: datetime
    updated_at: datetime
    items: list[GoodsReceiptItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summary Schema ---
class InventoryDashboardSummary(BaseModel):
    total_products: int
    total_warehouses: int
    total_suppliers: int
    total_stock_value: float
    low_stock_count: int
    out_of_stock_count: int
    pending_purchase_orders: int
    total_goods_received: int
