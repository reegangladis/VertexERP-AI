"""AI Gateway Direct Abstraction Endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.core.permissions import PermissionCode
from app.modules.ai.gateway.gateway import ai_gateway
from app.modules.ai.schemas.gateway import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StructuredOutputRequest,
    StructuredOutputResponse,
)
from app.modules.identity.api.dependencies import require_permission

router = APIRouter(prefix="/gateway", tags=["AI Gateway"])


@router.post(
    "/chat/completions",
    response_model=ChatCompletionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_COPILOT_USE.value))],
)
async def chat_completion(
    request: ChatCompletionRequest,
) -> ChatCompletionResponse:
    """Execute raw chat completion via decoupled AI Gateway."""
    return await ai_gateway.chat_completion(request)


@router.post(
    "/embeddings",
    response_model=EmbeddingResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_COPILOT_USE.value))],
)
async def create_embeddings(
    request: EmbeddingRequest,
) -> EmbeddingResponse:
    """Generate text vector embeddings via decoupled AI Gateway."""
    return await ai_gateway.create_embeddings(request)


@router.post(
    "/structured-output",
    response_model=StructuredOutputResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_COPILOT_USE.value))],
)
async def structured_output(
    request: StructuredOutputRequest,
) -> StructuredOutputResponse:
    """Generate structured JSON schema output via decoupled AI Gateway."""
    return await ai_gateway.structured_output(request)
