"""Server-Sent Events (SSE) Streaming Service for Copilot."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from app.modules.ai.gateway.gateway import ai_gateway
from app.modules.ai.schemas.copilot import CopilotChatRequest
from app.modules.ai.schemas.gateway import (
    ChatCompletionRequest,
    ChatMessage,
    MessageRole,
)
from app.modules.ai.security.guardrails import AIGuardrails

logger = logging.getLogger("vertexerp.ai.services.streaming")


class CopilotStreamingService:
    """Streams token chunks and tool status via Server-Sent Events (SSE)."""

    @staticmethod
    async def stream_chat_events(
        request: CopilotChatRequest,
    ) -> AsyncIterator[str]:
        """Stream JSON chunks formatted for SSE clients."""
        # 1. Inspect Guardrails
        guardrail = AIGuardrails.inspect_input(request.message)
        if not guardrail.is_safe:
            refusal_payload = {
                "event": "error",
                "data": {
                    "error": guardrail.reason,
                    "content": f"Security restriction: {guardrail.reason}",
                },
            }
            yield f"data: {json.dumps(refusal_payload)}\n\n"
            yield "data: [DONE]\n\n"
            return

        messages = [ChatMessage(role=MessageRole.USER, content=guardrail.sanitized_prompt)]
        gw_req = ChatCompletionRequest(
            model=request.model,
            provider=request.provider,
            messages=messages,
            stream=True,
        )

        try:
            async for chunk in ai_gateway.chat_completion_stream(gw_req):
                for choice in chunk.choices:
                    if choice.delta.content:
                        payload = {
                            "event": "token",
                            "data": {
                                "delta": choice.delta.content,
                            },
                        }
                        yield f"data: {json.dumps(payload)}\n\n"
                    elif choice.delta.tool_calls:
                        for tc in choice.delta.tool_calls:
                            payload = {
                                "event": "tool_call",
                                "data": {
                                    "tool_name": tc.function.name,
                                    "tool_id": tc.id,
                                },
                            }
                            yield f"data: {json.dumps(payload)}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as exc:
            logger.error(f"Streaming error: {str(exc)}", exc_info=True)
            err_payload = {"event": "error", "data": {"error": str(exc)}}
            yield f"data: {json.dumps(err_payload)}\n\n"
            yield "data: [DONE]\n\n"
