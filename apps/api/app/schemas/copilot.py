import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# --- Session Schemas ---
class CopilotSessionBase(BaseModel):
    title: str = Field(default="New Copilot Session", max_length=255)
    is_pinned: bool = False
    current_state: dict[str, Any] | None = None


class CopilotSessionCreate(BaseModel):
    title: str | None = Field(default="New Copilot Session", max_length=255)
    is_pinned: bool | None = False
    current_state: dict[str, Any] | None = None


class CopilotSessionUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    is_pinned: bool | None = None
    current_state: dict[str, Any] | None = None


class CopilotSessionResponse(CopilotSessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Message Schemas ---
class CopilotMessageBase(BaseModel):
    role: str = Field(..., description="system, user, assistant, or tool")
    content: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: int = 0
    tool_calls: list[dict[str, Any]] | None = None
    citations: list[dict[str, Any]] | None = None
    generated_from: str | None = None


class CopilotMessageCreate(BaseModel):
    role: str = Field("user", description="user or system or tool")
    content: str
    provider: str | None = None
    model_name: str | None = None
    temperature: float | None = None
    department: str | None = (
        None  # hr, crm, finance, inventory, manufacturing, executive, etc.
    )


class CopilotMessageResponse(CopilotMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime


# --- Chat Request/Response Schemas ---
class ChatRequest(BaseModel):
    content: str
    provider: str | None = "openai"
    model_name: str | None = "gpt-4o"
    temperature: float | None = 0.7
    department: str | None = (
        None  # hr, crm, etc. to load system/department prompt template
    )


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    user_message: CopilotMessageResponse
    assistant_message: CopilotMessageResponse


# --- Prompt Schemas ---
class CopilotPromptBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: str = Field("system", description="system, department, generic")
    department: str | None = Field(None, max_length=100)
    template: str
    variables: list[str] | None = Field(default_factory=list)
    version: str = Field("1.0.0", max_length=50)
    is_active: bool = True


class CopilotPromptCreate(CopilotPromptBase):
    pass


class CopilotPromptUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    type: str | None = None
    department: str | None = None
    template: str | None = None
    variables: list[str] | None = None
    version: str | None = None
    is_active: bool | None = None


class CopilotPromptResponse(CopilotPromptBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    created_by: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime


class PromptTestRequest(BaseModel):
    template: str
    variables: dict[str, Any]


class PromptTestResponse(BaseModel):
    rendered: str


# --- Tool Registry Schemas ---
class ToolRegistryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str
    parameters_schema: dict[str, Any]
    is_active: bool = True
    required_role: str | None = Field(None, max_length=100)


class ToolRegistryCreate(ToolRegistryBase):
    pass


class ToolRegistryUpdate(BaseModel):
    description: str | None = None
    parameters_schema: dict[str, Any] | None = None
    is_active: bool | None = None
    required_role: str | None = None


class ToolRegistryResponse(ToolRegistryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Tool Execution Schemas ---
class ToolExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message_id: uuid.UUID | None = None
    session_id: uuid.UUID
    tool_name: str
    input_arguments: dict[str, Any]
    output_result: dict[str, Any] | None = None
    status: str
    execution_time_ms: int
    error_message: str | None = None
    created_at: datetime


# --- Feedback Schemas ---
class ConversationFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comments: str | None = None
    metadata_json: dict[str, Any] | None = None


class ConversationFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    rating: int
    comments: str | None = None
    metadata_json: dict[str, Any] | None = None
    created_at: datetime


# --- Metadata Schemas ---
class ConversationMetadataBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: dict[str, Any]


class ConversationMetadataResponse(ConversationMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime
