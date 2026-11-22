"""Google Gemini Provider Adapter for VertexERP AI V2."""

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


class GeminiProviderAdapter(BaseAIAdapter):
    """Google Gemini REST API adapter."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://generativelanguage.googleapis.com/v1beta",
        default_model: str = "gemini-1.5-flash",
        timeout_seconds: float = 30.0,
    ):
        super().__init__(timeout_seconds=timeout_seconds)
        self.api_key = api_key or ""
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _convert_messages(self, messages: list[ChatMessage]) -> list[dict[str, Any]]:
        contents = []
        for msg in messages:
            role = "user" if msg.role in (MessageRole.USER, MessageRole.SYSTEM) else "model"
            parts = []
            if msg.content:
                parts.append({"text": msg.content})
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    parts.append(
                        {
                            "functionCall": {
                                "name": tc.function.name,
                                "args": args,
                            }
                        }
                    )
            if parts:
                contents.append({"role": role, "parts": parts})
        return contents

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.perf_counter()
        model = request.model or self.default_model
        clean_model = model if model.startswith("models/") else f"models/{model}"

        payload: dict[str, Any] = {
            "contents": self._convert_messages(request.messages),
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens or 2048,
            },
        }

        url = f"{self.base_url}/{clean_model}:generateContent"
        params = {"key": self.api_key} if self.api_key else {}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        text_parts = []
        tool_calls = []

        if candidates:
            first_candidate = candidates[0]
            content_obj = first_candidate.get("content", {})
            for part in content_obj.get("parts", []):
                if "text" in part:
                    text_parts.append(part["text"])
                elif "functionCall" in part:
                    fc = part["functionCall"]
                    tool_calls.append(
                        ToolCall(
                            id=f"gemini_call_{int(time.time())}",
                            type="function",
                            function=FunctionCall(
                                name=fc["name"],
                                arguments=json.dumps(fc.get("args", {})),
                            ),
                        )
                    )

        full_text = "".join(text_parts)
        usage_meta = data.get("usageMetadata", {})
        prompt_tokens = usage_meta.get("promptTokenCount", self.estimate_tokens(request.messages))
        completion_tokens = usage_meta.get("candidatesTokenCount", self.estimate_tokens(full_text))
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatCompletionResponse(
            id=f"gemini-{int(time.time())}",
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
                    finish_reason="stop",
                )
            ],
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
        clean_model = model if model.startswith("models/") else f"models/{model}"
        payload: dict[str, Any] = {
            "contents": self._convert_messages(request.messages),
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens or 2048,
            },
        }

        url = f"{self.base_url}/{clean_model}:streamGenerateContent"
        params = {"key": self.api_key} if self.api_key else {}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            async with client.stream("POST", url, params=params, json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk_json = json.loads(line)
                        for candidate in chunk_json.get("candidates", []):
                            for part in candidate.get("content", {}).get("parts", []):
                                if "text" in part:
                                    yield ChatCompletionChunk(
                                        id=f"chunk-{int(time.time())}",
                                        provider=self.provider_name,
                                        model=model,
                                        choices=[
                                            ChatCompletionChunkChoice(
                                                index=0,
                                                delta=ChatCompletionChunkDelta(
                                                    role=MessageRole.ASSISTANT,
                                                    content=part["text"],
                                                ),
                                            )
                                        ],
                                    )
                    except json.JSONDecodeError:
                        continue

    async def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        model = request.model or "text-embedding-004"
        clean_model = model if model.startswith("models/") else f"models/{model}"
        input_text = request.input if isinstance(request.input, str) else "\n".join(request.input)

        url = f"{self.base_url}/{clean_model}:embedContent"
        params = {"key": self.api_key} if self.api_key else {}
        payload = {"content": {"parts": [{"text": input_text}]}}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()

        embedding_values = data.get("embedding", {}).get("values", [])
        prompt_tokens = self.estimate_tokens(input_text)
        cost = self.calculate_cost(model, prompt_tokens, 0)

        return EmbeddingResponse(
            provider=self.provider_name,
            model=model,
            data=[EmbeddingItem(index=0, embedding=embedding_values)],
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=0,
                total_tokens=prompt_tokens,
            ),
            cost_usd=cost,
        )

    async def structured_output(self, request: StructuredOutputRequest) -> StructuredOutputResponse:
        model = request.model or self.default_model
        clean_model = model if model.startswith("models/") else f"models/{model}"

        payload: dict[str, Any] = {
            "contents": self._convert_messages(request.messages),
            "generationConfig": {
                "response_mime_type": "application/json",
                "response_schema": request.response_schema,
                "temperature": request.temperature,
            },
        }

        url = f"{self.base_url}/{clean_model}:generateContent"
        params = {"key": self.api_key} if self.api_key else {}

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            resp = await client.post(url, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()

        candidates = data.get("candidates", [])
        raw_text = "{}"
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            if parts and "text" in parts[0]:
                raw_text = parts[0]["text"]

        parsed = json.loads(raw_text)
        usage_meta = data.get("usageMetadata", {})
        prompt_tokens = usage_meta.get("promptTokenCount", self.estimate_tokens(request.messages))
        completion_tokens = usage_meta.get("candidatesTokenCount", self.estimate_tokens(raw_text))
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)

        return StructuredOutputResponse(
            id=f"gemini-struct-{int(time.time())}",
            provider=self.provider_name,
            model=model,
            parsed=parsed,
            raw_content=raw_text,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            cost_usd=cost,
        )
