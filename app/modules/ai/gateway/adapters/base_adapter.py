"""Base Adapter implementation with shared utilities."""

from __future__ import annotations

from app.modules.ai.gateway.cost_tracker import CostTracker
from app.modules.ai.gateway.provider_interface import LLMProviderInterface
from app.modules.ai.schemas.gateway import (
    ChatMessage,
)


class BaseAIAdapter(LLMProviderInterface):
    """Base class providing common functionality for provider adapters."""

    def __init__(self, timeout_seconds: float = 30.0):
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def estimate_tokens(messages_or_text: str | list[ChatMessage]) -> int:
        """Rough token count estimator (4 chars ~= 1 token) when exact metrics unavailable."""
        if isinstance(messages_or_text, str):
            return max(1, len(messages_or_text) // 4)
        total_chars = sum(len(m.content or "") + len(m.name or "") for m in messages_or_text)
        return max(1, total_chars // 4)

    def calculate_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        return CostTracker.calculate_cost(
            self.provider_name, model, prompt_tokens, completion_tokens
        )
