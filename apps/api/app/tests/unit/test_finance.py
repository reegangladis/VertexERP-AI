import uuid
import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock

from app.schemas.finance import (
    JournalEntryCreate,
    JournalEntryLineCreate,
    CustomerInvoiceCreate,
    InvoiceItemCreate,
    SupplierBillCreate,
    BillItemCreate,
    PaymentCreate,
    AccountCreate,
    ExpenseClaimCreate,
    BudgetCreate,
    BudgetItemCreate,
    CreditNoteCreate,
    DebitNoteCreate,
    BankAccountCreate,
)
from app.services.finance_service import FinanceService
from app.models.finance import Account, JournalEntry, CustomerInvoice, SupplierBill, ExpenseClaim, Budget, FixedAsset, BankAccount
from fastapi import HTTPException


def get_mock_db():
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    return db


@pytest.mark.asyncio
async def test_double_entry_balance_validation():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()

    # Unbalanced entry (Debit 100 != Credit 50)
    unbalanced_data = JournalEntryCreate(
        entry_date=date.today(),
        narration="Unbalanced Test",
        lines=[
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=100.0, credit=0.0),
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=0.0, credit=50.0),
        ]
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_journal_entry(org_id, unbalanced_data)
    
    assert exc_info.value.status_code == 400
    assert "Double-entry accounting error" in exc_info.value.detail


@pytest.mark.asyncio
async def test_balanced_journal_entry():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()

    balanced_data = JournalEntryCreate(
        entry_number="JE-TEST-001",
        entry_date=date.today(),
        narration="Balanced Test",
        lines=[
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=500.0, credit=0.0),
            JournalEntryLineCreate(account_id=uuid.uuid4(), debit=0.0, credit=500.0),
        ]
    )

    service.journal_repo.create = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), entry_number="JE-TEST-001"))
    service.journal_repo.get_with_lines = AsyncMock(return_value=MagicMock(
        id=uuid.uuid4(),
        entry_number="JE-TEST-001",
        lines=[]
    ))

    result = await service.create_journal_entry(org_id, balanced_data)
    assert result.entry_number == "JE-TEST-001"


@pytest.mark.asyncio
async def test_account_creation_and_seeding():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()

    # 1. Existing duplicate code check
    service.account_repo.get_by_code = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), account_code="1010"))
    account_in = AccountCreate(account_code="1010", account_name="Cash", account_type="Assets")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_account(org_id, account_in)
    assert exc_info.value.status_code == 400

    # 2. Account creation success
    service.account_repo.get_by_code = AsyncMock(return_value=None)
    mock_acct = Account(id=uuid.uuid4(), organization_id=org_id, account_code="1030", account_name="Test Account", account_type="Assets", balance=100.0, opening_balance=100.0)
    service.account_repo.create = AsyncMock(return_value=mock_acct)

    acct_in2 = AccountCreate(account_code="1030", account_name="Test Account", account_type="Assets", opening_balance=100.0)
    res = await service.create_account(org_id, acct_in2)
    assert res.account_code == "1030"
    assert res.balance == 100.0


@pytest.mark.asyncio
async def test_delete_account_restrictions():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    acct_id = uuid.uuid4()
    org_id = uuid.uuid4()

    # 1. System account delete rejection
    sys_acct = Account(id=acct_id, organization_id=org_id, account_code="1010", account_name="Cash", account_type="Assets", is_system=True, is_deleted=False)
    service.account_repo.get_by_id = AsyncMock(return_value=sys_acct)

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_account(acct_id)
    assert "system-defined" in exc_info.value.detail

    # 2. Account with ledgers delete rejection
    normal_acct = Account(id=acct_id, organization_id=org_id, account_code="9999", account_name="Temp", account_type="Assets", is_system=False, is_deleted=False)
    service.account_repo.get_by_id = AsyncMock(return_value=normal_acct)
    service.ledger_repo.get_by_account = AsyncMock(return_value=[MagicMock()])

    with pytest.raises(HTTPException) as exc_info:
        await service.delete_account(acct_id)
    assert "existing ledger entries" in exc_info.value.detail


@pytest.mark.asyncio
async def test_journal_entry_reversal():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()
    entry_id = uuid.uuid4()

    mock_original = MagicMock()
    mock_original.id = entry_id
    mock_original.organization_id = org_id
    mock_original.entry_number = "JE-001"
    mock_original.status = "POSTED"
    mock_original.source_type = "MANUAL"
    mock_original.lines = [
        MagicMock(account_id=uuid.uuid4(), debit=100.0, credit=0.0, description="Line 1", entity_type="CUSTOMER", entity_id=uuid.uuid4()),
        MagicMock(account_id=uuid.uuid4(), debit=0.0, credit=100.0, description="Line 2", entity_type=None, entity_id=None),
    ]

    service.journal_repo.get_with_lines = AsyncMock(return_value=mock_original)
    service.create_journal_entry = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), entry_number="REV-JE-001"))
    service.post_journal_entry = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), entry_number="REV-JE-001", status="POSTED"))

    res = await service.reverse_journal_entry(entry_id, uuid.uuid4())
    assert res.status == "POSTED"
    assert mock_original.status == "REVERSED"


@pytest.mark.asyncio
async def test_customer_invoice_creation():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()

    inv_data = CustomerInvoiceCreate(
        customer_id=uuid.uuid4(),
        issue_date=date.today(),
        due_date=date.today(),
        items=[
            InvoiceItemCreate(description="Service A", quantity=2, unit_price=100.0),
        ]
    )

    mock_inv = CustomerInvoice(
        id=uuid.uuid4(),
        organization_id=org_id,
        customer_id=inv_data.customer_id,
        invoice_number="INV-001",
        issue_date=inv_data.issue_date,
        due_date=inv_data.due_date,
        subtotal=200.0,
        tax_total=0.0,
        total_amount=200.0,
        paid_amount=0.0,
        status="SENT",
        is_deleted=False,
    )

    service.get_tax_profiles = AsyncMock(return_value=[])
    service.invoice_repo.create = AsyncMock(return_value=mock_inv)
    service.get_accounts = AsyncMock(return_value=[
        MagicMock(account_code="1100", id=uuid.uuid4()),
        MagicMock(account_code="4000", id=uuid.uuid4()),
    ])
    service.create_journal_entry = AsyncMock(return_value=MagicMock(id=uuid.uuid4()))
    service.post_journal_entry = AsyncMock(return_value=MagicMock())
    service.invoice_repo.get_with_items = AsyncMock(return_value=mock_inv)

    res = await service.create_invoice(org_id, inv_data)
    assert res.total_amount == 200.0
    assert res.status == "SENT"


@pytest.mark.asyncio
async def test_credit_note_creation():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()

    cn_data = CreditNoteCreate(
        customer_id=uuid.uuid4(),
        amount=75.0,
        reason="Sales Discount"
    )

    service.credit_note_repo.create = AsyncMock(return_value=MagicMock(
        id=uuid.uuid4(),
        organization_id=org_id,
        credit_note_number="CN-001",
        amount=75.0,
        status="OPEN"
    ))
    service.get_accounts = AsyncMock(return_value=[
        MagicMock(account_code="1100", id=uuid.uuid4()),
        MagicMock(account_code="4000", id=uuid.uuid4()),
    ])
    service.create_journal_entry = AsyncMock(return_value=MagicMock(id=uuid.uuid4()))
    service.post_journal_entry = AsyncMock(return_value=MagicMock())

    res = await service.create_credit_note(org_id, cn_data)
    assert res.amount == 75.0


@pytest.mark.asyncio
async def test_payment_and_bank_balance_update():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()
    bank_id = uuid.uuid4()
    inv_id = uuid.uuid4()

    pay_data = PaymentCreate(
        payment_type="RECEIPT",
        customer_id=uuid.uuid4(),
        invoice_id=inv_id,
        bank_account_id=bank_id,
        payment_date=date.today(),
        amount=150.0,
    )

    mock_bank = BankAccount(id=bank_id, organization_id=org_id, account_name="Ops Bank", bank_name="Bank A", account_number="123", current_balance=500.0)
    mock_inv = CustomerInvoice(id=inv_id, organization_id=org_id, customer_id=pay_data.customer_id, invoice_number="INV-100", issue_date=date.today(), due_date=date.today(), total_amount=150.0, paid_amount=0.0, status="SENT")

    service.payment_repo.create = AsyncMock(return_value=MagicMock(id=uuid.uuid4(), payment_number="PAY-001", amount=150.0))
    service.bank_repo.get_by_id = AsyncMock(return_value=mock_bank)
    service.invoice_repo.get_by_id = AsyncMock(return_value=mock_inv)
    service.get_accounts = AsyncMock(return_value=[
        MagicMock(account_code="1020", id=uuid.uuid4()),
        MagicMock(account_code="1100", id=uuid.uuid4()),
    ])
    service.create_journal_entry = AsyncMock(return_value=MagicMock(id=uuid.uuid4()))
    service.post_journal_entry = AsyncMock(return_value=MagicMock())

    res = await service.create_payment(org_id, pay_data)
    assert res.amount == 150.0
    assert mock_bank.current_balance == 650.0
    assert mock_inv.status == "PAID"


@pytest.mark.asyncio
async def test_reports_and_dashboard_summary():
    db = get_mock_db()
    service = FinanceService(db)
    service.audit_repo.create = AsyncMock()
    org_id = uuid.uuid4()

    service.get_profit_loss = AsyncMock(return_value=MagicMock(total_revenue=1000.0, total_expenses=400.0, net_profit=600.0))
    service.get_invoices = AsyncMock(return_value=[MagicMock(total_amount=500.0, paid_amount=100.0)])
    service.get_bills = AsyncMock(return_value=[MagicMock(total_amount=300.0, paid_amount=100.0)])
    service.get_bank_accounts = AsyncMock(return_value=[MagicMock(current_balance=2500.0)])
    service.get_expense_claims = AsyncMock(return_value=[MagicMock(status="SUBMITTED")])
    service.get_budgets = AsyncMock(return_value=[MagicMock(total_budgeted=1000.0)])

    summary = await service.get_dashboard_summary(org_id)
    assert summary.total_revenue == 1000.0
    assert summary.total_expenses == 400.0
    assert summary.net_profit == 600.0
    assert summary.total_receivables == 400.0
    assert summary.total_payables == 200.0
    assert summary.total_cash_balance == 2500.0
    assert summary.pending_expense_claims == 1
