"""Analytics Reports and Execution Logs ORM models."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class AnalyticsReport(Base):
    """Analytics and Deep-Dive Report Definition."""

    __tablename__ = "analytics_reports"
    __table_args__ = (
        UniqueConstraint("tenant_id", "organization_id", "code", name="uq_analytics_report_code"),
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
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    report_type: Mapped[str] = mapped_column(
        String(64), nullable=False, server_default="EXECUTIVE_SUMMARY"
    )  # EXECUTIVE_SUMMARY, FINANCIAL_PERFORMANCE, SALES_COHORT, INVENTORY_AGING, MANUFACTURING_EFFICIENCY, HR_PAYROLL_METRICS
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parameters_schema: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'")
    )
    required_permission: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    executions: Mapped[list["ReportExecution"]] = relationship(
        "ReportExecution",
        back_populates="report",
        cascade="all, delete-orphan",
        order_by="desc(ReportExecution.created_at)",
        lazy="selectin",
    )


class ReportExecution(Base):
    """Audit Log and Cache for Report Executions."""

    __tablename__ = "analytics_report_executions"

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
    report_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics_reports.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    executed_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    execution_time_ms: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    parameters: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'")
    )
    result_summary: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'")
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="COMPLETED")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    report: Mapped[AnalyticsReport] = relationship("AnalyticsReport", back_populates="executions")
