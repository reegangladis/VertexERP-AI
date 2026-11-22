"""Pydantic schemas for AI Copilot conversations, messages, and action workflows."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.modules.ai.schemas.gateway import TokenUsage, ToolCall


class AIConversationCreate(BaseModel):
    title: str | None = "New Conversation"
    context_type: str | None = "general"
    context_id: str | None = None
    system_prompt_override: str | None = None
    metadata_json: dict[str, Any] | None = None


class AIConversationUpdate(BaseModel):
    title: str | None = None
    domain_context: str | None = None
    is_active: bool | None = None
    metadata_json: dict[str, Any] | None = None


class AIConversationRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    domain_context: str = "GENERAL"
    model_used: str = "gpt-4o"
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    is_active: bool = True
    metadata_json: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AIConversationListResponse(BaseModel):
    items: list[AIConversationRead]
    total: int


class AIMessageRead(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = None
    role: str
    content: str | None = None
    tool_calls: list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    name: str | None = None
    token_count: int = 0
    cost: float = 0.0
    latency_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIMessageListResponse(BaseModel):
    items: list[AIMessageRead]
    total: int


class PendingActionProposal(BaseModel):
    action_id: str
    action_type: str
    tool_name: str
    parameters: dict[str, Any]
    preview_summary: str
    expires_at: datetime
    confirmation_token: str
    requires_confirmation: bool = True


class CopilotChatRequest(BaseModel):
    conversation_id: uuid.UUID | None = None
    message: str
    context: dict[str, Any] | None = None
    stream: bool = False
    tools_enabled: bool = True
    provider: str | None = None
    model: str | None = None


class CopilotChatResponse(BaseModel):
    conversation_id: uuid.UUID
    message_id: uuid.UUID
    role: str = "assistant"
    content: str
    tool_calls: list[ToolCall] | None = None
    tool_executions: list[dict[str, Any]] | None = None
    pending_action: PendingActionProposal | None = None
    usage: TokenUsage
    cost_usd: float = 0.0
    latency_ms: float | None = None


class ConfirmActionRequest(BaseModel):
    action_id: str
    confirmation_token: str
    confirmed: bool
    user_notes: str | None = None


class ConfirmActionResponse(BaseModel):
    action_id: str
    status: str  # "executed", "rejected", "expired", "failed"
    tool_name: str
    result: dict[str, Any] | None = None
    error: str | None = None
    executed_at: datetime | None = None
