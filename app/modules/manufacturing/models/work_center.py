"""Manufacturing Work Centers and Machines ORM models."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class WorkCenter(Base):
    """Manufacturing Work Center / Production Station."""

    __tablename__ = "mfg_work_centers"

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
    work_center_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="MACHINING"
    )
    capacity_per_day_hours: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, server_default="8.00"
    )
    cost_per_hour: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, server_default="50.0000"
    )
    overhead_cost_per_hour: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, server_default="20.0000"
    )
    location_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locations.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="ACTIVE")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    machines: Mapped[list["Machine"]] = relationship(
        "Machine", back_populates="work_center", cascade="all, delete-orphan", lazy="selectin"
    )


class Machine(Base):
    """Machine / Equipment inside a Work Center."""

    __tablename__ = "mfg_machines"

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
    work_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("mfg_work_centers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    serial_number: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hourly_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, server_default="30.0000"
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="OPERATIONAL")
    last_maintenance_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_maintenance_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    work_center: Mapped["WorkCenter"] = relationship("WorkCenter", back_populates="machines")
