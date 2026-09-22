"""Product / Item Master API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)
from app.modules.inventory.models.product import Product
from app.modules.inventory.repositories.product_repository import ProductRepository
from app.modules.inventory.schemas.product import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
)

router = APIRouter(prefix="/inventory/products", tags=["Inventory - Products Master"])


@router.get(
    "/",
    response_model=ProductListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def list_products(
    category_id: uuid.UUID | None = None,
    search: str | None = Query(None, description="Search by name, SKU, or barcode"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductListResponse:
    repo = ProductRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id, org_id, category_id=category_id, search=search, offset=offset, limit=page_size
    )
    total = await repo.count_by_org(tenant_id, org_id, category_id=category_id, search=search)
    return ProductListResponse(
        items=[ProductResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_WRITE.value))],
)
async def create_product(
    data: ProductCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    repo = ProductRepository(db)
    product = Product(
        tenant_id=tenant_id,
        organization_id=org_id,
        sku=data.sku.upper(),
        barcode=data.barcode,
        name=data.name,
        description=data.description,
        category_id=data.category_id,
        uom_id=data.uom_id,
        valuation_method=data.valuation_method,
        cost_price=data.cost_price,
        selling_price=data.selling_price,
        reorder_point=data.reorder_point,
        reorder_quantity=data.reorder_quantity,
        safety_stock=data.safety_stock,
        min_order_qty=data.min_order_qty,
        lead_time_days=data.lead_time_days,
        is_stockable=data.is_stockable,
        is_purchasable=data.is_purchasable,
        is_sellable=data.is_sellable,
        allow_negative_stock=data.allow_negative_stock,
        custom_fields=data.custom_fields,
        is_active=data.is_active,
    )
    await repo.create(product)
    return ProductResponse.model_validate(product)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def get_product(
    product_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    repo = ProductRepository(db)
    product = await repo.get_by_id(product_id, tenant_id, org_id)
    if not product:
        raise NotFoundException(f"Product {product_id} not found.")
    return ProductResponse.model_validate(product)
