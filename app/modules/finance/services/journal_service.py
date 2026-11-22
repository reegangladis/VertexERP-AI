"""High-Integrity Double-Entry Journal Entry Service."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.finance.models.journal import (
    EntryStatus,
    EntryType,
    GeneralLedger,
    JournalEntry,
    JournalLine,
)
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.repositories.fiscal_repository import FiscalRepository
from app.modules.finance.repositories.journal_repository import (
    GeneralLedgerRepository,
    JournalRepository,
)
from app.modules.finance.schemas.journal import JournalEntryCreate


class JournalEntryService:
    """Service enforcing double-entry rules, period locking, and General Ledger posting."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.journal_repo = JournalRepository(session)
        self.gl_repo = GeneralLedgerRepository(session)
        self.fiscal_repo = FiscalRepository(session)
        self.account_repo = AccountRepository(session)

    async def create_draft_entry(
        self,
        data: JournalEntryCreate,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> JournalEntry:
        """Create a draft journal entry."""
        if len(data.lines) < 2:
            raise BadRequestException("A journal entry must contain at least 2 lines.")

        total_debit = Decimal("0.0000")
        total_credit = Decimal("0.0000")

        # Validate accounts exist and accumulate totals
        for line in data.lines:
            acct = await self.account_repo.get_by_id(line.account_id, tenant_id, org_id)
            if not acct:
                raise NotFoundException(f"Account {line.account_id} not found.")
            if line.debit < 0 or line.credit < 0:
                raise BadRequestException("Debits and credits must be non-negative numbers.")
            if line.debit > 0 and line.credit > 0:
                raise BadRequestException("A journal line cannot have both debit and credit.")
            if line.debit == 0 and line.credit == 0:
                raise BadRequestException("A journal line must have either debit or credit.")
            total_debit += line.debit
            total_credit += line.credit

        entry_number = (
            data.entry_number
            or f"JE-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        )

        entry = JournalEntry(
            tenant_id=tenant_id,
            organization_id=org_id,
            entry_number=entry_number,
            entry_date=data.entry_date,
            posting_date=data.posting_date,
            fiscal_period_id=data.fiscal_period_id,
            entry_type=data.entry_type,
            status=EntryStatus.DRAFT,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            currency=data.currency,
            exchange_rate=data.exchange_rate,
            total_debit=total_debit,
            total_credit=total_credit,
            notes=data.notes,
        )

        for idx, line in enumerate(data.lines, start=1):
            jl = JournalLine(
                tenant_id=tenant_id,
                organization_id=org_id,
                line_number=idx,
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                currency=line.currency,
                currency_debit=line.debit * data.exchange_rate,
                currency_credit=line.credit * data.exchange_rate,
                partner_type=line.partner_type,
                partner_id=line.partner_id,
                description=line.description,
                cost_center_id=line.cost_center_id,
            )
            entry.lines.append(jl)

        await self.journal_repo.create(entry)
        await self.session.commit()
        return await self.journal_repo.get_by_id(entry.id, tenant_id, org_id)

    async def post_entry(
        self,
        entry_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> JournalEntry:
        """Validate strict debit==credit balance, check fiscal period locks, and post to GL."""
        entry = await self.journal_repo.get_by_id(entry_id, tenant_id, org_id)
        if not entry:
            raise NotFoundException(f"Journal Entry {entry_id} not found.")

        if entry.status == EntryStatus.POSTED:
            raise BadRequestException(f"Journal Entry {entry.entry_number} is already POSTED.")
        if entry.status == EntryStatus.REVERSED:
            raise BadRequestException(
                f"Journal Entry {entry.entry_number} is REVERSED and cannot be posted."
            )
        if entry.status == EntryStatus.CANCELLED:
            raise BadRequestException(f"Journal Entry {entry.entry_number} is CANCELLED.")

        # 1. Strict Balance Verification
        total_debit = sum(Decimal(str(line.debit)) for line in entry.lines)
        total_credit = sum(Decimal(str(line.credit)) for line in entry.lines)

        if total_debit != total_credit:
            raise BadRequestException(
                f"Unbalanced Journal Entry: Total debits ({total_debit}) must equal total credits ({total_credit})."
            )
        if total_debit <= 0:
            raise BadRequestException("Journal Entry must have a non-zero balanced amount.")

        # 2. Fiscal Period Verification and Locking Control
        period = None
        if entry.fiscal_period_id:
            period = await self.fiscal_repo.get_period_by_id(
                entry.fiscal_period_id, tenant_id, org_id
            )
        if not period:
            period = await self.fiscal_repo.find_period_for_date(
                entry.posting_date, tenant_id, org_id
            )

        if period:
            if period.is_locked:
                raise BadRequestException(
                    f"Fiscal period '{period.period_name}' is LOCKED. Posting disallowed."
                )
            if period.is_closed:
                raise BadRequestException(
                    f"Fiscal period '{period.period_name}' is CLOSED. Posting disallowed."
                )
            entry.fiscal_period_id = period.id

        # 3. Mark Entry Posted
        entry.status = EntryStatus.POSTED
        entry.total_debit = total_debit
        entry.total_credit = total_credit
        entry.posted_by_id = user_id
        entry.posted_at = datetime.now(UTC)

        # 4. Post each line to General Ledger
        for line in entry.lines:
            # Calculate running balance for account
            prior_debit, prior_credit = await self.gl_repo.get_account_totals(
                line.account_id, tenant_id, org_id
            )
            acct = await self.account_repo.get_by_id(line.account_id, tenant_id, org_id)

            # Asset & Expense increase with debit; Liability, Equity, Revenue increase with credit
            is_debit_normal = acct.account_type in ["ASSET", "EXPENSE"] if acct else True

            new_debit_total = Decimal(str(prior_debit)) + Decimal(str(line.debit))
            new_credit_total = Decimal(str(prior_credit)) + Decimal(str(line.credit))

            if is_debit_normal:
                balance_after = new_debit_total - new_credit_total
            else:
                balance_after = new_credit_total - new_debit_total

            gl_record = GeneralLedger(
                tenant_id=tenant_id,
                organization_id=org_id,
                account_id=line.account_id,
                journal_entry_id=entry.id,
                journal_line_id=line.id,
                posting_date=entry.posting_date,
                fiscal_period_id=entry.fiscal_period_id,
                debit=line.debit,
                credit=line.credit,
                balance_after=balance_after,
                currency=line.currency,
                description=line.description or entry.notes or f"JE {entry.entry_number}",
            )
            await self.gl_repo.record_gl_posting(gl_record)

        await self.session.commit()
        return await self.journal_repo.get_by_id(entry.id, tenant_id, org_id)

    async def create_and_post_entry(
        self,
        data: JournalEntryCreate,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> JournalEntry:
        """Create draft journal entry and immediately validate balance, period, and post to GL."""
        entry = await self.create_draft_entry(data, tenant_id, org_id)
        return await self.post_entry(entry.id, tenant_id, org_id, user_id=user_id)

    async def reverse_entry(
        self,
        entry_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
        notes: str | None = None,
    ) -> JournalEntry:
        """Create an atomic reversal entry flipping debits & credits, and mark original as REVERSED."""
        orig = await self.journal_repo.get_by_id(entry_id, tenant_id, org_id)
        if not orig:
            raise NotFoundException(f"Journal Entry {entry_id} not found.")

        if orig.status != EntryStatus.POSTED:
            raise BadRequestException(
                f"Only POSTED journal entries can be reversed. Current status: {orig.status}"
            )

        rev_number = f"REV-{orig.entry_number}"

        reversal_entry = JournalEntry(
            tenant_id=tenant_id,
            organization_id=org_id,
            entry_number=rev_number,
            entry_date=date.today(),
            posting_date=date.today(),
            fiscal_period_id=orig.fiscal_period_id,
            entry_type=EntryType.REVERSAL,
            status=EntryStatus.DRAFT,
            reference_type="REVERSAL",
            reference_id=str(orig.id),
            currency=orig.currency,
            exchange_rate=orig.exchange_rate,
            total_debit=orig.total_credit,
            total_credit=orig.total_debit,
            notes=notes or f"Reversal of {orig.entry_number}",
        )

        for line in orig.lines:
            rev_line = JournalLine(
                tenant_id=tenant_id,
                organization_id=org_id,
                line_number=line.line_number,
                account_id=line.account_id,
                debit=line.credit,  # FLIP DEBIT AND CREDIT
                credit=line.debit,
                currency=line.currency,
                currency_debit=line.currency_credit,
                currency_credit=line.currency_debit,
                partner_type=line.partner_type,
                partner_id=line.partner_id,
                description=f"Reversal: {line.description or orig.entry_number}",
                cost_center_id=line.cost_center_id,
            )
            reversal_entry.lines.append(rev_line)

        await self.journal_repo.create(reversal_entry)
        await self.session.flush()

        # Post the reversal entry
        posted_reversal = await self.post_entry(
            reversal_entry.id, tenant_id, org_id, user_id=user_id
        )

        # Mark original as REVERSED
        orig.status = EntryStatus.REVERSED
        orig.reversed_by_entry_id = posted_reversal.id
        await self.session.commit()

        return posted_reversal
