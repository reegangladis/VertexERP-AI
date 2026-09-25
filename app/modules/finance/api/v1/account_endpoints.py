"""Chart of Accounts API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.models.account import Account
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.schemas.account import (
    AccountCreate,
    AccountListResponse,
    AccountResponse,
)
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(prefix="/accounts", tags=["Finance - Chart of Accounts"])


@router.get(
    "",
    response_model=AccountListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_ACCOUNTS_READ.value))],
)
@router.get(
    "/",
    response_model=AccountListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_ACCOUNTS_READ.value))],
)
async def list_accounts(
    account_type: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> AccountListResponse:
    repo = AccountRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id, org_id, account_type=account_type, offset=offset, limit=page_size
    )
    total = await repo.count_by_org(tenant_id, org_id, account_type=account_type)
    return AccountListResponse(
        items=[AccountResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_ACCOUNTS_WRITE.value))],
)
@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_ACCOUNTS_WRITE.value))],
)
async def create_account(
    data: AccountCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> AccountResponse:
    repo = AccountRepository(db)
    existing = await repo.get_by_code(data.code, tenant_id, org_id)
    if existing:
        raise BadRequestException(f"Account code {data.code} already exists.")

    acct = Account(
        tenant_id=tenant_id,
        organization_id=org_id,
        code=data.code.upper(),
        name=data.name,
        account_type=data.account_type.upper(),
        account_category=data.account_category,
        parent_account_id=data.parent_account_id,
        currency=data.currency.upper(),
        is_reconciled=data.is_reconciled,
        is_active=data.is_active,
    )
    await repo.create(acct)
    await db.commit()
    return AccountResponse.model_validate(acct)


@router.get(
    "/{account_id}",
    response_model=AccountResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_ACCOUNTS_READ.value))],
)
async def get_account(
    account_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> AccountResponse:
    repo = AccountRepository(db)
    acct = await repo.get_by_id(account_id, tenant_id, org_id)
    if not acct:
        raise NotFoundException(f"Account {account_id} not found.")
    return AccountResponse.model_validate(acct)
