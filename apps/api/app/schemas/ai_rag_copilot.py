import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


# --- Knowledge Base Schemas ---
class KnowledgeCollectionBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    visibility: str = Field(default="Internal", max_length=50)
    status: str = Field(default="Active", max_length=50)


class KnowledgeCollectionCreate(KnowledgeCollectionBase):
    organization_id: uuid.UUID


class KnowledgeCollectionResponse(KnowledgeCollectionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RAGDocumentBase(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255)
    file_type: str = Field(..., min_length=1, max_length=50)  # pdf, docx, txt, xlsx
    file_size: int = Field(default=0, ge=0)
    status: str = Field(default="Processed", max_length=50)


class RAGDocumentCreate(RAGDocumentBase):
    collection_id: uuid.UUID
    document_content: str = Field(..., min_length=1)  # document text to ingest


class RAGDocumentResponse(RAGDocumentBase):
    id: uuid.UUID
    collection_id: uuid.UUID
    uploaded_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Copilot Chat Schemas ---
class RAGChatMessageBase(BaseModel):
    role: str = Field(..., max_length=50)  # user, assistant, system
    message: str = Field(..., min_length=1)


class RAGChatMessageCreate(RAGChatMessageBase):
    session_id: uuid.UUID


class RAGChatMessageResponse(RAGChatMessageBase):
    id: uuid.UUID
    session_id: uuid.UUID
    tokens: int
    latency: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RAGChatSessionBase(BaseModel):
    session_name: str = Field(..., min_length=1, max_length=255)
    model_name: str = Field(default="gpt-4o", max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    status: str = Field(default="Active", max_length=50)


class RAGChatSessionCreate(RAGChatSessionBase):
    organization_id: uuid.UUID
    user_id: uuid.UUID | None = None


class RAGChatSessionResponse(RAGChatSessionBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    messages: list[RAGChatMessageResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Prompt Engineering Schemas ---
class PromptTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(default="General", max_length=100)
    description: str | None = Field(None, max_length=1000)
    system_prompt: str = Field(..., min_length=1)
    status: str = Field(default="Active", max_length=50)


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateResponse(PromptTemplateBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- AI Agents & Tool Calling Schemas ---
class ToolRegistryBase(BaseModel):
    tool_name: str = Field(..., min_length=1, max_length=100)
    tool_description: str = Field(..., min_length=1, max_length=1000)
    tool_type: str = Field(default="API", max_length=50)
    endpoint: str | None = Field(None, max_length=500)
    enabled: bool = Field(default=True)


class ToolRegistryCreate(ToolRegistryBase):
    pass


class ToolRegistryResponse(ToolRegistryBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AIAgentBase(BaseModel):
    agent_name: str = Field(..., min_length=1, max_length=255)
    agent_type: str = Field(default="Conversational", max_length=100)
    system_prompt: str = Field(..., min_length=1)
    model: str = Field(default="gpt-4o", max_length=100)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    status: str = Field(default="Active", max_length=50)


class AIAgentCreate(AIAgentBase):
    organization_id: uuid.UUID


class AIAgentResponse(AIAgentBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentRunCreate(BaseModel):
    agent_id: uuid.UUID
    input_text: str = Field(..., min_length=1)


class AgentRunResponse(BaseModel):
    id: uuid.UUID
    agent_id: uuid.UUID
    input_text: str
    output_text: str
    execution_time: float
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- AI Dashboard Summary Schema ---
class AIDashboardSummary(BaseModel):
    total_documents: int
    total_embeddings: int
    total_collections: int
    active_chat_sessions: int
    total_agent_runs: int
    average_response_time_sec: float
    total_prompt_templates: int
    total_token_usage: int
