"""AI Gateway central router and orchestrator with Prometheus Telemetry."""

from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator

from app.core.config import settings
from app.core.metrics import metrics_registry
from app.modules.ai.gateway.adapters.anthropic_adapter import AnthropicProviderAdapter
from app.modules.ai.gateway.adapters.gemini_adapter import GeminiProviderAdapter
from app.modules.ai.gateway.adapters.mock_adapter import MockAIProviderAdapter
from app.modules.ai.gateway.adapters.openai_adapter import OpenAIProviderAdapter
from app.modules.ai.gateway.provider_interface import LLMProviderInterface
from app.modules.ai.schemas.gateway import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StructuredOutputRequest,
    StructuredOutputResponse,
)

logger = logging.getLogger("vertexerp.ai.gateway")


class AIGateway:
    """Central AI Gateway managing provider adapters, routing, resilience, and metrics."""

    def __init__(self):
        self._adapters: dict[str, LLMProviderInterface] = {}
        self._initialize_adapters()

    def _initialize_adapters(self) -> None:
        """Initialize provider adapters from app configuration."""
        timeout = getattr(settings, "AI_REQUEST_TIMEOUT_SECONDS", 30.0)

        # Mock adapter
        self.register_adapter(
            MockAIProviderAdapter(
                default_model=getattr(settings, "AI_DEFAULT_MODEL", "mock-gpt-4o")
            )
        )

        # OpenAI adapter
        openai_key = getattr(settings, "OPENAI_API_KEY", "")
        self.register_adapter(
            OpenAIProviderAdapter(
                api_key=openai_key,
                timeout_seconds=timeout,
            )
        )

        # Anthropic adapter
        anthropic_key = getattr(settings, "ANTHROPIC_API_KEY", "")
        self.register_adapter(
            AnthropicProviderAdapter(
                api_key=anthropic_key,
                timeout_seconds=timeout,
            )
        )

        # Gemini adapter
        gemini_key = getattr(settings, "GEMINI_API_KEY", "")
        self.register_adapter(
            GeminiProviderAdapter(
                api_key=gemini_key,
                timeout_seconds=timeout,
            )
        )

    def register_adapter(self, adapter: LLMProviderInterface) -> None:
        """Register a new or custom LLM provider adapter."""
        self._adapters[adapter.provider_name.lower()] = adapter
        logger.info(f"Registered AI provider adapter: {adapter.provider_name}")

    def get_adapter(self, provider_name: str | None = None) -> LLMProviderInterface:
        """Retrieve provider adapter by name or return the configured default."""
        name = (provider_name or getattr(settings, "AI_DEFAULT_PROVIDER", "mock")).lower()

        production = (
            settings.APP_ENV.value == "production"
            and settings.DEPLOYMENT_MODE.lower() == "production"
        )

        if name not in self._adapters:
            if production:
                raise RuntimeError(f"AI provider '{name}' is not configured")
            logger.warning("Provider '%s' not found; using mock provider in non-production", name)
            name = "mock"

        adapter = self._adapters[name]
        if name in ("openai", "anthropic", "gemini"):
            key = getattr(adapter, "api_key", "")
            if not key:
                if production:
                    raise RuntimeError(
                        f"API key for AI provider '{name}' is not configured in production"
                    )
                logger.warning(
                    "Provider '%s' has no API key; using mock provider in non-production", name
                )
                return self._adapters["mock"]

        if production and name == "mock":
            raise RuntimeError("Mock AI provider is disabled in production")

        return adapter

    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute chat completion through selected provider adapter and record telemetry."""
        adapter = self.get_adapter(request.provider)
        provider_name = adapter.provider_name
        model_name = request.model or getattr(settings, "AI_DEFAULT_MODEL", "default")
        start_time = time.perf_counter()

        try:
            response = await adapter.chat_completion(request)
            duration = time.perf_counter() - start_time

            # Record telemetry
            metrics_registry.ai_requests_total.inc(
                labels={"provider": provider_name, "model": model_name, "status": "success"}
            )
            metrics_registry.ai_request_duration_seconds.observe(
                duration, labels={"provider": provider_name, "model": model_name}
            )

            # Record tokens if present in usage
            if hasattr(response, "usage") and response.usage:
                prompt_tokens = getattr(response.usage, "prompt_tokens", 0)
                completion_tokens = getattr(response.usage, "completion_tokens", 0)
                metrics_registry.ai_tokens_consumed_total.inc(
                    amount=prompt_tokens,
                    labels={"provider": provider_name, "model": model_name, "type": "prompt"},
                )
                metrics_registry.ai_tokens_consumed_total.inc(
                    amount=completion_tokens,
                    labels={"provider": provider_name, "model": model_name, "type": "completion"},
                )

            return response
        except Exception:
            duration = time.perf_counter() - start_time
            metrics_registry.ai_requests_total.inc(
                labels={"provider": provider_name, "model": model_name, "status": "error"}
            )
            metrics_registry.ai_request_duration_seconds.observe(
                duration, labels={"provider": provider_name, "model": model_name}
            )
            raise

    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        """Stream chat completion chunks through selected provider adapter."""
        adapter = self.get_adapter(request.provider)
        async for chunk in adapter.chat_completion_stream(request):
            yield chunk

    async def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate vector embeddings through selected provider adapter."""
        adapter = self.get_adapter(request.provider)
        provider_name = adapter.provider_name
        model_name = request.model or "embedding"
        start_time = time.perf_counter()
        try:
            response = await adapter.create_embeddings(request)
            duration = time.perf_counter() - start_time
            metrics_registry.ai_requests_total.inc(
                labels={"provider": provider_name, "model": model_name, "status": "success"}
            )
            metrics_registry.ai_request_duration_seconds.observe(
                duration, labels={"provider": provider_name, "model": model_name}
            )
            return response
        except Exception:
            duration = time.perf_counter() - start_time
            metrics_registry.ai_requests_total.inc(
                labels={"provider": provider_name, "model": model_name, "status": "error"}
            )
            metrics_registry.ai_request_duration_seconds.observe(
                duration, labels={"provider": provider_name, "model": model_name}
            )
            raise

    async def structured_output(self, request: StructuredOutputRequest) -> StructuredOutputResponse:
        """Generate structured output through selected provider adapter."""
        adapter = self.get_adapter(request.provider)
        return await adapter.structured_output(request)


# Singleton AI Gateway instance
ai_gateway = AIGateway()
