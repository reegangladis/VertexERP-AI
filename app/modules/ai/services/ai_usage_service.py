"""AI Usage Telemetry and Audit Logging Service."""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models.usage import AIToolExecution, AIUsageLog
from app.modules.ai.schemas.usage import (
    AIUsageSummaryItem,
    AIUsageSummaryResponse,
)

logger = logging.getLogger("vertexerp.ai.services.usage")


class AIUsageService:
    """Service for recording and querying AI token usage and tool executions."""

    @staticmethod
    async def log_usage(
        db: AsyncSession,
        tenant_id: UUID,
        provider: str,
        model: str,
        feature_name: str,
        prompt_tokens: int,
        completion_tokens: int,
        cost_usd: float,
        organization_id: UUID | None = None,
        user_id: UUID | None = None,
        conversation_id: UUID | None = None,
        latency_ms: float | None = None,
        status_code: int = 200,
        is_error: bool = False,
        error_message: str | None = None,
        metadata_json: dict[str, Any] | None = None,
    ) -> AIUsageLog:
        """Create an immutable AI usage telemetry log entry."""
        total_tokens = prompt_tokens + completion_tokens
        org_id = organization_id or tenant_id
        entry = AIUsageLog(
            tenant_id=tenant_id,
            organization_id=org_id,
            user_id=user_id,
            conversation_id=conversation_id,
            operation_type="CHAT_COMPLETION",
            provider=provider,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            cost_usd=Decimal(str(round(cost_usd, 6))),
            latency_ms=int(latency_ms or 0),
            status="SUCCESS" if not is_error else "FAILED",
            error_message=error_message,
        )
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def log_tool_execution(
        db: AsyncSession,
        tenant_id: UUID,
        tool_name: str,
        action_type: str,
        execution_status: str,
        user_id: UUID | None = None,
        conversation_id: UUID | None = None,
        is_mutation: bool = False,
        is_confirmed: bool = False,
        parameters_redacted: dict[str, Any] | None = None,
        result_summary: str | None = None,
        error_message: str | None = None,
        execution_time_ms: float | None = None,
    ) -> AIToolExecution:
        """Record an immutable record of an AI tool execution."""
        category = action_type.split(".")[0].upper() if action_type else "GENERAL"
        conf_status = (
            "PENDING_CONFIRMATION"
            if (is_mutation and not is_confirmed)
            else ("CONFIRMED" if (is_mutation and is_confirmed) else "NOT_REQUIRED")
        )
        entry = AIToolExecution(
            tenant_id=tenant_id,
            organization_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
            tool_name=tool_name,
            tool_category=category,
            is_mutation=is_mutation,
            requires_confirmation=is_mutation,
            confirmation_status=conf_status,
            arguments_json=parameters_redacted or {},
            result_json={"summary": result_summary} if result_summary else {},
            execution_status=execution_status,
            error_message=error_message,
        )
        db.add(entry)
        await db.flush()
        return entry

    @staticmethod
    async def get_usage_summary(
        db: AsyncSession,
        tenant_id: UUID,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> AIUsageSummaryResponse:
        """Calculate aggregated AI usage and cost metrics for a tenant."""
        group_q = (
            select(
                AIUsageLog.provider,
                AIUsageLog.model,
                func.count(AIUsageLog.id).label("total_calls"),
                func.sum(AIUsageLog.prompt_tokens).label("total_prompt_tokens"),
                func.sum(AIUsageLog.completion_tokens).label("total_completion_tokens"),
                func.sum(AIUsageLog.total_tokens).label("total_tokens"),
                func.sum(AIUsageLog.cost_usd).label("total_cost_usd"),
                func.avg(AIUsageLog.latency_ms).label("avg_latency_ms"),
            )
            .where(AIUsageLog.tenant_id == tenant_id)
            .group_by(AIUsageLog.provider, AIUsageLog.model)
        )
        if date_from:
            group_q = group_q.where(AIUsageLog.created_at >= date_from)
        if date_to:
            group_q = group_q.where(AIUsageLog.created_at <= date_to)

        group_res = await db.execute(group_q)
        rows = group_res.all()

        by_provider: list[AIUsageSummaryItem] = []
        overall_calls = 0
        overall_tokens = 0
        overall_cost = 0.0

        for row in rows:
            calls = row.total_calls or 0
            tokens = row.total_tokens or 0
            cost = float(row.total_cost_usd or 0.0)

            overall_calls += calls
            overall_tokens += tokens
            overall_cost += cost

            by_provider.append(
                AIUsageSummaryItem(
                    provider=row.provider,
                    model=row.model,
                    total_calls=calls,
                    total_prompt_tokens=row.total_prompt_tokens or 0,
                    total_completion_tokens=row.total_completion_tokens or 0,
                    total_tokens=tokens,
                    total_cost_usd=round(cost, 6),
                    avg_latency_ms=round(float(row.avg_latency_ms or 0.0), 2),
                    error_rate=0.0,
                )
            )

        return AIUsageSummaryResponse(
            total_calls=overall_calls,
            total_tokens=overall_tokens,
            total_cost_usd=round(overall_cost, 6),
            by_provider=by_provider,
            by_feature={},
            date_from=date_from,
            date_to=date_to,
        )
