"""AI Copilot API Endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from redis.asyncio import Redis

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.ai.schemas.copilot import (
    AIConversationCreate,
    AIConversationListResponse,
    AIConversationRead,
    AIConversationUpdate,
    AIMessageListResponse,
    AIMessageRead,
    ConfirmActionRequest,
    ConfirmActionResponse,
    CopilotChatRequest,
    CopilotChatResponse,
)
from app.modules.ai.services.copilot_service import AICopilotService
from app.modules.ai.services.streaming_service import CopilotStreamingService
from app.modules.identity.api.dependencies import (
    get_current_tenant_id,
    get_current_user_claims,
    get_current_user_id,
    get_optional_redis,
    require_permission,
)
from app.modules.identity.services.rbac_service import RbacService

router = APIRouter(prefix="/copilot", tags=["AI Copilot"])


@router.post(
    "/chat",
    response_model=CopilotChatResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_COPILOT_USE.value))],
)
async def process_copilot_chat(
    request: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    redis: Redis | None = Depends(get_optional_redis),
) -> CopilotChatResponse:
    """Send a user message to Vertex Copilot with optional ERP context and tool execution."""
    org_id_str = claims.get("org_id")
    org_id = uuid.UUID(org_id_str) if org_id_str else None

    perms = claims.get("permissions")
    if perms is None:
        if org_id:
            rbac_service = RbacService(db, redis=redis)
            _, perms = await rbac_service.get_user_roles_and_permissions(
                user_id, org_id, tenant_id=tenant_id
            )
        else:
            perms = []

    user_permissions: set[str] = set(perms)
    is_superuser: bool = bool(claims.get("is_superuser", False))

    return await AICopilotService.process_chat(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        organization_id=org_id,
        user_permissions=user_permissions,
        is_superuser=is_superuser,
        request=request,
    )


@router.post(
    "/chat/stream",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_COPILOT_USE.value))],
)
async def stream_copilot_chat(
    request: CopilotChatRequest,
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> StreamingResponse:
    """Stream Copilot chat responses via Server-Sent Events (SSE)."""
    generator = CopilotStreamingService.stream_chat_events(request)
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/confirm-action",
    response_model=ConfirmActionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_MUTATION_CONFIRM.value))],
)
async def confirm_action(
    request: ConfirmActionRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    claims: dict[str, Any] = Depends(get_current_user_claims),
    redis: Redis | None = Depends(get_optional_redis),
) -> ConfirmActionResponse:
    """Explicit human-in-the-loop confirmation or rejection of a pending AI mutation."""
    org_id_str = claims.get("org_id")
    org_id = uuid.UUID(org_id_str) if org_id_str else None

    perms = claims.get("permissions")
    if perms is None:
        if org_id:
            rbac_service = RbacService(db, redis=redis)
            _, perms = await rbac_service.get_user_roles_and_permissions(
                user_id, org_id, tenant_id=tenant_id
            )
        else:
            perms = []

    user_permissions: set[str] = set(perms)
    is_superuser: bool = bool(claims.get("is_superuser", False))

    return await AICopilotService.confirm_action(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        user_permissions=user_permissions,
        is_superuser=is_superuser,
        request=request,
    )


@router.get(
    "/conversations",
    response_model=AIConversationListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_CONVERSATIONS_MANAGE.value))],
)
async def list_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AIConversationListResponse:
    """List active multi-turn conversations for the current user."""
    items = await AICopilotService.list_conversations(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )
    return AIConversationListResponse(
        items=[AIConversationRead.model_validate(c) for c in items],
        total=len(items),
    )


@router.post(
    "/conversations",
    response_model=AIConversationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.AI_CONVERSATIONS_MANAGE.value))],
)
async def create_conversation(
    data: AIConversationCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    claims: dict[str, Any] = Depends(get_current_user_claims),
) -> AIConversationRead:
    """Explicitly create a new conversation thread."""
    org_id_str = claims.get("org_id")
    org_id = uuid.UUID(org_id_str) if org_id_str else None

    conv = await AICopilotService.create_conversation(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        organization_id=org_id,
        data=data,
    )
    return AIConversationRead.model_validate(conv)


@router.get(
    "/conversations/{conversation_id}",
    response_model=AIConversationRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_CONVERSATIONS_MANAGE.value))],
)
async def get_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AIConversationRead:
    """Retrieve details for a single conversation."""
    conv = await AICopilotService.get_conversation(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
    )
    return AIConversationRead.model_validate(conv)


@router.patch(
    "/conversations/{conversation_id}",
    response_model=AIConversationRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_CONVERSATIONS_MANAGE.value))],
)
async def update_conversation(
    conversation_id: uuid.UUID,
    data: AIConversationUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AIConversationRead:
    """Update conversation title, pinned status, or metadata."""
    conv = await AICopilotService.update_conversation(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
        data=data,
    )
    return AIConversationRead.model_validate(conv)


@router.delete(
    "/conversations/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission(PermissionCode.AI_CONVERSATIONS_MANAGE.value))],
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> None:
    """Archive / soft-delete conversation."""
    await AICopilotService.delete_conversation(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
    )


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=AIMessageListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_CONVERSATIONS_MANAGE.value))],
)
async def list_conversation_messages(
    conversation_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
) -> AIMessageListResponse:
    """Retrieve full chronological message history for a conversation."""
    # Ensure conversation belongs to user
    await AICopilotService.get_conversation(
        db=db,
        tenant_id=tenant_id,
        user_id=user_id,
        conversation_id=conversation_id,
    )
    msgs = await AICopilotService.get_messages(
        db=db,
        tenant_id=tenant_id,
        conversation_id=conversation_id,
        skip=skip,
        limit=limit,
    )
    return AIMessageListResponse(
        items=[AIMessageRead.model_validate(m) for m in msgs],
        total=len(msgs),
    )
