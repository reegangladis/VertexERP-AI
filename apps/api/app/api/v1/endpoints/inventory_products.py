import uuid
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy import select, or_

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.models.inventory_product import Product, Brand, Unit
from app.repositories.inventory_mgmt import (
    ProductRepository,
    ProductCategoryRepository,
    BrandRepository,
    UnitRepository,
    WarehouseRepository,
    StockLevelRepository,
    PurchaseOrderRepository,
    StockTransferRepository,
)
from app.services.inventory_mgmt import ProductService
from app.schemas.inventory_mgmt import (
    ProductResponse,
    ProductCreate,
    ProductUpdate,
    BrandResponse,
    BrandCreate,
    UnitResponse,
    UnitCreate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_product_service(db=Depends(get_db_session)):
    return ProductService(ProductRepository(db), ProductCategoryRepository(db), UnitRepository(db))

# 1. Brands & Units Endpoints
@router.get("/brands", response_model=APIResponse[List[BrandResponse]])
async def list_brands(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    stmt = select(Brand).where(
        Brand.organization_id == current_user.organization_id,
        Brand.is_deleted == False
    )
    res = await db.execute(stmt)
    brands = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Brands retrieved successfully",
        data=brands
    )

@router.post("/brands", response_model=APIResponse[BrandResponse])
async def create_brand(
    payload: BrandCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = BrandRepository(db)
    brand = await repo.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Brand registered successfully",
        data=brand
    )

@router.get("/units", response_model=APIResponse[List[UnitResponse]])
async def list_units(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    stmt = select(Unit).where(
        Unit.organization_id == current_user.organization_id,
        Unit.is_deleted == False
    )
    res = await db.execute(stmt)
    units = list(res.scalars().all())
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Units retrieved successfully",
        data=units
    )

@router.post("/units", response_model=APIResponse[UnitResponse])
async def create_unit(
    payload: UnitCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = UnitRepository(db)
    unit = await repo.create({
        "organization_id": current_user.organization_id,
        **payload.dict()
    })
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Unit of measurement registered successfully",
        data=unit
    )

# 2. Export & Import CSV
@router.get("/export/csv")
async def export_products(
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    products = await service.repository.get_by_org(current_user.organization_id)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "sku", "barcode", "status", "safety_stock", "reorder_level"])
    for p in products:
        writer.writerow([p.name, p.sku, p.barcode or "", p.status, p.safety_stock, p.reorder_level])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products_export.csv"}
    )

@router.post("/bulk-upload")
async def bulk_upload_products(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        content = await file.read()
        count = await service.bulk_import_products_csv(current_user.organization_id, content)
        return standard_json_response(
            status_code=status.HTTP_200_OK,
            success=True,
            message=f"Successfully imported {count} products from CSV."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Telemetry Summary Endpoint
@router.get("/summary")
async def get_inventory_summary(
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    prod_repo = ProductRepository(db)
    wh_repo = WarehouseRepository(db)
    stock_repo = StockLevelRepository(db)
    po_repo = PurchaseOrderRepository(db)

    products = await prod_repo.get_by_org(current_user.organization_id)
    warehouses = await wh_repo.get_by_org(current_user.organization_id)
    stock_levels = await stock_repo.get_by_org(current_user.organization_id)
    pos = await po_repo.get_by_org(current_user.organization_id)

    total_stock_on_hand = sum(s.on_hand for s in stock_levels)
    low_stock = sum(1 for p in products if any(s.product_id == p.id and s.on_hand <= p.reorder_level for s in stock_levels))
    out_of_stock = sum(1 for p in products if not any(s.product_id == p.id and s.on_hand > 0 for s in stock_levels))

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Inventory telemetry metrics retrieved successfully",
        data={
            "total_products": len(products),
            "total_warehouses": len(warehouses),
            "total_stock_on_hand": total_stock_on_hand,
            "low_stock_count": low_stock,
            "out_of_stock_count": out_of_stock,
            "pending_purchase_orders": len([po for po in pos if po.status in ["draft", "ordered"]]),
        }
    )

# 4. Products Base & Parameterized Endpoints
@router.get("", response_model=APIResponse[List[ProductResponse]])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(Product).where(
        Product.organization_id == current_user.organization_id,
        Product.is_deleted == False
    )

    if search:
        stmt = stmt.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.sku.ilike(f"%{search}%"),
                Product.barcode.ilike(f"%{search}%")
            )
        )

    stmt = stmt.offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    products = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Products retrieved successfully",
        data=products
    )

@router.get("/{id}", response_model=APIResponse[ProductResponse])
async def get_product(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    product = await service.repository.get(id)
    if not product or product.organization_id != current_user.organization_id or product.is_deleted:
        raise HTTPException(status_code=404, detail="Product not found")

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Product details retrieved",
        data=product
    )

@router.post("", response_model=APIResponse[ProductResponse])
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    try:
        product = await service.create_product(current_user.organization_id, payload.dict())
        return standard_json_response(
            status_code=status.HTTP_201_CREATED,
            success=True,
            message="Product catalog master created",
            data=product
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{id}", response_model=APIResponse[ProductResponse])
async def update_product(
    id: uuid.UUID,
    payload: ProductUpdate,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    product = await service.repository.get(id)
    if not product or product.organization_id != current_user.organization_id or product.is_deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    updated = await service.repository.update(product, payload.dict(exclude_unset=True))
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Product details updated",
        data=updated
    )

@router.delete("/{id}")
async def delete_product(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ProductService = Depends(get_product_service)
):
    product = await service.repository.get(id)
    if not product or product.organization_id != current_user.organization_id or product.is_deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    await service.repository.delete(product)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Product deleted successfully"
    )
