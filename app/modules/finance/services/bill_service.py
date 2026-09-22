"""Vendor Bill (Accounts Payable) Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.finance.models.bill import Bill, BillLine, BillStatus
from app.modules.finance.models.journal import PartnerType
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.repositories.bill_repository import BillRepository
from app.modules.finance.repositories.party_repository import VendorPartyRepository
from app.modules.finance.schemas.bill import BillCreate
from app.modules.finance.schemas.journal import JournalEntryCreate, JournalLineCreate
from app.modules.finance.services.journal_service import JournalEntryService


class BillService:
    """Service managing vendor bills and AP journal posting."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.bill_repo = BillRepository(session)
        self.vendor_repo = VendorPartyRepository(session)
        self.account_repo = AccountRepository(session)
        self.journal_service = JournalEntryService(session)

    async def create_bill(
        self,
        data: BillCreate,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Bill:
        """Create a draft vendor bill with calculated line items."""
        vendor = await self.vendor_repo.get_by_id(data.vendor_id, tenant_id, org_id)
        if not vendor:
            raise NotFoundException(f"Vendor {data.vendor_id} not found.")

        ap_account_id = data.ap_account_id or vendor.ap_account_id
        if not ap_account_id:
            ap_acct = await self.account_repo.get_by_code("2000", tenant_id, org_id)
            if ap_acct:
                ap_account_id = ap_acct.id
            else:
                raise BadRequestException("No AP Account specified for vendor bill.")

        subtotal = Decimal("0.0000")
        tax_total = Decimal("0.0000")

        bill_number = (
            data.bill_number
            or f"BILL-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        )

        bill = Bill(
            tenant_id=tenant_id,
            organization_id=org_id,
            bill_number=bill_number,
            vendor_id=data.vendor_id,
            vendor_invoice_ref=data.vendor_invoice_ref,
            bill_date=data.bill_date,
            due_date=data.due_date,
            currency=data.currency,
            exchange_rate=data.exchange_rate,
            subtotal_amount=Decimal("0.0000"),
            tax_amount=Decimal("0.0000"),
            total_amount=Decimal("0.0000"),
            amount_paid=Decimal("0.0000"),
            amount_due=Decimal("0.0000"),
            status=BillStatus.DRAFT,
            ap_account_id=ap_account_id,
            notes=data.notes,
        )

        for line_data in data.lines:
            acct = await self.account_repo.get_by_id(
                line_data.expense_account_id, tenant_id, org_id
            )
            if not acct:
                raise NotFoundException(
                    f"Expense Account {line_data.expense_account_id} not found."
                )

            line_base = line_data.quantity * line_data.unit_price
            line_tax = line_base * line_data.tax_rate
            line_tot = line_base + line_tax

            subtotal += line_base
            tax_total += line_tax

            bl = BillLine(
                tenant_id=tenant_id,
                bill_id=bill.id,
                description=line_data.description,
                expense_account_id=line_data.expense_account_id,
                quantity=line_data.quantity,
                unit_price=line_data.unit_price,
                tax_rate=line_data.tax_rate,
                tax_amount=line_tax,
                line_total=line_tot,
            )
            bill.lines.append(bl)

        bill.subtotal_amount = subtotal
        bill.tax_amount = tax_total
        bill.total_amount = subtotal + tax_total
        bill.amount_due = bill.total_amount

        await self.bill_repo.create(bill)
        await self.session.commit()
        return await self.bill_repo.get_by_id(bill.id, tenant_id, org_id)

    async def post_bill(
        self,
        bill_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Bill:
        """Post the vendor bill and create a balanced journal entry (Debit Expense, Credit AP)."""
        bill = await self.bill_repo.get_by_id(bill_id, tenant_id, org_id)
        if not bill:
            raise NotFoundException(f"Bill {bill_id} not found.")

        if bill.status != BillStatus.DRAFT:
            raise BadRequestException(f"Bill {bill.bill_number} is already {bill.status}.")

        ap_account_id = bill.ap_account_id
        if not ap_account_id:
            vendor = await self.vendor_repo.get_by_id(bill.vendor_id, tenant_id, org_id)
            if vendor and vendor.ap_account_id:
                ap_account_id = vendor.ap_account_id
            else:
                default_ap = await self.account_repo.get_by_code("2000", tenant_id, org_id)
                if default_ap:
                    ap_account_id = default_ap.id
                else:
                    raise BadRequestException("No AP Account configured for bill posting.")
            bill.ap_account_id = ap_account_id

        journal_lines: list[JournalLineCreate] = []

        # 1. Debit Expense for each line
        for line in bill.lines:
            journal_lines.append(
                JournalLineCreate(
                    account_id=line.expense_account_id,
                    debit=line.quantity * line.unit_price,
                    credit=Decimal("0.0000"),
                    currency=bill.currency,
                    partner_type=PartnerType.VENDOR,
                    partner_id=bill.vendor_id,
                    description=line.description,
                )
            )

        # 2. Debit Tax Receivable if tax exists
        if bill.tax_amount > 0:
            tax_acct = await self.account_repo.get_by_code("1400", tenant_id, org_id)
            tax_acct_id = bill.lines[0].expense_account_id if not tax_acct else tax_acct.id

            journal_lines.append(
                JournalLineCreate(
                    account_id=tax_acct_id,
                    debit=bill.tax_amount,
                    credit=Decimal("0.0000"),
                    currency=bill.currency,
                    partner_type=PartnerType.VENDOR,
                    partner_id=bill.vendor_id,
                    description=f"Input VAT/Tax - Bill {bill.bill_number}",
                )
            )

        # 3. Credit AP Account
        journal_lines.append(
            JournalLineCreate(
                account_id=ap_account_id,
                debit=Decimal("0.0000"),
                credit=bill.total_amount,
                currency=bill.currency,
                partner_type=PartnerType.VENDOR,
                partner_id=bill.vendor_id,
                description=f"AP - Bill {bill.bill_number}",
            )
        )

        # Create and Post Journal Entry
        je_data = JournalEntryCreate(
            entry_date=bill.bill_date,
            posting_date=bill.bill_date,
            entry_type="STANDARD",
            reference_type="BILL",
            reference_id=str(bill.id),
            currency=bill.currency,
            exchange_rate=bill.exchange_rate,
            notes=f"Auto-generated for Vendor Bill {bill.bill_number}",
            lines=journal_lines,
        )

        draft_je = await self.journal_service.create_draft_entry(je_data, tenant_id, org_id)
        posted_je = await self.journal_service.post_entry(
            draft_je.id, tenant_id, org_id, user_id=user_id
        )

        bill.status = BillStatus.POSTED
        bill.posted_journal_entry_id = posted_je.id
        await self.session.commit()

        return await self.bill_repo.get_by_id(bill.id, tenant_id, org_id)
