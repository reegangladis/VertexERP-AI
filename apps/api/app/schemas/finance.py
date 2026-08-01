import uuid
from datetime import date, datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class FinanceBaseModel(BaseModel):
    class Config:
        from_attributes = True

# --- 1. CHART OF ACCOUNTS SCHEMAS ---
class AccountCreate(FinanceBaseModel):
    account_code: str
    account_name: str
    account_type: str  # Assets, Liabilities, Equity, Income, Expenses
    account_subtype: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    currency: str = "USD"
    opening_balance: float = 0.0

class AccountUpdate(FinanceBaseModel):
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    account_subtype: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None
    opening_balance: Optional[float] = None

class AccountResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    account_code: str
    account_name: str
    account_type: str
    account_subtype: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    currency: str
    balance: float
    opening_balance: float
    is_active: bool
    is_system: bool
    ai_risk_score: Optional[float] = None
    ai_category_tag: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# --- 2. FISCAL PERIOD SCHEMAS ---
class FiscalPeriodCreate(FinanceBaseModel):
    period_name: str
    fiscal_year: int
    start_date: date
    end_date: date

class FiscalPeriodResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    period_name: str
    fiscal_year: int
    start_date: date
    end_date: date
    is_closed: bool
    closed_at: Optional[datetime] = None


# --- 3. JOURNAL ENTRY & LEDGER SCHEMAS ---
class JournalEntryLineCreate(FinanceBaseModel):
    account_id: uuid.UUID
    debit: float = 0.0
    credit: float = 0.0
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None

class JournalEntryLineResponse(FinanceBaseModel):
    id: uuid.UUID
    journal_entry_id: uuid.UUID
    account_id: uuid.UUID
    debit: float
    credit: float
    description: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None

class JournalEntryCreate(FinanceBaseModel):
    entry_number: Optional[str] = None
    entry_date: date
    reference: Optional[str] = None
    narration: Optional[str] = None
    source_type: str = "MANUAL"
    lines: List[JournalEntryLineCreate]

class JournalEntryResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    entry_number: str
    entry_date: date
    reference: Optional[str] = None
    narration: Optional[str] = None
    status: str
    source_type: str
    posted_by: Optional[uuid.UUID] = None
    posted_at: Optional[datetime] = None
    ai_anomaly_flag: bool = False
    ai_fraud_score: Optional[float] = None
    lines: List[JournalEntryLineResponse] = []
    created_at: datetime

class LedgerResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    account_id: uuid.UUID
    period_id: Optional[uuid.UUID] = None
    journal_entry_id: uuid.UUID
    transaction_date: date
    debit: float
    credit: float
    running_balance: float


# --- 4. ACCOUNTS RECEIVABLE (INVOICES & CREDIT NOTES) ---
class InvoiceItemCreate(FinanceBaseModel):
    product_id: Optional[uuid.UUID] = None
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    tax_rate_id: Optional[uuid.UUID] = None

class InvoiceItemResponse(FinanceBaseModel):
    id: uuid.UUID
    invoice_id: uuid.UUID
    product_id: Optional[uuid.UUID] = None
    description: str
    quantity: float
    unit_price: float
    tax_rate_id: Optional[uuid.UUID] = None
    tax_amount: float
    line_total: float

class CustomerInvoiceCreate(FinanceBaseModel):
    customer_id: uuid.UUID
    invoice_number: Optional[str] = None
    issue_date: date
    due_date: date
    notes: Optional[str] = None
    items: List[InvoiceItemCreate]

class CustomerInvoiceResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    customer_id: uuid.UUID
    invoice_number: str
    issue_date: date
    due_date: date
    subtotal: float
    tax_total: float
    total_amount: float
    paid_amount: float
    status: str
    notes: Optional[str] = None
    ai_default_risk: Optional[float] = None
    items: List[InvoiceItemResponse] = []
    created_at: datetime

class CreditNoteCreate(FinanceBaseModel):
    customer_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    amount: float
    reason: Optional[str] = None

class CreditNoteResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    credit_note_number: str
    customer_id: uuid.UUID
    invoice_id: Optional[uuid.UUID] = None
    amount: float
    reason: Optional[str] = None
    status: str
    created_at: datetime


# --- 5. ACCOUNTS PAYABLE (BILLS & DEBIT NOTES) ---
class BillItemCreate(FinanceBaseModel):
    product_id: Optional[uuid.UUID] = None
    description: str
    quantity: float = 1.0
    unit_price: float = 0.0
    tax_rate_id: Optional[uuid.UUID] = None

class BillItemResponse(FinanceBaseModel):
    id: uuid.UUID
    bill_id: uuid.UUID
    product_id: Optional[uuid.UUID] = None
    description: str
    quantity: float
    unit_price: float
    tax_rate_id: Optional[uuid.UUID] = None
    tax_amount: float
    line_total: float

class SupplierBillCreate(FinanceBaseModel):
    supplier_id: uuid.UUID
    bill_number: Optional[str] = None
    bill_date: date
    due_date: date
    notes: Optional[str] = None
    items: List[BillItemCreate]

class SupplierBillResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    supplier_id: uuid.UUID
    bill_number: str
    bill_date: date
    due_date: date
    subtotal: float
    tax_total: float
    total_amount: float
    paid_amount: float
    status: str
    notes: Optional[str] = None
    items: List[BillItemResponse] = []
    created_at: datetime

class DebitNoteCreate(FinanceBaseModel):
    supplier_id: uuid.UUID
    bill_id: Optional[uuid.UUID] = None
    amount: float
    reason: Optional[str] = None

class DebitNoteResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    debit_note_number: str
    supplier_id: uuid.UUID
    bill_id: Optional[uuid.UUID] = None
    amount: float
    reason: Optional[str] = None
    status: str
    created_at: datetime


# --- 6. PAYMENTS ---
class PaymentCreate(FinanceBaseModel):
    payment_type: str  # RECEIPT (AR), DISBURSEMENT (AP)
    customer_id: Optional[uuid.UUID] = None
    supplier_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None
    bill_id: Optional[uuid.UUID] = None
    bank_account_id: Optional[uuid.UUID] = None
    payment_date: date
    amount: float
    payment_method: str = "BANK_TRANSFER"
    reference: Optional[str] = None

class PaymentResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    payment_number: str
    payment_type: str
    customer_id: Optional[uuid.UUID] = None
    supplier_id: Optional[uuid.UUID] = None
    invoice_id: Optional[uuid.UUID] = None
    bill_id: Optional[uuid.UUID] = None
    bank_account_id: Optional[uuid.UUID] = None
    payment_date: date
    amount: float
    payment_method: str
    reference: Optional[str] = None
    status: str
    created_at: datetime


# --- 7. BANKING ---
class BankAccountCreate(FinanceBaseModel):
    account_name: str
    bank_name: str
    account_number: str
    swift_code: Optional[str] = None
    currency: str = "USD"
    current_balance: float = 0.0
    gl_account_id: Optional[uuid.UUID] = None

class BankAccountResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    account_name: str
    bank_name: str
    account_number: str
    swift_code: Optional[str] = None
    currency: str
    current_balance: float
    gl_account_id: Optional[uuid.UUID] = None

class BankTransactionCreate(FinanceBaseModel):
    bank_account_id: uuid.UUID
    transaction_date: date
    description: str
    amount: float
    transaction_type: str  # DEPOSIT, WITHDRAWAL, TRANSFER
    reference: Optional[str] = None

class BankTransactionResponse(FinanceBaseModel):
    id: uuid.UUID
    bank_account_id: uuid.UUID
    transaction_date: date
    description: str
    amount: float
    transaction_type: str
    reference: Optional[str] = None
    is_reconciled: bool
    reconciliation_id: Optional[uuid.UUID] = None

class ReconciliationCreate(FinanceBaseModel):
    bank_account_id: uuid.UUID
    statement_date: date
    statement_balance: float

class ReconciliationResponse(FinanceBaseModel):
    id: uuid.UUID
    bank_account_id: uuid.UUID
    statement_date: date
    statement_balance: float
    gl_balance: float
    difference: float
    status: str


# --- 8. EXPENSE MANAGEMENT ---
class ExpenseCategoryCreate(FinanceBaseModel):
    name: str
    code: str
    gl_account_id: Optional[uuid.UUID] = None

class ExpenseCategoryResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    gl_account_id: Optional[uuid.UUID] = None
    is_active: bool

class ExpenseClaimCreate(FinanceBaseModel):
    employee_id: uuid.UUID
    category_id: uuid.UUID
    claim_date: date
    amount: float
    description: str
    receipt_url: Optional[str] = None

class ExpenseClaimResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    claim_number: str
    employee_id: uuid.UUID
    category_id: uuid.UUID
    claim_date: date
    amount: float
    description: str
    receipt_url: Optional[str] = None
    status: str
    approved_by: Optional[uuid.UUID] = None
    reimbursement_date: Optional[date] = None
    ai_fraud_flag: bool = False
    created_at: datetime


# --- 9. BUDGET MANAGEMENT ---
class BudgetItemCreate(FinanceBaseModel):
    account_id: uuid.UUID
    budgeted_amount: float

class BudgetItemResponse(FinanceBaseModel):
    id: uuid.UUID
    budget_id: uuid.UUID
    account_id: uuid.UUID
    budgeted_amount: float
    actual_amount: float

class BudgetCreate(FinanceBaseModel):
    name: str
    fiscal_year: int
    department_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    items: List[BudgetItemCreate]

class BudgetResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    fiscal_year: int
    department_id: Optional[uuid.UUID] = None
    project_id: Optional[uuid.UUID] = None
    total_budgeted: float
    status: str
    items: List[BudgetItemResponse] = []
    created_at: datetime


# --- 10. TAX MANAGEMENT ---
class TaxRateCreate(FinanceBaseModel):
    name: str
    code: str
    rate_percentage: float
    type: str = "VAT"
    gl_account_id: Optional[uuid.UUID] = None

class TaxRateResponse(FinanceBaseModel):
    id: uuid.UUID
    tax_profile_id: uuid.UUID
    name: str
    code: str
    rate_percentage: float
    type: str
    gl_account_id: Optional[uuid.UUID] = None

class TaxProfileCreate(FinanceBaseModel):
    name: str
    tax_number: Optional[str] = None
    country: str = "US"
    state: Optional[str] = None
    is_default: bool = False
    rates: List[TaxRateCreate] = []

class TaxProfileResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    tax_number: Optional[str] = None
    country: str
    state: Optional[str] = None
    is_default: bool
    rates: List[TaxRateResponse] = []


# --- 11. FIXED ASSETS ---
class AssetCategoryCreate(FinanceBaseModel):
    name: str
    depreciation_method: str = "STRAIGHT_LINE"
    useful_life_years: int = 5
    asset_gl_account_id: Optional[uuid.UUID] = None
    depreciation_gl_account_id: Optional[uuid.UUID] = None
    accumulated_depr_gl_account_id: Optional[uuid.UUID] = None

class AssetCategoryResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    depreciation_method: str
    useful_life_years: int
    asset_gl_account_id: Optional[uuid.UUID] = None
    depreciation_gl_account_id: Optional[uuid.UUID] = None
    accumulated_depr_gl_account_id: Optional[uuid.UUID] = None

class FixedAssetCreate(FinanceBaseModel):
    asset_name: str
    category_id: uuid.UUID
    purchase_date: date
    purchase_cost: float
    salvage_value: float = 0.0

class FixedAssetResponse(FinanceBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    asset_number: str
    asset_name: str
    category_id: uuid.UUID
    purchase_date: date
    purchase_cost: float
    salvage_value: float
    current_value: float
    accumulated_depreciation: float
    status: str
    disposal_date: Optional[date] = None
    disposal_amount: Optional[float] = None
    created_at: datetime


# --- 12. FINANCIAL REPORTS ---
class TrialBalanceItem(FinanceBaseModel):
    account_id: uuid.UUID
    account_code: str
    account_name: str
    account_type: str
    debit: float
    credit: float
    balance: float

class TrialBalanceReportResponse(FinanceBaseModel):
    as_of_date: date
    total_debit: float
    total_credit: float
    items: List[TrialBalanceItem]

class BalanceSheetResponse(FinanceBaseModel):
    as_of_date: date
    total_assets: float
    total_liabilities: float
    total_equity: float
    is_balanced: bool
    asset_accounts: List[TrialBalanceItem]
    liability_accounts: List[TrialBalanceItem]
    equity_accounts: List[TrialBalanceItem]

class ProfitLossResponse(FinanceBaseModel):
    start_date: date
    end_date: date
    total_revenue: float
    total_expenses: float
    net_profit: float
    revenue_items: List[TrialBalanceItem]
    expense_items: List[TrialBalanceItem]

class CashFlowResponse(FinanceBaseModel):
    start_date: date
    end_date: date
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float
    net_cash_flow: float
    ending_cash_balance: float

class AgingBucketItem(FinanceBaseModel):
    entity_id: uuid.UUID
    entity_name: str
    current: float  # 0-30 days
    days_31_60: float
    days_61_90: float
    days_over_90: float
    total_outstanding: float

class AgingReportResponse(FinanceBaseModel):
    report_type: str  # RECEIVABLE or PAYABLE
    as_of_date: date
    total_outstanding: float
    buckets: List[AgingBucketItem]

class BudgetVsActualItem(FinanceBaseModel):
    account_id: uuid.UUID
    account_name: str
    budgeted: float
    actual: float
    variance: float
    variance_percentage: float

class BudgetReportResponse(FinanceBaseModel):
    fiscal_year: int
    total_budgeted: float
    total_actual: float
    variance: float
    items: List[BudgetVsActualItem]


# --- 13. SEARCH & IMPORT/EXPORT & ADDITIONAL REPORTS ---
class FinanceSearchResult(FinanceBaseModel):
    entity_type: str
    id: uuid.UUID
    title: str
    subtitle: str
    status: Optional[str] = None
    amount: Optional[float] = None
    created_at: datetime


class GeneralLedgerEntryItem(FinanceBaseModel):
    id: uuid.UUID
    journal_entry_id: uuid.UUID
    entry_number: str
    transaction_date: date
    narration: Optional[str] = None
    debit: float
    credit: float
    running_balance: float


class GeneralLedgerReportResponse(FinanceBaseModel):
    account_id: uuid.UUID
    account_code: str
    account_name: str
    opening_balance: float
    closing_balance: float
    entries: List[GeneralLedgerEntryItem]


class TaxReportItem(FinanceBaseModel):
    tax_rate_id: Optional[uuid.UUID] = None
    tax_name: str
    tax_code: str
    rate_percentage: float
    taxable_amount: float
    tax_amount: float


class TaxReportResponse(FinanceBaseModel):
    as_of_date: date
    total_tax_collected: float  # Output tax (Sales/AR)
    total_tax_paid: float       # Input tax (Purchases/AP)
    net_tax_payable: float
    items: List[TaxReportItem]


class ExpenseReportItem(FinanceBaseModel):
    category_id: uuid.UUID
    category_name: str
    category_code: str
    total_amount: float
    claim_count: int


class ExpenseReportResponse(FinanceBaseModel):
    start_date: date
    end_date: date
    total_expenses: float
    categories: List[ExpenseReportItem]


class RevenueReportItem(FinanceBaseModel):
    customer_id: uuid.UUID
    total_revenue: float
    invoice_count: int


class RevenueReportResponse(FinanceBaseModel):
    start_date: date
    end_date: date
    total_revenue: float
    items: List[RevenueReportItem]


class FinanceDashboardSummary(FinanceBaseModel):
    total_revenue: float
    total_expenses: float
    net_profit: float
    total_receivables: float
    total_payables: float
    total_cash_balance: float
    budget_utilization_pct: float
    recent_transactions_count: int
    pending_expense_claims: int

