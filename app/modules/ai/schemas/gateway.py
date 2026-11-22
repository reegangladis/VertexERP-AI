"""Pydantic schemas for AI Gateway and Provider Interfaces."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class MessageRole(StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class FunctionDefinition(BaseModel):
    name: str
    description: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    type: str = "function"
    function: FunctionDefinition


class FunctionCall(BaseModel):
    name: str
    arguments: str  # JSON-encoded string arguments


class ToolCall(BaseModel):
    id: str
    type: str = "function"
    function: FunctionCall


class ChatMessage(BaseModel):
    role: MessageRole
    content: str | None = None
    name: str | None = None
    tool_calls: list[ToolCall] | None = None
    tool_call_id: str | None = None


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatCompletionChoice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: str | None = "stop"


class ChatCompletionRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    temperature: float = 0.2
    max_tokens: int | None = 2048
    top_p: float | None = 1.0
    tools: list[ToolDefinition] | None = None
    tool_choice: str | dict[str, Any] | None = None
    response_format: dict[str, Any] | None = None
    stream: bool = False
    provider: str | None = None


class ChatCompletionResponse(BaseModel):
    id: str
    provider: str
    model: str
    choices: list[ChatCompletionChoice]
    usage: TokenUsage
    cost_usd: float = 0.0
    latency_ms: float | None = None


class ChatCompletionChunkDelta(BaseModel):
    role: MessageRole | None = None
    content: str | None = None
    tool_calls: list[ToolCall] | None = None


class ChatCompletionChunkChoice(BaseModel):
    index: int = 0
    delta: ChatCompletionChunkDelta
    finish_reason: str | None = None


class ChatCompletionChunk(BaseModel):
    id: str
    provider: str
    model: str
    choices: list[ChatCompletionChunkChoice]
    usage: TokenUsage | None = None


class EmbeddingItem(BaseModel):
    index: int
    embedding: list[float]


class EmbeddingRequest(BaseModel):
    model: str | None = None
    input: str | list[str]
    provider: str | None = None


class EmbeddingResponse(BaseModel):
    provider: str
    model: str
    data: list[EmbeddingItem]
    usage: TokenUsage
    cost_usd: float = 0.0


class StructuredOutputRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage]
    response_schema: dict[str, Any]
    schema_name: str
    schema_description: str | None = None
    temperature: float = 0.0
    provider: str | None = None


class StructuredOutputResponse(BaseModel):
    id: str
    provider: str
    model: str
    parsed: dict[str, Any]
    raw_content: str
    usage: TokenUsage
    cost_usd: float = 0.0
