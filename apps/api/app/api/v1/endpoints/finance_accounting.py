import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.finance_accounting import (
    AccountRepository,
    BankAccountRepository,
    CustomerInvoiceRepository,
    JournalEntryRepository,
    PaymentRepository,
    SupplierBillRepository,
)
from app.schemas.finance_accounting import (
    AccountCreate,
    AccountResponse,
    BankAccountCreate,
    BankAccountResponse,
    CustomerInvoiceCreate,
    CustomerInvoiceResponse,
    FinanceDashboardSummary,
    JournalEntryCreate,
    JournalEntryResponse,
    PaymentCreate,
    PaymentResponse,
    SupplierBillCreate,
    SupplierBillResponse,
)
from app.services.finance_accounting import (
    AccountingEngine,
    BankAccountService,
    FinanceAnalyticsService,
    InvoiceService,
    PaymentService,
    SupplierBillService,
)

router = APIRouter()


# --- Chart of Accounts ---
@router.post("/finance/accounts", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    payload: AccountCreate,
    current_user: User = Depends(PermissionChecker("finance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = AccountingEngine(db)
    return await engine.create_account(payload)


@router.get("/finance/accounts", response_model=list[AccountResponse])
async def list_accounts(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = AccountRepository(db)
    return await repo.get_by_org(org_id)


# --- Journal Entries ---
@router.post("/finance/journal-entries", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_journal_entry(
    payload: JournalEntryCreate,
    current_user: User = Depends(PermissionChecker("journal.post")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = AccountingEngine(db)
    return await engine.create_journal_entry(payload, current_user.id)


@router.get("/finance/journal-entries", response_model=list[JournalEntryResponse])
async def list_journal_entries(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = JournalEntryRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/finance/journal-entries/{id}/post", response_model=JournalEntryResponse)
async def post_journal_entry(
    id: uuid.UUID,
    current_user: User = Depends(PermissionChecker("journal.post")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = AccountingEngine(db)
    return await engine.post_journal_entry(id, current_user.id)


# --- Customer Invoices ---
@router.post("/finance/invoices", response_model=CustomerInvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    payload: CustomerInvoiceCreate,
    current_user: User = Depends(PermissionChecker("invoice.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = InvoiceService(db)
    return await service.create_invoice(payload)


@router.get("/finance/invoices", response_model=list[CustomerInvoiceResponse])
async def list_invoices(
    customer_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = CustomerInvoiceRepository(db)
    records, _ = await repo.get_multi(filters={"customer_id": customer_id} if customer_id else None)
    return records


@router.get("/finance/invoices/{invoice_number}/download-pdf")
async def download_invoice_pdf(
    invoice_number: str,
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = InvoiceService(db)
    pdf_text = await service.generate_pdf_text(invoice_number)
    return Response(
        content=pdf_text,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="Invoice_{invoice_number}.txt"'},
    )


# --- Supplier Bills ---
@router.post("/finance/supplier-bills", response_model=SupplierBillResponse, status_code=status.HTTP_201_CREATED)
async def create_supplier_bill(
    payload: SupplierBillCreate,
    current_user: User = Depends(PermissionChecker("finance.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = SupplierBillService(db)
    return await service.create_bill(payload)


@router.get("/finance/supplier-bills", response_model=list[SupplierBillResponse])
async def list_supplier_bills(
    supplier_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = SupplierBillRepository(db)
    records, _ = await repo.get_multi(filters={"supplier_id": supplier_id} if supplier_id else None)
    return records


# --- Payments ---
@router.post("/finance/payments", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    payload: PaymentCreate,
    current_user: User = Depends(PermissionChecker("payment.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = PaymentService(db)
    return await service.process_payment(payload)


@router.get("/finance/payments", response_model=list[PaymentResponse])
async def list_payments(
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = PaymentRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- Bank Accounts ---
@router.post("/finance/bank-accounts", response_model=BankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    payload: BankAccountCreate,
    current_user: User = Depends(PermissionChecker("bank.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    service = BankAccountService(db)
    return await service.create_bank_account(payload)


@router.get("/finance/bank-accounts", response_model=list[BankAccountResponse])
async def list_bank_accounts(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = BankAccountRepository(db)
    return await repo.get_by_org(org_id)


# --- Executive Dashboard Summary ---
@router.get("/finance/dashboard", response_model=FinanceDashboardSummary)
async def get_finance_dashboard(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("finance.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = FinanceAnalyticsService(db)
    return await service.get_dashboard_summary(org_id)
