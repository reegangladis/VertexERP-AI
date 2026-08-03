import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.inventory_procurement import (
    BrandRepository,
    ProductCategoryRepository,
    ProductRepository,
    PurchaseOrderRepository,
    StockLevelRepository,
    SupplierRepository,
    UnitOfMeasureRepository,
    WarehouseRepository,
)
from app.schemas.inventory_procurement import (
    BrandCreate,
    BrandResponse,
    GoodsReceiptCreate,
    GoodsReceiptResponse,
    InventoryDashboardSummary,
    ProductCategoryCreate,
    ProductCategoryResponse,
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    PurchaseOrderCreate,
    PurchaseOrderResponse,
    StockAdjustmentPayload,
    StockLevelResponse,
    StockTransferCreatePayload,
    StockTransferResponse,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
    UnitOfMeasureCreate,
    UnitOfMeasureResponse,
    WarehouseCreate,
    WarehouseResponse,
    WarehouseUpdate,
)
from app.services.inventory_procurement import (
    InventoryReportService,
    ProductService,
    PurchaseService,
    StockService,
    SupplierService,
    WarehouseService,
)

router = APIRouter()


# --- Categories, Brands & Units ---
@router.post("/inventory/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: ProductCategoryCreate,
    current_user: User = Depends(PermissionChecker("inventory.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ProductCategoryRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/inventory/categories", response_model=list[ProductCategoryResponse])
async def list_categories(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ProductCategoryRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/inventory/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    payload: BrandCreate,
    current_user: User = Depends(PermissionChecker("inventory.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = BrandRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/inventory/brands", response_model=list[BrandResponse])
async def list_brands(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = BrandRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/inventory/units", response_model=UnitOfMeasureResponse, status_code=status.HTTP_201_CREATED)
async def create_unit(
    payload: UnitOfMeasureCreate,
    current_user: User = Depends(PermissionChecker("inventory.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = UnitOfMeasureRepository(db)
    return await repo.create(payload.model_dump())


@router.get("/inventory/units", response_model=list[UnitOfMeasureResponse])
async def list_units(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = UnitOfMeasureRepository(db)
    return await repo.get_by_org(org_id)


# --- Products ---
@router.post("/inventory/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(PermissionChecker("inventory.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = ProductService(db)
    return await service.create_product(payload)


@router.get("/inventory/products", response_model=list[ProductResponse])
async def list_products(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ProductRepository(db)
    return await repo.get_by_org(org_id)


# --- Warehouses ---
@router.post("/inventory/warehouses", response_model=WarehouseResponse, status_code=status.HTTP_201_CREATED)
async def create_warehouse(
    payload: WarehouseCreate,
    current_user: User = Depends(PermissionChecker("warehouse.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = WarehouseService(db)
    return await service.create_warehouse(payload)


@router.get("/inventory/warehouses", response_model=list[WarehouseResponse])
async def list_warehouses(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = WarehouseRepository(db)
    return await repo.get_by_org(org_id)


# --- Stock Levels & Movements ---
@router.get("/inventory/stock-levels", response_model=list[StockLevelResponse])
async def list_stock_levels(
    warehouse_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = StockLevelRepository(db)
    if warehouse_id:
        return await repo.get_by_warehouse(warehouse_id)
    records, _ = await repo.get_multi()
    return records


@router.post("/inventory/stock-adjustments", response_model=StockLevelResponse)
async def adjust_stock(
    payload: StockAdjustmentPayload,
    current_user: User = Depends(PermissionChecker("stock.adjust")),
    db: AsyncSession = Depends(get_db_session),
):
    service = StockService(db)
    return await service.adjust_stock(payload, current_user.id)


@router.post("/inventory/stock-transfers", response_model=StockTransferResponse, status_code=status.HTTP_201_CREATED)
async def transfer_stock(
    payload: StockTransferCreatePayload,
    current_user: User = Depends(PermissionChecker("stock.transfer")),
    db: AsyncSession = Depends(get_db_session),
):
    service = StockService(db)
    return await service.transfer_stock(payload)


# --- Suppliers ---
@router.post("/inventory/suppliers", response_model=SupplierResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier(
    payload: SupplierCreate,
    current_user: User = Depends(PermissionChecker("supplier.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = SupplierService(db)
    return await service.create_supplier(payload)


@router.get("/inventory/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = SupplierRepository(db)
    return await repo.get_by_org(org_id)


# --- Purchase Orders & Goods Receipts ---
@router.post("/inventory/purchase-orders", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_purchase_order(
    payload: PurchaseOrderCreate,
    current_user: User = Depends(PermissionChecker("purchase.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PurchaseService(db)
    return await service.create_purchase_order(payload)


@router.get("/inventory/purchase-orders", response_model=list[PurchaseOrderResponse])
async def list_purchase_orders(
    supplier_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = PurchaseOrderRepository(db)
    records, _ = await repo.get_multi(filters={"supplier_id": supplier_id} if supplier_id else None)
    return records


@router.post("/inventory/goods-receipts", response_model=GoodsReceiptResponse, status_code=status.HTTP_201_CREATED)
async def receive_goods(
    payload: GoodsReceiptCreate,
    current_user: User = Depends(PermissionChecker("purchase.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PurchaseService(db)
    return await service.receive_goods(payload, current_user.id)


# --- Inventory Executive Dashboard ---
@router.get("/inventory/dashboard", response_model=InventoryDashboardSummary)
async def get_inventory_dashboard(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("inventory.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = InventoryReportService(db)
    return await service.get_dashboard_summary(org_id)
