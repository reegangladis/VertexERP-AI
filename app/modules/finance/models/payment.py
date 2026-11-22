"""Payments and Payment Allocations ORM Models."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class PaymentType(StrEnum):
    RECEIPT = "RECEIPT"  # Customer payment (AR)
    DISBURSEMENT = "DISBURSEMENT"  # Vendor payment (AP)


class PaymentMethod(StrEnum):
    BANK = "BANK"
    CASH = "CASH"
    WIRE = "WIRE"
    CHECK = "CHECK"
    CARD = "CARD"


class PaymentStatus(StrEnum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"


class Payment(Base):
    """Financial Payment record (Inflow or Outflow)."""

    __tablename__ = "fin_payments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payment_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    payment_type: Mapped[str] = mapped_column(String(32), nullable=False)  # RECEIPT, DISBURSEMENT
    partner_type: Mapped[str] = mapped_column(String(32), nullable=False)  # CUSTOMER, VENDOR
    partner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str] = mapped_column(
        String(32), default="BANK", server_default=text("'BANK'")
    )
    bank_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_bank_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    amount: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    allocated_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    unallocated_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", server_default=text("'DRAFT'"))
    posted_journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_entries.id", ondelete="SET NULL"),
        nullable=True,
    )
    reference: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.clock_timestamp(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.clock_timestamp(),
        onupdate=lambda: datetime.now(UTC),
    )

    bank_account: Mapped["BankAccount | None"] = relationship("BankAccount")
    posted_journal_entry: Mapped["JournalEntry | None"] = relationship("JournalEntry")
    allocations: Mapped[list["PaymentAllocation"]] = relationship(
        "PaymentAllocation", back_populates="payment", cascade="all, delete-orphan"
    )


class PaymentAllocation(Base):
    """Allocation of payment to specific Invoices (AR) or Bills (AP)."""

    __tablename__ = "fin_payment_allocations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_invoices.id", ondelete="CASCADE"),
        nullable=True,
    )
    bill_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_bills.id", ondelete="CASCADE"),
        nullable=True,
    )
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.clock_timestamp(),
    )

    payment: Mapped["Payment"] = relationship("Payment", back_populates="allocations")
    invoice: Mapped["Invoice | None"] = relationship("Invoice")
    bill: Mapped["Bill | None"] = relationship("Bill")
