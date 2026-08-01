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
    CreditNoteRepository,
    DebitNoteRepository,
)
from app.repositories.audit import AuditLogRepository
from app.schemas.finance import (
    AccountCreate,
    AccountUpdate,
    FiscalPeriodCreate,
    JournalEntryCreate,
    JournalEntryLineCreate,
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
    CreditNoteCreate,
    CreditNoteResponse,
    DebitNoteCreate,
    DebitNoteResponse,
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
    GeneralLedgerReportResponse,
    GeneralLedgerEntryItem,
    TaxReportResponse,
    TaxReportItem,
    ExpenseReportResponse,
    ExpenseReportItem,
    RevenueReportResponse,
    RevenueReportItem,
    FinanceDashboardSummary,
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
        self.credit_note_repo = CreditNoteRepository(db)
        self.debit_note_repo = DebitNoteRepository(db)
        self.audit_repo = AuditLogRepository(db)

    async def log_audit(self, org_id: Optional[uuid.UUID], user_id: Optional[uuid.UUID], action: str, details: Optional[Dict[str, Any]] = None):
        try:
            await self.audit_repo.create({
                "organization_id": org_id,
                "user_id": user_id,
                "action": action,
                "ip_address": "127.0.0.1",
                "user_agent": "FinanceService",
                "details": details or {},
            })
        except Exception:
            pass  # Audit logging should not crash business transactions


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
        updated = await self.account_repo.update(account, update_data)
        await self.log_audit(account.organization_id, None, "UPDATE_ACCOUNT", {"account_id": str(account_id), "code": account.account_code})
        return updated

    async def delete_account(self, account_id: uuid.UUID) -> bool:
        account = await self.account_repo.get_by_id(account_id)
        if not account or account.is_deleted:
            raise HTTPException(status_code=404, detail="Account not found.")
        if account.is_system:
            raise HTTPException(status_code=400, detail="Cannot delete a system-defined account.")
        
        # Check if ledger entries exist for this account
        ledgers = await self.ledger_repo.get_by_account(account.organization_id, account_id)
        if ledgers:
            raise HTTPException(status_code=400, detail="Cannot delete account with existing ledger entries.")

        await self.account_repo.delete(account_id)
        await self.log_audit(account.organization_id, None, "DELETE_ACCOUNT", {"account_id": str(account_id), "code": account.account_code})
        return True


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
                entity_type=line.entity_type,
                entity_id=line.entity_id,
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
        await self.log_audit(original.organization_id, user_id, "REVERSE_JOURNAL_ENTRY", {"original_id": str(entry_id), "reversal_id": str(posted_reversal.id)})

        return posted_reversal

    async def get_journal_entries(self, org_id: uuid.UUID) -> List[JournalEntry]:
        return await self.journal_repo.get_by_org(org_id)

    # --- 4. ACCOUNTS RECEIVABLE (CUSTOMER INVOICES & CREDIT NOTES) ---
    async def create_invoice(self, org_id: uuid.UUID, data: CustomerInvoiceCreate) -> CustomerInvoice:
        inv_num = data.invoice_number or f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        subtotal = 0.0
        tax_total = 0.0
        processed_items = []

        tax_profiles = await self.get_tax_profiles(org_id)
        tax_rates_map = {}
        for p in tax_profiles:
            for r in getattr(p, "rates", []):
                tax_rates_map[r.id] = float(r.rate_percentage)

        for item in data.items:
            line_val = round(item.quantity * item.unit_price, 2)
            item_tax = 0.0
            if item.tax_rate_id and item.tax_rate_id in tax_rates_map:
                item_tax = round(line_val * (tax_rates_map[item.tax_rate_id] / 100.0), 2)
            
            subtotal += line_val
            tax_total += item_tax
            processed_items.append((item, line_val, item_tax))

        total_amount = round(subtotal + tax_total, 2)

        invoice = CustomerInvoice(
            organization_id=org_id,
            customer_id=data.customer_id,
            invoice_number=inv_num,
            issue_date=data.issue_date,
            due_date=data.due_date,
            subtotal=round(subtotal, 2),
            tax_total=round(tax_total, 2),
            total_amount=total_amount,
            paid_amount=0.0,
            status="SENT",
            notes=data.notes,
        )
        saved_inv = await self.invoice_repo.create(invoice)

        for item, line_val, item_tax in processed_items:
            inv_item = InvoiceItem(
                invoice_id=saved_inv.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_id=item.tax_rate_id,
                tax_amount=item_tax,
                line_total=line_val + item_tax,
            )
            self.db.add(inv_item)

        # Auto-create posting GL Journal Entry (AR Debit, Revenue Credit, Tax Credit if applicable)
        accounts = await self.get_accounts(org_id)
        ar_acct = next((a for a in accounts if a.account_code == "1100"), accounts[0])
        rev_acct = next((a for a in accounts if a.account_code in ["4000", "4100"]), accounts[-1])
        tax_acct = next((a for a in accounts if a.account_code == "2100"), None)

        lines = [
            JournalEntryLineCreate(account_id=ar_acct.id, debit=total_amount, credit=0.0, entity_type="CUSTOMER", entity_id=data.customer_id),
        ]
        if tax_total > 0 and tax_acct:
            lines.append(JournalEntryLineCreate(account_id=rev_acct.id, debit=0.0, credit=round(subtotal, 2)))
            lines.append(JournalEntryLineCreate(account_id=tax_acct.id, debit=0.0, credit=round(tax_total, 2)))
        else:
            lines.append(JournalEntryLineCreate(account_id=rev_acct.id, debit=0.0, credit=total_amount))

        je_data = JournalEntryCreate(
            entry_number=f"JE-{inv_num}",
            entry_date=data.issue_date,
            reference=inv_num,
            narration=f"Automated Posting for Customer Invoice {inv_num}",
            source_type="INVOICE",
            lines=lines,
        )
        je = await self.create_journal_entry(org_id, je_data)
        await self.post_journal_entry(je.id, None)

        await self.db.commit()
        await self.log_audit(org_id, None, "CREATE_INVOICE", {"invoice_id": str(saved_inv.id), "number": inv_num, "amount": total_amount})
        return await self.invoice_repo.get_with_items(saved_inv.id)

    async def get_invoices(self, org_id: uuid.UUID) -> List[CustomerInvoice]:
        return await self.invoice_repo.get_by_org(org_id)

    async def create_credit_note(self, org_id: uuid.UUID, data: CreditNoteCreate) -> CreditNote:
        cn_num = f"CN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        credit_note = CreditNote(
            organization_id=org_id,
            credit_note_number=cn_num,
            customer_id=data.customer_id,
            invoice_id=data.invoice_id,
            amount=data.amount,
            reason=data.reason,
            status="OPEN",
        )
        saved_cn = await self.credit_note_repo.create(credit_note)

        # GL Posting: Debit Sales Revenue, Credit AR
        accounts = await self.get_accounts(org_id)
        ar_acct = next((a for a in accounts if a.account_code == "1100"), accounts[0])
        rev_acct = next((a for a in accounts if a.account_code in ["4000", "4100"]), accounts[-1])

        je_data = JournalEntryCreate(
            entry_number=f"JE-{cn_num}",
            entry_date=date.today(),
            reference=cn_num,
            narration=f"Credit Note issued: {data.reason or 'Sales Return/Discount'}",
            source_type="CREDIT_NOTE",
            lines=[
                JournalEntryLineCreate(account_id=rev_acct.id, debit=data.amount, credit=0.0),
                JournalEntryLineCreate(account_id=ar_acct.id, debit=0.0, credit=data.amount, entity_type="CUSTOMER", entity_id=data.customer_id),
            ],
        )
        je = await self.create_journal_entry(org_id, je_data)
        await self.post_journal_entry(je.id, None)

        await self.db.commit()
        await self.log_audit(org_id, None, "CREATE_CREDIT_NOTE", {"credit_note_id": str(saved_cn.id), "number": cn_num, "amount": data.amount})
        return saved_cn

    async def get_credit_notes(self, org_id: uuid.UUID) -> List[CreditNote]:
        return await self.credit_note_repo.get_by_org(org_id)


    # --- 5. ACCOUNTS PAYABLE (SUPPLIER BILLS & DEBIT NOTES) ---
    async def create_bill(self, org_id: uuid.UUID, data: SupplierBillCreate) -> SupplierBill:
        bill_num = data.bill_number or f"BILL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        subtotal = 0.0
        tax_total = 0.0
        processed_items = []

        tax_profiles = await self.get_tax_profiles(org_id)
        tax_rates_map = {}
        for p in tax_profiles:
            for r in getattr(p, "rates", []):
                tax_rates_map[r.id] = float(r.rate_percentage)

        for item in data.items:
            line_val = round(item.quantity * item.unit_price, 2)
            item_tax = 0.0
            if item.tax_rate_id and item.tax_rate_id in tax_rates_map:
                item_tax = round(line_val * (tax_rates_map[item.tax_rate_id] / 100.0), 2)

            subtotal += line_val
            tax_total += item_tax
            processed_items.append((item, line_val, item_tax))

        total_amount = round(subtotal + tax_total, 2)

        bill = SupplierBill(
            organization_id=org_id,
            supplier_id=data.supplier_id,
            bill_number=bill_num,
            bill_date=data.bill_date,
            due_date=data.due_date,
            subtotal=round(subtotal, 2),
            tax_total=round(tax_total, 2),
            total_amount=total_amount,
            paid_amount=0.0,
            status="RECEIVED",
            notes=data.notes,
        )
        saved_bill = await self.bill_repo.create(bill)

        for item, line_val, item_tax in processed_items:
            bill_item = BillItem(
                bill_id=saved_bill.id,
                product_id=item.product_id,
                description=item.description,
                quantity=item.quantity,
                unit_price=item.unit_price,
                tax_rate_id=item.tax_rate_id,
                tax_amount=item_tax,
                line_total=line_val + item_tax,
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
        await self.log_audit(org_id, None, "CREATE_BILL", {"bill_id": str(saved_bill.id), "number": bill_num, "amount": total_amount})
        return await self.bill_repo.get_with_items(saved_bill.id)

    async def get_bills(self, org_id: uuid.UUID) -> List[SupplierBill]:
        return await self.bill_repo.get_by_org(org_id)

    async def create_debit_note(self, org_id: uuid.UUID, data: DebitNoteCreate) -> DebitNote:
        dn_num = f"DN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        debit_note = DebitNote(
            organization_id=org_id,
            debit_note_number=dn_num,
            supplier_id=data.supplier_id,
            bill_id=data.bill_id,
            amount=data.amount,
            reason=data.reason,
            status="OPEN",
        )
        saved_dn = await self.debit_note_repo.create(debit_note)

        # GL Posting: Debit AP, Credit Expense
        accounts = await self.get_accounts(org_id)
        ap_acct = next((a for a in accounts if a.account_code == "2000"), accounts[0])
        exp_acct = next((a for a in accounts if a.account_code == "5100"), accounts[-1])

        je_data = JournalEntryCreate(
            entry_number=f"JE-{dn_num}",
            entry_date=date.today(),
            reference=dn_num,
            narration=f"Debit Note issued: {data.reason or 'Purchase Return/Discount'}",
            source_type="DEBIT_NOTE",
            lines=[
                JournalEntryLineCreate(account_id=ap_acct.id, debit=data.amount, credit=0.0, entity_type="SUPPLIER", entity_id=data.supplier_id),
                JournalEntryLineCreate(account_id=exp_acct.id, debit=0.0, credit=data.amount),
            ],
        )
        je = await self.create_journal_entry(org_id, je_data)
        await self.post_journal_entry(je.id, None)

        await self.db.commit()
        await self.log_audit(org_id, None, "CREATE_DEBIT_NOTE", {"debit_note_id": str(saved_dn.id), "number": dn_num, "amount": data.amount})
        return saved_dn

    async def get_debit_notes(self, org_id: uuid.UUID) -> List[DebitNote]:
        return await self.debit_note_repo.get_by_org(org_id)

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

        # Update Bank Account balance & log transaction if bank account provided
        if data.bank_account_id:
            bank_acct = await self.bank_repo.get_by_id(data.bank_account_id)
            if bank_acct:
                tx_type = "DEPOSIT" if data.payment_type == "RECEIPT" else "WITHDRAWAL"
                if tx_type == "DEPOSIT":
                    bank_acct.current_balance = float(bank_acct.current_balance) + float(data.amount)
                else:
                    bank_acct.current_balance = float(bank_acct.current_balance) - float(data.amount)

                bank_tx = BankTransaction(
                    bank_account_id=data.bank_account_id,
                    transaction_date=data.payment_date,
                    description=f"Payment {pay_num} ({data.payment_type})",
                    amount=data.amount,
                    transaction_type=tx_type,
                    reference=data.reference or pay_num,
                )
                self.db.add(bank_tx)

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
        await self.log_audit(org_id, None, "CREATE_PAYMENT", {"payment_id": str(saved_pay.id), "number": pay_num, "amount": data.amount, "type": data.payment_type})
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

    async def get_bank_transactions(self, bank_account_id: uuid.UUID) -> List[BankTransaction]:
        return await self.bank_tx_repo.get_by_bank_account(bank_account_id)

    async def get_general_ledger_report(self, org_id: uuid.UUID, account_id: uuid.UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> GeneralLedgerReportResponse:
        account = await self.account_repo.get_by_id(account_id)
        if not account or account.organization_id != org_id:
            raise HTTPException(status_code=404, detail="Account not found.")

        entries = await self.ledger_repo.get_by_account(org_id, account_id)
        filtered_entries = []
        for e in entries:
            if start_date and e.transaction_date < start_date:
                continue
            if end_date and e.transaction_date > end_date:
                continue
            
            # Fetch journal entry number narration if available
            je = await self.journal_repo.get_by_id(e.journal_entry_id)
            filtered_entries.append(
                GeneralLedgerEntryItem(
                    id=e.id,
                    journal_entry_id=e.journal_entry_id,
                    entry_number=je.entry_number if je else "JE-UNMAPPED",
                    transaction_date=e.transaction_date,
                    narration=je.narration if je else None,
                    debit=float(e.debit),
                    credit=float(e.credit),
                    running_balance=float(e.running_balance),
                )
            )

        open_bal = float(account.opening_balance)
        close_bal = float(account.balance)
        return GeneralLedgerReportResponse(
            account_id=account.id,
            account_code=account.account_code,
            account_name=account.account_name,
            opening_balance=open_bal,
            closing_balance=close_bal,
            entries=filtered_entries,
        )

    async def get_tax_report(self, org_id: uuid.UUID, as_of: Optional[date] = None) -> TaxReportResponse:
        as_of_date = as_of or date.today()
        invoices = await self.get_invoices(org_id)
        bills = await self.get_bills(org_id)

        tot_tax_collected = sum(float(inv.tax_total) for inv in invoices if inv.issue_date <= as_of_date)
        tot_tax_paid = sum(float(b.tax_total) for b in bills if b.bill_date <= as_of_date)

        profiles = await self.get_tax_profiles(org_id)
        items = []
        for p in profiles:
            for r in getattr(p, "rates", []):
                items.append(
                    TaxReportItem(
                        tax_rate_id=r.id,
                        tax_name=r.name,
                        tax_code=r.code,
                        rate_percentage=float(r.rate_percentage),
                        taxable_amount=round(tot_tax_collected * 10, 2) if r.type == "VAT" else 0.0,
                        tax_amount=tot_tax_collected if r.type == "VAT" else 0.0,
                    )
                )

        return TaxReportResponse(
            as_of_date=as_of_date,
            total_tax_collected=round(tot_tax_collected, 2),
            total_tax_paid=round(tot_tax_paid, 2),
            net_tax_payable=round(tot_tax_collected - tot_tax_paid, 2),
            items=items,
        )

    async def get_expense_report(self, org_id: uuid.UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> ExpenseReportResponse:
        st = start_date or date(date.today().year, 1, 1)
        en = end_date or date.today()
        claims = await self.get_expense_claims(org_id)
        cats = await self.get_expense_categories(org_id)

        cat_map = {c.id: c for c in cats}
        summary = {}

        tot_exp = 0.0
        for claim in claims:
            if claim.claim_date < st or claim.claim_date > en:
                continue
            tot_exp += float(claim.amount)
            cid = claim.category_id
            if cid not in summary:
                c_obj = cat_map.get(cid)
                summary[cid] = {
                    "category_id": cid,
                    "category_name": c_obj.name if c_obj else "General",
                    "category_code": c_obj.code if c_obj else "EXP-GEN",
                    "total_amount": 0.0,
                    "claim_count": 0,
                }
            summary[cid]["total_amount"] += float(claim.amount)
            summary[cid]["claim_count"] += 1

        items = [ExpenseReportItem(**vals) for vals in summary.values()]
        return ExpenseReportResponse(
            start_date=st,
            end_date=en,
            total_expenses=round(tot_exp, 2),
            categories=items,
        )

    async def get_revenue_report(self, org_id: uuid.UUID, start_date: Optional[date] = None, end_date: Optional[date] = None) -> RevenueReportResponse:
        st = start_date or date(date.today().year, 1, 1)
        en = end_date or date.today()
        invoices = await self.get_invoices(org_id)

        cust_summary = {}
        tot_rev = 0.0

        for inv in invoices:
            if inv.issue_date < st or inv.issue_date > en:
                continue
            tot_rev += float(inv.total_amount)
            cid = inv.customer_id
            if cid not in cust_summary:
                cust_summary[cid] = {
                    "customer_id": cid,
                    "total_revenue": 0.0,
                    "invoice_count": 0,
                }
            cust_summary[cid]["total_revenue"] += float(inv.total_amount)
            cust_summary[cid]["invoice_count"] += 1

        items = [RevenueReportItem(**vals) for vals in cust_summary.values()]
        return RevenueReportResponse(
            start_date=st,
            end_date=en,
            total_revenue=round(tot_rev, 2),
            items=items,
        )

    async def get_budget_report(self, org_id: uuid.UUID, fiscal_year: Optional[int] = None) -> BudgetReportResponse:
        fy = fiscal_year or date.today().year
        budgets = await self.get_budgets(org_id)
        fy_budgets = [b for b in budgets if b.fiscal_year == fy]

        accounts = await self.get_accounts(org_id)
        acct_map = {a.id: a.account_name for a in accounts}

        tot_b = 0.0
        tot_a = 0.0
        items = []

        for b in fy_budgets:
            for item in getattr(b, "items", []):
                b_amt = float(item.budgeted_amount)
                a_amt = float(item.actual_amount)
                var = b_amt - a_amt
                pct = round((var / b_amt * 100.0) if b_amt > 0 else 0.0, 2)
                tot_b += b_amt
                tot_a += a_amt
                items.append(
                    BudgetVsActualItem(
                        account_id=item.account_id,
                        account_name=acct_map.get(item.account_id, "Unknown Account"),
                        budgeted=b_amt,
                        actual=a_amt,
                        variance=round(var, 2),
                        variance_percentage=pct,
                    )
                )

        return BudgetReportResponse(
            fiscal_year=fy,
            total_budgeted=round(tot_b, 2),
            total_actual=round(tot_a, 2),
            variance=round(tot_b - tot_a, 2),
            items=items,
        )

    async def get_dashboard_summary(self, org_id: uuid.UUID) -> FinanceDashboardSummary:
        pl = await self.get_profit_loss(org_id)
        invoices = await self.get_invoices(org_id)
        bills = await self.get_bills(org_id)
        banks = await self.get_bank_accounts(org_id)
        claims = await self.get_expense_claims(org_id)
        budgets = await self.get_budgets(org_id)

        tot_ar = sum(float(inv.total_amount) - float(inv.paid_amount) for inv in invoices)
        tot_ap = sum(float(b.total_amount) - float(b.paid_amount) for b in bills)
        tot_cash = sum(float(b.current_balance) for b in banks)

        pending_claims = sum(1 for c in claims if c.status == "SUBMITTED")
        tot_budgeted = sum(float(b.total_budgeted) for b in budgets)
        utilization = round((pl.total_expenses / tot_budgeted * 100.0) if tot_budgeted > 0 else 0.0, 2)

        return FinanceDashboardSummary(
            total_revenue=pl.total_revenue,
            total_expenses=pl.total_expenses,
            net_profit=pl.net_profit,
            total_receivables=round(tot_ar, 2),
            total_payables=round(tot_ap, 2),
            total_cash_balance=round(tot_cash, 2),
            budget_utilization_pct=utilization,
            recent_transactions_count=len(invoices) + len(bills),
            pending_expense_claims=pending_claims,
        )

