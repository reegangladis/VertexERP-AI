import uuid
from typing import List, Optional
from sqlalchemy import select, or_, and_, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
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

class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: AsyncSession):
        super().__init__(Account, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Account]:
        stmt = select(Account).where(Account.organization_id == org_id, Account.is_deleted == False).order_by(Account.account_code)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Optional[Account]:
        stmt = select(Account).where(Account.organization_id == org_id, Account.account_code == code, Account.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()


class FiscalPeriodRepository(BaseRepository[FiscalPeriod]):
    def __init__(self, db: AsyncSession):
        super().__init__(FiscalPeriod, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[FiscalPeriod]:
        stmt = select(FiscalPeriod).where(FiscalPeriod.organization_id == org_id, FiscalPeriod.is_deleted == False).order_by(FiscalPeriod.start_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class JournalEntryRepository(BaseRepository[JournalEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(JournalEntry, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .options(joinedload(JournalEntry.lines))
            .where(JournalEntry.organization_id == org_id, JournalEntry.is_deleted == False)
            .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_lines(self, entry_id: uuid.UUID) -> Optional[JournalEntry]:
        stmt = select(JournalEntry).options(joinedload(JournalEntry.lines)).where(JournalEntry.id == entry_id, JournalEntry.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()


class LedgerRepository(BaseRepository[Ledger]):
    def __init__(self, db: AsyncSession):
        super().__init__(Ledger, db)

    async def get_by_account(self, org_id: uuid.UUID, account_id: uuid.UUID) -> List[Ledger]:
        stmt = select(Ledger).where(Ledger.organization_id == org_id, Ledger.account_id == account_id).order_by(Ledger.transaction_date)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_org(self, org_id: uuid.UUID) -> List[Ledger]:
        stmt = select(Ledger).where(Ledger.organization_id == org_id).order_by(Ledger.transaction_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CustomerInvoiceRepository(BaseRepository[CustomerInvoice]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerInvoice, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[CustomerInvoice]:
        stmt = (
            select(CustomerInvoice)
            .options(joinedload(CustomerInvoice.items))
            .where(CustomerInvoice.organization_id == org_id, CustomerInvoice.is_deleted == False)
            .order_by(CustomerInvoice.issue_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_items(self, invoice_id: uuid.UUID) -> Optional[CustomerInvoice]:
        stmt = select(CustomerInvoice).options(joinedload(CustomerInvoice.items)).where(CustomerInvoice.id == invoice_id, CustomerInvoice.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()


class SupplierBillRepository(BaseRepository[SupplierBill]):
    def __init__(self, db: AsyncSession):
        super().__init__(SupplierBill, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[SupplierBill]:
        stmt = (
            select(SupplierBill)
            .options(joinedload(SupplierBill.items))
            .where(SupplierBill.organization_id == org_id, SupplierBill.is_deleted == False)
            .order_by(SupplierBill.bill_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_items(self, bill_id: uuid.UUID) -> Optional[SupplierBill]:
        stmt = select(SupplierBill).options(joinedload(SupplierBill.items)).where(SupplierBill.id == bill_id, SupplierBill.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalars().first()


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Payment]:
        stmt = select(Payment).where(Payment.organization_id == org_id, Payment.is_deleted == False).order_by(Payment.payment_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BankAccountRepository(BaseRepository[BankAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(BankAccount, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[BankAccount]:
        stmt = select(BankAccount).where(BankAccount.organization_id == org_id, BankAccount.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BankTransactionRepository(BaseRepository[BankTransaction]):
    def __init__(self, db: AsyncSession):
        super().__init__(BankTransaction, db)

    async def get_by_bank_account(self, bank_account_id: uuid.UUID) -> List[BankTransaction]:
        stmt = select(BankTransaction).where(BankTransaction.bank_account_id == bank_account_id).order_by(BankTransaction.transaction_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class ExpenseCategoryRepository(BaseRepository[ExpenseCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ExpenseCategory, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[ExpenseCategory]:
        stmt = select(ExpenseCategory).where(ExpenseCategory.organization_id == org_id, ExpenseCategory.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class ExpenseClaimRepository(BaseRepository[ExpenseClaim]):
    def __init__(self, db: AsyncSession):
        super().__init__(ExpenseClaim, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[ExpenseClaim]:
        stmt = select(ExpenseClaim).where(ExpenseClaim.organization_id == org_id, ExpenseClaim.is_deleted == False).order_by(ExpenseClaim.claim_date.desc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, db: AsyncSession):
        super().__init__(Budget, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[Budget]:
        stmt = select(Budget).options(joinedload(Budget.items)).where(Budget.organization_id == org_id, Budget.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())


class TaxProfileRepository(BaseRepository[TaxProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(TaxProfile, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[TaxProfile]:
        stmt = select(TaxProfile).options(joinedload(TaxProfile.rates)).where(TaxProfile.organization_id == org_id, TaxProfile.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())


class FixedAssetRepository(BaseRepository[FixedAsset]):
    def __init__(self, db: AsyncSession):
        super().__init__(FixedAsset, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[FixedAsset]:
        stmt = select(FixedAsset).where(FixedAsset.organization_id == org_id, FixedAsset.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class AssetCategoryRepository(BaseRepository[AssetCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(AssetCategory, db)

    async def get_by_org(self, org_id: uuid.UUID) -> List[AssetCategory]:
        stmt = select(AssetCategory).where(AssetCategory.organization_id == org_id, AssetCategory.is_deleted == False)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
