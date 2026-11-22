"""Journal Entries, Journal Lines, and General Ledger ORM Models."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class EntryType(StrEnum):
    STANDARD = "STANDARD"
    ADJUSTING = "ADJUSTING"
    CLOSING = "CLOSING"
    REVERSAL = "REVERSAL"


class EntryStatus(StrEnum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    REVERSED = "REVERSED"
    CANCELLED = "CANCELLED"


class PartnerType(StrEnum):
    CUSTOMER = "CUSTOMER"
    VENDOR = "VENDOR"
    EMPLOYEE = "EMPLOYEE"
    NONE = "NONE"


class JournalEntry(Base):
    """High-integrity double-entry journal header."""

    __tablename__ = "fin_journal_entries"

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
    entry_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    posting_date: Mapped[date] = mapped_column(Date, nullable=False)
    fiscal_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_fiscal_periods.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    entry_type: Mapped[str] = mapped_column(
        String(32), default="STANDARD", server_default=text("'STANDARD'")
    )
    status: Mapped[str] = mapped_column(String(32), default="DRAFT", server_default=text("'DRAFT'"))
    reference_type: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )  # INVOICE, BILL, PAYMENT, BANK, MANUAL
    reference_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    exchange_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 6), default=Decimal("1.000000"), server_default=text("1.000000")
    )
    total_debit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    total_credit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    posted_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reversed_by_entry_id: Mapped[uuid.UUID | None] = mapped_column(
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

    lines: Mapped[list["JournalLine"]] = relationship(
        "JournalLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
        order_by="JournalLine.line_number",
    )
    fiscal_period: Mapped["FiscalPeriod | None"] = relationship("FiscalPeriod")


class JournalLine(Base):
    """Debit / Credit Line in a Journal Entry."""

    __tablename__ = "fin_journal_lines"

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
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    line_number: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    debit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    credit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    currency_debit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    currency_credit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    partner_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # CUSTOMER, VENDOR, EMPLOYEE
    partner_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cost_center_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cost_centers.id", ondelete="SET NULL"),
        nullable=True,
    )
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

    __table_args__ = (
        CheckConstraint("debit >= 0", name="chk_fin_journal_lines_debit_positive"),
        CheckConstraint("credit >= 0", name="chk_fin_journal_lines_credit_positive"),
    )

    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry", back_populates="lines")
    account: Mapped["Account"] = relationship("Account")


class GeneralLedger(Base):
    """Immutable General Ledger transaction record posted from Journal Lines."""

    __tablename__ = "fin_general_ledger"

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
    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounts.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    journal_entry_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_entries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    journal_line_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_journal_lines.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    posting_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    fiscal_period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_fiscal_periods.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    debit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    credit: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    balance_after: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), default=Decimal("0.0000"), server_default=text("0.0000")
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.clock_timestamp(),
    )

    account: Mapped["Account"] = relationship("Account")
    journal_entry: Mapped["JournalEntry"] = relationship("JournalEntry")
