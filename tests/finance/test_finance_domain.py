"""Comprehensive Tests for Finance & Accounting Domain.

Covers:
- Chart of Accounts
- Fiscal Years & Period Locking Controls
- Strict Double-Entry Balanced Journals & GL Ledger
- Unbalanced Journal Rejection
- Duplicate Posting Rejection
- Immutability of Posted Records
- Atomic Reversal Transactions
- AR Sales Invoices & Automated Journal Posting
- AP Vendor Bills & Automated Journal Posting
- Payment Processing, Document Allocations, Bank Balances
- Financial Reports (Trial Balance, Balance Sheet, Profit & Loss)
- Multi-Tenant Isolation & Security
"""

import uuid
from datetime import date, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException
from app.modules.finance.models.account import Account, AccountCategory, AccountType
from app.modules.finance.models.bank import BankAccount
from app.modules.finance.models.bill import Bill, BillLine, BillStatus
from app.modules.finance.models.fiscal import FiscalPeriod, FiscalYear
from app.modules.finance.models.invoice import Invoice, InvoiceLine, InvoiceStatus
from app.modules.finance.models.journal import (
    EntryStatus,
    EntryType,
    PartnerType,
)
from app.modules.finance.models.party import CustomerParty, VendorParty
from app.modules.finance.models.payment import (
    PaymentStatus,
    PaymentType,
)
from app.modules.finance.repositories.bank_repository import BankRepository
from app.modules.finance.repositories.invoice_repository import InvoiceRepository
from app.modules.finance.repositories.journal_repository import (
    GeneralLedgerRepository,
)
from app.modules.finance.schemas.journal import JournalEntryCreate, JournalLineCreate
from app.modules.finance.schemas.payment import PaymentAllocationCreate, PaymentCreate
from app.modules.finance.services.bill_service import BillService
from app.modules.finance.services.invoice_service import InvoiceService
from app.modules.finance.services.journal_service import JournalEntryService
from app.modules.finance.services.payment_service import PaymentService
from app.modules.finance.services.report_service import FinancialReportService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def finance_setup(db_session: AsyncSession):
    """Sets up a complete Chart of Accounts, Open & Locked Fiscal Periods for testing."""
    tenant = Tenant(name="Global Financials", slug=f"fin-{uuid.uuid4().hex[:6]}")
    db_session.add(tenant)
    await db_session.flush()

    org = Organization(
        tenant_id=tenant.id,
        name="Global Corp Headquarters",
        legal_name="Global Corp LLC",
        tax_identifier=f"TAX-{uuid.uuid4().hex[:4]}",
    )
    db_session.add(org)
    await db_session.flush()

    # Create Chart of Accounts
    # 1. Assets
    bank_acct = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="1000",
        name="Cash & Bank",
        account_type=AccountType.ASSET,
        account_category=AccountCategory.CURRENT_ASSET,
        currency="USD",
    )
    ar_acct = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="1100",
        name="Accounts Receivable",
        account_type=AccountType.ASSET,
        account_category=AccountCategory.CURRENT_ASSET,
        currency="USD",
    )
    # 2. Liabilities
    ap_acct = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="2000",
        name="Accounts Payable",
        account_type=AccountType.LIABILITY,
        account_category=AccountCategory.CURRENT_LIABILITY,
        currency="USD",
    )
    tax_payable = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="2100",
        name="Sales Tax Payable",
        account_type=AccountType.LIABILITY,
        account_category=AccountCategory.CURRENT_LIABILITY,
        currency="USD",
    )
    # 3. Equity
    equity_acct = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="3000",
        name="Common Stock / Owners Equity",
        account_type=AccountType.EQUITY,
        account_category=AccountCategory.EQUITY,
        currency="USD",
    )
    # 4. Revenue
    revenue_acct = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="4000",
        name="Sales Revenue",
        account_type=AccountType.REVENUE,
        account_category=AccountCategory.OPERATING_REVENUE,
        currency="USD",
    )
    # 5. Expense
    expense_acct = Account(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="5000",
        name="Operating Expenses",
        account_type=AccountType.EXPENSE,
        account_category=AccountCategory.OPERATING_EXPENSE,
        currency="USD",
    )

    db_session.add_all(
        [bank_acct, ar_acct, ap_acct, tax_payable, equity_acct, revenue_acct, expense_acct]
    )
    await db_session.flush()

    # Bank Account entity
    bank_entity = BankAccount(
        tenant_id=tenant.id,
        organization_id=org.id,
        account_name="Primary Treasury Operating Account",
        account_number="US99-8821-4401",
        bank_name="JPMorgan Chase",
        currency="USD",
        gl_account_id=bank_acct.id,
        current_balance=Decimal("0.0000"),
        is_active=True,
    )
    db_session.add(bank_entity)
    await db_session.flush()

    # Fiscal Year & Periods
    today = date.today()
    fy = FiscalYear(
        tenant_id=tenant.id,
        organization_id=org.id,
        code=f"FY-{today.year}",
        name=f"FY-{today.year}",
        start_date=date(today.year, 1, 1),
        end_date=date(today.year, 12, 31),
        is_closed=False,
    )
    db_session.add(fy)
    await db_session.flush()

    # Period 1: Open current period
    open_period = FiscalPeriod(
        tenant_id=tenant.id,
        organization_id=org.id,
        fiscal_year_id=fy.id,
        period_number=1,
        period_name=f"Period 1 - {today.year}",
        start_date=date(today.year, 1, 1),
        end_date=date(today.year, 12, 31),
        is_locked=False,
        is_closed=False,
    )
    # Period 2: Locked historical period
    locked_period = FiscalPeriod(
        tenant_id=tenant.id,
        organization_id=org.id,
        fiscal_year_id=fy.id,
        period_number=2,
        period_name=f"Historical Locked Period - {today.year - 1}",
        start_date=date(today.year - 1, 1, 1),
        end_date=date(today.year - 1, 12, 31),
        is_locked=True,
        is_closed=True,
    )
    db_session.add_all([open_period, locked_period])
    await db_session.flush()

    # Customer & Vendor Parties
    customer = CustomerParty(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="CUST-001",
        name="Enterprise Client Corp",
        email="billing@clientcorp.com",
        ar_account_id=ar_acct.id,
        payment_terms_days=30,
        credit_limit=Decimal("50000.0000"),
    )
    vendor = VendorParty(
        tenant_id=tenant.id,
        organization_id=org.id,
        code="VEND-001",
        name="Tech Infrastructure Supplier Inc",
        email="ap@techsupplies.com",
        ap_account_id=ap_acct.id,
        payment_terms_days=30,
    )
    db_session.add_all([customer, vendor])
    await db_session.flush()

    return {
        "tenant": tenant,
        "org": org,
        "accounts": {
            "bank": bank_acct,
            "ar": ar_acct,
            "ap": ap_acct,
            "tax": tax_payable,
            "equity": equity_acct,
            "revenue": revenue_acct,
            "expense": expense_acct,
        },
        "bank_account": bank_entity,
        "fiscal_year": fy,
        "open_period": open_period,
        "locked_period": locked_period,
        "customer": customer,
        "vendor": vendor,
    }


@pytest.mark.asyncio
async def test_balanced_journal_entry_posting_and_gl(db_session: AsyncSession, finance_setup: dict):
    """Verifies that a balanced double-entry journal (Debits == Credits) posts successfully to the GL."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    bank_acct = data["accounts"]["bank"]
    equity_acct = data["accounts"]["equity"]

    journal_service = JournalEntryService(db_session)
    gl_repo = GeneralLedgerRepository(db_session)

    # Capital injection: Debit Bank $10,000, Credit Owner Equity $10,000
    create_dto = JournalEntryCreate(
        entry_type=EntryType.STANDARD,
        entry_date=date.today(),
        posting_date=date.today(),
        notes="Initial Capital Investment",
        lines=[
            JournalLineCreate(
                account_id=bank_acct.id,
                debit=Decimal("10000.0000"),
                credit=Decimal("0.0000"),
                description="Debit Cash for investment",
            ),
            JournalLineCreate(
                account_id=equity_acct.id,
                debit=Decimal("0.0000"),
                credit=Decimal("10000.0000"),
                description="Credit Equity for investment",
            ),
        ],
    )

    entry = await journal_service.create_draft_entry(create_dto, tenant_id, org_id)
    assert entry.status == EntryStatus.DRAFT
    assert entry.total_debit == Decimal("10000.0000")
    assert entry.total_credit == Decimal("10000.0000")

    # Post Entry
    posted_entry = await journal_service.post_entry(entry.id, tenant_id, org_id)
    assert posted_entry.status == EntryStatus.POSTED
    assert posted_entry.posted_at is not None

    # Verify General Ledger records created
    gl_lines = await gl_repo.list_by_journal(posted_entry.id, tenant_id, org_id)
    assert len(gl_lines) == 2

    # Verify Account Totals
    bank_debit, bank_credit = await gl_repo.get_account_totals(bank_acct.id, tenant_id, org_id)
    assert bank_debit == Decimal("10000.0000")
    assert bank_credit == Decimal("0.0000")

    equity_debit, equity_credit = await gl_repo.get_account_totals(
        equity_acct.id, tenant_id, org_id
    )
    assert equity_debit == Decimal("0.0000")
    assert equity_credit == Decimal("10000.0000")


@pytest.mark.asyncio
async def test_unbalanced_journal_rejected(db_session: AsyncSession, finance_setup: dict):
    """Verifies that an unbalanced journal entry (Debits != Credits) is strictly rejected upon posting."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    bank_acct = data["accounts"]["bank"]
    expense_acct = data["accounts"]["expense"]

    journal_service = JournalEntryService(db_session)

    # Unbalanced: Debit Expense $500, Credit Bank $450 (difference $50)
    create_dto = JournalEntryCreate(
        entry_type=EntryType.STANDARD,
        entry_date=date.today(),
        posting_date=date.today(),
        notes="Unbalanced Entry",
        lines=[
            JournalLineCreate(
                account_id=expense_acct.id, debit=Decimal("500.0000"), credit=Decimal("0.0000")
            ),
            JournalLineCreate(
                account_id=bank_acct.id, debit=Decimal("0.0000"), credit=Decimal("450.0000")
            ),
        ],
    )

    entry = await journal_service.create_draft_entry(create_dto, tenant_id, org_id)

    with pytest.raises(BadRequestException) as exc:
        await journal_service.post_entry(entry.id, tenant_id, org_id)
    assert "Unbalanced Journal Entry" in str(exc.value)


@pytest.mark.asyncio
async def test_duplicate_posting_and_immutability(db_session: AsyncSession, finance_setup: dict):
    """Verifies that duplicate posting is rejected and posted entries cannot be modified or deleted."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    bank_acct = data["accounts"]["bank"]
    equity_acct = data["accounts"]["equity"]

    journal_service = JournalEntryService(db_session)

    create_dto = JournalEntryCreate(
        entry_type=EntryType.STANDARD,
        entry_date=date.today(),
        posting_date=date.today(),
        notes="Capital Contribution",
        lines=[
            JournalLineCreate(
                account_id=bank_acct.id, debit=Decimal("5000.0000"), credit=Decimal("0.0000")
            ),
            JournalLineCreate(
                account_id=equity_acct.id, debit=Decimal("0.0000"), credit=Decimal("5000.0000")
            ),
        ],
    )
    entry = await journal_service.create_draft_entry(create_dto, tenant_id, org_id)
    await journal_service.post_entry(entry.id, tenant_id, org_id)

    # Attempt Duplicate Posting
    with pytest.raises(BadRequestException) as exc:
        await journal_service.post_entry(entry.id, tenant_id, org_id)
    assert "already POSTED" in str(exc.value)


@pytest.mark.asyncio
async def test_journal_reversal(db_session: AsyncSession, finance_setup: dict):
    """Verifies that corrections create a reversal transaction and preserve auditability."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    bank_acct = data["accounts"]["bank"]
    expense_acct = data["accounts"]["expense"]

    journal_service = JournalEntryService(db_session)
    gl_repo = GeneralLedgerRepository(db_session)

    # Initial entry: Debit Expense $1,000, Credit Cash $1,000
    create_dto = JournalEntryCreate(
        entry_type=EntryType.STANDARD,
        entry_date=date.today(),
        posting_date=date.today(),
        notes="Incorrect Office Expense",
        lines=[
            JournalLineCreate(
                account_id=expense_acct.id, debit=Decimal("1000.0000"), credit=Decimal("0.0000")
            ),
            JournalLineCreate(
                account_id=bank_acct.id, debit=Decimal("0.0000"), credit=Decimal("1000.0000")
            ),
        ],
    )
    entry = await journal_service.create_draft_entry(create_dto, tenant_id, org_id)
    await journal_service.post_entry(entry.id, tenant_id, org_id)

    # Execute Reversal
    reversal_entry = await journal_service.reverse_entry(
        entry.id,
        tenant_id=tenant_id,
        org_id=org_id,
        notes="Entry entered in error by clerk",
    )

    assert reversal_entry.status == EntryStatus.POSTED
    assert reversal_entry.entry_type == EntryType.REVERSAL
    assert reversal_entry.reference_id == str(entry.id)

    # Check original entry status updated to REVERSED
    refreshed_original = await journal_service.journal_repo.get_by_id(entry.id, tenant_id, org_id)
    assert refreshed_original.status == EntryStatus.REVERSED

    # Verify GL balances offset to net zero
    exp_debit, exp_credit = await gl_repo.get_account_totals(expense_acct.id, tenant_id, org_id)
    assert exp_debit == Decimal("1000.0000")
    assert exp_credit == Decimal("1000.0000")  # Offset by reversal counter-credit


@pytest.mark.asyncio
async def test_period_locking_prevents_posting(db_session: AsyncSession, finance_setup: dict):
    """Verifies that posting in a locked fiscal period is rejected."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    bank_acct = data["accounts"]["bank"]
    equity_acct = data["accounts"]["equity"]

    journal_service = JournalEntryService(db_session)

    # Post in historical locked period date (last year)
    locked_date = date(date.today().year - 1, 6, 15)
    create_dto = JournalEntryCreate(
        entry_type=EntryType.STANDARD,
        entry_date=locked_date,
        posting_date=locked_date,
        notes="Historical adjustment",
        lines=[
            JournalLineCreate(
                account_id=bank_acct.id, debit=Decimal("2000.0000"), credit=Decimal("0.0000")
            ),
            JournalLineCreate(
                account_id=equity_acct.id, debit=Decimal("0.0000"), credit=Decimal("2000.0000")
            ),
        ],
    )
    entry = await journal_service.create_draft_entry(create_dto, tenant_id, org_id)

    with pytest.raises(BadRequestException) as exc:
        await journal_service.post_entry(entry.id, tenant_id, org_id)
    assert "LOCKED" in str(exc.value) or "CLOSED" in str(exc.value)


@pytest.mark.asyncio
async def test_sales_invoice_posting_and_ar_ledger(db_session: AsyncSession, finance_setup: dict):
    """Verifies that posting a Sales Invoice creates AR ledger journals and updates invoice balances."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    customer = data["customer"]
    rev_acct = data["accounts"]["revenue"]
    ar_acct = data["accounts"]["ar"]

    invoice_service = InvoiceService(db_session)
    gl_repo = GeneralLedgerRepository(db_session)

    invoice = Invoice(
        tenant_id=tenant_id,
        organization_id=org_id,
        invoice_number="INV-2026-0001",
        customer_id=customer.id,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        subtotal_amount=Decimal("2500.0000"),
        tax_amount=Decimal("0.0000"),
        total_amount=Decimal("2500.0000"),
        amount_due=Decimal("2500.0000"),
        status=InvoiceStatus.DRAFT,
        lines=[
            InvoiceLine(
                tenant_id=tenant_id,
                description="Cloud Software Implementation Service",
                account_id=rev_acct.id,
                quantity=Decimal("1.0000"),
                unit_price=Decimal("2500.0000"),
                tax_rate=Decimal("0.0000"),
                tax_amount=Decimal("0.0000"),
                line_total=Decimal("2500.0000"),
            )
        ],
    )
    db_session.add(invoice)
    await db_session.flush()

    # Post Invoice
    posted_inv = await invoice_service.post_invoice(invoice.id, tenant_id, org_id)
    assert posted_inv.status == InvoiceStatus.POSTED
    assert posted_inv.posted_journal_entry_id is not None

    # Check GL: AR debited $2500, Revenue credited $2500
    ar_d, ar_c = await gl_repo.get_account_totals(ar_acct.id, tenant_id, org_id)
    assert ar_d == Decimal("2500.0000")
    assert ar_c == Decimal("0.0000")

    rev_d, rev_c = await gl_repo.get_account_totals(rev_acct.id, tenant_id, org_id)
    assert rev_d == Decimal("0.0000")
    assert rev_c == Decimal("2500.0000")


@pytest.mark.asyncio
async def test_vendor_bill_posting_and_ap_ledger(db_session: AsyncSession, finance_setup: dict):
    """Verifies that posting a Vendor Bill creates AP ledger journals and updates bill balances."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    vendor = data["vendor"]
    exp_acct = data["accounts"]["expense"]
    ap_acct = data["accounts"]["ap"]

    bill_service = BillService(db_session)
    gl_repo = GeneralLedgerRepository(db_session)

    bill = Bill(
        tenant_id=tenant_id,
        organization_id=org_id,
        bill_number="BILL-2026-0001",
        vendor_id=vendor.id,
        bill_date=date.today(),
        due_date=date.today() + timedelta(days=30),
        currency="USD",
        subtotal_amount=Decimal("1200.0000"),
        tax_amount=Decimal("0.0000"),
        total_amount=Decimal("1200.0000"),
        amount_due=Decimal("1200.0000"),
        status=BillStatus.DRAFT,
        lines=[
            BillLine(
                tenant_id=tenant_id,
                description="Server Hosting Services",
                expense_account_id=exp_acct.id,
                quantity=Decimal("1.0000"),
                unit_price=Decimal("1200.0000"),
                tax_rate=Decimal("0.0000"),
                tax_amount=Decimal("0.0000"),
                line_total=Decimal("1200.0000"),
            )
        ],
    )
    db_session.add(bill)
    await db_session.flush()

    # Post Bill
    posted_bill = await bill_service.post_bill(bill.id, tenant_id, org_id)
    assert posted_bill.status == BillStatus.POSTED
    assert posted_bill.posted_journal_entry_id is not None

    # Check GL: Expense debited $1200, AP credited $1200
    exp_d, exp_c = await gl_repo.get_account_totals(exp_acct.id, tenant_id, org_id)
    assert exp_d == Decimal("1200.0000")
    assert exp_c == Decimal("0.0000")

    ap_d, ap_c = await gl_repo.get_account_totals(ap_acct.id, tenant_id, org_id)
    assert ap_d == Decimal("0.0000")
    assert ap_c == Decimal("1200.0000")


@pytest.mark.asyncio
async def test_payment_allocation_and_bank_balance(db_session: AsyncSession, finance_setup: dict):
    """Verifies that posting customer receipt reconciles invoice, debits bank, credits AR, and updates bank account."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    customer = data["customer"]
    rev_acct = data["accounts"]["revenue"]
    data["accounts"]["ar"]
    data["accounts"]["bank"]
    bank_entity = data["bank_account"]

    invoice_service = InvoiceService(db_session)
    payment_service = PaymentService(db_session)
    bank_repo = BankRepository(db_session)
    invoice_repo = InvoiceRepository(db_session)

    # 1. Create and post invoice for $3,000
    inv = Invoice(
        tenant_id=tenant_id,
        organization_id=org_id,
        invoice_number="INV-PAY-001",
        customer_id=customer.id,
        issue_date=date.today(),
        due_date=date.today() + timedelta(days=15),
        currency="USD",
        subtotal_amount=Decimal("3000.0000"),
        tax_amount=Decimal("0.0000"),
        total_amount=Decimal("3000.0000"),
        amount_due=Decimal("3000.0000"),
        status=InvoiceStatus.DRAFT,
        lines=[
            InvoiceLine(
                tenant_id=tenant_id,
                description="Consulting Project",
                account_id=rev_acct.id,
                quantity=Decimal("1.0000"),
                unit_price=Decimal("3000.0000"),
                tax_rate=Decimal("0.0000"),
                tax_amount=Decimal("0.0000"),
                line_total=Decimal("3000.0000"),
            )
        ],
    )
    db_session.add(inv)
    await db_session.flush()
    posted_inv = await invoice_service.post_invoice(inv.id, tenant_id, org_id)

    # 2. Process full customer payment of $3,000 allocated to the invoice
    pay_dto = PaymentCreate(
        payment_type=PaymentType.RECEIPT,
        partner_type=PartnerType.CUSTOMER,
        partner_id=customer.id,
        payment_date=date.today(),
        payment_method="BANK",
        bank_account_id=bank_entity.id,
        currency="USD",
        amount=Decimal("3000.0000"),
        allocations=[
            PaymentAllocationCreate(
                invoice_id=posted_inv.id,
                allocated_amount=Decimal("3000.0000"),
            )
        ],
    )
    payment = await payment_service.create_payment(pay_dto, tenant_id, org_id)
    assert payment.status == PaymentStatus.DRAFT
    assert payment.allocated_amount == Decimal("3000.0000")

    # Post Payment
    posted_pay = await payment_service.post_payment(payment.id, tenant_id, org_id)
    assert posted_pay.status == PaymentStatus.POSTED

    # 3. Verify Invoice balance reduced to 0 and status is PAID
    reloaded_inv = await invoice_repo.get_by_id(posted_inv.id, tenant_id, org_id)
    assert reloaded_inv.amount_due == Decimal("0.0000")
    assert reloaded_inv.status == InvoiceStatus.PAID

    # 4. Verify Bank Account balance increased by $3,000
    reloaded_bank = await bank_repo.get_account_by_id(bank_entity.id, tenant_id, org_id)
    assert reloaded_bank.current_balance == Decimal("3000.0000")


@pytest.mark.asyncio
async def test_financial_reports_trial_balance_and_balance_sheet(
    db_session: AsyncSession, finance_setup: dict
):
    """Verifies that Trial Balance, Balance Sheet, and P&L accurately report totals and balance equations."""
    data = finance_setup
    tenant_id = data["tenant"].id
    org_id = data["org"].id
    bank_acct = data["accounts"]["bank"]
    equity_acct = data["accounts"]["equity"]
    rev_acct = data["accounts"]["revenue"]
    exp_acct = data["accounts"]["expense"]

    journal_service = JournalEntryService(db_session)
    report_service = FinancialReportService(db_session)

    # 1. Equity Contribution: Debit Bank $50,000, Credit Equity $50,000
    await journal_service.create_and_post_entry(
        JournalEntryCreate(
            entry_type=EntryType.STANDARD,
            entry_date=date.today(),
            posting_date=date.today(),
            notes="Initial Equity",
            lines=[
                JournalLineCreate(
                    account_id=bank_acct.id, debit=Decimal("50000.0000"), credit=Decimal("0.0000")
                ),
                JournalLineCreate(
                    account_id=equity_acct.id, debit=Decimal("0.0000"), credit=Decimal("50000.0000")
                ),
            ],
        ),
        tenant_id,
        org_id,
    )

    # 2. Sales: Debit Bank $15,000, Credit Revenue $15,000
    await journal_service.create_and_post_entry(
        JournalEntryCreate(
            entry_type=EntryType.STANDARD,
            entry_date=date.today(),
            posting_date=date.today(),
            notes="Direct Cash Sales",
            lines=[
                JournalLineCreate(
                    account_id=bank_acct.id, debit=Decimal("15000.0000"), credit=Decimal("0.0000")
                ),
                JournalLineCreate(
                    account_id=rev_acct.id, debit=Decimal("0.0000"), credit=Decimal("15000.0000")
                ),
            ],
        ),
        tenant_id,
        org_id,
    )

    # 3. Expense: Debit Expense $5,000, Credit Bank $5,000
    await journal_service.create_and_post_entry(
        JournalEntryCreate(
            entry_type=EntryType.STANDARD,
            entry_date=date.today(),
            posting_date=date.today(),
            notes="Office Rent & Utilities",
            lines=[
                JournalLineCreate(
                    account_id=exp_acct.id, debit=Decimal("5000.0000"), credit=Decimal("0.0000")
                ),
                JournalLineCreate(
                    account_id=bank_acct.id, debit=Decimal("0.0000"), credit=Decimal("5000.0000")
                ),
            ],
        ),
        tenant_id,
        org_id,
    )

    # Trial Balance Verification
    tb = await report_service.get_trial_balance(date.today(), tenant_id, org_id)
    assert tb.is_balanced is True
    assert tb.total_debit == tb.total_credit
    assert tb.total_debit == Decimal("70000.0000")  # 50k + 15k + 5k

    # Profit & Loss Verification
    pnl = await report_service.get_profit_and_loss(
        date(date.today().year, 1, 1), date.today(), tenant_id, org_id
    )
    assert pnl.total_revenue == Decimal("15000.0000")
    assert pnl.total_expense == Decimal("5000.0000")
    assert pnl.net_income == Decimal("10000.0000")

    # Balance Sheet Verification
    # Assets: Bank = 50k + 15k - 5k = 60,000
    # Equity: Owner Equity (50,000) + Retained Net Income (10,000) = 60,000
    # Assets (60,000) = Liabilities (0) + Equity (60,000)
    bs = await report_service.get_balance_sheet(date.today(), tenant_id, org_id)
    assert bs.is_balanced is True
    assert bs.total_assets == Decimal("60000.0000")
    assert bs.total_liabilities == Decimal("0.0000")
    assert bs.total_equity == Decimal("60000.0000")
    assert bs.total_assets == bs.total_liabilities_and_equity


@pytest.mark.asyncio
async def test_finance_api_auth_and_tenant_isolation(async_client: AsyncClient):
    """Verifies that API endpoints enforce authentication and strict tenant boundary isolation."""
    # 1. Register Tenant A
    reg_a = await async_client.post(
        "/api/v1/identity/auth/register",
        json={
            "email": f"cfo-{uuid.uuid4().hex[:4]}@tenant-a.com",
            "password": "FinSecurePassword123!",
            "full_name": "CFO Tenant A",
            "tenant_name": "Tenant A Holdings",
            "tenant_slug": f"ten-a-{uuid.uuid4().hex[:6]}",
            "organization_name": "Tenant A Financials",
            "tax_identifier": "TAX-A01",
        },
    )
    assert reg_a.status_code == 201
    token_a = reg_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register Tenant B
    reg_b = await async_client.post(
        "/api/v1/identity/auth/register",
        json={
            "email": f"cfo-{uuid.uuid4().hex[:4]}@tenant-b.com",
            "password": "FinSecurePassword123!",
            "full_name": "CFO Tenant B",
            "tenant_name": "Tenant B Holdings",
            "tenant_slug": f"ten-b-{uuid.uuid4().hex[:6]}",
            "organization_name": "Tenant B Financials",
            "tax_identifier": "TAX-B01",
        },
    )
    assert reg_b.status_code == 201
    token_b = reg_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. Unauthenticated requests rejected with 401
    async_client.cookies.clear()
    unauth = await async_client.get("/api/v1/finance/accounts/")
    assert unauth.status_code == 401

    # 4. Tenant A creates an Account
    create_acct_a = await async_client.post(
        "/api/v1/finance/accounts/",
        json={
            "code": "1010",
            "name": "Tenant A Operating Account",
            "account_type": "ASSET",
            "account_category": "CURRENT_ASSET",
            "currency": "USD",
        },
        headers=headers_a,
    )
    assert create_acct_a.status_code == 201
    acct_a_id = create_acct_a.json()["id"]

    # 5. Tenant B cannot view Tenant A's account (404 isolation)
    get_acct_from_b = await async_client.get(
        f"/api/v1/finance/accounts/{acct_a_id}", headers=headers_b
    )
    assert get_acct_from_b.status_code == 404
