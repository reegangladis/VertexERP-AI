"""Payment Processing and Allocation Service."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.modules.finance.models.bank import BankTransaction, BankTransactionType
from app.modules.finance.models.bill import BillStatus
from app.modules.finance.models.invoice import InvoiceStatus
from app.modules.finance.models.journal import PartnerType
from app.modules.finance.models.payment import (
    Payment,
    PaymentAllocation,
    PaymentStatus,
    PaymentType,
)
from app.modules.finance.repositories.account_repository import AccountRepository
from app.modules.finance.repositories.bank_repository import BankRepository
from app.modules.finance.repositories.bill_repository import BillRepository
from app.modules.finance.repositories.invoice_repository import InvoiceRepository
from app.modules.finance.repositories.party_repository import (
    CustomerPartyRepository,
    VendorPartyRepository,
)
from app.modules.finance.repositories.payment_repository import PaymentRepository
from app.modules.finance.schemas.journal import JournalEntryCreate, JournalLineCreate
from app.modules.finance.schemas.payment import PaymentCreate
from app.modules.finance.services.journal_service import JournalEntryService


class PaymentService:
    """Service managing customer receipts, vendor disbursements, and AR/AP allocations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.payment_repo = PaymentRepository(session)
        self.invoice_repo = InvoiceRepository(session)
        self.bill_repo = BillRepository(session)
        self.bank_repo = BankRepository(session)
        self.account_repo = AccountRepository(session)
        self.customer_repo = CustomerPartyRepository(session)
        self.vendor_repo = VendorPartyRepository(session)
        self.journal_service = JournalEntryService(session)

    async def create_payment(
        self,
        data: PaymentCreate,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
    ) -> Payment:
        """Create a draft payment with optional document allocations."""
        if data.amount <= 0:
            raise BadRequestException("Payment amount must be greater than zero.")

        total_alloc = Decimal("0.0000")
        for alloc in data.allocations:
            total_alloc += alloc.allocated_amount

        if total_alloc > data.amount:
            raise BadRequestException(
                f"Total allocated ({total_alloc}) exceeds payment amount ({data.amount})."
            )

        payment_number = (
            data.payment_number
            or f"PAY-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"
        )

        payment = Payment(
            tenant_id=tenant_id,
            organization_id=org_id,
            payment_number=payment_number,
            payment_type=data.payment_type,
            partner_type=data.partner_type,
            partner_id=data.partner_id,
            payment_date=data.payment_date,
            payment_method=data.payment_method,
            bank_account_id=data.bank_account_id,
            currency=data.currency,
            amount=data.amount,
            allocated_amount=total_alloc,
            unallocated_amount=data.amount - total_alloc,
            status=PaymentStatus.DRAFT,
            reference=data.reference,
            notes=data.notes,
        )

        for alloc in data.allocations:
            pa = PaymentAllocation(
                tenant_id=tenant_id,
                payment_id=payment.id,
                invoice_id=alloc.invoice_id,
                bill_id=alloc.bill_id,
                allocated_amount=alloc.allocated_amount,
            )
            payment.allocations.append(pa)

        await self.payment_repo.create(payment)
        await self.session.commit()
        return await self.payment_repo.get_by_id(payment.id, tenant_id, org_id)

    async def post_payment(
        self,
        payment_id: uuid.UUID,
        tenant_id: uuid.UUID,
        org_id: uuid.UUID,
        user_id: uuid.UUID | None = None,
    ) -> Payment:
        """Post payment, create double-entry journal, update bank balances and reconcile Invoices/Bills."""
        payment = await self.payment_repo.get_by_id(payment_id, tenant_id, org_id)
        if not payment:
            raise NotFoundException(f"Payment {payment_id} not found.")

        if payment.status != PaymentStatus.DRAFT:
            raise BadRequestException(
                f"Payment {payment.payment_number} is already {payment.status}."
            )

        # Lookup Bank Account & its GL Account
        bank_gl_id = None
        if payment.bank_account_id:
            bank_acc = await self.bank_repo.get_account_by_id(
                payment.bank_account_id, tenant_id, org_id
            )
            if bank_acc:
                bank_gl_id = bank_acc.gl_account_id
        if not bank_gl_id:
            # Fallback to default Cash/Bank asset account (1000)
            cash_acct = await self.account_repo.get_by_code("1000", tenant_id, org_id)
            if cash_acct:
                bank_gl_id = cash_acct.id
            else:
                raise BadRequestException("No Bank or Cash GL Account configured for payment.")

        journal_lines: list[JournalLineCreate] = []

        if payment.payment_type == PaymentType.RECEIPT:
            # Customer Payment (AR): Debit Bank/Cash, Credit AR Control Account
            customer = await self.customer_repo.get_by_id(payment.partner_id, tenant_id, org_id)
            ar_gl_id = (
                customer.ar_account_id
                if customer and customer.ar_account_id
                else ((await self.account_repo.get_by_code("1100", tenant_id, org_id)).id)
            )

            # 1. Debit Bank
            journal_lines.append(
                JournalLineCreate(
                    account_id=bank_gl_id,
                    debit=payment.amount,
                    credit=Decimal("0.0000"),
                    currency=payment.currency,
                    partner_type=PartnerType.CUSTOMER,
                    partner_id=payment.partner_id,
                    description=f"Receipt - {payment.payment_number}",
                )
            )
            # 2. Credit AR
            journal_lines.append(
                JournalLineCreate(
                    account_id=ar_gl_id,
                    debit=Decimal("0.0000"),
                    credit=payment.amount,
                    currency=payment.currency,
                    partner_type=PartnerType.CUSTOMER,
                    partner_id=payment.partner_id,
                    description=f"AR Settlement - {payment.payment_number}",
                )
            )

        elif payment.payment_type == PaymentType.DISBURSEMENT:
            # Vendor Payment (AP): Debit AP Control Account, Credit Bank/Cash
            vendor = await self.vendor_repo.get_by_id(payment.partner_id, tenant_id, org_id)
            ap_gl_id = (
                vendor.ap_account_id
                if vendor and vendor.ap_account_id
                else ((await self.account_repo.get_by_code("2000", tenant_id, org_id)).id)
            )

            # 1. Debit AP
            journal_lines.append(
                JournalLineCreate(
                    account_id=ap_gl_id,
                    debit=payment.amount,
                    credit=Decimal("0.0000"),
                    currency=payment.currency,
                    partner_type=PartnerType.VENDOR,
                    partner_id=payment.partner_id,
                    description=f"AP Settlement - {payment.payment_number}",
                )
            )
            # 2. Credit Bank
            journal_lines.append(
                JournalLineCreate(
                    account_id=bank_gl_id,
                    debit=Decimal("0.0000"),
                    credit=payment.amount,
                    currency=payment.currency,
                    partner_type=PartnerType.VENDOR,
                    partner_id=payment.partner_id,
                    description=f"Disbursement - {payment.payment_number}",
                )
            )

        # Create and Post Journal Entry
        je_data = JournalEntryCreate(
            entry_date=payment.payment_date,
            posting_date=payment.payment_date,
            entry_type="STANDARD",
            reference_type="PAYMENT",
            reference_id=str(payment.id),
            currency=payment.currency,
            exchange_rate=Decimal("1.000000"),
            notes=f"Auto-generated for Payment {payment.payment_number}",
            lines=journal_lines,
        )

        draft_je = await self.journal_service.create_draft_entry(je_data, tenant_id, org_id)
        posted_je = await self.journal_service.post_entry(
            draft_je.id, tenant_id, org_id, user_id=user_id
        )

        # Reconcile allocations
        for alloc in payment.allocations:
            if alloc.invoice_id:
                inv = await self.invoice_repo.get_by_id(alloc.invoice_id, tenant_id, org_id)
                if inv:
                    inv.amount_paid += alloc.allocated_amount
                    inv.amount_due = max(Decimal("0.0000"), inv.total_amount - inv.amount_paid)
                    if inv.amount_due == 0:
                        inv.status = InvoiceStatus.PAID
                    else:
                        inv.status = InvoiceStatus.PARTIALLY_PAID

            if alloc.bill_id:
                bill = await self.bill_repo.get_by_id(alloc.bill_id, tenant_id, org_id)
                if bill:
                    bill.amount_paid += alloc.allocated_amount
                    bill.amount_due = max(Decimal("0.0000"), bill.total_amount - bill.amount_paid)
                    if bill.amount_due == 0:
                        bill.status = BillStatus.PAID
                    else:
                        bill.status = BillStatus.PARTIALLY_PAID

        # Update Bank Account Balance and Transaction Log
        if payment.bank_account_id:
            bank_acc = await self.bank_repo.get_account_by_id(
                payment.bank_account_id, tenant_id, org_id
            )
            if bank_acc:
                if payment.payment_type == PaymentType.RECEIPT:
                    bank_acc.current_balance += payment.amount
                    tx_type = BankTransactionType.DEPOSIT
                else:
                    bank_acc.current_balance -= payment.amount
                    tx_type = BankTransactionType.WITHDRAWAL

                tx = BankTransaction(
                    tenant_id=tenant_id,
                    organization_id=org_id,
                    bank_account_id=bank_acc.id,
                    transaction_date=payment.payment_date,
                    value_date=payment.payment_date,
                    transaction_type=tx_type,
                    amount=payment.amount,
                    balance_after=bank_acc.current_balance,
                    reference=payment.payment_number,
                    description=payment.notes or f"Payment {payment.payment_number}",
                    is_reconciled=True,
                    journal_entry_id=posted_je.id,
                )
                await self.bank_repo.create_transaction(tx)

        payment.status = PaymentStatus.POSTED
        payment.posted_journal_entry_id = posted_je.id
        await self.session.commit()

        return await self.payment_repo.get_by_id(payment.id, tenant_id, org_id)
