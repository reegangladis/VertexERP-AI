"""AI Copilot Core Service."""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.modules.ai.gateway.gateway import ai_gateway
from app.modules.ai.models.conversation import AIConversation
from app.modules.ai.models.message import AIMessage
from app.modules.ai.schemas.copilot import (
    AIConversationCreate,
    AIConversationUpdate,
    ConfirmActionRequest,
    ConfirmActionResponse,
    CopilotChatRequest,
    CopilotChatResponse,
    PendingActionProposal,
)
from app.modules.ai.schemas.gateway import (
    ChatCompletionRequest,
    ChatMessage,
    MessageRole,
    TokenUsage,
)
from app.modules.ai.security.confirmation import action_confirmation_manager
from app.modules.ai.security.guardrails import AIGuardrails
from app.modules.ai.security.tool_authorizer import ToolAuthorizer
from app.modules.ai.services.ai_usage_service import AIUsageService
from app.modules.ai.tools.registry import erp_tool_registry

logger = logging.getLogger("vertexerp.ai.services.copilot")

SYSTEM_PROMPT_DEFAULT = """You are Vertex Copilot, an enterprise-grade AI assistant embedded directly inside VertexERP AI V2.
You have access to ERP business tools across Inventory, Finance, CRM/Sales, and HR.

Guidelines:
1. Always maintain zero-trust security and respect tenant boundaries.
2. Be professional, concise, accurate, and helpful.
3. For data queries, invoke relevant ERP read tools to fetch live tenant data.
4. For actions that modify ERP data (such as creating deals, stock transfers, or drafting vendor bills), the system will require user confirmation.
5. Never execute arbitrary SQL or reveal internal API keys or secrets.
"""


class AICopilotService:
    """Core orchestration service for multi-turn Copilot conversations, tool execution, and guardrails."""

    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        organization_id: UUID | None,
        data: AIConversationCreate,
    ) -> AIConversation:
        """Create a new Copilot conversation."""
        org_id = organization_id or tenant_id
        conversation = AIConversation(
            tenant_id=tenant_id,
            organization_id=org_id,
            user_id=user_id,
            title=data.title or "New Conversation",
            domain_context=data.context_type.upper() if data.context_type else "GENERAL",
            metadata_json=data.metadata_json or {},
        )
        db.add(conversation)
        await db.flush()
        return conversation

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[AIConversation]:
        """List active conversations for the authenticated user."""
        query = (
            select(AIConversation)
            .where(
                AIConversation.tenant_id == tenant_id,
                AIConversation.user_id == user_id,
                AIConversation.is_active.is_(True),
            )
            .order_by(AIConversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID,
    ) -> AIConversation:
        """Fetch conversation by ID with tenant and user verification."""
        query = select(AIConversation).where(
            AIConversation.id == conversation_id,
            AIConversation.tenant_id == tenant_id,
            AIConversation.user_id == user_id,
        )
        result = await db.execute(query)
        conversation = result.scalars().first()
        if not conversation:
            raise NotFoundException(f"Conversation '{conversation_id}' not found.")
        return conversation

    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID,
        data: AIConversationUpdate,
    ) -> AIConversation:
        """Update conversation properties."""
        conv = await AICopilotService.get_conversation(db, tenant_id, user_id, conversation_id)
        if data.title is not None:
            conv.title = data.title
        if data.domain_context is not None:
            conv.domain_context = data.domain_context
        if data.is_active is not None:
            conv.is_active = data.is_active
        if data.metadata_json is not None:
            conv.metadata_json = data.metadata_json

        await db.flush()
        return conv

    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        conversation_id: UUID,
    ) -> bool:
        """Soft delete / archive conversation."""
        conv = await AICopilotService.get_conversation(db, tenant_id, user_id, conversation_id)
        conv.is_active = False
        await db.flush()
        return True

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        tenant_id: UUID,
        conversation_id: UUID,
        skip: int = 0,
        limit: int = 100,
    ) -> list[AIMessage]:
        """Fetch chronological messages for a conversation."""
        query = (
            select(AIMessage)
            .where(
                AIMessage.conversation_id == conversation_id,
                AIMessage.tenant_id == tenant_id,
            )
            .order_by(AIMessage.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def process_chat(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        organization_id: UUID | None,
        user_permissions: set[str],
        is_superuser: bool,
        request: CopilotChatRequest,
    ) -> CopilotChatResponse:
        """Process a multi-turn chat message with guardrails, tool execution, and usage tracking."""
        start_time = time.perf_counter()

        # 1. Guardrail inspection
        guardrail = AIGuardrails.inspect_input(request.message)
        if not guardrail.is_safe:
            logger.warning(f"Guardrail triggered for user {user_id}: {guardrail.reason}")
            refusal_msg = f"I am unable to process this request: {guardrail.reason}."
            return CopilotChatResponse(
                conversation_id=request.conversation_id or uuid.uuid4(),
                message_id=uuid.uuid4(),
                role="assistant",
                content=refusal_msg,
                usage=TokenUsage(),
                cost_usd=0.0,
                latency_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
            )

        sanitized_input = guardrail.sanitized_prompt

        # 2. Get or create conversation
        if request.conversation_id:
            conv = await AICopilotService.get_conversation(
                db, tenant_id, user_id, request.conversation_id
            )
        else:
            conv_title = sanitized_input[:40] + ("..." if len(sanitized_input) > 40 else "")
            conv = await AICopilotService.create_conversation(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                organization_id=organization_id,
                data=AIConversationCreate(title=conv_title),
            )

        # 3. Record User Message
        user_msg = AIMessage(
            conversation_id=conv.id,
            tenant_id=tenant_id,
            user_id=user_id,
            role="user",
            content=sanitized_input,
            token_count=max(1, len(sanitized_input) // 4),
        )
        db.add(user_msg)
        await db.flush()

        # 4. Assemble Messages & History
        history = await AICopilotService.get_messages(db, tenant_id, conv.id, limit=20)
        messages: list[ChatMessage] = []

        # System message
        sys_prompt = SYSTEM_PROMPT_DEFAULT
        if request.context:
            sys_prompt += f"\nActive ERP Context: {json.dumps(request.context)}"
        messages.append(ChatMessage(role=MessageRole.SYSTEM, content=sys_prompt))

        # History messages
        for m in history:
            role = (
                MessageRole(m.role)
                if m.role in [r.value for r in MessageRole]
                else MessageRole.USER
            )
            messages.append(ChatMessage(role=role, content=m.content, tool_calls=None))

        # Tools setup
        tools = erp_tool_registry.get_tool_definitions() if request.tools_enabled else None

        # 5. Invoke AI Gateway
        gw_req = ChatCompletionRequest(
            model=request.model,
            provider=request.provider,
            messages=messages,
            tools=tools,
        )
        gw_resp = await ai_gateway.chat_completion(gw_req)

        choice = gw_resp.choices[0]
        assistant_reply = choice.message.content or ""
        tool_calls = choice.message.tool_calls
        pending_action: PendingActionProposal | None = None
        tool_executions_list: list[dict[str, Any]] = []

        total_prompt_tokens = gw_resp.usage.prompt_tokens
        total_completion_tokens = gw_resp.usage.completion_tokens
        total_cost = gw_resp.cost_usd

        # 6. Process Tool Calls if any
        if tool_calls and len(tool_calls) > 0:
            for tc in tool_calls:
                fn_name = tc.function.name
                try:
                    fn_args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                except json.JSONDecodeError:
                    fn_args = {}

                tool_inst = erp_tool_registry.get_tool(fn_name)
                is_mutation = (
                    ToolAuthorizer.is_mutation_tool(fn_name)
                    if not tool_inst
                    else tool_inst.is_mutation
                )

                if is_mutation:
                    # Create pending proposal requiring confirmation
                    preview_text = (
                        tool_inst.preview(fn_args)
                        if tool_inst
                        else f"Execute {fn_name} with {fn_args}"
                    )
                    proposal = action_confirmation_manager.create_proposal(
                        tool_name=fn_name,
                        action_type=tool_inst.action_type if tool_inst else "mutation",
                        parameters=fn_args,
                        preview_summary=preview_text,
                        tenant_id=tenant_id,
                        user_id=user_id,
                    )
                    pending_action = proposal
                    assistant_reply = (
                        f"I have prepared the requested action:\n\n**{preview_text}**\n\n"
                        f"Because this operation modifies ERP data, please confirm to proceed."
                    )
                    # Log pending tool execution
                    await AIUsageService.log_tool_execution(
                        db=db,
                        tenant_id=tenant_id,
                        user_id=user_id,
                        conversation_id=conv.id,
                        tool_name=fn_name,
                        action_type=proposal.action_type,
                        execution_status="PENDING_CONFIRMATION",
                        is_mutation=True,
                        is_confirmed=False,
                        parameters_redacted=fn_args,
                        result_summary=preview_text,
                    )
                    break
                else:
                    # Execute read tool immediately
                    tool_res = await erp_tool_registry.execute_tool(
                        tool_name=fn_name,
                        db=db,
                        tenant_id=tenant_id,
                        user_id=user_id,
                        user_permissions=user_permissions,
                        is_superuser=is_superuser,
                        parameters=fn_args,
                    )
                    tool_executions_list.append(tool_res)

                    # Log tool execution
                    await AIUsageService.log_tool_execution(
                        db=db,
                        tenant_id=tenant_id,
                        user_id=user_id,
                        conversation_id=conv.id,
                        tool_name=fn_name,
                        action_type=tool_inst.action_type if tool_inst else "query",
                        execution_status="SUCCESS" if tool_res.get("success") else "FAILED",
                        is_mutation=False,
                        is_confirmed=True,
                        parameters_redacted=fn_args,
                        result_summary=str(tool_res.get("result", ""))[:500],
                        error_message=tool_res.get("error"),
                        execution_time_ms=tool_res.get("execution_time_ms"),
                    )

                    # If read tool succeeded, send back result to LLM for final natural response
                    messages.append(
                        ChatMessage(
                            role=MessageRole.ASSISTANT,
                            tool_calls=[tc],
                        )
                    )
                    messages.append(
                        ChatMessage(
                            role=MessageRole.TOOL,
                            tool_call_id=tc.id,
                            name=fn_name,
                            content=json.dumps(tool_res.get("result", {})),
                        )
                    )

                    second_req = ChatCompletionRequest(
                        model=request.model,
                        provider=request.provider,
                        messages=messages,
                    )
                    second_resp = await ai_gateway.chat_completion(second_req)
                    assistant_reply = second_resp.choices[0].message.content or ""
                    total_prompt_tokens += second_resp.usage.prompt_tokens
                    total_completion_tokens += second_resp.usage.completion_tokens
                    total_cost += second_resp.cost_usd

        # 7. Record Assistant Message
        assistant_msg = AIMessage(
            conversation_id=conv.id,
            tenant_id=tenant_id,
            user_id=user_id,
            role="assistant",
            content=assistant_reply,
            tool_calls=[tc.model_dump() for tc in tool_calls] if tool_calls else None,
            token_count=total_prompt_tokens + total_completion_tokens,
            cost=Decimal(str(round(total_cost, 6))),
            latency_ms=int((time.perf_counter() - start_time) * 1000.0),
        )
        db.add(assistant_msg)

        # 8. Update Conversation Stats
        conv.total_prompt_tokens += total_prompt_tokens
        conv.total_completion_tokens += total_completion_tokens
        conv.total_cost += Decimal(str(round(total_cost, 6)))
        conv.updated_at = datetime.now(UTC)
        await db.flush()

        # 9. Log Telemetry
        await AIUsageService.log_usage(
            db=db,
            tenant_id=tenant_id,
            organization_id=organization_id,
            user_id=user_id,
            conversation_id=conv.id,
            provider=gw_resp.provider,
            model=gw_resp.model,
            feature_name="copilot_chat",
            prompt_tokens=total_prompt_tokens,
            completion_tokens=total_completion_tokens,
            cost_usd=total_cost,
            latency_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
        )

        return CopilotChatResponse(
            conversation_id=conv.id,
            message_id=assistant_msg.id,
            role="assistant",
            content=assistant_reply,
            tool_calls=tool_calls,
            tool_executions=tool_executions_list if tool_executions_list else None,
            pending_action=pending_action,
            usage=TokenUsage(
                prompt_tokens=total_prompt_tokens,
                completion_tokens=total_completion_tokens,
                total_tokens=total_prompt_tokens + total_completion_tokens,
            ),
            cost_usd=total_cost,
            latency_ms=round((time.perf_counter() - start_time) * 1000.0, 2),
        )

    @staticmethod
    async def confirm_action(
        db: AsyncSession,
        tenant_id: UUID,
        user_id: UUID,
        user_permissions: set[str],
        is_superuser: bool,
        request: ConfirmActionRequest,
    ) -> ConfirmActionResponse:
        """Confirm or reject a proposed pending AI mutation."""
        action = action_confirmation_manager.verify_and_consume(
            action_id=request.action_id,
            confirmation_token=request.confirmation_token,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        if not request.confirmed:
            await AIUsageService.log_tool_execution(
                db=db,
                tenant_id=tenant_id,
                user_id=user_id,
                tool_name=action.tool_name,
                action_type=action.action_type,
                execution_status="REJECTED_BY_USER",
                is_mutation=True,
                is_confirmed=False,
                parameters_redacted=action.parameters,
                result_summary="User rejected action confirmation proposal.",
            )
            return ConfirmActionResponse(
                action_id=request.action_id,
                status="rejected",
                tool_name=action.tool_name,
                result={"message": "Action proposal rejected by user."},
            )

        tool_res = await erp_tool_registry.execute_tool(
            tool_name=action.tool_name,
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            user_permissions=user_permissions,
            is_superuser=is_superuser,
            parameters=action.parameters,
        )

        await AIUsageService.log_tool_execution(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            tool_name=action.tool_name,
            action_type=action.action_type,
            execution_status="EXECUTED" if tool_res.get("success") else "FAILED",
            is_mutation=True,
            is_confirmed=True,
            parameters_redacted=action.parameters,
            result_summary=str(tool_res.get("result", ""))[:500],
            error_message=tool_res.get("error"),
            execution_time_ms=tool_res.get("execution_time_ms"),
        )

        return ConfirmActionResponse(
            action_id=request.action_id,
            status="executed" if tool_res.get("success") else "failed",
            tool_name=action.tool_name,
            result=tool_res.get("result"),
            error=tool_res.get("error"),
            executed_at=datetime.now(UTC),
        )
