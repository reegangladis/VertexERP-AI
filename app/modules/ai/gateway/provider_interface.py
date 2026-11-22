"""Abstract interface for LLM providers in VertexERP AI V2."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.modules.ai.schemas.gateway import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    EmbeddingRequest,
    EmbeddingResponse,
    StructuredOutputRequest,
    StructuredOutputResponse,
)


class LLMProviderInterface(ABC):
    """Abstract interface defining the contract that all LLM provider adapters must implement."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the unique identifier of the provider (e.g. 'openai', 'anthropic', 'gemini', 'mock')."""
        pass

    @abstractmethod
    async def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        """Execute a synchronous/non-streaming chat completion."""
        pass

    @abstractmethod
    async def chat_completion_stream(
        self, request: ChatCompletionRequest
    ) -> AsyncIterator[ChatCompletionChunk]:
        """Stream chat completion chunks."""
        pass

    @abstractmethod
    async def create_embeddings(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate vector embeddings for input text."""
        pass

    @abstractmethod
    async def structured_output(self, request: StructuredOutputRequest) -> StructuredOutputResponse:
        """Generate a response strictly conforming to a JSON Schema."""
        pass
