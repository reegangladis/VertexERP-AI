"""Analytics Dashboards and Dashboard Widgets ORM models."""

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


class Dashboard(Base):
    """Configurable Analytics Dashboard."""

    __tablename__ = "analytics_dashboards"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "organization_id", "code", name="uq_analytics_dashboard_code"
        ),
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
    )  # EXECUTIVE, FINANCE, SALES, INVENTORY, MANUFACTURING, HR, CUSTOM
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    layout_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'")
    )
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    required_permission: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    widgets: Mapped[list["DashboardWidget"]] = relationship(
        "DashboardWidget",
        back_populates="dashboard",
        cascade="all, delete-orphan",
        order_by="DashboardWidget.sort_order",
        lazy="selectin",
    )


class DashboardWidget(Base):
    """Visual Analytics Widget attached to a Dashboard."""

    __tablename__ = "analytics_dashboard_widgets"

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
    dashboard_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analytics_dashboards.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(128), nullable=False)
    widget_type: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="METRIC_CARD"
    )  # METRIC_CARD, LINE_CHART, BAR_CHART, DONUT_CHART, AREA_CHART, DATA_TABLE, GAUGE
    kpi_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    data_source: Mapped[str] = mapped_column(String(64), nullable=False)
    query_config: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, server_default=text("'{}'")
    )
    grid_x: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    grid_y: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    grid_w: Mapped[int] = mapped_column(Integer, nullable=False, server_default="6")
    grid_h: Mapped[int] = mapped_column(Integer, nullable=False, server_default="4")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    dashboard: Mapped[Dashboard] = relationship("Dashboard", back_populates="widgets")
