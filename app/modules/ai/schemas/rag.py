"""Pydantic schemas for RAG knowledge domain."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class RAGAccessLevel(StrEnum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"


class RAGJobStatus(StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ------------------------------------------------------------------------------
# Document Schemas
# ------------------------------------------------------------------------------
class RAGDocumentCreate(BaseModel):
    """Schema for uploading/creating a new knowledge document."""

    title: str = Field(..., min_length=1, max_length=255, description="Document title")
    description: str | None = Field(None, description="Optional document summary/description")
    raw_content: str = Field(..., min_length=1, description="Raw text, markdown, json, or csv body")
    file_type: str = Field("text", description="File format: text, markdown, json, csv, pdf, docx")
    access_level: RAGAccessLevel = Field(
        RAGAccessLevel.INTERNAL, description="Security classification level"
    )
    allowed_departments: list[str] = Field(
        default_factory=lambda: ["*"], description="List of allowed department codes or ['*']"
    )
    allowed_roles: list[str] = Field(
        default_factory=lambda: ["*"], description="List of allowed system roles or ['*']"
    )
    tags: list[str] = Field(default_factory=list, description="Categorization tags")
    metadata_json: dict[str, Any] = Field(
        default_factory=dict, description="Custom metadata attributes"
    )


class RAGDocumentUpdate(BaseModel):
    """Schema for updating document metadata."""

    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    access_level: RAGAccessLevel | None = None
    allowed_departments: list[str] | None = None
    allowed_roles: list[str] | None = None
    tags: list[str] | None = None
    metadata_json: dict[str, Any] | None = None
    is_active: bool | None = None


class RAGDocumentVersionCreate(BaseModel):
    """Schema for uploading a new version of an existing document."""

    raw_content: str = Field(..., min_length=1, description="Updated raw text or markdown body")
    changelog: str | None = Field(None, description="Summary of changes in this version")


class RAGDocumentVersionRead(BaseModel):
    """Schema for reading document version metadata."""

    id: UUID
    document_id: UUID
    version_number: int
    changelog: str | None = None
    checksum: str
    is_active: bool
    created_at: datetime


class RAGDocumentChunkRead(BaseModel):
    """Schema for reading chunk items."""

    id: UUID
    document_id: UUID
    version_id: UUID
    chunk_index: int
    content: str
    token_count: int
    char_count: int
    section_heading: str | None = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class RAGDocumentRead(BaseModel):
    """Schema for reading document summary."""

    id: UUID
    tenant_id: UUID
    organization_id: UUID
    title: str
    description: str | None = None
    file_type: str
    file_size_bytes: int
    access_level: str
    allowed_departments: list[str]
    allowed_roles: list[str]
    tags: list[str]
    metadata_json: dict[str, Any]
    is_active: bool
    active_version: int | None = 1
    total_chunks: int | None = 0
    latest_job_status: str | None = None
    created_at: datetime
    updated_at: datetime


class RAGDocumentDetailRead(RAGDocumentRead):
    """Detailed document response including versions and chunks."""

    versions: list[RAGDocumentVersionRead] = Field(default_factory=list)
    recent_chunks: list[RAGDocumentChunkRead] = Field(default_factory=list)


# ------------------------------------------------------------------------------
# Ingestion Job Schemas
# ------------------------------------------------------------------------------
class RAGIngestionJobRead(BaseModel):
    """Schema for reading asynchronous ingestion job state."""

    id: UUID
    tenant_id: UUID
    organization_id: UUID
    document_id: UUID
    version_id: UUID
    status: str
    retry_count: int
    max_retries: int
    error_message: str | None = None
    dead_letter: bool
    dead_letter_reason: str | None = None
    metrics_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None = None


class RAGJobRetryRequest(BaseModel):
    """Request to retry a failed or dead-letter ingestion job."""

    force_reset: bool = Field(True, description="Reset retry counter to 0")


# ------------------------------------------------------------------------------
# Retrieval & Search Schemas
# ------------------------------------------------------------------------------
class RAGSearchRequest(BaseModel):
    """Request for vector and hybrid document chunk search."""

    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(5, ge=1, le=50, description="Maximum number of chunks to return")
    access_level_filter: RAGAccessLevel | None = None
    tags_filter: list[str] | None = None
    min_score: float = Field(0.0, ge=0.0, le=1.0, description="Minimum relevance threshold score")


class RAGSearchResultItem(BaseModel):
    """Ranked chunk result with scoring breakdown."""

    chunk_id: UUID
    document_id: UUID
    document_title: str
    version_number: int
    chunk_index: int
    content: str
    section_heading: str | None = None
    vector_score: float
    lexical_score: float
    composite_score: float
    metadata: dict[str, Any] = Field(default_factory=dict)


class RAGSearchResponse(BaseModel):
    """Response containing ranked search results."""

    query: str
    total_results: int
    results: list[RAGSearchResultItem]
    latency_ms: float


# ------------------------------------------------------------------------------
# Generation & Citation Schemas
# ------------------------------------------------------------------------------
class RAGQueryRequest(BaseModel):
    """Request for end-to-end grounded RAG generation."""

    query: str = Field(..., min_length=1, description="User question to answer using RAG context")
    top_k: int = Field(5, ge=1, le=20, description="Number of context chunks to retrieve")
    provider: str | None = None
    model: str | None = None
    temperature: float = Field(0.2, ge=0.0, le=1.0)
    include_chunks: bool = Field(
        True, description="Whether to include retrieved chunk details in response"
    )


class RAGQueryCitation(BaseModel):
    """Structured in-line citation reference."""

    document_id: UUID
    document_title: str
    version_number: int
    chunk_index: int
    section_heading: str | None = None
    snippet: str
    relevance_score: float


class RAGQueryResponse(BaseModel):
    """Response containing grounded answer and verified citations."""

    query: str
    answer: str
    citations: list[RAGQueryCitation]
    retrieved_chunks_count: int
    provider_used: str
    model_used: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float
