import uuid
from datetime import date
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException, status

from app.models.finance_accounting_v12 import (
    Account,
    BankAccount,
    CustomerInvoice,
    JournalEntry,
    Payment,
    SupplierBill,
)
from app.services.finance_accounting import (
    AccountingEngine,
    BankAccountService,
    FinanceAnalyticsService,
    InvoiceService,
    PaymentService,
    SupplierBillService,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_account_creation_and_duplicate_validation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    engine = AccountingEngine(mock_db_session)
    org_id = uuid.uuid4()

    from app.schemas.finance_accounting import AccountCreate
    payload = AccountCreate(
        organization_id=org_id,
        account_code="1010",
        account_name="Cash and Cash Equivalents",
        account_type="Asset",
    )

    acc_obj = Account(
        id=uuid.uuid4(),
        organization_id=org_id,
        account_code=payload.account_code,
        account_name=payload.account_name,
        account_type=payload.account_type,
        status="Active",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
    ]
    acc = await engine.create_account(payload)
    assert acc is not None

    # Duplicate code check
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(acc_obj)
    with pytest.raises(HTTPException) as exc_info:
        await engine.create_account(payload)
    assert exc_info.value.status_code == 400
    assert "already exists in this organization" in exc_info.value.detail


@pytest.mark.asyncio
async def test_double_entry_journal_validation(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    engine = AccountingEngine(mock_db_session)
    org_id = uuid.uuid4()
    acc1_id = uuid.uuid4()
    acc2_id = uuid.uuid4()

    from app.schemas.finance_accounting import JournalEntryCreate, JournalEntryLineCreate
    # Unbalanced entry check (debit 1000 != credit 500)
    unbalanced_payload = JournalEntryCreate(
        organization_id=org_id,
        journal_number="JV-2026-0001",
        posting_date=date(2026, 8, 1),
        description="Unbalanced trial entry",
        lines=[
            JournalEntryLineCreate(account_id=acc1_id, debit=1000.0, credit=0.0),
            JournalEntryLineCreate(account_id=acc2_id, debit=0.0, credit=500.0),
        ],
    )

    with pytest.raises(HTTPException) as exc_info:
        await engine.create_journal_entry(unbalanced_payload)
    assert exc_info.value.status_code == 400
    assert "Unbalanced Journal Entry" in exc_info.value.detail

    # Balanced entry check (debit 1000 == credit 1000)
    balanced_payload = JournalEntryCreate(
        organization_id=org_id,
        journal_number="JV-2026-0002",
        posting_date=date(2026, 8, 1),
        description="Balanced rent payment",
        lines=[
            JournalEntryLineCreate(account_id=acc1_id, debit=1000.0, credit=0.0),
            JournalEntryLineCreate(account_id=acc2_id, debit=0.0, credit=1000.0),
        ],
    )

    entry_obj = JournalEntry(
        id=uuid.uuid4(),
        organization_id=org_id,
        journal_number="JV-2026-0002",
        posting_date=balanced_payload.posting_date,
        description=balanced_payload.description,
        status="Draft",
        lines=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # duplicate check
        create_mock_execute_result(None),  # line 1 insert
        create_mock_execute_result(None),  # line 2 insert
        create_mock_execute_result(entry_obj),  # get_with_lines
    ]
    entry = await engine.create_journal_entry(balanced_payload)
    assert entry is not None
    assert entry.journal_number == "JV-2026-0002"


@pytest.mark.asyncio
async def test_customer_invoice_creation_and_pdf(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    inv_service = InvoiceService(mock_db_session)
    cust_id = uuid.uuid4()

    from app.schemas.finance_accounting import CustomerInvoiceCreate, InvoiceItemCreate
    payload = CustomerInvoiceCreate(
        customer_id=cust_id,
        invoice_number="INV-2026-0001",
        invoice_date=date(2026, 8, 1),
        due_date=date(2026, 8, 31),
        discount=200.0,
        items=[
            InvoiceItemCreate(
                item_description="Enterprise ERP Consulting",
                quantity=10.0,
                unit_price=200.0,
                tax_amount=100.0,
            )
        ],
    )

    inv_obj = CustomerInvoice(
        id=uuid.uuid4(),
        customer_id=cust_id,
        invoice_number="INV-2026-0001",
        invoice_date=payload.invoice_date,
        due_date=payload.due_date,
        subtotal=2000.0,
        tax=100.0,
        discount=200.0,
        grand_total=1900.0,
        paid_amount=0.0,
        balance_due=1900.0,
        status="Unpaid",
        items=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # duplicate check
        create_mock_execute_result(None),  # line insert
        create_mock_execute_result(inv_obj),  # get_with_items
    ]

    inv = await inv_service.create_invoice(payload)
    assert inv is not None
    assert inv.grand_total == 1900.0

    # PDF generation test
    mock_db_session.execute.side_effect = [
        create_mock_execute_result(inv_obj),
        create_mock_execute_result(inv_obj, []),
    ]
    pdf_text = await inv_service.generate_pdf_text("INV-2026-0001")
    assert "VERTEXERP AI ENTERPRISE FINANCE" in pdf_text
    assert "INV-2026-0001" in pdf_text


@pytest.mark.asyncio
async def test_payment_processing(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    pay_service = PaymentService(mock_db_session)
    inv_id = uuid.uuid4()
    cust_id = uuid.uuid4()

    from app.schemas.finance_accounting import PaymentCreate
    pay_payload = PaymentCreate(
        payment_reference="PAY-REF-1001",
        payment_type="Customer Receipt",
        payment_method="Bank Transfer",
        customer_id=cust_id,
        invoice_id=inv_id,
        amount=1000.0,
        payment_date=date(2026, 8, 5),
    )

    pay_obj = Payment(
        id=uuid.uuid4(),
        payment_reference="PAY-REF-1001",
        payment_type="Customer Receipt",
        payment_method="Bank Transfer",
        customer_id=cust_id,
        invoice_id=inv_id,
        amount=1000.0,
        payment_date=pay_payload.payment_date,
        status="Completed",
    )

    inv_obj = CustomerInvoice(
        id=inv_id,
        customer_id=cust_id,
        invoice_number="INV-2026-0001",
        grand_total=1900.0,
        paid_amount=0.0,
        balance_due=1900.0,
        status="Unpaid",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
        create_mock_execute_result(inv_obj),  # get invoice
        create_mock_execute_result(inv_obj),  # update invoice balance
    ]

    payment = await pay_service.process_payment(pay_payload)
    assert payment is not None
    assert payment.amount == 1000.0


@pytest.mark.asyncio
async def test_finance_analytics_dashboard_summary(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    service = FinanceAnalyticsService(mock_db_session)
    org_id = uuid.uuid4()

    summary = await service.get_dashboard_summary(org_id)
    assert summary.total_revenue == 0.0
    assert summary.cash_flow == 0.0
