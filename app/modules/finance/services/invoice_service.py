"""Sales Invoice (Accounts Receivable) Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.finance.models.invoice import Invoice, InvoiceLine, InvoiceStatus
from app.modules.finance.models.journal import PartnerType
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.repositories.invoice_repository import InvoiceRepository
from app.modules.finance.repositories.party_repository import CustomerPartyRepository
from app.modules.finance.schemas.invoice import InvoiceCreate
from app.modules.finance.schemas.journal import JournalEntryCreate, JournalLineCreate
from app.modules.finance.services.journal_service import JournalEntryService


class InvoiceService:
    """Service managing customer invoicing and AR journal posting."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.invoice_repo = InvoiceRepository(session)
        self.customer_repo = CustomerPartyRepository(session)
        self.account_repo = AccountRepository(session)
        self.journal_service = JournalEntryService(session)

    async def create_invoice(
        self,
        data: InvoiceCreate,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Invoice:
        """Create a draft invoice with calculated line items and taxes."""
        customer = await self.customer_repo.get_by_id(data.customer_id, tenant_id, org_id)
        if not customer:
            raise NotFoundException(f"Customer {data.customer_id} not found.")

        ar_account_id = data.ar_account_id or customer.ar_account_id
        if not ar_account_id:
            # Try to lookup default AR account
            ar_acct = await self.account_repo.get_by_code("1100", tenant_id, org_id)
            if ar_acct:
                ar_account_id = ar_acct.id
            else:
                raise BadRequestException("No AR Account specified for customer invoice.")

        subtotal = Decimal("0.0000")
        tax_total = Decimal("0.0000")

        invoice_number = (
            data.invoice_number
            or f"INV-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        )

        invoice = Invoice(
            tenant_id=tenant_id,
            organization_id=org_id,
            invoice_number=invoice_number,
            customer_id=data.customer_id,
            issue_date=data.issue_date,
            due_date=data.due_date,
            currency=data.currency,
            exchange_rate=data.exchange_rate,
            subtotal_amount=Decimal("0.0000"),
            tax_amount=Decimal("0.0000"),
            total_amount=Decimal("0.0000"),
            amount_paid=Decimal("0.0000"),
            amount_due=Decimal("0.0000"),
            status=InvoiceStatus.DRAFT,
            ar_account_id=ar_account_id,
            notes=data.notes,
        )

        for line_data in data.lines:
            acct = await self.account_repo.get_by_id(line_data.account_id, tenant_id, org_id)
            if not acct:
                raise NotFoundException(f"Account {line_data.account_id} not found.")

            line_base = line_data.quantity * line_data.unit_price
            line_tax = line_base * line_data.tax_rate
            line_tot = line_base + line_tax

            subtotal += line_base
            tax_total += line_tax

            il = InvoiceLine(
                tenant_id=tenant_id,
                invoice_id=invoice.id,
                product_id=line_data.product_id,
                description=line_data.description,
                account_id=line_data.account_id,
                quantity=line_data.quantity,
                unit_price=line_data.unit_price,
                tax_rate=line_data.tax_rate,
                tax_amount=line_tax,
                line_total=line_tot,
            )
            invoice.lines.append(il)

        invoice.subtotal_amount = subtotal
        invoice.tax_amount = tax_total
        invoice.total_amount = subtotal + tax_total
        invoice.amount_due = invoice.total_amount

        await self.invoice_repo.create(invoice)
        await self.session.commit()
        return await self.invoice_repo.get_by_id(invoice.id, tenant_id, org_id)

    async def post_invoice(
        self,
        invoice_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Invoice:
        """Post the invoice and create a balanced double-entry journal (Debit AR, Credit Revenue)."""
        inv = await self.invoice_repo.get_by_id(invoice_id, tenant_id, org_id)
        if not inv:
            raise NotFoundException(f"Invoice {invoice_id} not found.")

        if inv.status != InvoiceStatus.DRAFT:
            raise BadRequestException(f"Invoice {inv.invoice_number} is already {inv.status}.")

        ar_account_id = inv.ar_account_id
        if not ar_account_id:
            customer = await self.customer_repo.get_by_id(inv.customer_id, tenant_id, org_id)
            if customer and customer.ar_account_id:
                ar_account_id = customer.ar_account_id
            else:
                default_ar = await self.account_repo.get_by_code("1100", tenant_id, org_id)
                if default_ar:
                    ar_account_id = default_ar.id
                else:
                    raise BadRequestException("No AR Account configured for invoice posting.")
            inv.ar_account_id = ar_account_id

        journal_lines: list[JournalLineCreate] = []

        # 1. Debit AR Account
        journal_lines.append(
            JournalLineCreate(
                account_id=ar_account_id,
                debit=inv.total_amount,
                credit=Decimal("0.0000"),
                currency=inv.currency,
                partner_type=PartnerType.CUSTOMER,
                partner_id=inv.customer_id,
                description=f"AR - Invoice {inv.invoice_number}",
            )
        )

        # 2. Credit Revenue for each line
        for line in inv.lines:
            journal_lines.append(
                JournalLineCreate(
                    account_id=line.account_id,
                    debit=Decimal("0.0000"),
                    credit=line.quantity * line.unit_price,
                    currency=inv.currency,
                    partner_type=PartnerType.CUSTOMER,
                    partner_id=inv.customer_id,
                    description=line.description,
                )
            )

        # 3. Credit Tax Payable if tax exists
        if inv.tax_amount > 0:
            tax_acct = await self.account_repo.get_by_code("2200", tenant_id, org_id)
            tax_acct_id = tax_acct.id if tax_acct else inv.lines[0].account_id

            journal_lines.append(
                JournalLineCreate(
                    account_id=tax_acct_id,
                    debit=Decimal("0.0000"),
                    credit=inv.tax_amount,
                    currency=inv.currency,
                    partner_type=PartnerType.CUSTOMER,
                    partner_id=inv.customer_id,
                    description=f"Sales Tax - Invoice {inv.invoice_number}",
                )
            )

        # Create and Post Journal Entry
        je_data = JournalEntryCreate(
            entry_date=inv.issue_date,
            posting_date=inv.issue_date,
            entry_type="STANDARD",
            reference_type="INVOICE",
            reference_id=str(inv.id),
            currency=inv.currency,
            exchange_rate=inv.exchange_rate,
            notes=f"Auto-generated for Customer Invoice {inv.invoice_number}",
            lines=journal_lines,
        )

        draft_je = await self.journal_service.create_draft_entry(je_data, tenant_id, org_id)
        posted_je = await self.journal_service.post_entry(
            draft_je.id, tenant_id, org_id, user_id=user_id
        )

        inv.status = InvoiceStatus.POSTED
        inv.posted_journal_entry_id = posted_je.id
        await self.session.commit()

        return await self.invoice_repo.get_by_id(inv.id, tenant_id, org_id)
