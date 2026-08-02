import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.finance import (
    Account,
    AssetCategory,
    BankAccount,
    BankTransaction,
    Budget,
    CreditNote,
    CustomerInvoice,
    DebitNote,
    ExpenseCategory,
    ExpenseClaim,
    FiscalPeriod,
    FixedAsset,
    JournalEntry,
    Ledger,
    Payment,
    SupplierBill,
    TaxProfile,
)
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: AsyncSession):
        super().__init__(Account, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Account]:
        stmt = (
            select(Account)
            .where(Account.organization_id == org_id, Account.is_deleted == False)
            .order_by(Account.account_code)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_code(self, org_id: uuid.UUID, code: str) -> Account | None:
        stmt = select(Account).where(
            Account.organization_id == org_id,
            Account.account_code == code,
            Account.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()


class FiscalPeriodRepository(BaseRepository[FiscalPeriod]):
    def __init__(self, db: AsyncSession):
        super().__init__(FiscalPeriod, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[FiscalPeriod]:
        stmt = (
            select(FiscalPeriod)
            .where(
                FiscalPeriod.organization_id == org_id, FiscalPeriod.is_deleted == False
            )
            .order_by(FiscalPeriod.start_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class JournalEntryRepository(BaseRepository[JournalEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(JournalEntry, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .options(joinedload(JournalEntry.lines))
            .where(
                JournalEntry.organization_id == org_id, JournalEntry.is_deleted == False
            )
            .order_by(JournalEntry.entry_date.desc(), JournalEntry.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_lines(self, entry_id: uuid.UUID) -> JournalEntry | None:
        stmt = (
            select(JournalEntry)
            .options(joinedload(JournalEntry.lines))
            .where(JournalEntry.id == entry_id, JournalEntry.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()


class LedgerRepository(BaseRepository[Ledger]):
    def __init__(self, db: AsyncSession):
        super().__init__(Ledger, db)

    async def get_by_account(
        self, org_id: uuid.UUID, account_id: uuid.UUID
    ) -> list[Ledger]:
        stmt = (
            select(Ledger)
            .where(Ledger.organization_id == org_id, Ledger.account_id == account_id)
            .order_by(Ledger.transaction_date)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_org(self, org_id: uuid.UUID) -> list[Ledger]:
        stmt = (
            select(Ledger)
            .where(Ledger.organization_id == org_id)
            .order_by(Ledger.transaction_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CustomerInvoiceRepository(BaseRepository[CustomerInvoice]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerInvoice, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[CustomerInvoice]:
        stmt = (
            select(CustomerInvoice)
            .options(joinedload(CustomerInvoice.items))
            .where(
                CustomerInvoice.organization_id == org_id,
                CustomerInvoice.is_deleted == False,
            )
            .order_by(CustomerInvoice.issue_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_items(self, invoice_id: uuid.UUID) -> CustomerInvoice | None:
        stmt = (
            select(CustomerInvoice)
            .options(joinedload(CustomerInvoice.items))
            .where(
                CustomerInvoice.id == invoice_id, CustomerInvoice.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()


class SupplierBillRepository(BaseRepository[SupplierBill]):
    def __init__(self, db: AsyncSession):
        super().__init__(SupplierBill, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[SupplierBill]:
        stmt = (
            select(SupplierBill)
            .options(joinedload(SupplierBill.items))
            .where(
                SupplierBill.organization_id == org_id, SupplierBill.is_deleted == False
            )
            .order_by(SupplierBill.bill_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_with_items(self, bill_id: uuid.UUID) -> SupplierBill | None:
        stmt = (
            select(SupplierBill)
            .options(joinedload(SupplierBill.items))
            .where(SupplierBill.id == bill_id, SupplierBill.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Payment]:
        stmt = (
            select(Payment)
            .where(Payment.organization_id == org_id, Payment.is_deleted == False)
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BankAccountRepository(BaseRepository[BankAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(BankAccount, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[BankAccount]:
        stmt = select(BankAccount).where(
            BankAccount.organization_id == org_id, BankAccount.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BankTransactionRepository(BaseRepository[BankTransaction]):
    def __init__(self, db: AsyncSession):
        super().__init__(BankTransaction, db)

    async def get_by_bank_account(
        self, bank_account_id: uuid.UUID
    ) -> list[BankTransaction]:
        stmt = (
            select(BankTransaction)
            .where(BankTransaction.bank_account_id == bank_account_id)
            .order_by(BankTransaction.transaction_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class ExpenseCategoryRepository(BaseRepository[ExpenseCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ExpenseCategory, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[ExpenseCategory]:
        stmt = select(ExpenseCategory).where(
            ExpenseCategory.organization_id == org_id,
            ExpenseCategory.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class ExpenseClaimRepository(BaseRepository[ExpenseClaim]):
    def __init__(self, db: AsyncSession):
        super().__init__(ExpenseClaim, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[ExpenseClaim]:
        stmt = (
            select(ExpenseClaim)
            .where(
                ExpenseClaim.organization_id == org_id, ExpenseClaim.is_deleted == False
            )
            .order_by(ExpenseClaim.claim_date.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class BudgetRepository(BaseRepository[Budget]):
    def __init__(self, db: AsyncSession):
        super().__init__(Budget, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[Budget]:
        stmt = (
            select(Budget)
            .options(joinedload(Budget.items))
            .where(Budget.organization_id == org_id, Budget.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())


class TaxProfileRepository(BaseRepository[TaxProfile]):
    def __init__(self, db: AsyncSession):
        super().__init__(TaxProfile, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[TaxProfile]:
        stmt = (
            select(TaxProfile)
            .options(joinedload(TaxProfile.rates))
            .where(TaxProfile.organization_id == org_id, TaxProfile.is_deleted == False)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().unique().all())


class FixedAssetRepository(BaseRepository[FixedAsset]):
    def __init__(self, db: AsyncSession):
        super().__init__(FixedAsset, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[FixedAsset]:
        stmt = select(FixedAsset).where(
            FixedAsset.organization_id == org_id, FixedAsset.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class AssetCategoryRepository(BaseRepository[AssetCategory]):
    def __init__(self, db: AsyncSession):
        super().__init__(AssetCategory, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[AssetCategory]:
        stmt = select(AssetCategory).where(
            AssetCategory.organization_id == org_id, AssetCategory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class CreditNoteRepository(BaseRepository[CreditNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(CreditNote, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[CreditNote]:
        stmt = (
            select(CreditNote)
            .where(CreditNote.organization_id == org_id, CreditNote.is_deleted == False)
            .order_by(CreditNote.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


class DebitNoteRepository(BaseRepository[DebitNote]):
    def __init__(self, db: AsyncSession):
        super().__init__(DebitNote, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[DebitNote]:
        stmt = (
            select(DebitNote)
            .where(DebitNote.organization_id == org_id, DebitNote.is_deleted == False)
            .order_by(DebitNote.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
