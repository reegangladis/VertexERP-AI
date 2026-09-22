"""Cost tracking and pricing calculator for AI model invocations."""

from __future__ import annotations

# Pricing in USD per 1,000,000 tokens (Prompt, Completion)
# Based on current industry rates
MODEL_PRICING_PER_MILLION: dict[str, tuple[float, float]] = {
    # OpenAI
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-2024-08-06": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-3.5-turbo": (0.50, 1.50),
    "text-embedding-3-small": (0.02, 0.00),
    "text-embedding-3-large": (0.13, 0.00),
    # Anthropic
    "claude-3-5-sonnet-20241022": (3.00, 15.00),
    "claude-3-5-sonnet": (3.00, 15.00),
    "claude-3-5-haiku-20241022": (0.80, 4.00),
    "claude-3-5-haiku": (0.80, 4.00),
    "claude-3-opus-20240229": (15.00, 75.00),
    # Google Gemini
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-2.0-flash-exp": (0.00, 0.00),
    "text-embedding-004": (0.025, 0.00),
    # Mock / Default
    "mock-gpt-4o": (0.00, 0.00),
    "mock-default": (0.00, 0.00),
}


class CostTracker:
    """Calculates dollar costs for prompt and completion token usage."""

    @staticmethod
    def calculate_cost(
        provider: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculate total USD cost for the given model and token counts.

        Returns cost rounded to 6 decimal places.
        """
        model_key = model.lower()
        pricing = None

        for key, (prompt_rate, completion_rate) in MODEL_PRICING_PER_MILLION.items():
            if key in model_key or model_key in key:
                pricing = (prompt_rate, completion_rate)
                break

        if not pricing:
            # Default fallback rates (similar to gpt-4o-mini)
            pricing = (0.15, 0.60)

        prompt_cost = (prompt_tokens / 1_000_000.0) * pricing[0]
        completion_cost = (completion_tokens / 1_000_000.0) * pricing[1]
        total_cost = prompt_cost + completion_cost
        return round(total_cost, 6)
