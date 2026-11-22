"""Material Requirements Planning (MRP) ORM models."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class MRPRun(Base):
    """Execution instance of an MRP calculation run."""

    __tablename__ = "mfg_mrp_runs"

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
    run_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    planning_horizon_days: Mapped[int] = mapped_column(Integer, nullable=False, server_default="30")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="COMPLETED"
    )  # RUNNING, COMPLETED, FAILED
    run_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    total_items_planned: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    total_purchase_requests_generated: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    total_production_orders_generated: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    execution_log: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    planned_orders: Mapped[list["MRPPlannedOrder"]] = relationship(
        "MRPPlannedOrder",
        back_populates="mrp_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class MRPPlannedOrder(Base):
    """Calculated planned order recommendation from an MRP run."""

    __tablename__ = "mfg_mrp_planned_orders"

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
    mrp_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_mrp_runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    order_type: Mapped[str] = mapped_column(String(32), nullable=False)  # MANUFACTURE, PURCHASE
    gross_requirement: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    on_hand_stock: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    scheduled_receipts: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    net_requirement: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    required_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="PLANNED"
    )  # PLANNED, CONVERTED, IGNORED
    converted_doc_type: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )  # PRODUCTION_ORDER, PURCHASE_REQUEST
    converted_doc_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    mrp_run: Mapped["MRPRun"] = relationship("MRPRun", back_populates="planned_orders")
