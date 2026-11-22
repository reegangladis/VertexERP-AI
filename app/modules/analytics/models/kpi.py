"""Analytics KPI Definitions and Periodic Snapshots ORM models."""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class KPIDefinition(Base):
    """Enterprise KPI Definition and Metrics Catalog."""

    __tablename__ = "analytics_kpi_definitions"
    __table_args__ = (
        UniqueConstraint("tenant_id", "organization_id", "code", name="uq_analytics_kpi_code"),
    )

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
    code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="EXECUTIVE"
    )  # FINANCE, SALES, INVENTORY, MANUFACTURING, HR, EXECUTIVE
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    unit: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="COUNT"
    )  # CURRENCY, PERCENTAGE, COUNT, RATIO, DAYS, HOURS
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(16, 4), nullable=True)
    warning_threshold: Mapped[Decimal | None] = mapped_column(Numeric(16, 4), nullable=True)
    critical_threshold: Mapped[Decimal | None] = mapped_column(Numeric(16, 4), nullable=True)
    trend_direction: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="HIGHER_IS_BETTER"
    )  # HIGHER_IS_BETTER, LOWER_IS_BETTER
    calculation_method: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="REALTIME_SQL"
    )  # REALTIME_SQL, SNAPSHOT_ROLLUP
    required_permission: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    snapshots: Mapped[list["KPISnapshot"]] = relationship(
        "KPISnapshot", back_populates="kpi", lazy="selectin"
    )


class KPISnapshot(Base):
    """Pre-computed / Periodic Rollup Snapshot for KPI trend analysis without OLTP load."""

    __tablename__ = "analytics_kpi_snapshots"

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
    kpi_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics_kpi_definitions.id", ondelete="SET NULL"),
        nullable=True,
    )
    kpi_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    period_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="MONTHLY"
    )  # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dimension_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="OVERALL"
    )  # OVERALL, BRANCH, DEPARTMENT, WAREHOUSE, PRODUCT_CATEGORY
    dimension_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metric_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, server_default="0.0000"
    )
    target_value: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    variance_pct: Mapped[Decimal | None] = mapped_column(Numeric(8, 4), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="ON_TRACK"
    )  # ON_TRACK, WARNING, CRITICAL
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    kpi: Mapped[KPIDefinition | None] = relationship("KPIDefinition", back_populates="snapshots")
