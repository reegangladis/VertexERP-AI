"""RAG Knowledge Base and Document ORM models."""

import uuid
from datetime import UTC, datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class RAGDocument(Base):
    """Knowledge Base Document master entity."""

    __tablename__ = "rag_documents"

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
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="text", server_default=text("'text'")
    )
    file_size_bytes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    access_level: Mapped[str] = mapped_column(
        String(32), nullable=False, default="INTERNAL", server_default=text("'INTERNAL'")
    )
    allowed_departments: Mapped[Any] = mapped_column(
        JSONB, nullable=False, default=lambda: ["*"], server_default=text("'[\"*\"]'")
    )
    allowed_roles: Mapped[Any] = mapped_column(
        JSONB, nullable=False, default=lambda: ["*"], server_default=text("'[\"*\"]'")
    )
    tags: Mapped[Any] = mapped_column(
        JSONB, nullable=False, default=list, server_default=text("'[]'")
    )
    metadata_json: Mapped[Any] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'")
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    # Relationships
    versions: Mapped[list["RAGDocumentVersion"]] = relationship(
        "RAGDocumentVersion",
        back_populates="document",
        cascade="all, delete-orphan",
        order_by="RAGDocumentVersion.version_number.desc()",
    )
    chunks: Mapped[list["RAGDocumentChunk"]] = relationship(
        "RAGDocumentChunk",
        back_populates="document",
        cascade="all, delete-orphan",
    )
    jobs: Mapped[list["RAGIngestionJob"]] = relationship(
        "RAGIngestionJob",
        back_populates="document",
        cascade="all, delete-orphan",
    )


class RAGDocumentVersion(Base):
    """Document Version tracking content revisions."""

    __tablename__ = "rag_document_versions"

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
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_number: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1")
    )
    changelog: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    cleaned_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    # Relationships
    document: Mapped["RAGDocument"] = relationship("RAGDocument", back_populates="versions")
    chunks: Mapped[list["RAGDocumentChunk"]] = relationship(
        "RAGDocumentChunk",
        back_populates="version",
        cascade="all, delete-orphan",
        order_by="RAGDocumentChunk.chunk_index.asc()",
    )
    jobs: Mapped[list["RAGIngestionJob"]] = relationship(
        "RAGIngestionJob",
        back_populates="version",
        cascade="all, delete-orphan",
    )


class RAGDocumentChunk(Base):
    """Indexed chunk of text with vector embeddings and structural metadata."""

    __tablename__ = "rag_document_chunks"

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
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    char_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    section_heading: Mapped[str | None] = mapped_column(String(255), nullable=True)
    embedding: Mapped[Any] = mapped_column(Vector(1536), nullable=True)
    embedding_json: Mapped[Any] = mapped_column(JSONB, nullable=True)
    metadata_json: Mapped[Any] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )

    # Relationships
    document: Mapped["RAGDocument"] = relationship("RAGDocument", back_populates="chunks")
    version: Mapped["RAGDocumentVersion"] = relationship(
        "RAGDocumentVersion", back_populates="chunks"
    )


class RAGIngestionJob(Base):
    """Asynchronous ingestion pipeline job tracking."""

    __tablename__ = "rag_ingestion_jobs"

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
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_document_versions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="PENDING", server_default=text("'PENDING'")
    )  # PENDING, PROCESSING, COMPLETED, FAILED
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    max_retries: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default=text("3")
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    dead_letter: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    dead_letter_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[Any] = mapped_column(
        JSONB, nullable=False, default=dict, server_default=text("'{}'")
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    document: Mapped["RAGDocument"] = relationship("RAGDocument", back_populates="jobs")
    version: Mapped["RAGDocumentVersion"] = relationship(
        "RAGDocumentVersion", back_populates="jobs"
    )
