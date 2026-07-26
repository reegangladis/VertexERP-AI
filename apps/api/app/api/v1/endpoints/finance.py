import uuid
import io
import csv
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from datetime import date

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.services.finance_service import FinanceService
from app.schemas.finance import (
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    FiscalPeriodCreate,
    FiscalPeriodResponse,
    JournalEntryCreate,
    JournalEntryResponse,
    CustomerInvoiceCreate,
    CustomerInvoiceResponse,
    SupplierBillCreate,
    SupplierBillResponse,
    PaymentCreate,
    PaymentResponse,
    BankAccountCreate,
    BankAccountResponse,
    BankTransactionCreate,
    BankTransactionResponse,
    ReconciliationCreate,
    ReconciliationResponse,
    ExpenseCategoryCreate,
    ExpenseCategoryResponse,
    ExpenseClaimCreate,
    ExpenseClaimResponse,
    BudgetCreate,
    BudgetResponse,
    TaxProfileCreate,
    TaxProfileResponse,
    AssetCategoryCreate,
    AssetCategoryResponse,
    FixedAssetCreate,
    FixedAssetResponse,
    TrialBalanceReportResponse,
    BalanceSheetResponse,
    ProfitLossResponse,
    CashFlowResponse,
    AgingReportResponse,
    FinanceSearchResult,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()

async def get_finance_service(db=Depends(get_db_session)) -> FinanceService:
    return FinanceService(db)


# --- 1. CHART OF ACCOUNTS ---
@router.post("/accounts", response_model=APIResponse[AccountResponse])
async def create_account(
    data: AccountCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_account(current_user.organization_id, data)
    return standard_json_response(data=res, message="Account created successfully.")

@router.get("/accounts", response_model=APIResponse[List[AccountResponse]])
async def list_accounts(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    accounts = await service.get_accounts(current_user.organization_id)
    return standard_json_response(data=accounts)

@router.put("/accounts/{account_id}", response_model=APIResponse[AccountResponse])
async def update_account(
    account_id: uuid.UUID,
    data: AccountUpdate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.update_account(account_id, data)
    return standard_json_response(data=res, message="Account updated successfully.")


# --- 2. FISCAL PERIODS ---
@router.post("/fiscal-periods", response_model=APIResponse[FiscalPeriodResponse])
async def create_fiscal_period(
    data: FiscalPeriodCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_fiscal_period(current_user.organization_id, data)
    return standard_json_response(data=res, message="Fiscal period created successfully.")

@router.get("/fiscal-periods", response_model=APIResponse[List[FiscalPeriodResponse]])
async def list_fiscal_periods(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    periods = await service.get_fiscal_periods(current_user.organization_id)
    return standard_json_response(data=periods)

@router.post("/fiscal-periods/{period_id}/close", response_model=APIResponse[FiscalPeriodResponse])
async def close_fiscal_period(
    period_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.close_fiscal_period(period_id)
    return standard_json_response(data=res, message="Fiscal period closed.")


# --- 3. JOURNAL ENTRIES ---
@router.post("/journal-entries", response_model=APIResponse[JournalEntryResponse])
async def create_journal_entry(
    data: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_journal_entry(current_user.organization_id, data)
    return standard_json_response(data=res, message="Journal entry draft created.")

@router.get("/journal-entries", response_model=APIResponse[List[JournalEntryResponse]])
async def list_journal_entries(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    entries = await service.get_journal_entries(current_user.organization_id)
    return standard_json_response(data=entries)

@router.post("/journal-entries/{entry_id}/post", response_model=APIResponse[JournalEntryResponse])
async def post_journal_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.post_journal_entry(entry_id, current_user.id)
    return standard_json_response(data=res, message="Journal entry posted to General Ledger.")

@router.post("/journal-entries/{entry_id}/reverse", response_model=APIResponse[JournalEntryResponse])
async def reverse_journal_entry(
    entry_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.reverse_journal_entry(entry_id, current_user.id)
    return standard_json_response(data=res, message="Journal entry reversed successfully.")


# --- 4. INVOICES (AR) ---
@router.post("/invoices", response_model=APIResponse[CustomerInvoiceResponse])
async def create_invoice(
    data: CustomerInvoiceCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_invoice(current_user.organization_id, data)
    return standard_json_response(data=res, message="Customer invoice issued.")

@router.get("/invoices", response_model=APIResponse[List[CustomerInvoiceResponse]])
async def list_invoices(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    invoices = await service.get_invoices(current_user.organization_id)
    return standard_json_response(data=invoices)


# --- 5. BILLS (AP) ---
@router.post("/bills", response_model=APIResponse[SupplierBillResponse])
async def create_bill(
    data: SupplierBillCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_bill(current_user.organization_id, data)
    return standard_json_response(data=res, message="Supplier bill recorded.")

@router.get("/bills", response_model=APIResponse[List[SupplierBillResponse]])
async def list_bills(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    bills = await service.get_bills(current_user.organization_id)
    return standard_json_response(data=bills)


# --- 6. PAYMENTS ---
@router.post("/payments", response_model=APIResponse[PaymentResponse])
async def create_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_payment(current_user.organization_id, data)
    return standard_json_response(data=res, message="Payment recorded.")

@router.get("/payments", response_model=APIResponse[List[PaymentResponse]])
async def list_payments(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    payments = await service.get_payments(current_user.organization_id)
    return standard_json_response(data=payments)


# --- 7. BANKING ---
@router.post("/bank-accounts", response_model=APIResponse[BankAccountResponse])
async def create_bank_account(
    data: BankAccountCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_bank_account(current_user.organization_id, data)
    return standard_json_response(data=res, message="Bank account added.")

@router.get("/bank-accounts", response_model=APIResponse[List[BankAccountResponse]])
async def list_bank_accounts(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    accounts = await service.get_bank_accounts(current_user.organization_id)
    return standard_json_response(data=accounts)

@router.post("/bank-transactions", response_model=APIResponse[BankTransactionResponse])
async def create_bank_transaction(
    data: BankTransactionCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.create_bank_transaction(data)
    return standard_json_response(data=res, message="Bank transaction recorded.")

@router.post("/reconciliations", response_model=APIResponse[ReconciliationResponse])
async def reconcile_bank_account(
    data: ReconciliationCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.reconcile_bank_account(data)
    return standard_json_response(data=res, message="Bank reconciliation processed.")


# --- 8. EXPENSES ---
@router.post("/expense-categories", response_model=APIResponse[ExpenseCategoryResponse])
async def create_expense_category(
    data: ExpenseCategoryCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_expense_category(current_user.organization_id, data)
    return standard_json_response(data=res, message="Expense category added.")

@router.get("/expense-categories", response_model=APIResponse[List[ExpenseCategoryResponse]])
async def list_expense_categories(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    categories = await service.get_expense_categories(current_user.organization_id)
    return standard_json_response(data=categories)

@router.post("/expense-claims", response_model=APIResponse[ExpenseClaimResponse])
async def create_expense_claim(
    data: ExpenseClaimCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_expense_claim(current_user.organization_id, data)
    return standard_json_response(data=res, message="Expense claim submitted.")

@router.get("/expense-claims", response_model=APIResponse[List[ExpenseClaimResponse]])
async def list_expense_claims(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    claims = await service.get_expense_claims(current_user.organization_id)
    return standard_json_response(data=claims)

@router.post("/expense-claims/{claim_id}/approve", response_model=APIResponse[ExpenseClaimResponse])
async def approve_expense_claim(
    claim_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.approve_expense_claim(claim_id, current_user.id)
    return standard_json_response(data=res, message="Expense claim approved.")

@router.post("/expense-claims/{claim_id}/reimburse", response_model=APIResponse[ExpenseClaimResponse])
async def reimburse_expense_claim(
    claim_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.reimburse_expense_claim(claim_id)
    return standard_json_response(data=res, message="Expense claim reimbursed and posted to GL.")


# --- 9. BUDGETS ---
@router.post("/budgets", response_model=APIResponse[BudgetResponse])
async def create_budget(
    data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_budget(current_user.organization_id, data)
    return standard_json_response(data=res, message="Budget created.")

@router.get("/budgets", response_model=APIResponse[List[BudgetResponse]])
async def list_budgets(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    budgets = await service.get_budgets(current_user.organization_id)
    return standard_json_response(data=budgets)


# --- 10. TAXES ---
@router.post("/tax-profiles", response_model=APIResponse[TaxProfileResponse])
async def create_tax_profile(
    data: TaxProfileCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_tax_profile(current_user.organization_id, data)
    return standard_json_response(data=res, message="Tax profile created.")

@router.get("/tax-profiles", response_model=APIResponse[List[TaxProfileResponse]])
async def list_tax_profiles(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    profiles = await service.get_tax_profiles(current_user.organization_id)
    return standard_json_response(data=profiles)


# --- 11. FIXED ASSETS ---
@router.post("/asset-categories", response_model=APIResponse[AssetCategoryResponse])
async def create_asset_category(
    data: AssetCategoryCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_asset_category(current_user.organization_id, data)
    return standard_json_response(data=res, message="Asset category created.")

@router.get("/asset-categories", response_model=APIResponse[List[AssetCategoryResponse]])
async def list_asset_categories(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    categories = await service.get_asset_categories(current_user.organization_id)
    return standard_json_response(data=categories)

@router.post("/fixed-assets", response_model=APIResponse[FixedAssetResponse])
async def create_fixed_asset(
    data: FixedAssetCreate,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.create_fixed_asset(current_user.organization_id, data)
    return standard_json_response(data=res, message="Fixed asset registered.")

@router.get("/fixed-assets", response_model=APIResponse[List[FixedAssetResponse]])
async def list_fixed_assets(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    assets = await service.get_fixed_assets(current_user.organization_id)
    return standard_json_response(data=assets)

@router.post("/fixed-assets/{asset_id}/dispose", response_model=APIResponse[FixedAssetResponse])
async def dispose_fixed_asset(
    asset_id: uuid.UUID,
    disposal_amount: float = Query(0.0),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    res = await service.dispose_fixed_asset(asset_id, disposal_amount)
    return standard_json_response(data=res, message="Fixed asset disposed.")


# --- 12. FINANCIAL REPORTS ---
@router.get("/reports/trial-balance", response_model=APIResponse[TrialBalanceReportResponse])
async def get_trial_balance(
    as_of: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.get_trial_balance(current_user.organization_id, as_of)
    return standard_json_response(data=res)

@router.get("/reports/balance-sheet", response_model=APIResponse[BalanceSheetResponse])
async def get_balance_sheet(
    as_of: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.get_balance_sheet(current_user.organization_id, as_of)
    return standard_json_response(data=res)

@router.get("/reports/profit-loss", response_model=APIResponse[ProfitLossResponse])
async def get_profit_loss(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.get_profit_loss(current_user.organization_id, start_date, end_date)
    return standard_json_response(data=res)

@router.get("/reports/cash-flow", response_model=APIResponse[CashFlowResponse])
async def get_cash_flow(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.get_cash_flow(current_user.organization_id, start_date, end_date)
    return standard_json_response(data=res)

@router.get("/reports/aging", response_model=APIResponse[AgingReportResponse])
async def get_aging_report(
    report_type: str = Query("RECEIVABLE", pattern="^(RECEIVABLE|PAYABLE)$"),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    res = await service.get_aging_report(current_user.organization_id, report_type)
    return standard_json_response(data=res)


# --- 13. SEARCH & CSV IMPORT/EXPORT ---
@router.get("/search", response_model=APIResponse[List[FinanceSearchResult]])
async def search_finance(
    q: str = Query(..., min_length=1),
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    results = await service.search_finance(current_user.organization_id, q)
    return standard_json_response(data=results)

@router.get("/export/accounts/csv")
async def export_accounts_csv(
    current_user: User = Depends(get_current_user),
    service: FinanceService = Depends(get_finance_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    accounts = await service.get_accounts(current_user.organization_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Account Code", "Account Name", "Account Type", "Subtype", "Currency", "Balance", "Opening Balance"])

    for a in accounts:
        writer.writerow([a.account_code, a.account_name, a.account_type, a.account_subtype or "", a.currency, a.balance, a.opening_balance])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=chart_of_accounts.csv"},
    )
