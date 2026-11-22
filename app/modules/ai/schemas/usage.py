"""Pydantic schemas for AI usage telemetry, token logs, and analytics."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AIUsageLogRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    conversation_id: uuid.UUID | None = None
    provider: str
    model: str
    feature_name: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float
    latency_ms: float | None = None
    status_code: int = 200
    is_error: bool = False
    error_message: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIUsageSummaryItem(BaseModel):
    provider: str
    model: str
    total_calls: int
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    total_cost_usd: float
    avg_latency_ms: float
    error_rate: float


class AIUsageSummaryResponse(BaseModel):
    total_calls: int
    total_tokens: int
    total_cost_usd: float
    by_provider: list[AIUsageSummaryItem]
    by_feature: dict[str, dict[str, Any]]
    date_from: datetime | None = None
    date_to: datetime | None = None


class AIToolExecutionRead(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID | None = None
    conversation_id: uuid.UUID | None = None
    tool_name: str
    action_type: str
    execution_status: str
    is_mutation: bool = False
    is_confirmed: bool = False
    parameters_redacted: dict[str, Any] | None = None
    result_summary: str | None = None
    error_message: str | None = None
    execution_time_ms: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AIToolExecutionListResponse(BaseModel):
    items: list[AIToolExecutionRead]
    total: int
