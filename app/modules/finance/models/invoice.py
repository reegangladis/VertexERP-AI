"""Sales Invoices (Accounts Receivable) ORM Models."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class InvoiceStatus(StrEnum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    PARTIALLY_PAID = "PARTIALLY_PAID"
    PAID = "PAID"
    CANCELLED = "CANCELLED"


class Invoice(Base):
    """Accounts Receivable Customer Invoice."""

    __tablename__ = "fin_invoices"

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
    invoice_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 6), default=Decimal("1.000000"), server_default=text("1.000000")
    )
    subtotal_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    amount_due: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", server_default=text("'DRAFT'"))
    ar_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounts.id", ondelete="RESTRICT"),
        nullable=True,
    )
    posted_journal_entry_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_entries.id", ondelete="SET NULL"),
        nullable=True,
    )
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

    customer: Mapped["CustomerParty"] = relationship("CustomerParty")
    ar_account: Mapped["Account | None"] = relationship("Account")
    posted_journal_entry: Mapped["JournalEntry | None"] = relationship("JournalEntry")
    lines: Mapped[list["InvoiceLine"]] = relationship(
        "InvoiceLine", back_populates="invoice", cascade="all, delete-orphan"
    )


class InvoiceLine(Base):
    """Line item in a customer invoice."""

    __tablename__ = "fin_invoice_lines"

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
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_products.id", ondelete="SET NULL"),
        nullable=True,
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounts.id", ondelete="RESTRICT"),
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), default=Decimal("1.0000"), server_default=text("1.0000")
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    tax_rate: Mapped[Decimal] = mapped_column(
        Numeric(6, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    tax_amount: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    line_total: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.clock_timestamp(),
    )

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="lines")
    account: Mapped["Account"] = relationship("Account")
