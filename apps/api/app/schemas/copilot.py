import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


# --- Session Schemas ---
class CopilotSessionBase(BaseModel):
    title: str = Field(default="New Copilot Session", max_length=255)
    is_pinned: bool = False
    current_state: Optional[Dict[str, Any]] = None


class CopilotSessionCreate(BaseModel):
    title: Optional[str] = Field(default="New Copilot Session", max_length=255)
    is_pinned: Optional[bool] = False
    current_state: Optional[Dict[str, Any]] = None


class CopilotSessionUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    is_pinned: Optional[bool] = None
    current_state: Optional[Dict[str, Any]] = None


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
    tool_calls: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    generated_from: Optional[str] = None


class CopilotMessageCreate(BaseModel):
    role: str = Field("user", description="user or system or tool")
    content: str
    provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    department: Optional[str] = None  # hr, crm, finance, inventory, manufacturing, executive, etc.


class CopilotMessageResponse(CopilotMessageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime


# --- Chat Request/Response Schemas ---
class ChatRequest(BaseModel):
    content: str
    provider: Optional[str] = "openai"
    model_name: Optional[str] = "gpt-4o"
    temperature: Optional[float] = 0.7
    department: Optional[str] = None  # hr, crm, etc. to load system/department prompt template


class ChatResponse(BaseModel):
    session_id: uuid.UUID
    user_message: CopilotMessageResponse
    assistant_message: CopilotMessageResponse


# --- Prompt Schemas ---
class CopilotPromptBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: str = Field("system", description="system, department, generic")
    department: Optional[str] = Field(None, max_length=100)
    template: str
    variables: Optional[List[str]] = Field(default_factory=list)
    version: str = Field("1.0.0", max_length=50)
    is_active: bool = True


class CopilotPromptCreate(CopilotPromptBase):
    pass


class CopilotPromptUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    type: Optional[str] = None
    department: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[List[str]] = None
    version: Optional[str] = None
    is_active: Optional[bool] = None


class CopilotPromptResponse(CopilotPromptBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: Optional[uuid.UUID] = None
    created_by: Optional[uuid.UUID] = None
    created_at: datetime
    updated_at: datetime


class PromptTestRequest(BaseModel):
    template: str
    variables: Dict[str, Any]


class PromptTestResponse(BaseModel):
    rendered: str


# --- Tool Registry Schemas ---
class ToolRegistryBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: str
    parameters_schema: Dict[str, Any]
    is_active: bool = True
    required_role: Optional[str] = Field(None, max_length=100)


class ToolRegistryCreate(ToolRegistryBase):
    pass


class ToolRegistryUpdate(BaseModel):
    description: Optional[str] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    required_role: Optional[str] = None


class ToolRegistryResponse(ToolRegistryBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Tool Execution Schemas ---
class ToolExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message_id: Optional[uuid.UUID] = None
    session_id: uuid.UUID
    tool_name: str
    input_arguments: Dict[str, Any]
    output_result: Optional[Dict[str, Any]] = None
    status: str
    execution_time_ms: int
    error_message: Optional[str] = None
    created_at: datetime


# --- Feedback Schemas ---
class ConversationFeedbackCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ConversationFeedbackResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message_id: uuid.UUID
    user_id: uuid.UUID
    organization_id: uuid.UUID
    rating: int
    comments: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime


# --- Metadata Schemas ---
class ConversationMetadataBase(BaseModel):
    key: str = Field(..., max_length=100)
    value: Dict[str, Any]


class ConversationMetadataResponse(ConversationMetadataBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    session_id: uuid.UUID
    created_at: datetime
