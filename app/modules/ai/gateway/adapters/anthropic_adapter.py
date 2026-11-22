"""Anthropic Claude Provider Adapter for VertexERP AI V2."""

from __future__ import annotations

import json
import time
from collections.abc import AsyncIterator
from typing import Any

import httpx

from app.modules.ai.gateway.adapters.base_adapter import BaseAIAdapter
from app.modules.ai.schemas.gateway import (
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionChunkChoice,
    ChatCompletionChunkDelta,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    EmbeddingRequest,
    EmbeddingResponse,
    FunctionCall,
    MessageRole,
    StructuredOutputRequest,
    StructuredOutputResponse,
    TokenUsage,
    ToolCall,
)


class AnthropicProviderAdapter(BaseAIAdapter):
    """Anthropic Claude API provider adapter."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.anthropic.com/v1",
        default_model: str = "claude-3-5-sonnet-20241022",
        timeout_seconds: float = 30.0,
    ):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = api_key or ""
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers

    def _convert_messages(
        self, messages: list[ChatMessage]
    ) -> tuple[str | None, list[dict[str, Any]]]:
        system_prompt: str | None = None
        anthropic_messages: list[dict[str, Any]] = []

        for msg in messages:
            if msg.role == MessageRole.SYSTEM:
                system_prompt = msg.content
                continue

            role = "user" if msg.role == MessageRole.USER else "assistant"
            content: Any = msg.content or ""

            if msg.role == MessageRole.TOOL:
                anthropic_messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": msg.tool_call_id or "",
                                "content": msg.content or "",
                            }
                        ],
                    }
                )
                continue

            if msg.tool_calls:
                content_blocks: list[dict[str, Any]] = []
                if msg.content:
                    content_blocks.append({"type": "text", "text": msg.content})
                for tc in msg.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    content_blocks.append(
                        {
                            "type": "tool_use",
                            "id": tc.id,
                            "name": tc.function.name,
                            "input": args,
                        }
                    )
                anthropic_messages.append({"role": role, "content": content_blocks})
            else:
                anthropic_messages.append({"role": role, "content": content})

        return system_prompt, anthropic_messages

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.perf_counter()
        model = request.model or self.default_model
        system_prompt, messages = self._convert_messages(request.messages)

        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 2048,
            "temperature": request.temperature,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if request.tools:
            payload["tools"] = [
                {
                    "name": t.function.name,
                    "description": t.function.description or "",
                    "input_schema": t.function.parameters or {"type": "object", "properties": {}},
                }
                for t in request.tools
            ]

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        # Parse response
        text_parts = []
        tool_calls = []
        for block in data.get("content", []):
            if block.get("type") == "text":
                text_parts.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                tool_calls.append(
                    ToolCall(
                        id=block["id"],
                        type="function",
                        function=FunctionCall(
                            name=block["name"],
                            arguments=json.dumps(block.get("input", {})),
                        ),
                    )
                )

        full_text = "".join(text_parts)
        usage_data = data.get("usage", {})
        prompt_tokens = usage_data.get("input_tokens", self.estimate_tokens(request.messages))
        completion_tokens = usage_data.get("output_tokens", self.estimate_tokens(full_text))
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatCompletionResponse(
            id=data.get("id", f"msg-{int(time.time())}"),
            provider=self.provider_name,
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT,
                        content=full_text if full_text else None,
                        tool_calls=tool_calls if tool_calls else None,
                    ),
                    finish_reason=data.get("stop_reason", "stop"),
                )
            ],
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            cost_usd=cost,
            latency_ms=round(latency_ms, 2),
        )

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        model = request.model or self.default_model
        system_prompt, messages = self._convert_messages(request.messages)
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": request.max_tokens or 2048,
            "temperature": request.temperature,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with (
            httpx.AsyncClient(timeout=self.timeout_seconds) as client,
            client.stream(
                "POST",
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
            ) as response,
        ):
            response.raise_for_status()
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data_str = line[6:].strip()
                try:
                    event = json.loads(data_str)
                    event_type = event.get("type")
                    if event_type == "content_block_delta":
                        delta = event.get("delta", {})
                        if delta.get("type") == "text_delta":
                            yield ChatCompletionChunk(
                                id=event.get("id", "chunk"),
                                provider=self.provider_name,
                                model=model,
                                choices=[
                                    ChatCompletionChunkChoice(
                                        index=0,
                                        delta=ChatCompletionChunkDelta(
                                            role=MessageRole.ASSISTANT,
                                            content=delta.get("text", ""),
                                        ),
                                    )
                                ],
                            )
                    elif event_type == "message_stop":
                        yield ChatCompletionChunk(
                            id="stop",
                            provider=self.provider_name,
                            model=model,
                            choices=[
                                ChatCompletionChunkChoice(
                                    index=0,
                                    delta=ChatCompletionChunkDelta(),
                                    finish_reason="stop",
                                )
                            ],
                        )
                except json.JSONDecodeError:
                    continue

    async def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        # Anthropic does not provide a native embeddings endpoint; raise informative exception or fallback
        raise NotImplementedError(
            "Anthropic does not offer a standalone embeddings API. Use OpenAI or Gemini embeddings."
        )

    async def structured_output(self, request: StructuredOutputRequest) -> StructuredOutputResponse:
        # Anthropic tool-assisted structured output
        tool = {
            "name": request.schema_name,
            "description": request.schema_description
            or "Generate structured output matching schema",
            "input_schema": request.response_schema,
        }
        system_prompt, messages = self._convert_messages(request.messages)
        payload = {
            "model": request.model or self.default_model,
            "messages": messages,
            "max_tokens": 2048,
            "tools": [tool],
            "tool_choice": {"type": "tool", "name": request.schema_name},
        }
        if system_prompt:
            payload["system"] = system_prompt

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/messages",
                headers=self._get_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        for block in data.get("content", []):
            if block.get("type") == "tool_use" and block.get("name") == request.schema_name:
                parsed_json = block.get("input", {})
                raw_str = json.dumps(parsed_json)
                usage_data = data.get("usage", {})
                prompt_tokens = usage_data.get("input_tokens", 0)
                completion_tokens = usage_data.get("output_tokens", 0)
                cost = self.calculate_cost(
                    request.model or self.default_model, prompt_tokens, completion_tokens
                )
                return StructuredOutputResponse(
                    id=data.get("id", f"struct-{int(time.time())}"),
                    provider=self.provider_name,
                    model=request.model or self.default_model,
                    parsed=parsed_json,
                    raw_content=raw_str,
                    usage=TokenUsage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    ),
                    cost_usd=cost,
                )

        raise ValueError("Anthropic did not return the expected structured tool call.")
