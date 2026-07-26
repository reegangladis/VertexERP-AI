import uuid
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.finance import (
    Account,
    FiscalPeriod,
    JournalEntry,
    JournalEntryLine,
    Ledger,
    CustomerInvoice,
    InvoiceItem,
    SupplierBill,
    BillItem,
    Payment,
    CreditNote,
    DebitNote,
    BankAccount,
    BankTransaction,
    Reconciliation,
    ExpenseCategory,
    ExpenseClaim,
    Budget,
    BudgetItem,
    TaxProfile,
    TaxRate,
    AssetCategory,
    FixedAsset,
)
from app.repositories.finance_repository import (
    AccountRepository,
    FiscalPeriodRepository,
    JournalEntryRepository,
    LedgerRepository,
    CustomerInvoiceRepository,
    SupplierBillRepository,
    PaymentRepository,
    BankAccountRepository,
    BankTransactionRepository,
    ExpenseCategoryRepository,
    ExpenseClaimRepository,
    BudgetRepository,
    TaxProfileRepository,
    FixedAssetRepository,
    AssetCategoryRepository,
)
from app.schemas.finance import (
    AccountCreate,
    AccountUpdate,
    FiscalPeriodCreate,
    JournalEntryCreate,
    CustomerInvoiceCreate,
    SupplierBillCreate,
    PaymentCreate,
    BankAccountCreate,
    BankTransactionCreate,
    ReconciliationCreate,
    ExpenseCategoryCreate,
    ExpenseClaimCreate,
    BudgetCreate,
    TaxProfileCreate,
    AssetCategoryCreate,
    FixedAssetCreate,
    TrialBalanceReportResponse,
    TrialBalanceItem,
    BalanceSheetResponse,
    ProfitLossResponse,
    CashFlowResponse,
    AgingReportResponse,
    AgingBucketItem,
    BudgetReportResponse,
    BudgetVsActualItem,
    FinanceSearchResult,
)


class FinanceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.account_repo = AccountRepository(db)
        self.period_repo = FiscalPeriodRepository(db)
        self.journal_repo = JournalEntryRepository(db)
        self.ledger_repo = LedgerRepository(db)
        self.invoice_repo = CustomerInvoiceRepository(db)
        self.bill_repo = SupplierBillRepository(db)
        self.payment_repo = PaymentRepository(db)
        self.bank_repo = BankAccountRepository(db)
        self.bank_tx_repo = BankTransactionRepository(db)
        self.expense_cat_repo = ExpenseCategoryRepository(db)
        self.expense_claim_repo = ExpenseClaimRepository(db)
        self.budget_repo = BudgetRepository(db)
        self.tax_repo = TaxProfileRepository(db)
        self.asset_repo = FixedAssetRepository(db)
        self.asset_cat_repo = AssetCategoryRepository(db)

    # --- 1. CHART OF ACCOUNTS ---
    async def create_account(self, org_id: uuid.UUID, data: AccountCreate) -> Account:
        existing = await self.account_repo.get_by_code(org_id, data.account_code)
        if existing:
            raise HTTPException(status_code=400, detail=f"Account code '{data.account_code}' already exists.")

        account = Account(
            organization_id=org_id,
            account_code=data.account_code,
            account_name=data.account_name,
            account_type=data.account_type,
            account_subtype=data.account_subtype,
            parent_id=data.parent_id,
            currency=data.currency,
            opening_balance=data.opening_balance,
            balance=data.opening_balance,
        )
        return await self.account_repo.create(account)

    async def get_accounts(self, org_id: uuid.UUID) -> List[Account]:
        accounts = await self.account_repo.get_by_org(org_id)
        if not accounts:
            # Seed standard default Chart of Accounts if empty
            return await self.seed_default_accounts(org_id)
        return accounts

    async def seed_default_accounts(self, org_id: uuid.UUID) -> List[Account]:
        defaults = [
            ("1010", "Cash on Hand", "Assets", "Current Assets", 0.0),
            ("1020", "Operating Bank Account", "Assets", "Current Assets", 50000.0),
            ("1100", "Accounts Receivable", "Assets", "Current Assets", 0.0),
            ("1500", "Fixed Assets - Equipment", "Assets", "Fixed Assets", 25000.0),
            ("2000", "Accounts Payable", "Liabilities", "Current Liabilities", 0.0),
            ("2100", "Sales Tax Payable", "Liabilities", "Current Liabilities", 0.0),
            ("3000", "Owner's Equity", "Equity", "Equity", 75000.0),
            ("4000", "Sales Revenue", "Income", "Operating Revenue", 0.0),
            ("4100", "Services Revenue", "Income", "Operating Revenue", 0.0),
            ("5000", "Cost of Goods Sold", "Expenses", "Direct Expenses", 0.0),
            ("5100", "Office Expense", "Expenses", "Operating Expenses", 0.0),
            ("5200", "Salaries Expense", "Expenses", "Operating Expenses", 0.0),
        ]
        created = []
        for code, name, acct_type, subtype, opening in defaults:
            acct = Account(
                organization_id=org_id,
                account_code=code,
                account_name=name,
                account_type=acct_type,
                account_subtype=subtype,
                opening_balance=opening,
                balance=opening,
                is_system=True,
            )
            created.append(await self.account_repo.create(acct))
        return created

    async def update_account(self, account_id: uuid.UUID, data: AccountUpdate) -> Account:
        account = await self.account_repo.get_by_id(account_id)
        if not account or account.is_deleted:
            raise HTTPException(status_code=404, detail="Account not found.")
        update_data = data.model_dump(exclude_unset=True)
        return await self.account_repo.update(account, update_data)

    # --- 2. FISCAL PERIODS ---
    async def create_fiscal_period(self, org_id: uuid.UUID, data: FiscalPeriodCreate) -> FiscalPeriod:
        period = FiscalPeriod(
            organization_id=org_id,
            period_name=data.period_name,
            fiscal_year=data.fiscal_year,
            start_date=data.start_date,
            end_date=data.end_date,
        )
        return await self.period_repo.create(period)

    async def get_fiscal_periods(self, org_id: uuid.UUID) -> List[FiscalPeriod]:
        return await self.period_repo.get_by_org(org_id)

    async def close_fiscal_period(self, period_id: uuid.UUID) -> FiscalPeriod:
        period = await self.period_repo.get_by_id(period_id)
        if not period or period.is_deleted:
            raise HTTPException(status_code=404, detail="Fiscal period not found.")
        period.is_closed = True
        period.closed_at = datetime.utcnow()
        return await self.period_repo.update(period, {"is_closed": True, "closed_at": datetime.utcnow()})

    # --- 3. JOURNAL ENTRIES & LEDGER POSTING ---
    async def create_journal_entry(self, org_id: uuid.UUID, data: JournalEntryCreate) -> JournalEntry:
        # Validate Double Entry rule: sum(debit) == sum(credit)
        total_debit = round(sum(line.debit for line in data.lines), 2)
        total_credit = round(sum(line.credit for line in data.lines), 2)

        if total_debit != total_credit:
            raise HTTPException(
                status_code=400,
                detail=f"Double-entry accounting error: Total debits (${total_debit}) must equal total credits (${total_credit}).",
            )
        if total_debit <= 0:
            raise HTTPException(status_code=400, detail="Journal entry lines must have a non-zero debit/credit amount.")

        entry_num = data.entry_number or f"JE-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        journal_entry = JournalEntry(
            organization_id=org_id,
            entry_number=entry_num,
            entry_date=data.entry_date,
            reference=data.reference,
            narration=data.narration,
            status="DRAFT",
            source_type=data.source_type,
        )
        saved_entry = await self.journal_repo.create(journal_entry)

        lines = []
        for line in data.lines:
            entry_line = JournalEntryLine(
                journal_entry_id=saved_entry.id,
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                description=line.description,
                entity_type=line.entity_type,
                entity_id=line.entity_id,
            )
            self.db.add(entry_line)
        await self.db.commit()

        return await self.journal_repo.get_with_lines(saved_entry.id)

    async def post_journal_entry(self, entry_id: uuid.UUID, user_id: uuid.UUID) -> JournalEntry:
        entry = await self.journal_repo.get_with_lines(entry_id)
        if not entry or entry.is_deleted:
            raise HTTPException(status_code=404, detail="Journal entry not found.")
        if entry.status == "POSTED":
            raise HTTPException(status_code=400, detail="Journal entry is already posted.")

        # Post to Ledgers & update account balances
        for line in entry.lines:
            account = await self.account_repo.get_by_id(line.account_id)
            if not account:
                continue

            # Update running balance based on account type normal balances
            # Assets/Expenses increase with Debit, decrease with Credit
            # Liabilities/Equity/Income increase with Credit, decrease with Debit
            if account.account_type in ["Assets", "Expenses"]:
                account.balance = float(account.balance) + float(line.debit) - float(line.credit)
            else:
                account.balance = float(account.balance) + float(line.credit) - float(line.debit)

            ledger_entry = Ledger(
                organization_id=entry.organization_id,
                account_id=line.account_id,
                journal_entry_id=entry.id,
                transaction_date=entry.entry_date,
                debit=line.debit,
                credit=line.credit,
                running_balance=account.balance,
            )
            self.db.add(ledger_entry)

        entry.status = "POSTED"
        entry.posted_by = user_id
        entry.posted_at = datetime.utcnow()
        await self.db.commit()

        return entry

    async def reverse_journal_entry(self, entry_id: uuid.UUID, user_id: uuid.UUID) -> JournalEntry:
        original = await self.journal_repo.get_with_lines(entry_id)
        if not original or original.status != "POSTED":
            raise HTTPException(status_code=400, detail="Only posted journal entries can be reversed.")

        # Create reversal entry with debits and credits swapped
        reversal_lines = [
            JournalEntryLineCreate(
                account_id=line.account_id,
                debit=line.credit,
                credit=line.debit,
                description=f"Reversal of {original.entry_number}: {line.description or ''}",
            )
            for line in original.lines
        ]

        reversal_create = JournalEntryCreate(
            entry_number=f"REV-{original.entry_number}",
            entry_date=date.today(),
            reference=f"Reversal of {original.id}",
            narration=f"System reversal of journal entry {original.entry_number}",
            source_type=original.source_type,
            lines=reversal_lines,
        )
        reversal_entry = await self.create_journal_entry(original.organization_id, reversal_create)
        posted_reversal = await self.post_journal_entry(reversal_entry.id, user_id)

        original.status = "REVERSED"
        await self.db.commit()

        return posted_reversal

    async def get_journal_entries(self, org_id: uuid.UUID) -> List[JournalEntry]:
        return await self.journal_repo.get_by_org(org_id)

    # --- 4. ACCOUNTS RECEIVABLE (CUSTOMER INVOICES) ---
    async def create_invoice(self, org_id: uuid.UUID, data: CustomerInvoiceCreate) -> CustomerInvoice:
        inv_num = data.invoice_number or f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        subtotal = 0.0
        tax_total = 0.0

        for item in data.items:
            line_val = round(item.quantity * item.unit_price, 2)
            subtotal += line_val
            # Tax placeholder logic if rate assigned
            tax_total += 0.0

        total_amount = subtotal + tax_total

        invoice = CustomerInvoice(
            organization_id=org_id,
            customer_id=data.customer_id,
            invoice_number=inv_num,
            issue_date=data.issue_date,
            due_date=data.due_date,
            subtotal=subtotal,
            tax_total=tax_total,
            total_amount=total_amount,
            paid_amount=0.0,
            status="SENT",
            notes=data.notes,
        )
        saved_inv = await self.invoice_repo.create(invoice)

        for item in data.items:
            line_val = round(item.quantity * item.unit_price, 2)
            inv_item = InvoiceItem(
                invoice_id=saved_inv.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_id=item.tax_rate_id,
                tax_amount=0.0,
                line_total=line_val,
            )
            self.db.add(inv_item)

        # Auto-create posting GL Journal Entry (AR Debit, Revenue Credit)
        accounts = await self.get_accounts(org_id)
        ar_acct = next((a for a in accounts if a.account_code == "1100"), accounts[0])
        rev_acct = next((a for a in accounts if a.account_code in ["4000", "4100"]), accounts[-1])

        je_data = JournalEntryCreate(
            entry_number=f"JE-{inv_num}",
            entry_date=data.issue_date,
            reference=inv_num,
            narration=f"Automated Posting for Customer Invoice {inv_num}",
            source_type="INVOICE",
            lines=[
                JournalEntryLineCreate(account_id=ar_acct.id, debit=total_amount, credit=0.0, entity_type="CUSTOMER", entity_id=data.customer_id),
                JournalEntryLineCreate(account_id=rev_acct.id, debit=0.0, credit=total_amount),
            ],
        )
        je = await self.create_journal_entry(org_id, je_data)
        await self.post_journal_entry(je.id, None)

        await self.db.commit()
        return await self.invoice_repo.get_with_items(saved_inv.id)

    async def get_invoices(self, org_id: uuid.UUID) -> List[CustomerInvoice]:
        return await self.invoice_repo.get_by_org(org_id)

    # --- 5. ACCOUNTS PAYABLE (SUPPLIER BILLS) ---
    async def create_bill(self, org_id: uuid.UUID, data: SupplierBillCreate) -> SupplierBill:
        bill_num = data.bill_number or f"BILL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        subtotal = sum(round(item.quantity * item.unit_price, 2) for item in data.items)
        tax_total = 0.0
        total_amount = subtotal + tax_total

        bill = SupplierBill(
            organization_id=org_id,
            supplier_id=data.supplier_id,
            bill_number=bill_num,
            bill_date=data.bill_date,
            due_date=data.due_date,
            subtotal=subtotal,
            tax_total=tax_total,
            total_amount=total_amount,
            paid_amount=0.0,
            status="RECEIVED",
            notes=data.notes,
        )
        saved_bill = await self.bill_repo.create(bill)

        for item in data.items:
            line_val = round(item.quantity * item.unit_price, 2)
            bill_item = BillItem(
                bill_id=saved_bill.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_id=item.tax_rate_id,
                tax_amount=0.0,
                line_total=line_val,
            )
            self.db.add(bill_item)

        # Auto GL Posting (Expense Debit, AP Credit)
        accounts = await self.get_accounts(org_id)
        ap_acct = next((a for a in accounts if a.account_code == "2000"), accounts[0])
        exp_acct = next((a for a in accounts if a.account_code == "5100"), accounts[-1])

        je_data = JournalEntryCreate(
            entry_number=f"JE-{bill_num}",
            entry_date=data.bill_date,
            reference=bill_num,
            narration=f"Automated Posting for Supplier Bill {bill_num}",
            source_type="BILL",
            lines=[
                JournalEntryLineCreate(account_id=exp_acct.id, debit=total_amount, credit=0.0),
                JournalEntryLineCreate(account_id=ap_acct.id, debit=0.0, credit=total_amount, entity_type="SUPPLIER", entity_id=data.supplier_id),
            ],
        )
        je = await self.create_journal_entry(org_id, je_data)
        await self.post_journal_entry(je.id, None)

        await self.db.commit()
        return await self.bill_repo.get_with_items(saved_bill.id)

    async def get_bills(self, org_id: uuid.UUID) -> List[SupplierBill]:
        return await self.bill_repo.get_by_org(org_id)

    # --- 6. PAYMENTS ---
    async def create_payment(self, org_id: uuid.UUID, data: PaymentCreate) -> Payment:
        pay_num = f"PAY-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        payment = Payment(
            organization_id=org_id,
            payment_number=pay_num,
            payment_type=data.payment_type,
            customer_id=data.customer_id,
            supplier_id=data.supplier_id,
            invoice_id=data.invoice_id,
            bill_id=data.bill_id,
            bank_account_id=data.bank_account_id,
            payment_date=data.payment_date,
            amount=data.amount,
            payment_method=data.payment_method,
            reference=data.reference,
            status="COMPLETED",
        )
        saved_pay = await self.payment_repo.create(payment)

        # Update Invoice / Bill paid amount if applicable
        accounts = await self.get_accounts(org_id)
        cash_bank_acct = next((a for a in accounts if a.account_code == "1020"), accounts[0])

        if data.payment_type == "RECEIPT" and data.invoice_id:
            inv = await self.invoice_repo.get_by_id(data.invoice_id)
            if inv:
                inv.paid_amount = float(inv.paid_amount) + float(data.amount)
                if inv.paid_amount >= inv.total_amount:
                    inv.status = "PAID"
                else:
                    inv.status = "PARTIAL"

                # GL: Debit Cash/Bank, Credit AR
                ar_acct = next((a for a in accounts if a.account_code == "1100"), accounts[0])
                je_data = JournalEntryCreate(
                    entry_number=f"JE-{pay_num}",
                    entry_date=data.payment_date,
                    reference=pay_num,
                    narration=f"Payment received for Invoice {inv.invoice_number}",
                    source_type="PAYMENT",
                    lines=[
                        JournalEntryLineCreate(account_id=cash_bank_acct.id, debit=data.amount, credit=0.0),
                        JournalEntryLineCreate(account_id=ar_acct.id, debit=0.0, credit=data.amount, entity_type="CUSTOMER", entity_id=data.customer_id),
                    ],
                )
                je = await self.create_journal_entry(org_id, je_data)
                await self.post_journal_entry(je.id, None)

        elif data.payment_type == "DISBURSEMENT" and data.bill_id:
            bill = await self.bill_repo.get_by_id(data.bill_id)
            if bill:
                bill.paid_amount = float(bill.paid_amount) + float(data.amount)
                if bill.paid_amount >= bill.total_amount:
                    bill.status = "PAID"
                else:
                    bill.status = "PARTIAL"

                # GL: Debit AP, Credit Cash/Bank
                ap_acct = next((a for a in accounts if a.account_code == "2000"), accounts[0])
                je_data = JournalEntryCreate(
                    entry_number=f"JE-{pay_num}",
                    entry_date=data.payment_date,
                    reference=pay_num,
                    narration=f"Payment disbursed for Bill {bill.bill_number}",
                    source_type="PAYMENT",
                    lines=[
                        JournalEntryLineCreate(account_id=ap_acct.id, debit=data.amount, credit=0.0, entity_type="SUPPLIER", entity_id=data.supplier_id),
                        JournalEntryLineCreate(account_id=cash_bank_acct.id, debit=0.0, credit=data.amount),
                    ],
                )
                je = await self.create_journal_entry(org_id, je_data)
                await self.post_journal_entry(je.id, None)

        await self.db.commit()
        return saved_pay

    async def get_payments(self, org_id: uuid.UUID) -> List[Payment]:
        return await self.payment_repo.get_by_org(org_id)

    # --- 7. BANKING ---
    async def create_bank_account(self, org_id: uuid.UUID, data: BankAccountCreate) -> BankAccount:
        account = BankAccount(
            organization_id=org_id,
            account_name=data.account_name,
            bank_name=data.bank_name,
            account_number=data.account_number,
            swift_code=data.swift_code,
            currency=data.currency,
            current_balance=data.current_balance,
            gl_account_id=data.gl_account_id,
        )
        return await self.bank_repo.create(account)

    async def get_bank_accounts(self, org_id: uuid.UUID) -> List[BankAccount]:
        return await self.bank_repo.get_by_org(org_id)

    async def create_bank_transaction(self, data: BankTransactionCreate) -> BankTransaction:
        bank_acct = await self.bank_repo.get_by_id(data.bank_account_id)
        if not bank_acct:
            raise HTTPException(status_code=404, detail="Bank account not found.")

        if data.transaction_type in ["DEPOSIT"]:
            bank_acct.current_balance = float(bank_acct.current_balance) + float(data.amount)
        elif data.transaction_type in ["WITHDRAWAL", "TRANSFER"]:
            bank_acct.current_balance = float(bank_acct.current_balance) - float(data.amount)

        tx = BankTransaction(
            bank_account_id=data.bank_account_id,
            transaction_date=data.transaction_date,
            description=data.description,
            amount=data.amount,
            transaction_type=data.transaction_type,
            reference=data.reference,
        )
        self.db.add(tx)
        await self.db.commit()
        await self.db.refresh(tx)
        return tx

    async def reconcile_bank_account(self, data: ReconciliationCreate) -> Reconciliation:
        bank_acct = await self.bank_repo.get_by_id(data.bank_account_id)
        if not bank_acct:
            raise HTTPException(status_code=404, detail="Bank account not found.")

        gl_bal = float(bank_acct.current_balance)
        diff = round(float(data.statement_balance) - gl_bal, 2)

        recon = Reconciliation(
            bank_account_id=data.bank_account_id,
            statement_date=data.statement_date,
            statement_balance=data.statement_balance,
            gl_balance=gl_bal,
            difference=diff,
            status="COMPLETED" if diff == 0.0 else "DISCREPANCY",
        )
        self.db.add(recon)
        await self.db.commit()
        await self.db.refresh(recon)
        return recon

    # --- 8. EXPENSES ---
    async def create_expense_category(self, org_id: uuid.UUID, data: ExpenseCategoryCreate) -> ExpenseCategory:
        cat = ExpenseCategory(
            organization_id=org_id,
            name=data.name,
            code=data.code,
            gl_account_id=data.gl_account_id,
        )
        return await self.expense_cat_repo.create(cat)

    async def get_expense_categories(self, org_id: uuid.UUID) -> List[ExpenseCategory]:
        cats = await self.expense_cat_repo.get_by_org(org_id)
        if not cats:
            default_cat = ExpenseCategory(organization_id=org_id, name="Travel & Meals", code="EXP-TRV")
            cats.append(await self.expense_cat_repo.create(default_cat))
        return cats

    async def create_expense_claim(self, org_id: uuid.UUID, data: ExpenseClaimCreate) -> ExpenseClaim:
        claim_num = f"EXP-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        claim = ExpenseClaim(
            organization_id=org_id,
            claim_number=claim_num,
            employee_id=data.employee_id,
            category_id=data.category_id,
            claim_date=data.claim_date,
            amount=data.amount,
            description=data.description,
            receipt_url=data.receipt_url,
            status="SUBMITTED",
        )
        return await self.expense_claim_repo.create(claim)

    async def get_expense_claims(self, org_id: uuid.UUID) -> List[ExpenseClaim]:
        return await self.expense_claim_repo.get_by_org(org_id)

    async def approve_expense_claim(self, claim_id: uuid.UUID, user_id: uuid.UUID) -> ExpenseClaim:
        claim = await self.expense_claim_repo.get_by_id(claim_id)
        if not claim or claim.is_deleted:
            raise HTTPException(status_code=404, detail="Expense claim not found.")
        claim.status = "APPROVED"
        claim.approved_by = user_id
        await self.db.commit()
        return claim

    async def reimburse_expense_claim(self, claim_id: uuid.UUID) -> ExpenseClaim:
        claim = await self.expense_claim_repo.get_by_id(claim_id)
        if not claim or claim.status != "APPROVED":
            raise HTTPException(status_code=400, detail="Only approved expense claims can be reimbursed.")

        claim.status = "REIMBURSED"
        claim.reimbursement_date = date.today()

        # GL Posting (Expense Debit, Cash Credit)
        accounts = await self.get_accounts(claim.organization_id)
        exp_acct = next((a for a in accounts if a.account_code == "5100"), accounts[-1])
        cash_acct = next((a for a in accounts if a.account_code == "1020"), accounts[0])

        je_data = JournalEntryCreate(
            entry_number=f"JE-{claim.claim_number}",
            entry_date=date.today(),
            reference=claim.claim_number,
            narration=f"Expense reimbursement: {claim.description}",
            source_type="EXPENSE",
            lines=[
                JournalEntryLineCreate(account_id=exp_acct.id, debit=claim.amount, credit=0.0),
                JournalEntryLineCreate(account_id=cash_acct.id, debit=0.0, credit=claim.amount),
            ],
        )
        je = await self.create_journal_entry(claim.organization_id, je_data)
        await self.post_journal_entry(je.id, None)

        await self.db.commit()
        return claim

    # --- 9. BUDGET MANAGEMENT ---
    async def create_budget(self, org_id: uuid.UUID, data: BudgetCreate) -> Budget:
        tot = sum(item.budgeted_amount for item in data.items)
        budget = Budget(
            organization_id=org_id,
            name=data.name,
            fiscal_year=data.fiscal_year,
            department_id=data.department_id,
            project_id=data.project_id,
            total_budgeted=tot,
            status="APPROVED",
        )
        saved_budget = await self.budget_repo.create(budget)

        for item in data.items:
            b_item = BudgetItem(
                budget_id=saved_budget.id,
                account_id=item.account_id,
                budgeted_amount=item.budgeted_amount,
                actual_amount=0.0,
            )
            self.db.add(b_item)

        await self.db.commit()
        return await self.budget_repo.get_by_id(saved_budget.id)

    async def get_budgets(self, org_id: uuid.UUID) -> List[Budget]:
        return await self.budget_repo.get_by_org(org_id)

    # --- 10. TAX MANAGEMENT ---
    async def create_tax_profile(self, org_id: uuid.UUID, data: TaxProfileCreate) -> TaxProfile:
        profile = TaxProfile(
            organization_id=org_id,
            name=data.name,
            tax_number=data.tax_number,
            country=data.country,
            state=data.state,
            is_default=data.is_default,
        )
        saved = await self.tax_repo.create(profile)
        for r in data.rates:
            rate = TaxRate(
                tax_profile_id=saved.id,
                name=r.name,
                code=r.code,
                rate_percentage=r.rate_percentage,
                type=r.type,
                gl_account_id=r.gl_account_id,
            )
            self.db.add(rate)
        await self.db.commit()
        return saved

    async def get_tax_profiles(self, org_id: uuid.UUID) -> List[TaxProfile]:
        profiles = await self.tax_repo.get_by_org(org_id)
        if not profiles:
            def_profile = TaxProfile(organization_id=org_id, name="Standard US Tax Profile", country="US", is_default=True)
            saved = await self.tax_repo.create(def_profile)
            rate = TaxRate(tax_profile_id=saved.id, name="Standard VAT/GST", code="VAT-10", rate_percentage=10.0, type="VAT")
            self.db.add(rate)
            await self.db.commit()
            profiles = [saved]
        return profiles

    # --- 11. FIXED ASSETS ---
    async def create_asset_category(self, org_id: uuid.UUID, data: AssetCategoryCreate) -> AssetCategory:
        cat = AssetCategory(
            organization_id=org_id,
            name=data.name,
            depreciation_method=data.depreciation_method,
            useful_life_years=data.useful_life_years,
            asset_gl_account_id=data.asset_gl_account_id,
            depreciation_gl_account_id=data.depreciation_gl_account_id,
            accumulated_depr_gl_account_id=data.accumulated_depr_gl_account_id,
        )
        return await self.asset_cat_repo.create(cat)

    async def get_asset_categories(self, org_id: uuid.UUID) -> List[AssetCategory]:
        cats = await self.asset_cat_repo.get_by_org(org_id)
        if not cats:
            c = AssetCategory(organization_id=org_id, name="IT Hardware & Equipment", depreciation_method="STRAIGHT_LINE", useful_life_years=4)
            cats.append(await self.asset_cat_repo.create(c))
        return cats

    async def create_fixed_asset(self, org_id: uuid.UUID, data: FixedAssetCreate) -> FixedAsset:
        asset_num = f"AST-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        asset = FixedAsset(
            organization_id=org_id,
            asset_number=asset_num,
            asset_name=data.asset_name,
            category_id=data.category_id,
            purchase_date=data.purchase_date,
            purchase_cost=data.purchase_cost,
            salvage_value=data.salvage_value,
            current_value=data.purchase_cost,
            accumulated_depreciation=0.0,
            status="ACTIVE",
        )
        return await self.asset_repo.create(asset)

    async def get_fixed_assets(self, org_id: uuid.UUID) -> List[FixedAsset]:
        return await self.asset_repo.get_by_org(org_id)

    async def dispose_fixed_asset(self, asset_id: uuid.UUID, disposal_amount: float) -> FixedAsset:
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset or asset.is_deleted:
            raise HTTPException(status_code=404, detail="Fixed asset not found.")
        asset.status = "DISPOSED"
        asset.disposal_date = date.today()
        asset.disposal_amount = disposal_amount
        await self.db.commit()
        return asset

    # --- 12. FINANCIAL REPORTS ---
    async def get_trial_balance(self, org_id: uuid.UUID, as_of: Optional[date] = None) -> TrialBalanceReportResponse:
        as_of_date = as_of or date.today()
        accounts = await self.get_accounts(org_id)

        items = []
        tot_debit = 0.0
        tot_credit = 0.0

        for acct in accounts:
            bal = float(acct.balance)
            d = 0.0
            c = 0.0
            if acct.account_type in ["Assets", "Expenses"]:
                if bal >= 0:
                    d = bal
                else:
                    c = abs(bal)
            else:
                if bal >= 0:
                    c = bal
                else:
                    d = abs(bal)

            tot_debit += d
            tot_credit += c

            items.append(
                TrialBalanceItem(
                    account_id=acct.id,
                    account_code=acct.account_code,
                    account_name=acct.account_name,
                    account_type=acct.account_type,
                    debit=d,
                    credit=c,
                    balance=bal,
                )
            )

        return TrialBalanceReportResponse(
            as_of_date=as_of_date,
            total_debit=round(tot_debit, 2),
            total_credit=round(tot_credit, 2),
            items=items,
        )

    async def get_balance_sheet(self, org_id: uuid.UUID, as_of: Optional[date] = None) -> BalanceSheetResponse:
        tb = await self.get_trial_balance(org_id, as_of)

        assets = [i for i in tb.items if i.account_type == "Assets"]
        liabilities = [i for i in tb.items if i.account_type == "Liabilities"]
        equity = [i for i in tb.items if i.account_type == "Equity"]

        tot_assets = sum(i.balance for i in assets)
        tot_liabilities = sum(i.balance for i in liabilities)
        tot_equity = sum(i.balance for i in equity)

        return BalanceSheetResponse(
            as_of_date=tb.as_of_date,
            total_assets=round(tot_assets, 2),
            total_liabilities=round(tot_liabilities, 2),
            total_equity=round(tot_equity, 2),
            is_balanced=round(tot_assets, 2) == round(tot_liabilities + tot_equity, 2),
            asset_accounts=assets,
            liability_accounts=liabilities,
            equity_accounts=equity,
        )

    async def get_profit_loss(self, org_id: uuid.UUID, start: Optional[date] = None, end: Optional[date] = None) -> ProfitLossResponse:
        st = start or date(date.today().year, 1, 1)
        en = end or date.today()

        tb = await self.get_trial_balance(org_id)
        revenue = [i for i in tb.items if i.account_type == "Income"]
        expenses = [i for i in tb.items if i.account_type == "Expenses"]

        tot_rev = sum(i.balance for i in revenue)
        tot_exp = sum(i.balance for i in expenses)
        net_prof = tot_rev - tot_exp

        return ProfitLossResponse(
            start_date=st,
            end_date=en,
            total_revenue=round(tot_rev, 2),
            total_expenses=round(tot_exp, 2),
            net_profit=round(net_prof, 2),
            revenue_items=revenue,
            expense_items=expenses,
        )

    async def get_cash_flow(self, org_id: uuid.UUID, start: Optional[date] = None, end: Optional[date] = None) -> CashFlowResponse:
        st = start or date(date.today().year, 1, 1)
        en = end or date.today()
        pl = await self.get_profit_loss(org_id, st, en)

        op_cf = pl.net_profit
        inv_cf = 0.0
        fin_cf = 0.0
        net_cf = op_cf + inv_cf + fin_cf

        banks = await self.get_bank_accounts(org_id)
        ending_cash = sum(float(b.current_balance) for b in banks)

        return CashFlowResponse(
            start_date=st,
            end_date=en,
            operating_cash_flow=round(op_cf, 2),
            investing_cash_flow=round(inv_cf, 2),
            financing_cash_flow=round(fin_cf, 2),
            net_cash_flow=round(net_cf, 2),
            ending_cash_balance=round(ending_cash, 2),
        )

    async def get_aging_report(self, org_id: uuid.UUID, report_type: str = "RECEIVABLE") -> AgingReportResponse:
        buckets = []
        tot_outstanding = 0.0

        if report_type == "RECEIVABLE":
            invoices = await self.get_invoices(org_id)
            for inv in invoices:
                outstanding = float(inv.total_amount) - float(inv.paid_amount)
                if outstanding <= 0:
                    continue
                tot_outstanding += outstanding
                days_overdue = (date.today() - inv.due_date).days

                curr = outstanding if days_overdue <= 30 else 0.0
                d30_60 = outstanding if 31 <= days_overdue <= 60 else 0.0
                d60_90 = outstanding if 61 <= days_overdue <= 90 else 0.0
                d90_plus = outstanding if days_overdue > 90 else 0.0

                buckets.append(
                    AgingBucketItem(
                        entity_id=inv.customer_id,
                        entity_name=f"Invoice #{inv.invoice_number}",
                        current=curr,
                        days_31_60=d30_60,
                        days_61_90=d60_90,
                        days_over_90=d90_plus,
                        total_outstanding=outstanding,
                    )
                )
        else:
            bills = await self.get_bills(org_id)
            for bill in bills:
                outstanding = float(bill.total_amount) - float(bill.paid_amount)
                if outstanding <= 0:
                    continue
                tot_outstanding += outstanding
                days_overdue = (date.today() - bill.due_date).days

                curr = outstanding if days_overdue <= 30 else 0.0
                d30_60 = outstanding if 31 <= days_overdue <= 60 else 0.0
                d60_90 = outstanding if 61 <= days_overdue <= 90 else 0.0
                d90_plus = outstanding if days_overdue > 90 else 0.0

                buckets.append(
                    AgingBucketItem(
                        entity_id=bill.supplier_id,
                        entity_name=f"Bill #{bill.bill_number}",
                        current=curr,
                        days_31_60=d30_60,
                        days_61_90=d60_90,
                        days_over_90=d90_plus,
                        total_outstanding=outstanding,
                    )
                )

        return AgingReportResponse(
            report_type=report_type,
            as_of_date=date.today(),
            total_outstanding=round(tot_outstanding, 2),
            buckets=buckets,
        )

    # --- 13. ENTERPRISE SEARCH ---
    async def search_finance(self, org_id: uuid.UUID, query: str) -> List[FinanceSearchResult]:
        q = query.lower()
        results = []

        # 1. Accounts
        accounts = await self.get_accounts(org_id)
        for a in accounts:
            if q in a.account_name.lower() or q in a.account_code.lower():
                results.append(
                    FinanceSearchResult(
                        entity_type="Account",
                        id=a.id,
                        title=f"{a.account_code} - {a.account_name}",
                        subtitle=f"Type: {a.account_type}",
                        status="Active" if a.is_active else "Inactive",
                        amount=float(a.balance),
                        created_at=a.created_at,
                    )
                )

        # 2. Invoices
        invoices = await self.get_invoices(org_id)
        for inv in invoices:
            if q in inv.invoice_number.lower():
                results.append(
                    FinanceSearchResult(
                        entity_type="Invoice",
                        id=inv.id,
                        title=inv.invoice_number,
                        subtitle=f"Due: {inv.due_date}",
                        status=inv.status,
                        amount=float(inv.total_amount),
                        created_at=inv.created_at,
                    )
                )

        # 3. Bills
        bills = await self.get_bills(org_id)
        for b in bills:
            if q in b.bill_number.lower():
                results.append(
                    FinanceSearchResult(
                        entity_type="Bill",
                        id=b.id,
                        title=b.bill_number,
                        subtitle=f"Due: {b.due_date}",
                        status=b.status,
                        amount=float(b.total_amount),
                        created_at=b.created_at,
                    )
                )

        # 4. Journal Entries
        journals = await self.get_journal_entries(org_id)
        for je in journals:
            if q in je.entry_number.lower() or (je.reference and q in je.reference.lower()):
                results.append(
                    FinanceSearchResult(
                        entity_type="Journal Entry",
                        id=je.id,
                        title=je.entry_number,
                        subtitle=je.narration or "Journal Entry",
                        status=je.status,
                        amount=0.0,
                        created_at=je.created_at,
                    )
                )

        return results
