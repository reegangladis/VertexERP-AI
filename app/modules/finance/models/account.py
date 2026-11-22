"""Chart of Accounts ORM Models."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class AccountType(StrEnum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    REVENUE = "REVENUE"
    EXPENSE = "EXPENSE"


class AccountCategory(StrEnum):
    CURRENT_ASSET = "CURRENT_ASSET"
    NON_CURRENT_ASSET = "NON_CURRENT_ASSET"
    CURRENT_LIABILITY = "CURRENT_LIABILITY"
    NON_CURRENT_LIABILITY = "NON_CURRENT_LIABILITY"
    EQUITY = "EQUITY"
    OPERATING_REVENUE = "OPERATING_REVENUE"
    NON_OPERATING_REVENUE = "NON_OPERATING_REVENUE"
    OPERATING_EXPENSE = "OPERATING_EXPENSE"
    COST_OF_GOODS_SOLD = "COST_OF_GOODS_SOLD"
    TAX_EXPENSE = "TAX_EXPENSE"


class Account(Base):
    """Chart of Accounts ledger account."""

    __tablename__ = "fin_accounts"

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
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    account_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    account_category: Mapped[str] = mapped_column(
        String(64), nullable=False, default="CURRENT_ASSET"
    )
    parent_account_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("fin_accounts.id", ondelete="SET NULL"),
        nullable=True,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    is_reconciled: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
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

    parent_account: Mapped["Account | None"] = relationship(
        "Account", remote_side=[id], backref="child_accounts"
    )
