import json
import logging
import time
import uuid
from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

# Import Core Setting and DB Repos
from app.core.config import settings
from app.models.copilot import (
    ConversationFeedback,
    CopilotMessage,
    CopilotPrompt,
    CopilotSession,
    ToolExecution,
    ToolRegistry,
)
from app.models.user import User
from app.repositories.copilot_repository import CopilotRepository
from app.services.copilot.engine import (
    ContextManager,
    PIIMasker,
    PromptManager,
    RedisRateLimiter,
)

# Import Copilot Sub-modules
from app.services.copilot.llm_provider import LLMProviderRegistry
from app.services.copilot.tools import registry as tool_executor_registry

logger = logging.getLogger(__name__)


class CopilotService:
    def __init__(self, db: AsyncSession, redis_service: Any | None = None):
        self.db = db
        self.repo = CopilotRepository(db)
        self.redis_service = redis_service

    async def initialize_default_prompts(self) -> None:
        """
        Registers default system prompt templates in the DB if none exist.
        """
        prompts = await self.repo.list_prompts(
            org_id=uuid.UUID("00000000-0000-0000-0000-000000000000")
        )  # Placeholder
        if not prompts:
            # Add general default
            from app.services.copilot.engine import DEFAULT_SYSTEM_PROMPTS

            for dept, template in DEFAULT_SYSTEM_PROMPTS.items():
                p = CopilotPrompt(
                    name=f"Default System Prompt - {dept.upper()}",
                    type="system" if dept == "generic" else "department",
                    department=dept if dept != "generic" else None,
                    template=template,
                    variables=["user_name", "org_name", "org_id"],
                    version="1.0.0",
                    is_active=True,
                )
                await self.repo.create_prompt(p)

    async def initialize_tool_registry(self) -> None:
        """
        Dynamically registers all decorated tools from Python registry into the DB tool_registry table.
        """
        active_tools = await self.repo.list_tools(only_active=False)
        db_tool_names = {t.name for t in active_tools}

        for python_tool in tool_executor_registry.list_tools():
            if python_tool["name"] not in db_tool_names:
                t = ToolRegistry(
                    name=python_tool["name"],
                    description=python_tool["description"],
                    parameters_schema=python_tool["parameters_schema"],
                    required_role=python_tool["required_role"],
                    is_active=True,
                )
                await self.repo.create_tool(t)

    # --- Session Management ---
    async def create_session(
        self, org_id: uuid.UUID, user_id: uuid.UUID, title: str = "New Copilot Session"
    ) -> CopilotSession:
        await self.initialize_default_prompts()
        await self.initialize_tool_registry()

        session = CopilotSession(
            organization_id=org_id,
            user_id=user_id,
            title=title,
            is_pinned=False,
            current_state={},
        )
        return await self.repo.create_session(session)

    async def get_session(
        self, session_id: uuid.UUID, org_id: uuid.UUID
    ) -> CopilotSession | None:
        return await self.repo.get_session(session_id, org_id)

    async def list_sessions(
        self, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[CopilotSession]:
        return await self.repo.list_sessions(org_id, user_id)

    async def update_session(
        self, session_id: uuid.UUID, org_id: uuid.UUID, data: dict[str, Any]
    ) -> CopilotSession | None:
        return await self.repo.update_session(session_id, org_id, data)

    async def delete_session(self, session_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        return await self.repo.delete_session(session_id, org_id)

    # --- Messaging & Conversation Flow ---
    async def chat(
        self,
        session_id: uuid.UUID,
        user: User,
        content: str,
        provider: str = "openai",
        model_name: str | None = None,
        temperature: float = 0.7,
        department: str | None = None,
    ) -> dict[str, Any]:
        """
        Coordinates context assembly, rate limits, permission checks, tools triggers, and AI generation.
        """
        org_id = user.organization_id
        if not org_id:
            raise ValueError("User not bound to any organization")

        # 1. Rate Limiting Check
        is_limited = await RedisRateLimiter.is_rate_limited(self.redis_service, user.id)
        if is_limited:
            raise RuntimeError(
                "Rate limit exceeded. Please wait before sending more messages."
            )

        # Load active session
        session = await self.get_session(session_id, org_id)
        if not session:
            raise ValueError("Session not found or access denied")

        start_time = time.time()

        # Save User Message to DB
        user_msg = CopilotMessage(
            session_id=session_id,
            role="user",
            content=content,
            prompt_tokens=int(len(content) / 4),
            completion_tokens=0,
            latency_ms=0,
        )
        user_msg = await self.repo.create_message(user_msg)

        # 2. Context Prompt Engineering
        # Load Prompt template (from DB or fallback default)
        db_prompt = await self.repo.get_active_prompt(
            org_id, "department" if department else "system", department
        )
        template_str = (
            db_prompt.template
            if db_prompt
            else PromptManager.get_default_prompt(department)
        )
        prompt_version = db_prompt.version if db_prompt else "default"

        # Compile variables
        variables = {
            "user_name": (
                f"{user.first_name} {user.last_name}"
                if user.first_name
                else user.username
            ),
            "org_name": "VertexERP Tenant",  # In production, pull Organization name
            "org_id": str(org_id),
        }
        system_prompt = PromptManager.render_template(template_str, variables)

        # 3. Assemble Sliding Messages History
        messages = await self.repo.list_messages(session_id)
        chat_history = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.id != user_msg.id
        ]

        # Include current message
        chat_history.append({"role": "user", "content": content})

        compiled_messages = ContextManager.compile_history(system_prompt, chat_history)

        # 4. Pull Active DB Tools for LLM parameter mapping
        db_tools = await self.repo.list_tools(only_active=True)
        llm_tools = []
        for t in db_tools:
            # Check user role authorization for this tool
            if t.required_role:
                user_role_names = (
                    {role.name for role in user.roles} if user.roles else set()
                )
                # Bypass tool if role check fails
                if (
                    t.required_role not in user_role_names
                    and "Super Admin" not in user_role_names
                ):
                    continue

            llm_tools.append(
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.parameters_schema,
                    },
                }
            )

        # 5. Execute LLM Call
        llm = LLMProviderRegistry.get_provider(
            provider=provider,
            model_name=model_name,
            api_key=getattr(settings, f"{provider.upper()}_API_KEY", None),
            endpoint=getattr(settings, "AZURE_OPENAI_ENDPOINT", None),
            local_url=getattr(settings, "LOCAL_MODEL_URL", None),
        )

        llm_response = await llm.generate_response(
            messages=compiled_messages,
            tools=llm_tools if llm_tools else None,
            temperature=temperature,
        )

        assistant_content = llm_response["content"]
        tool_calls = llm_response["tool_calls"]
        prompt_tokens = llm_response["prompt_tokens"]
        completion_tokens = llm_response["completion_tokens"]
        citations = []

        # 6. Workflow Tool Execution Loop (If tool calls requested)
        executed_tools_logs = []
        if tool_calls:
            for tool_call in tool_calls:
                t_name = tool_call["function"]["name"]
                t_args_str = tool_call["function"]["arguments"]

                try:
                    t_args = json.loads(t_args_str)
                except Exception:
                    t_args = {}

                # Record execution trace start
                exec_start = time.time()

                # Check DB configuration to ensure tool active status
                db_tool = await self.repo.get_tool_by_name(t_name)
                if not db_tool or not db_tool.is_active:
                    status = "error"
                    result_payload = {
                        "error": "Tool is currently disabled or unregistered"
                    }
                else:
                    # Run execution
                    try:
                        resp = await tool_executor_registry.execute(
                            name=t_name,
                            arguments=t_args,
                            db=self.db,
                            org_id=org_id,
                            user_id=user.id,
                        )
                        status = resp["status"]
                        result_payload = resp.get("result") or {
                            "error": resp.get("error")
                        }
                    except Exception as e:
                        status = "error"
                        result_payload = {"error": str(e)}

                exec_latency = int((time.time() - exec_start) * 1000)

                # Save tool execution to DB
                t_exec = ToolExecution(
                    session_id=session_id,
                    tool_name=t_name,
                    input_arguments=t_args,
                    output_result=result_payload if status == "success" else None,
                    status=status,
                    execution_time_ms=exec_latency,
                    error_message=(
                        result_payload.get("error") if status == "error" else None
                    ),
                )
                t_exec = await self.repo.create_tool_execution(t_exec)
                executed_tools_logs.append(t_exec)

                # Re-invoke LLM with the tool execution response to synthesize final explanation
                # Append tool messages to chat context
                compiled_messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_content or "Calling system api...",
                    }
                )
                compiled_messages.append(
                    {"role": "tool", "content": json.dumps(result_payload)}
                )

            # Call LLM again to synthesize the answer
            second_llm_response = await llm.generate_response(
                messages=compiled_messages, temperature=temperature
            )
            assistant_content = second_llm_response["content"]
            prompt_tokens += second_llm_response["prompt_tokens"]
            completion_tokens += second_llm_response["completion_tokens"]

            # Map citations based on tool outputs
            citations.append(
                {
                    "source": "ERP APIs",
                    "details": f"Invoked tool workflow parameters: {[log.tool_name for log in executed_tools_logs]}",
                }
            )

        # 7. Sensitive Data PII Masking (based on user roles)
        user_roles = [role.name for role in user.roles] if user.roles else []
        final_content = PIIMasker.mask(assistant_content, user_roles)

        # Save Assistant Message to DB
        latency_ms = int((time.time() - start_time) * 1000)
        assistant_msg = CopilotMessage(
            session_id=session_id,
            role="assistant",
            content=final_content,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            tool_calls=tool_calls,
            citations=citations if citations else None,
            generated_from=prompt_version,
        )
        assistant_msg = await self.repo.create_message(assistant_msg)

        # Link executed tools to this message ID
        for log in executed_tools_logs:
            log.message_id = assistant_msg.id
        await self.db.flush()

        # Audit Log Trigger
        try:
            from app.repositories.audit import AuditLogRepository
            from app.services.audit import AuditService

            audit_repo = AuditLogRepository(self.db)
            audit_service = AuditService(audit_repo)
            await audit_service.log_action(
                user_id=user.id,
                organization_id=org_id,
                action="copilot.chat",
                ip_address="127.0.0.1",
                user_agent="copilot-client",
                details={
                    "session_id": str(session_id),
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "latency_ms": latency_ms,
                    "tools_called": [log.tool_name for log in executed_tools_logs],
                },
            )
        except Exception as e:
            logger.warning(f"Audit logging failure: {e}")

        return {
            "session_id": session_id,
            "user_message": user_msg,
            "assistant_message": assistant_msg,
        }

    # --- Prompts Management ---
    async def create_prompt(
        self, org_id: uuid.UUID, user_id: uuid.UUID, prompt: CopilotPrompt
    ) -> CopilotPrompt:
        prompt.organization_id = org_id
        prompt.created_by = user_id
        return await self.repo.create_prompt(prompt)

    async def get_prompt(
        self, prompt_id: uuid.UUID, org_id: uuid.UUID
    ) -> CopilotPrompt | None:
        return await self.repo.get_prompt(prompt_id, org_id)

    async def list_prompts(self, org_id: uuid.UUID) -> Sequence[CopilotPrompt]:
        return await self.repo.list_prompts(org_id)

    async def update_prompt(
        self, prompt_id: uuid.UUID, org_id: uuid.UUID, update_data: dict[str, Any]
    ) -> CopilotPrompt | None:
        return await self.repo.update_prompt(prompt_id, org_id, update_data)

    async def delete_prompt(self, prompt_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        return await self.repo.delete_prompt(prompt_id, org_id)

    # --- Tools Management ---
    async def list_registered_tools(
        self, only_active: bool = True
    ) -> Sequence[ToolRegistry]:
        await self.initialize_tool_registry()
        return await self.repo.list_tools(only_active)

    async def update_tool_status(
        self, tool_name: str, is_active: bool
    ) -> ToolRegistry | None:
        tool = await self.repo.get_tool_by_name(tool_name)
        if tool:
            tool.is_active = is_active
            await self.db.flush()
        return tool

    async def get_tool_executions(
        self, session_id: uuid.UUID
    ) -> Sequence[ToolExecution]:
        return await self.repo.list_tool_executions(session_id)

    # --- Feedback ---
    async def submit_feedback(
        self,
        message_id: uuid.UUID,
        user_id: uuid.UUID,
        org_id: uuid.UUID,
        rating: int,
        comments: str | None = None,
    ) -> ConversationFeedback:
        # Check if feedback exists
        existing = await self.repo.get_feedback_by_message(message_id)
        if existing:
            existing.rating = rating
            existing.comments = comments
            await self.db.flush()
            return existing

        feedback = ConversationFeedback(
            message_id=message_id,
            user_id=user_id,
            organization_id=org_id,
            rating=rating,
            comments=comments,
        )
        return await self.repo.create_feedback(feedback)

    # --- Analytics & Dashboard ---
    async def get_analytics(self, org_id: uuid.UUID) -> dict[str, Any]:
        """
        Gathers system-wide usage analytics metrics.
        """
        # Select all sessions
        from sqlalchemy import func, select

        # Token usage count
        usage_query = (
            select(
                func.sum(CopilotMessage.prompt_tokens).label("prompt"),
                func.sum(CopilotMessage.completion_tokens).label("completion"),
                func.avg(CopilotMessage.latency_ms).label("latency"),
            )
            .join(CopilotSession)
            .where(CopilotSession.organization_id == org_id)
        )

        usage_res = await self.db.execute(usage_query)
        row = usage_res.fetchone()

        # Tool success count
        success_query = (
            select(func.count(ToolExecution.id))
            .join(CopilotSession)
            .where(
                CopilotSession.organization_id == org_id,
                ToolExecution.status == "success",
            )
        )
        total_success = (await self.db.execute(success_query)).scalar() or 0

        failed_query = (
            select(func.count(ToolExecution.id))
            .join(CopilotSession)
            .where(
                CopilotSession.organization_id == org_id,
                ToolExecution.status == "error",
            )
        )
        total_failed = (await self.db.execute(failed_query)).scalar() or 0

        # Feedback averages
        feedback_query = select(
            func.avg(ConversationFeedback.rating).label("avg_rating"),
            func.count(ConversationFeedback.id).label("count"),
        ).where(ConversationFeedback.organization_id == org_id)
        feedback_res = await self.db.execute(feedback_query)
        frow = feedback_res.fetchone()

        return {
            "total_prompt_tokens": int(row.prompt) if row and row.prompt else 0,
            "total_completion_tokens": (
                int(row.completion) if row and row.completion else 0
            ),
            "average_latency_ms": int(row.latency) if row and row.latency else 0,
            "tool_success_rate": (
                (total_success / (total_success + total_failed) * 100)
                if (total_success + total_failed) > 0
                else 100
            ),
            "total_tool_executions": total_success + total_failed,
            "average_feedback_rating": (
                float(frow.avg_rating) if frow and frow.avg_rating else 4.5
            ),
            "total_feedbacks": frow.count if frow and frow.count else 0,
        }
