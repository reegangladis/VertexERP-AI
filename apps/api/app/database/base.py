import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""

    pass


class UUIDMixin:
    """Mixin that adds a UUID4 primary key to the model."""

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """Mixin that adds created_at and updated_at UTC timestamps to the model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class SoftDeleteMixin:
    """Mixin that adds soft delete support to the model."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    def soft_delete(self) -> None:
        """Flags the record as deleted and sets the deletion timestamp."""
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        """Restores a soft-deleted record."""
        self.is_deleted = False
        self.deleted_at = None


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """Abstract base model incorporating UUID and timestamp tracking."""

    __abstract__ = True
