"""Stock Movement (Immutable Double-Entry / Audit Ledger) ORM model."""

import uuid
from datetime import UTC, date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class StockMovement(Base):
    """Immutable Stock Movement Ledger Entry.

    Every single inventory mutation in the system creates an immutable ledger row here.
    """

    __tablename__ = "inv_stock_movements"

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
    movement_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    movement_type: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )  # PURCHASE_RECEIPT, GOODS_ISSUE, TRANSFER_IN, TRANSFER_OUT, ADJUSTMENT_IN, ADJUSTMENT_OUT, RETURN_IN, RETURN_OUT, SCRAP, CYCLE_COUNT
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_locations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    batch_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    serial_number: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False
    )  # Signed: positive for inflow, negative for outflow
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, default=Decimal("0.0000"), server_default=text("0.0000")
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00"), server_default=text("0.00")
    )
    reference_doc_type: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )  # PURCHASE_ORDER, GOODS_RECEIPT, SALES_ORDER, STOCK_TRANSFER, STOCK_ADJUSTMENT
    reference_doc_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    reference_doc_line_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    running_balance_qty: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, default=Decimal("0.0000"), server_default=text("0.0000")
    )
    running_balance_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, default=Decimal("0.0000"), server_default=text("0.0000")
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.clock_timestamp(),
        index=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
