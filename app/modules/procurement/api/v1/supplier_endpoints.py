"""Suppliers / Vendors API Endpoints."""

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
from app.modules.procurement.models.supplier import Supplier
from app.modules.procurement.repositories.supplier_repository import SupplierRepository
from app.modules.procurement.schemas.supplier import (
    SupplierCreate,
    SupplierListResponse,
    SupplierResponse,
)

router = APIRouter(prefix="/procurement/suppliers", tags=["Procurement - Suppliers"])


@router.get(
    "/",
    response_model=SupplierListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_SUPPLIERS_READ.value))],
)
async def list_suppliers(
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None, description="Search by name, code, or email"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> SupplierListResponse:
    repo = SupplierRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id, org_id, status=status_filter, search=search, offset=offset, limit=page_size
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter, search=search)
    return SupplierListResponse(
        items=[SupplierResponse.model_validate(s) for s in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_SUPPLIERS_WRITE.value))],
)
async def create_supplier(
    data: SupplierCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    repo = SupplierRepository(db)
    sup = Supplier(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code.upper(),
        name=data.name,
        contact_name=data.contact_name,
        email=data.email,
        phone=data.phone,
        website=data.website,
        tax_id=data.tax_id,
        currency=data.currency,
        payment_terms=data.payment_terms,
        lead_time_days=data.lead_time_days,
        address=data.address,
        status=data.status,
        rating=data.rating,
        notes=data.notes,
        custom_fields=data.custom_fields,
        is_active=data.is_active,
    )
    await repo.create(sup)
    return SupplierResponse.model_validate(sup)


@router.get(
    "/{supplier_id}",
    response_model=SupplierResponse,
    dependencies=[Depends(require_permission(PermissionCode.PROCUREMENT_SUPPLIERS_READ.value))],
)
async def get_supplier(
    supplier_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> SupplierResponse:
    repo = SupplierRepository(db)
    sup = await repo.get_by_id(supplier_id, tenant_id, org_id)
    if not sup:
        raise NotFoundException(f"Supplier {supplier_id} not found.")
    return SupplierResponse.model_validate(sup)
