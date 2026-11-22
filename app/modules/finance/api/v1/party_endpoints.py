"""Financial Customers and Vendors API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.models.party import CustomerParty, VendorParty
from app.modules.finance.repositories.party_repository import (
    CustomerPartyRepository,
    VendorPartyRepository,
)
from app.modules.finance.schemas.party import (
    CustomerListResponse,
    CustomerPartyCreate,
    CustomerPartyResponse,
    VendorListResponse,
    VendorPartyCreate,
    VendorPartyResponse,
)
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(tags=["Finance - Customers & Vendors"])


# Customers
@router.get(
    "/partners/customers",
    response_model=CustomerListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_READ.value))],
)
@router.get(
    "/partners/customers/",
    response_model=CustomerListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_READ.value))],
)
@router.get(
    "/parties/customers",
    response_model=CustomerListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_READ.value))],
)
@router.get(
    "/parties/customers/",
    response_model=CustomerListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_READ.value))],
)
async def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> CustomerListResponse:
    repo = CustomerPartyRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_by_org(tenant_id, org_id)
    return CustomerListResponse(
        items=[CustomerPartyResponse.model_validate(c) for c in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/partners/customers",
    response_model=CustomerPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_WRITE.value))],
)
@router.post(
    "/partners/customers/",
    response_model=CustomerPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_WRITE.value))],
)
@router.post(
    "/parties/customers",
    response_model=CustomerPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_WRITE.value))],
)
@router.post(
    "/parties/customers/",
    response_model=CustomerPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_INVOICES_WRITE.value))],
)
async def create_customer(
    data: CustomerPartyCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> CustomerPartyResponse:
    repo = CustomerPartyRepository(db)
    c = CustomerParty(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code.upper(),
        name=data.name,
        tax_id=data.tax_id,
        email=data.email,
        phone=data.phone,
        credit_limit=data.credit_limit,
        ar_account_id=data.ar_account_id,
        payment_terms_days=data.payment_terms_days,
        is_active=data.is_active,
    )
    await repo.create(c)
    await db.commit()
    return CustomerPartyResponse.model_validate(c)


# Vendors
@router.get(
    "/partners/vendors",
    response_model=VendorListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_READ.value))],
)
@router.get(
    "/partners/vendors/",
    response_model=VendorListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_READ.value))],
)
@router.get(
    "/parties/vendors",
    response_model=VendorListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_READ.value))],
)
@router.get(
    "/parties/vendors/",
    response_model=VendorListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_READ.value))],
)
async def list_vendors(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> VendorListResponse:
    repo = VendorPartyRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_by_org(tenant_id, org_id)
    return VendorListResponse(
        items=[VendorPartyResponse.model_validate(v) for v in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/partners/vendors",
    response_model=VendorPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_WRITE.value))],
)
@router.post(
    "/partners/vendors/",
    response_model=VendorPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_WRITE.value))],
)
@router.post(
    "/parties/vendors",
    response_model=VendorPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_WRITE.value))],
)
@router.post(
    "/parties/vendors/",
    response_model=VendorPartyResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BILLS_WRITE.value))],
)
async def create_vendor(
    data: VendorPartyCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> VendorPartyResponse:
    repo = VendorPartyRepository(db)
    v = VendorParty(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code.upper(),
        name=data.name,
        tax_id=data.tax_id,
        email=data.email,
        phone=data.phone,
        ap_account_id=data.ap_account_id,
        payment_terms_days=data.payment_terms_days,
        is_active=data.is_active,
    )
    await repo.create(v)
    await db.commit()
    return VendorPartyResponse.model_validate(v)
