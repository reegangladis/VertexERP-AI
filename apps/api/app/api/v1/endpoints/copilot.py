import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session, get_redis
from app.database.redis import RedisService
from app.models.user import User

# Import Schemas
from app.schemas.copilot import (
    ChatRequest,
    ChatResponse,
    ConversationFeedbackCreate,
    ConversationFeedbackResponse,
    CopilotMessageResponse,
    CopilotPromptCreate,
    CopilotPromptResponse,
    CopilotPromptUpdate,
    CopilotSessionCreate,
    CopilotSessionResponse,
    CopilotSessionUpdate,
    PromptTestRequest,
    PromptTestResponse,
    ToolExecutionResponse,
    ToolRegistryResponse,
)

# Import Service
from app.services.copilot_service import CopilotService

router = APIRouter()


# ==================== Sessions endpoints ====================


@router.post(
    "/sessions",
    response_model=CopilotSessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Copilot conversation session",
)
async def create_session(
    payload: CopilotSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    return await service.create_session(
        org_id=current_user.organization_id,
        user_id=current_user.id,
        title=payload.title or "New Copilot Session",
    )


@router.get(
    "/sessions",
    response_model=list[CopilotSessionResponse],
    summary="List all conversational sessions for the current user",
)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    return await service.list_sessions(
        org_id=current_user.organization_id, user_id=current_user.id
    )


@router.get(
    "/sessions/{session_id}",
    response_model=CopilotSessionResponse,
    summary="Get detailed metadata for a specific session",
)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    session = await service.get_session(session_id, current_user.organization_id)
    if not session:
        raise HTTPException(status_code=404, detail="Copilot session not found")
    return session


@router.put(
    "/sessions/{session_id}",
    response_model=CopilotSessionResponse,
    summary="Update session parameters (title, pinning)",
)
async def update_session(
    session_id: uuid.UUID,
    payload: CopilotSessionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    session = await service.update_session(
        session_id=session_id,
        org_id=current_user.organization_id,
        data=payload.model_dump(exclude_unset=True),
    )
    if not session:
        raise HTTPException(status_code=404, detail="Copilot session not found")
    return session


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a specific session",
)
async def delete_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    success = await service.delete_session(session_id, current_user.organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Copilot session not found")


# ==================== Messaging Chat endpoints ====================


@router.post(
    "/sessions/{session_id}/chat",
    response_model=ChatResponse,
    summary="Send a chat message and execute automated tools if required",
)
async def send_chat_message(
    session_id: uuid.UUID,
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    try:
        return await service.chat(
            session_id=session_id,
            user=current_user,
            content=payload.content,
            provider=payload.provider or "openai",
            model_name=payload.model_name,
            temperature=payload.temperature or 0.7,
            department=payload.department,
        )
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err)) from val_err
    except RuntimeError as run_err:
        raise HTTPException(status_code=429, detail=str(run_err)) from run_err
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Internal chat processing failure: {e}"
        ) from e


@router.get(
    "/sessions/{session_id}/messages",
    response_model=list[CopilotMessageResponse],
    summary="Retrieve full messages history transcript for a session",
)
async def list_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    session = await service.get_session(session_id, current_user.organization_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return await service.repo.list_messages(session_id)


# ==================== Reusable Prompts endpoints ====================


@router.post(
    "/prompts",
    response_model=CopilotPromptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom prompt template (Administrative)",
)
async def create_prompt_template(
    payload: CopilotPromptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)

    from app.models.copilot import CopilotPrompt

    p = CopilotPrompt(
        name=payload.name,
        type=payload.type,
        department=payload.department,
        template=payload.template,
        variables=payload.variables or [],
        version=payload.version or "1.0.0",
        is_active=payload.is_active,
    )
    return await service.create_prompt(current_user.organization_id, current_user.id, p)


@router.get(
    "/prompts",
    response_model=list[CopilotPromptResponse],
    summary="List all available system and department prompts templates",
)
async def list_prompts_templates(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    return await service.list_prompts(current_user.organization_id)


@router.put(
    "/prompts/{prompt_id}",
    response_model=CopilotPromptResponse,
    summary="Modify prompt template configurations",
)
async def update_prompt_template(
    prompt_id: uuid.UUID,
    payload: CopilotPromptUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    prompt = await service.update_prompt(
        prompt_id=prompt_id,
        org_id=current_user.organization_id,
        update_data=payload.model_dump(exclude_unset=True),
    )
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return prompt


@router.delete(
    "/prompts/{prompt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a custom prompt template",
)
async def delete_prompt_template(
    prompt_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    success = await service.delete_prompt(prompt_id, current_user.organization_id)
    if not success:
        raise HTTPException(
            status_code=403, detail="Cannot delete template or template not found"
        )


@router.post(
    "/prompts/test",
    response_model=PromptTestResponse,
    summary="Render test inputs inside a prompt template variables",
)
async def test_prompt_rendering(
    payload: PromptTestRequest, current_user: User = Depends(get_current_user)
):
    from app.services.copilot.engine import PromptManager

    rendered = PromptManager.render_template(payload.template, payload.variables)
    return PromptTestResponse(rendered=rendered)


# ==================== Pluggable Tools endpoints ====================


@router.get(
    "/tools",
    response_model=list[ToolRegistryResponse],
    summary="List all registered backend tools",
)
async def list_tools(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    service = CopilotService(db, redis)
    return await service.list_registered_tools(only_active=False)


@router.put(
    "/tools/{tool_name}/status",
    response_model=ToolRegistryResponse,
    summary="Enable or disable a specific tool trigger (Administrative)",
)
async def update_tool_status(
    tool_name: str,
    is_active: bool,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    service = CopilotService(db, redis)
    tool = await service.update_tool_status(tool_name, is_active)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool name not found")
    return tool


@router.get(
    "/sessions/{session_id}/tool-executions",
    response_model=list[ToolExecutionResponse],
    summary="Fetch all executed tools logs within a session context",
)
async def get_tool_executions(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    session = await service.get_session(session_id, current_user.organization_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return await service.get_tool_executions(session_id)


# ==================== Feedback endpoints ====================


@router.post(
    "/messages/{message_id}/feedback",
    response_model=ConversationFeedbackResponse,
    summary="Submit user feedback rating and reviews for a message",
)
async def submit_message_feedback(
    message_id: uuid.UUID,
    payload: ConversationFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    return await service.submit_feedback(
        message_id=message_id,
        user_id=current_user.id,
        org_id=current_user.organization_id,
        rating=payload.rating,
        comments=payload.comments,
    )


# ==================== Analytics Dashboard endpoints ====================


@router.get(
    "/analytics", summary="Retrieve analytics dashboard metrics for the Copilot service"
)
async def get_copilot_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session),
    redis: RedisService = Depends(get_redis),
):
    if not current_user.organization_id:
        raise HTTPException(
            status_code=400, detail="User is not bound to any organization"
        )
    service = CopilotService(db, redis)
    return await service.get_analytics(current_user.organization_id)
