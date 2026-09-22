"""Product Categories API Endpoints."""

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
from app.modules.inventory.models.category import ProductCategory
from app.modules.inventory.repositories.uom_repository import CategoryRepository
from app.modules.inventory.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
)

router = APIRouter(prefix="/inventory/categories", tags=["Inventory - Categories"])


@router.get(
    "/",
    response_model=CategoryListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def list_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> CategoryListResponse:
    repo = CategoryRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_by_org(tenant_id, org_id)
    return CategoryListResponse(
        items=[CategoryResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_WRITE.value))],
)
async def create_category(
    data: CategoryCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    repo = CategoryRepository(db)
    cat = ProductCategory(
        tenant_id=tenant_id,
        organization_id=org_id,
        name=data.name,
        code=data.code.upper(),
        parent_id=data.parent_id,
        description=data.description,
        is_active=data.is_active,
    )
    await repo.create(cat)
    return CategoryResponse.model_validate(cat)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_permission(PermissionCode.INVENTORY_PRODUCTS_READ.value))],
)
async def get_category(
    category_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> CategoryResponse:
    repo = CategoryRepository(db)
    cat = await repo.get_by_id(category_id, tenant_id, org_id)
    if not cat:
        raise NotFoundException(f"Category {category_id} not found.")
    return CategoryResponse.model_validate(cat)
