"""Quality Inspections ORM model."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class QualityInspection(Base):
    """Quality Control Inspection for production or incoming goods."""

    __tablename__ = "mfg_quality_inspections"

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
    inspection_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
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
    inspection_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="FINAL_ASSEMBLY"
    )  # RECEIVING, IN_PROCESS, FINAL_ASSEMBLY
    inspected_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    passed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    failed_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 4), nullable=False, server_default="0.0000"
    )
    result: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="PASSED"
    )  # PENDING, PASSED, FAILED, CONDITIONALLY_PASSED
    inspector_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    inspection_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    defect_reason: Mapped[str | None] = mapped_column(String(128), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
