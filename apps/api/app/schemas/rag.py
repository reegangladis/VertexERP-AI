import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# Collection Schemas
class KnowledgeCollectionBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: str | None = None
    category: str = "general"
    tags: list[str] = Field(default_factory=list)
    is_public: bool = False
    metadata_json: dict[str, Any] | None = None


class KnowledgeCollectionCreate(KnowledgeCollectionBase):
    pass


class KnowledgeCollectionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    is_public: bool | None = None
    metadata_json: dict[str, Any] | None = None


class KnowledgeCollectionResponse(KnowledgeCollectionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    slug: str
    created_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


# Document & Version Schemas
class RAGDocumentBase(BaseModel):
    title: str = Field(..., max_length=255)
    collection_id: uuid.UUID | None = None
    document_type: str = (
        "policy"  # policy, manual, report, contract, procedure, guideline, specification
    )
    category: str = "general"
    tags: list[str] = Field(default_factory=list)
    language: str = "en"
    approval_status: str = "approved"  # pending, approved, rejected
    retention_days: int | None = None
    metadata_json: dict[str, Any] | None = None


class RAGDocumentCreate(RAGDocumentBase):
    file_name: str
    file_path: str
    file_size: int = 0
    mime_type: str = "text/plain"
    format: str = "txt"  # pdf, docx, txt, md, csv, html, json, ocr


class RAGDocumentUpdate(BaseModel):
    title: str | None = None
    collection_id: uuid.UUID | None = None
    document_type: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    status: str | None = None
    approval_status: str | None = None
    retention_days: int | None = None
    metadata_json: dict[str, Any] | None = None


class DocumentVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    version_number: int
    file_path: str
    file_size: int
    file_hash: str
    change_summary: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_by: uuid.UUID | None = None
    created_at: datetime


class RAGDocumentResponse(RAGDocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    file_name: str
    file_path: str
    file_size: int
    mime_type: str
    format: str
    current_version: int
    status: str
    created_by: uuid.UUID | None = None
    updated_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0


# Chunk & Embedding Schemas
class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_id: uuid.UUID
    version_id: uuid.UUID | None = None
    chunk_index: int
    content: str
    clean_content: str
    token_count: int
    word_count: int
    chunk_hash: str
    language: str
    metadata_json: dict[str, Any] | None = None
    created_at: datetime


class EmbeddingMetadataResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    chunk_id: uuid.UUID
    provider: str
    model_name: str
    vector_id: str
    dimension: int
    status: str
    created_at: datetime


# Search & Retrieval Schemas
class RetrievalRequest(BaseModel):
    query: str
    collection_ids: list[uuid.UUID] | None = None
    categories: list[str] | None = None
    document_types: list[str] | None = None
    tags: list[str] | None = None
    top_k: int = 5
    search_type: str = "hybrid"  # semantic, hybrid, metadata
    provider: str = "openai"  # openai, gemini, azure_openai, anthropic, local
    min_score: float = 0.0


class RetrievalChunkResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    document_title: str
    document_type: str
    category: str
    content: str
    score: float
    chunk_index: int
    metadata: dict[str, Any] | None = None


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalChunkResult]
    total_found: int
    execution_time_ms: float
    search_type: str


# RAG Chat Schemas
class RAGChatSessionCreate(BaseModel):
    title: str = "New Conversation"
    context_metadata: dict[str, Any] | None = None


class RAGChatSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    is_pinned: bool
    context_metadata: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime


class CitationSource(BaseModel):
    document_id: uuid.UUID
    document_title: str
    chunk_id: uuid.UUID
    chunk_index: int
    snippet: str
    score: float


class PromptChatRequest(BaseModel):
    session_id: uuid.UUID | None = None
    query: str
    collection_ids: list[uuid.UUID] | None = None
    provider: str = "openai"  # openai, gemini, azure_openai, anthropic, local
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    top_k: int = 5
    search_type: str = "hybrid"


class RAGChatMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    prompt_tokens: int
    completion_tokens: int
    citations: list[CitationSource] | None = None
    feedback_rating: int | None = None
    feedback_text: str | None = None
    created_at: datetime


class ChatPromptResponse(BaseModel):
    session_id: uuid.UUID
    user_message: RAGChatMessageResponse
    assistant_message: RAGChatMessageResponse


# Feedback Schema
class FeedbackCreate(BaseModel):
    chat_message_id: uuid.UUID | None = None
    chunk_id: uuid.UUID | None = None
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str = "accuracy"  # accuracy, relevance, clarity, safety
    comments: str | None = None
    metadata_json: dict[str, Any] | None = None


class FeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    chat_message_id: uuid.UUID | None = None
    chunk_id: uuid.UUID | None = None
    rating: int
    feedback_type: str
    comments: str | None = None
    created_at: datetime
