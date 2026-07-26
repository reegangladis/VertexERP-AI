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
from app.repositories.inventory_mgmt import ProductRepository, ProductCategoryRepository, UnitRepository
from app.services.inventory_mgmt import ProductService
from app.schemas.inventory_mgmt import ProductResponse, ProductCreate, ProductUpdate, BrandResponse, UnitResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_product_service(db=Depends(get_db_session)):
    return ProductService(ProductRepository(db), ProductCategoryRepository(db), UnitRepository(db))

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
    if not product:
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
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await service.repository.delete(product)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Product deleted successfully"
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
