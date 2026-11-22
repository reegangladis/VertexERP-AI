"""OpenAI Provider Adapter for VertexERP AI V2."""

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
    EmbeddingItem,
    EmbeddingRequest,
    EmbeddingResponse,
    FunctionCall,
    MessageRole,
    StructuredOutputRequest,
    StructuredOutputResponse,
    TokenUsage,
    ToolCall,
)


class OpenAIProviderAdapter(BaseAIAdapter):
    """OpenAI API provider adapter using standard REST endpoints."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        default_model: str = "gpt-4o",
        timeout_seconds: float = 30.0,
    ):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = api_key or ""
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "openai"

    def _get_headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _convert_messages(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        result = []
        for msg in messages:
            item: dict[str, Any] = {
                "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role)
            }
            if msg.content is not None:
                item["content"] = msg.content
            if msg.name:
                item["name"] = msg.name
            if msg.tool_call_id:
                item["tool_call_id"] = msg.tool_call_id
            if msg.tool_calls:
                item["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in msg.tool_calls
                ]
            result.append(item)
        return result

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.perf_counter()
        model = request.model or self.default_model
        payload: dict[str, Any] = {
            "model": model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "stream": False,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.tools:
            payload["tools"] = [t.model_dump() for t in request.tools]
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice
        if request.response_format:
            payload["response_format"] = request.response_format

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choices = []
        for c in data.get("choices", []):
            msg_data = c.get("message", {})
            tool_calls = None
            if "tool_calls" in msg_data and msg_data["tool_calls"]:
                tool_calls = [
                    ToolCall(
                        id=tc["id"],
                        type=tc.get("type", "function"),
                        function=FunctionCall(
                            name=tc["function"]["name"],
                            arguments=tc["function"]["arguments"],
                        ),
                    )
                    for tc in msg_data["tool_calls"]
                ]

            choices.append(
                ChatCompletionChoice(
                    index=c.get("index", 0),
                    message=ChatMessage(
                        role=MessageRole(msg_data.get("role", "assistant")),
                        content=msg_data.get("content"),
                        tool_calls=tool_calls,
                    ),
                    finish_reason=c.get("finish_reason", "stop"),
                )
            )

        raw_usage = data.get("usage", {})
        prompt_tokens = raw_usage.get("prompt_tokens", self.estimate_tokens(request.messages))
        completion_tokens = raw_usage.get("completion_tokens", 0)
        total_tokens = raw_usage.get("total_tokens", prompt_tokens + completion_tokens)
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatCompletionResponse(
            id=data.get("id", f"chatcmpl-{int(time.time())}"),
            provider=self.provider_name,
            model=model,
            choices=choices,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            cost_usd=cost,
            latency_ms=round(latency_ms, 2),
        )

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        model = request.model or self.default_model
        payload: dict[str, Any] = {
            "model": model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "stream": True,
        }
        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens
        if request.tools:
            payload["tools"] = [t.model_dump() for t in request.tools]
        if request.tool_choice:
            payload["tool_choice"] = request.tool_choice

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    if data_str == "[DONE]":
                        break
                    try:
                        chunk_json = json.loads(data_str)
                        choices = []
                        for c in chunk_json.get("choices", []):
                            delta_data = c.get("delta", {})
                            tool_calls = None
                            if "tool_calls" in delta_data:
                                tool_calls = [
                                    ToolCall(
                                        id=tc.get("id", ""),
                                        type=tc.get("type", "function"),
                                        function=FunctionCall(
                                            name=tc.get("function", {}).get("name", ""),
                                            arguments=tc.get("function", {}).get("arguments", ""),
                                        ),
                                    )
                                    for tc in delta_data["tool_calls"]
                                ]
                            choices.append(
                                ChatCompletionChunkChoice(
                                    index=c.get("index", 0),
                                    delta=ChatCompletionChunkDelta(
                                        role=MessageRole(delta_data.get("role"))
                                        if delta_data.get("role")
                                        else None,
                                        content=delta_data.get("content"),
                                        tool_calls=tool_calls,
                                    ),
                                    finish_reason=c.get("finish_reason"),
                                )
                            )
                        yield ChatCompletionChunk(
                            id=chunk_json.get("id", "chunk"),
                            provider=self.provider_name,
                            model=model,
                            choices=choices,
                        )
                    except json.JSONDecodeError:
                        continue

    async def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or "text-embedding-3-small"
        payload = {
            "model": model,
            "input": request.input,
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/embeddings",
                headers=self._get_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        items = [
            EmbeddingItem(index=item["index"], embedding=item["embedding"])
            for item in data.get("data", [])
        ]
        raw_usage = data.get("usage", {})
        prompt_tokens = raw_usage.get("prompt_tokens", 0)
        cost = self.calculate_cost(model, prompt_tokens, 0)

        return EmbeddingResponse(
            provider=self.provider_name,
            model=model,
            data=items,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=0,
                total_tokens=prompt_tokens,
            ),
            cost_usd=cost,
        )

    async def structured_output(self, request: StructuredOutputRequest) -> StructuredOutputResponse:
        model = request.model or self.default_model
        payload = {
            "model": model,
            "messages": self._convert_messages(request.messages),
            "temperature": request.temperature,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": request.schema_name,
                    "description": request.schema_description or "",
                    "schema": request.response_schema,
                    "strict": True,
                },
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]
        raw_content = choice["message"]["content"]
        parsed = json.loads(raw_content)

        raw_usage = data.get("usage", {})
        prompt_tokens = raw_usage.get("prompt_tokens", 0)
        completion_tokens = raw_usage.get("completion_tokens", 0)
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

        return StructuredOutputResponse(
            id=data.get("id", f"struct-{int(time.time())}"),
            provider=self.provider_name,
            model=model,
            parsed=parsed,
            raw_content=raw_content,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            cost_usd=cost,
        )
