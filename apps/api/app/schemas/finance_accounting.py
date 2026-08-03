import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


# --- Chart of Accounts Schemas ---
class AccountBase(BaseModel):
    account_code: str = Field(..., min_length=1, max_length=50)
    account_name: str = Field(..., min_length=1, max_length=255)
    account_type: str = Field(..., min_length=1, max_length=100)  # Asset, Liability, Equity, Revenue, Expense
    currency: str = Field(default="USD", max_length=10)
    is_control_account: bool = Field(default=False)
    status: str = Field(default="Active", max_length=50)


class AccountCreate(AccountBase):
    organization_id: uuid.UUID
    parent_account_id: uuid.UUID | None = None


class AccountResponse(AccountBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    parent_account_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Journal Entry Schemas ---
class JournalEntryLineBase(BaseModel):
    account_id: uuid.UUID
    debit: float = Field(default=0.0, ge=0)
    credit: float = Field(default=0.0, ge=0)
    description: str | None = Field(None, max_length=1000)


class JournalEntryLineCreate(JournalEntryLineBase):
    pass


class JournalEntryLineResponse(JournalEntryLineBase):
    id: uuid.UUID
    journal_entry_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JournalEntryBase(BaseModel):
    journal_number: str = Field(..., min_length=1, max_length=100)
    posting_date: date
    reference: str | None = Field(None, max_length=100)
    description: str = Field(..., min_length=1, max_length=2000)
    status: str = Field(default="Draft", max_length=50)


class JournalEntryCreate(JournalEntryBase):
    organization_id: uuid.UUID
    lines: list[JournalEntryLineCreate] = Field(..., min_length=2)


class JournalEntryResponse(JournalEntryBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_by: uuid.UUID | None = None
    approved_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    lines: list[JournalEntryLineResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Customer Invoice Schemas ---
class InvoiceItemBase(BaseModel):
    item_description: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: uuid.UUID
    invoice_id: uuid.UUID
    total_price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CustomerInvoiceBase(BaseModel):
    invoice_number: str = Field(..., min_length=1, max_length=100)
    invoice_date: date
    due_date: date
    discount: float = Field(default=0.0, ge=0)
    status: str = Field(default="Unpaid", max_length=50)


class CustomerInvoiceCreate(CustomerInvoiceBase):
    customer_id: uuid.UUID
    items: list[InvoiceItemCreate] = Field(..., min_length=1)


class CustomerInvoiceResponse(CustomerInvoiceBase):
    id: uuid.UUID
    customer_id: uuid.UUID
    subtotal: float
    tax: float
    grand_total: float
    paid_amount: float
    balance_due: float
    created_at: datetime
    updated_at: datetime
    items: list[InvoiceItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Supplier Bill Schemas ---
class BillItemBase(BaseModel):
    item_description: str = Field(..., min_length=1, max_length=255)
    quantity: float = Field(default=1.0, gt=0)
    unit_price: float = Field(default=0.0, ge=0)
    tax_amount: float = Field(default=0.0, ge=0)


class BillItemCreate(BillItemBase):
    pass


class BillItemResponse(BillItemBase):
    id: uuid.UUID
    bill_id: uuid.UUID
    total_price: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SupplierBillBase(BaseModel):
    bill_number: str = Field(..., min_length=1, max_length=100)
    bill_date: date
    due_date: date
    discount: float = Field(default=0.0, ge=0)
    status: str = Field(default="Unpaid", max_length=50)


class SupplierBillCreate(SupplierBillBase):
    supplier_id: uuid.UUID
    items: list[BillItemCreate] = Field(..., min_length=1)


class SupplierBillResponse(SupplierBillBase):
    id: uuid.UUID
    supplier_id: uuid.UUID
    subtotal: float
    tax: float
    grand_total: float
    paid_amount: float
    balance_due: float
    created_at: datetime
    updated_at: datetime
    items: list[BillItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Payment Schemas ---
class PaymentBase(BaseModel):
    payment_reference: str = Field(..., min_length=1, max_length=100)
    payment_type: str = Field(..., max_length=50)  # Customer Receipt, Vendor Payment
    payment_method: str = Field(default="Bank Transfer", max_length=50)
    amount: float = Field(..., gt=0)
    payment_date: date
    status: str = Field(default="Completed", max_length=50)


class PaymentCreate(PaymentBase):
    customer_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    invoice_id: uuid.UUID | None = None
    bill_id: uuid.UUID | None = None


class PaymentResponse(PaymentBase):
    id: uuid.UUID
    customer_id: uuid.UUID | None = None
    supplier_id: uuid.UUID | None = None
    invoice_id: uuid.UUID | None = None
    bill_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Bank Account Schemas ---
class BankAccountBase(BaseModel):
    bank_name: str = Field(..., min_length=1, max_length=255)
    account_holder: str = Field(..., min_length=1, max_length=255)
    account_number: str = Field(..., min_length=1, max_length=100)
    ifsc_code: str | None = Field(None, max_length=50)
    branch: str | None = Field(None, max_length=100)
    currency: str = Field(default="USD", max_length=10)
    status: str = Field(default="Active", max_length=50)


class BankAccountCreate(BankAccountBase):
    organization_id: uuid.UUID


class BankAccountResponse(BankAccountBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Dashboard Summary Schema ---
class FinanceDashboardSummary(BaseModel):
    total_revenue: float
    total_expenses: float
    cash_flow: float
    net_profit: float
    outstanding_invoices_amount: float
    outstanding_bills_amount: float
    total_bank_balance: float
    budget_usage_percentage: float
