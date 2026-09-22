"""Journal Entries and General Ledger API Endpoints."""

import uuid

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.finance.repositories.journal_repository import (
    GeneralLedgerRepository,
    JournalRepository,
)
from app.modules.finance.schemas.journal import (
    GeneralLedgerListResponse,
    GeneralLedgerResponse,
    JournalEntryCreate,
    JournalEntryListResponse,
    JournalEntryResponse,
)
from app.modules.finance.services.journal_service import JournalEntryService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_id,
    require_permission,
)

router = APIRouter(prefix="/journals", tags=["Finance - Double-Entry Journals & General Ledger"])


@router.get(
    "/",
    response_model=JournalEntryListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_JOURNALS_READ.value))],
)
async def list_journal_entries(
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> JournalEntryListResponse:
    repo = JournalRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_org(
        tenant_id, org_id, status=status_filter, offset=offset, limit=page_size
    )
    total = await repo.count_by_org(tenant_id, org_id, status=status_filter)
    return JournalEntryListResponse(
        items=[JournalEntryResponse.model_validate(e) for e in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post(
    "/",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_JOURNALS_WRITE.value))],
)
async def create_journal_entry(
    data: JournalEntryCreate,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> JournalEntryResponse:
    service = JournalEntryService(db)
    entry = await service.create_draft_entry(data, tenant_id, org_id)
    return JournalEntryResponse.model_validate(entry)


@router.get(
    "/{entry_id}",
    response_model=JournalEntryResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_JOURNALS_READ.value))],
)
async def get_journal_entry(
    entry_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> JournalEntryResponse:
    repo = JournalRepository(db)
    entry = await repo.get_by_id(entry_id, tenant_id, org_id)
    if not entry:
        raise NotFoundException(f"Journal Entry {entry_id} not found.")
    return JournalEntryResponse.model_validate(entry)


@router.post(
    "/{entry_id}/post",
    response_model=JournalEntryResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_JOURNALS_POST.value))],
)
async def post_journal_entry(
    entry_id: uuid.UUID,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> JournalEntryResponse:
    service = JournalEntryService(db)
    posted = await service.post_entry(entry_id, tenant_id, org_id, user_id=user_id)
    return JournalEntryResponse.model_validate(posted)


@router.post(
    "/{entry_id}/reverse",
    response_model=JournalEntryResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_JOURNALS_REVERSE.value))],
)
async def reverse_journal_entry(
    entry_id: uuid.UUID,
    notes: str | None = None,
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> JournalEntryResponse:
    service = JournalEntryService(db)
    reversal = await service.reverse_entry(
        entry_id, tenant_id, org_id, user_id=user_id, notes=notes
    )
    return JournalEntryResponse.model_validate(reversal)


@router.get(
    "/general-ledger/{account_id}",
    response_model=GeneralLedgerListResponse,
    dependencies=[Depends(require_permission(PermissionCode.FINANCE_JOURNALS_READ.value))],
)
async def get_account_general_ledger(
    account_id: uuid.UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> GeneralLedgerListResponse:
    repo = GeneralLedgerRepository(db)
    offset = (page - 1) * page_size
    items = await repo.list_by_account(
        account_id, tenant_id, org_id, offset=offset, limit=page_size
    )
    return GeneralLedgerListResponse(
        items=[GeneralLedgerResponse.model_validate(g) for g in items],
        total=len(items),
        page=page,
        page_size=page_size,
    )
