"""Bank Account and Bank Transaction API Endpoints."""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.models.bank import BankAccount
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.repositories.bank_repository import BankRepository
from app.modules.finance.schemas.bank import (
    BankAccountCreate,
    BankAccountListResponse,
    BankAccountResponse,
    BankTransactionListResponse,
    BankTransactionResponse,
)
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(prefix="/banks", tags=["Finance - Bank Accounts & Banking Transactions"])


@router.get(
    "/accounts",
    response_model=BankAccountListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BANKING_READ.value))],
)
async def list_bank_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BankAccountListResponse:
    repo = BankRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_accounts_by_org(tenant_id, org_id, offset=offset, limit=page_size)
    total = await repo.count_accounts_by_org(tenant_id, org_id)
    return BankAccountListResponse(
        items=[BankAccountResponse.model_validate(a) for a in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/accounts",
    response_model=BankAccountResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BANKING_WRITE.value))],
)
async def create_bank_account(
    payload: BankAccountCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BankAccountResponse:
    acct_repo = AccountRepository(db)
    gl_acct = await acct_repo.get_by_id(payload.gl_account_id, tenant_id, org_id)
    if not gl_acct:
        raise NotFoundException(f"GL Account {payload.gl_account_id} not found.")

    repo = BankRepository(db)
    bank_account = BankAccount(
        tenant_id=tenant_id,
        organization_id=org_id,
        account_name=payload.account_name,
        account_number=payload.account_number,
        bank_name=payload.bank_name,
        currency=payload.currency,
        gl_account_id=payload.gl_account_id,
        current_balance=Decimal("0.0000"),
        is_active=payload.is_active,
    )
    await repo.create_account(bank_account)
    await db.commit()
    return BankAccountResponse.model_validate(bank_account)


@router.get(
    "/accounts/{account_id}",
    response_model=BankAccountResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BANKING_READ.value))],
)
async def get_bank_account(
    account_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BankAccountResponse:
    repo = BankRepository(db)
    account = await repo.get_account_by_id(account_id, tenant_id, org_id)
    if not account:
        raise NotFoundException(f"Bank Account {account_id} not found.")
    return BankAccountResponse.model_validate(account)


@router.get(
    "/accounts/{account_id}/transactions",
    response_model=BankTransactionListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_BANKING_READ.value))],
)
async def list_bank_transactions(
    account_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> BankTransactionListResponse:
    repo = BankRepository(db)
    account = await repo.get_account_by_id(account_id, tenant_id, org_id)
    if not account:
        raise NotFoundException(f"Bank Account {account_id} not found.")

    offset = (page - 1) * page_size
    items = await repo.list_transactions_by_account(
        account_id, tenant_id, org_id, offset=offset, limit=page_size
    )
    return BankTransactionListResponse(
        items=[BankTransactionResponse.model_validate(t) for t in items],
        total=len(items),
        page=page,
        page_size=page_size,
    )
