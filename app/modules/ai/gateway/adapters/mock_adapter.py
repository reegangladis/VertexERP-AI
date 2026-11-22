"""Deterministic Mock AI Provider Adapter for robust testing and local development."""

from __future__ import annotations

import asyncio
import hashlib
import json
import time
import uuid
from collections.abc import AsyncIterator
from typing import Any

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


class MockAIProviderAdapter(BaseAIAdapter):
    """Deterministic Mock AI Provider Adapter."""

    def __init__(
        self,
        default_model: str = "mock-gpt-4o",
        simulated_delay_seconds: float = 0.0,
    ):
        super().__init__()
        self._default_model = default_model
        self.simulated_delay_seconds = simulated_delay_seconds

    @property
    def provider_name(self) -> str:
        return "mock"

    def _check_simulation_flags(self, model: str | None) -> None:
        """Check for simulated errors or timeouts based on model name."""
        model_str = (model or self._default_model).lower()
        if "timeout" in model_str:
            raise TimeoutError("Simulated LLM provider request timeout")
        if "error" in model_str or "fail" in model_str or "500" in model_str:
            raise RuntimeError("Simulated LLM upstream provider internal server error (500)")

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        start_time = time.perf_counter()
        self._check_simulation_flags(request.model)

        if self.simulated_delay_seconds > 0:
            await asyncio.sleep(self.simulated_delay_seconds)

        model = request.model or self._default_model
        last_message = (
            request.messages[-1]
            if request.messages
            else ChatMessage(role=MessageRole.USER, content="")
        )
        content_text = last_message.content or ""

        # Check if the prompt triggers a tool call simulation
        tool_calls: list[ToolCall] | None = None
        finish_reason = "stop"
        response_text = f"Mock response to: {content_text}"

        if request.tools and len(request.tools) > 0:
            # Check if user message or context hints at tool usage
            for tool_def in request.tools:
                fn_name = tool_def.function.name
                if fn_name.lower() in content_text.lower() or any(
                    kw in content_text.lower()
                    for kw in [
                        "check",
                        "get",
                        "find",
                        "create",
                        "draft",
                        "stock",
                        "invoice",
                        "deal",
                        "headcount",
                        "transfer",
                    ]
                ):
                    # Trigger simulated tool call
                    tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
                    dummy_args = {}
                    if "stock" in fn_name or "product" in fn_name:
                        dummy_args = {"product_sku": "SKU-TEST-001"}
                    elif "invoice" in fn_name or "bill" in fn_name:
                        dummy_args = {"invoice_number": "INV-2026-001", "limit": 5}
                    elif "deal" in fn_name:
                        dummy_args = {"title": "Q3 Enterprise License", "amount": 50000.0}
                    elif "transfer" in fn_name:
                        dummy_args = {
                            "source_location": "Main Warehouse",
                            "target_location": "Branch A",
                            "quantity": 10,
                        }
                    elif "headcount" in fn_name or "hr" in fn_name:
                        dummy_args = {"department": "Engineering"}

                    tool_calls = [
                        ToolCall(
                            id=tool_call_id,
                            type="function",
                            function=FunctionCall(
                                name=fn_name,
                                arguments=json.dumps(dummy_args),
                            ),
                        )
                    ]
                    finish_reason = "tool_calls"
                    response_text = ""
                    break

        prompt_tokens = self.estimate_tokens(request.messages)
        completion_tokens = self.estimate_tokens(response_text) if response_text else 20
        total_tokens = prompt_tokens + completion_tokens
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ChatCompletionResponse(
            id=f"mock-{uuid.uuid4().hex[:12]}",
            provider="mock",
            model=model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(
                        role=MessageRole.ASSISTANT,
                        content=response_text if response_text else None,
                        tool_calls=tool_calls,
                    ),
                    finish_reason=finish_reason,
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
        self._check_simulation_flags(request.model)
        model = request.model or self._default_model
        req_id = f"mock-chunk-{uuid.uuid4().hex[:8]}"

        last_message = (
            request.messages[-1]
            if request.messages
            else ChatMessage(role=MessageRole.USER, content="")
        )
        content_text = last_message.content or ""

        # Check if tools are requested
        if request.tools and any(
            kw in content_text.lower()
            for kw in ["check", "get", "find", "create", "draft", "stock", "invoice", "deal"]
        ):
            tool_def = request.tools[0]
            fn_name = tool_def.function.name
            tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
            yield ChatCompletionChunk(
                id=req_id,
                provider="mock",
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(
                            role=MessageRole.ASSISTANT,
                            tool_calls=[
                                ToolCall(
                                    id=tool_call_id,
                                    type="function",
                                    function=FunctionCall(
                                        name=fn_name,
                                        arguments=json.dumps({"query": content_text}),
                                    ),
                                )
                            ],
                        ),
                        finish_reason="tool_calls",
                    )
                ],
            )
            return

        words = f"Mock streaming response: {content_text}".split(" ")
        for i, word in enumerate(words):
            chunk_text = word + (" " if i < len(words) - 1 else "")
            yield ChatCompletionChunk(
                id=req_id,
                provider="mock",
                model=model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(
                            role=MessageRole.ASSISTANT if i == 0 else None,
                            content=chunk_text,
                        ),
                        finish_reason=None if i < len(words) - 1 else "stop",
                    )
                ],
            )
            if self.simulated_delay_seconds > 0:
                await asyncio.sleep(self.simulated_delay_seconds)

    async def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        self._check_simulation_flags(request.model)
        model = request.model or "mock-text-embedding-3-small"
        inputs = [request.input] if isinstance(request.input, str) else request.input

        items: list[EmbeddingItem] = []
        total_prompt_tokens = 0

        for idx, text in enumerate(inputs):
            # Generate deterministic 1536-dimensional mock embedding vector from hash
            hasher = hashlib.sha256(text.encode("utf-8")).digest()
            # Construct 1536 float elements deterministically
            embedding: list[float] = []
            for i in range(1536):
                byte_val = hasher[i % len(hasher)]
                embedding.append(round((float(byte_val) / 255.0) * 2.0 - 1.0, 6))

            items.append(EmbeddingItem(index=idx, embedding=embedding))
            total_prompt_tokens += max(1, len(text) // 4)

        return EmbeddingResponse(
            provider="mock",
            model=model,
            data=items,
            usage=TokenUsage(
                prompt_tokens=total_prompt_tokens,
                completion_tokens=0,
                total_tokens=total_prompt_tokens,
            ),
            cost_usd=0.0,
        )

    async def structured_output(self, request: StructuredOutputRequest) -> StructuredOutputResponse:
        self._check_simulation_flags(request.model)
        model = request.model or self._default_model

        # Build mock dictionary satisfying schema properties if present
        properties = request.response_schema.get("properties", {})
        parsed_data: dict[str, Any] = {}
        for key, prop_def in properties.items():
            prop_type = prop_def.get("type", "string")
            if prop_type == "string":
                parsed_data[key] = f"Mock {key}"
            elif prop_type == "number" or prop_type == "integer":
                parsed_data[key] = 100
            elif prop_type == "boolean":
                parsed_data[key] = True
            elif prop_type == "array":
                parsed_data[key] = ["item1", "item2"]
            else:
                parsed_data[key] = {}

        raw_content = json.dumps(parsed_data, indent=2)
        prompt_tokens = self.estimate_tokens(request.messages)
        completion_tokens = self.estimate_tokens(raw_content)

        return StructuredOutputResponse(
            id=f"mock-struct-{uuid.uuid4().hex[:8]}",
            provider="mock",
            model=model,
            parsed=parsed_data,
            raw_content=raw_content,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            cost_usd=0.0,
        )
