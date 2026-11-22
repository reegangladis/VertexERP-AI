"""Production Orders, Work Orders, Consumptions, Outputs, and Scrap ORM models."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class ProductionOrder(Base):
    """Manufacturing / Production Order Header (MO)."""

    __tablename__ = "mfg_production_orders"

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
    order_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    bom_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_boms.id", ondelete="RESTRICT"),
        nullable=False,
    )
    bom_version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_bom_versions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    routing_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_routings.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_sales_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("crm_sales_orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    produced_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    rejected_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    scrap_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    target_warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_warehouses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_start_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    actual_end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="PLANNED", index=True
    )  # PLANNED, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED
    priority: Mapped[str] = mapped_column(String(16), nullable=False, server_default="MEDIUM")
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), nullable=False, server_default="0.0000"
    )
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    work_orders: Mapped[list["WorkOrder"]] = relationship(
        "WorkOrder",
        back_populates="production_order",
        order_by="WorkOrder.sequence",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    consumptions: Mapped[list["MaterialConsumption"]] = relationship(
        "MaterialConsumption",
        back_populates="production_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    outputs: Mapped[list["ProductionOutput"]] = relationship(
        "ProductionOutput",
        back_populates="production_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    scraps: Mapped[list["ProductionScrap"]] = relationship(
        "ProductionScrap",
        back_populates="production_order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class WorkOrder(Base):
    """Specific shop-floor operation on a Production Order."""

    __tablename__ = "mfg_work_orders"

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
    production_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_production_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    operation_name: Mapped[str] = mapped_column(String(128), nullable=False)
    work_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_work_centers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    machine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_machines.id", ondelete="SET NULL"),
        nullable=True,
    )
    planned_duration_hours: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="1.00"
    )
    actual_duration_hours: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="0.00"
    )
    technician_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="PENDING"
    )  # PENDING, IN_PROGRESS, PAUSED, COMPLETED, CANCELLED
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    hourly_rate: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, server_default="50.0000"
    )
    total_labor_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    production_order: Mapped["ProductionOrder"] = relationship(
        "ProductionOrder", back_populates="work_orders"
    )


class MaterialConsumption(Base):
    """Raw material issuance / deduction from inventory for production."""

    __tablename__ = "mfg_material_consumptions"

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
    production_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_production_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_work_orders.id", ondelete="SET NULL"),
        nullable=True,
    )
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
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    planned_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    consumed_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    total_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), nullable=False, server_default="0.0000"
    )
    stock_movement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_stock_movements.id", ondelete="SET NULL"),
        nullable=True,
    )
    batch_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    consumed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    consumed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    production_order: Mapped["ProductionOrder"] = relationship(
        "ProductionOrder", back_populates="consumptions"
    )


class ProductionOutput(Base):
    """Finished goods receipt into inventory from production."""

    __tablename__ = "mfg_production_outputs"

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
    production_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_production_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    target_warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_warehouses.id", ondelete="RESTRICT"),
        nullable=False,
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    produced_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    unit_manufacturing_cost: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    total_manufacturing_cost: Mapped[Decimal] = mapped_column(Numeric(16, 4), nullable=False)
    stock_movement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_stock_movements.id", ondelete="SET NULL"),
        nullable=True,
    )
    batch_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    output_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    production_order: Mapped["ProductionOrder"] = relationship(
        "ProductionOrder", back_populates="outputs"
    )


class ProductionScrap(Base):
    """Scrap / Waste generated during manufacturing."""

    __tablename__ = "mfg_production_scraps"

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
    production_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_production_orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    work_order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_work_orders.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    scrap_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    scrap_reason: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default="DEFECTIVE_RAW_MATERIAL"
    )
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    total_scrap_cost: Mapped[Decimal] = mapped_column(
        Numeric(16, 4), nullable=False, server_default="0.0000"
    )
    stock_movement_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("inv_stock_movements.id", ondelete="SET NULL"),
        nullable=True,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    recorded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    production_order: Mapped["ProductionOrder"] = relationship(
        "ProductionOrder", back_populates="scraps"
    )
