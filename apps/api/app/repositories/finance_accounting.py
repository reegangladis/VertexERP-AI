import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.finance_accounting_v12 import (
    Account,
    AccountType,
    BankAccount,
    BankTransaction,
    BillItem,
    Budget,
    BudgetItem,
    CustomerInvoice,
    GeneralLedger,
    InvoiceItem,
    JournalEntry,
    JournalEntryLine,
    Payment,
    SupplierBill,
)
from app.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account]):
    def __init__(self, db: AsyncSession):
        super().__init__(Account, db)

    async def find_by_code(self, org_id: uuid.UUID, code: str) -> Account | None:
        stmt = select(Account).where(
            Account.organization_id == org_id, Account.account_code == code, Account.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[Account]:
        stmt = select(Account).where(
            Account.organization_id == org_id, Account.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class JournalEntryRepository(BaseRepository[JournalEntry]):
    def __init__(self, db: AsyncSession):
        super().__init__(JournalEntry, db)

    async def get_with_lines(self, entry_id: uuid.UUID) -> JournalEntry | None:
        stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(JournalEntry.id == entry_id, JournalEntry.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_number(self, j_number: str) -> JournalEntry | None:
        stmt = select(JournalEntry).where(
            JournalEntry.journal_number == j_number, JournalEntry.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .options(selectinload(JournalEntry.lines))
            .where(JournalEntry.organization_id == org_id, JournalEntry.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class GeneralLedgerRepository(BaseRepository[GeneralLedger]):
    def __init__(self, db: AsyncSession):
        super().__init__(GeneralLedger, db)


class CustomerInvoiceRepository(BaseRepository[CustomerInvoice]):
    def __init__(self, db: AsyncSession):
        super().__init__(CustomerInvoice, db)

    async def get_with_items(self, inv_id: uuid.UUID) -> CustomerInvoice | None:
        stmt = (
            select(CustomerInvoice)
            .options(selectinload(CustomerInvoice.items))
            .where(CustomerInvoice.id == inv_id, CustomerInvoice.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_number(self, inv_number: str) -> CustomerInvoice | None:
        stmt = select(CustomerInvoice).where(
            CustomerInvoice.invoice_number == inv_number, CustomerInvoice.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class SupplierBillRepository(BaseRepository[SupplierBill]):
    def __init__(self, db: AsyncSession):
        super().__init__(SupplierBill, db)

    async def get_with_items(self, bill_id: uuid.UUID) -> SupplierBill | None:
        stmt = (
            select(SupplierBill)
            .options(selectinload(SupplierBill.items))
            .where(SupplierBill.id == bill_id, SupplierBill.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_by_number(self, bill_number: str) -> SupplierBill | None:
        stmt = select(SupplierBill).where(
            SupplierBill.bill_number == bill_number, SupplierBill.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Payment, db)

    async def find_by_reference(self, ref: str) -> Payment | None:
        stmt = select(Payment).where(
            Payment.payment_reference == ref, Payment.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class BankAccountRepository(BaseRepository[BankAccount]):
    def __init__(self, db: AsyncSession):
        super().__init__(BankAccount, db)

    async def find_by_account_number(self, org_id: uuid.UUID, acc_num: str) -> BankAccount | None:
        stmt = select(BankAccount).where(
            BankAccount.organization_id == org_id, BankAccount.account_number == acc_num, BankAccount.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[BankAccount]:
        stmt = select(BankAccount).where(
            BankAccount.organization_id == org_id, BankAccount.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
