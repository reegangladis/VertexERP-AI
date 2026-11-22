"""Product / Item Master ORM model."""

import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class Product(Base):
    """Product / SKU Master item."""

    __tablename__ = "inv_products"

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
    sku: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    uom_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_units_of_measure.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    valuation_method: Mapped[str] = mapped_column(
        String(32), nullable=False, default="AVERAGE_COST", server_default=text("'AVERAGE_COST'")
    )  # FIFO, LIFO, AVERAGE_COST, STANDARD_COST
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00"), server_default=text("0.00")
    )
    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False, default=Decimal("0.00"), server_default=text("0.00")
    )
    reorder_point: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=Decimal("0.0000"), server_default=text("0.0000")
    )
    reorder_quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=Decimal("0.0000"), server_default=text("0.0000")
    )
    safety_stock: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=Decimal("0.0000"), server_default=text("0.0000")
    )
    min_order_qty: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=Decimal("1.0000"), server_default=text("1.0000")
    )
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7, server_default=text("7"))
    is_stockable: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    is_purchasable: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    is_sellable: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
    allow_negative_stock: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    custom_fields: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'")
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
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
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"))
