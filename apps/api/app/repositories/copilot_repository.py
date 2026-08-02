import uuid
from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.copilot import (
    ConversationFeedback,
    ConversationMetadata,
    CopilotMessage,
    CopilotPrompt,
    CopilotSession,
    ToolExecution,
    ToolRegistry,
)


class CopilotRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # --- Session CRUD ---
    async def create_session(self, session: CopilotSession) -> CopilotSession:
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_session(
        self, session_id: uuid.UUID, org_id: uuid.UUID
    ) -> CopilotSession | None:
        query = (
            select(CopilotSession)
            .where(
                and_(
                    CopilotSession.id == session_id,
                    CopilotSession.organization_id == org_id,
                    CopilotSession.is_deleted == False,
                )
            )
            .options(selectinload(CopilotSession.messages))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_sessions(
        self, org_id: uuid.UUID, user_id: uuid.UUID
    ) -> Sequence[CopilotSession]:
        query = (
            select(CopilotSession)
            .where(
                and_(
                    CopilotSession.organization_id == org_id,
                    CopilotSession.user_id == user_id,
                    CopilotSession.is_deleted == False,
                )
            )
            .order_by(CopilotSession.is_pinned.desc(), CopilotSession.updated_at.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_session(
        self, session_id: uuid.UUID, org_id: uuid.UUID, update_data: dict[str, Any]
    ) -> CopilotSession | None:
        session = await self.get_session(session_id, org_id)
        if not session:
            return None
        for key, val in update_data.items():
            if val is not None:
                setattr(session, key, val)
        await self.db.flush()
        return session

    async def delete_session(self, session_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        session = await self.get_session(session_id, org_id)
        if not session:
            return False
        session.soft_delete()
        await self.db.flush()
        return True

    # --- Message CRUD ---
    async def create_message(self, message: CopilotMessage) -> CopilotMessage:
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)

        # Touch session to update its updated_at timestamp
        query = select(CopilotSession).where(CopilotSession.id == message.session_id)
        res = await self.db.execute(query)
        session = res.scalar_one_or_none()
        if session:
            # Force trigger update tracking
            session.updated_at = datetime.utcnow()

        await self.db.flush()
        return message

    async def list_messages(self, session_id: uuid.UUID) -> Sequence[CopilotMessage]:
        query = (
            select(CopilotMessage)
            .where(CopilotMessage.session_id == session_id)
            .order_by(CopilotMessage.created_at.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # --- Prompt CRUD ---
    async def create_prompt(self, prompt: CopilotPrompt) -> CopilotPrompt:
        self.db.add(prompt)
        await self.db.flush()
        await self.db.refresh(prompt)
        return prompt

    async def get_prompt(
        self, prompt_id: uuid.UUID, org_id: uuid.UUID
    ) -> CopilotPrompt | None:
        query = select(CopilotPrompt).where(
            and_(
                CopilotPrompt.id == prompt_id,
                or_(
                    CopilotPrompt.organization_id == org_id,
                    CopilotPrompt.organization_id == None,
                ),
                CopilotPrompt.is_deleted == False,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_active_prompt(
        self, org_id: uuid.UUID, prompt_type: str, department: str | None = None
    ) -> CopilotPrompt | None:
        conditions = [
            CopilotPrompt.type == prompt_type,
            CopilotPrompt.is_active == True,
            CopilotPrompt.is_deleted == False,
            or_(
                CopilotPrompt.organization_id == org_id,
                CopilotPrompt.organization_id == None,
            ),
        ]
        if department:
            conditions.append(CopilotPrompt.department == department)

        query = (
            select(CopilotPrompt)
            .where(and_(*conditions))
            .order_by(
                CopilotPrompt.organization_id.desc(), CopilotPrompt.version.desc()
            )
        )
        result = await self.db.execute(query)
        # Returns tenant-specific prompt if available, fallback to system prompt (where org_id is null)
        return result.scalars().first()

    async def list_prompts(self, org_id: uuid.UUID) -> Sequence[CopilotPrompt]:
        query = (
            select(CopilotPrompt)
            .where(
                and_(
                    or_(
                        CopilotPrompt.organization_id == org_id,
                        CopilotPrompt.organization_id == None,
                    ),
                    CopilotPrompt.is_deleted == False,
                )
            )
            .order_by(CopilotPrompt.type.asc(), CopilotPrompt.name.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_prompt(
        self, prompt_id: uuid.UUID, org_id: uuid.UUID, update_data: dict[str, Any]
    ) -> CopilotPrompt | None:
        prompt = await self.get_prompt(prompt_id, org_id)
        if not prompt:
            return None
        for key, val in update_data.items():
            if val is not None:
                setattr(prompt, key, val)
        await self.db.flush()
        return prompt

    async def delete_prompt(self, prompt_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        prompt = await self.get_prompt(prompt_id, org_id)
        if not prompt or prompt.organization_id is None:
            # Prevent deleting system default prompts by standard tenants
            return False
        prompt.soft_delete()
        await self.db.flush()
        return True

    # --- Tool Registry CRUD ---
    async def get_tool(self, tool_id: uuid.UUID) -> ToolRegistry | None:
        query = select(ToolRegistry).where(ToolRegistry.id == tool_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_tool_by_name(self, name: str) -> ToolRegistry | None:
        query = select(ToolRegistry).where(ToolRegistry.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_tool(self, tool: ToolRegistry) -> ToolRegistry:
        self.db.add(tool)
        await self.db.flush()
        await self.db.refresh(tool)
        return tool

    async def list_tools(self, only_active: bool = True) -> Sequence[ToolRegistry]:
        query = select(ToolRegistry)
        if only_active:
            query = query.where(ToolRegistry.is_active == True)
        query = query.order_by(ToolRegistry.name.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_tool(self, name: str) -> bool:
        tool = await self.get_tool_by_name(name)
        if not tool:
            return False
        await self.db.delete(tool)
        await self.db.flush()
        return True

    # --- Tool Execution Logging ---
    async def create_tool_execution(self, execution: ToolExecution) -> ToolExecution:
        self.db.add(execution)
        await self.db.flush()
        await self.db.refresh(execution)
        return execution

    async def list_tool_executions(
        self, session_id: uuid.UUID
    ) -> Sequence[ToolExecution]:
        query = (
            select(ToolExecution)
            .where(ToolExecution.session_id == session_id)
            .order_by(ToolExecution.created_at.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # --- Feedback CRUD ---
    async def create_feedback(
        self, feedback: ConversationFeedback
    ) -> ConversationFeedback:
        self.db.add(feedback)
        await self.db.flush()
        await self.db.refresh(feedback)
        return feedback

    async def get_feedback_by_message(
        self, message_id: uuid.UUID
    ) -> ConversationFeedback | None:
        query = select(ConversationFeedback).where(
            ConversationFeedback.message_id == message_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    # --- Metadata CRUD ---
    async def create_metadata(
        self, metadata: ConversationMetadata
    ) -> ConversationMetadata:
        self.db.add(metadata)
        await self.db.flush()
        await self.db.refresh(metadata)
        return metadata

    async def list_metadata(
        self, session_id: uuid.UUID
    ) -> Sequence[ConversationMetadata]:
        query = select(ConversationMetadata).where(
            ConversationMetadata.session_id == session_id
        )
        result = await self.db.execute(query)
        return result.scalars().all()
