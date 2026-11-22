"""Tenant ORM model."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import BigInteger, Boolean, DateTime, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class Tenant(Base):
    """Global Root Tenant container."""

    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    subscription_tier: Mapped[str] = mapped_column(
        String(32), default="STANDARD", server_default=text("'STANDARD'")
    )
    subscription_status: Mapped[str] = mapped_column(
        String(32), default="ACTIVE", server_default=text("'ACTIVE'")
    )
    ai_monthly_token_quota: Mapped[int] = mapped_column(
        BigInteger, default=5000000, server_default=text("5000000")
    )
    storage_quota_bytes: Mapped[int] = mapped_column(
        BigInteger, default=107374182400, server_default=text("107374182400")
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"))
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
