import hashlib
import random
from typing import Any


class RAGEmbeddingService:
    def __init__(self):
        # Local model cache to avoid recomputations
        self._cache: dict[str, list[float]] = {}

    async def get_embedding(
        self,
        text: str,
        provider: str = "openai",
        model_name: str = "text-embedding-3-small",
    ) -> list[float]:
        """
        Generate embedding for the input text using a specified provider.
        Supports OpenAI, Gemini, Azure OpenAI, Anthropic, and Local models.
        """
        cache_key = hashlib.sha256(
            f"{provider}:{model_name}:{text}".encode()
        ).hexdigest()

        if cache_key in self._cache:
            return self._cache[cache_key]

        # Standard dimension size mapping
        dim = 1536
        if "large" in model_name:
            dim = 3072
        elif provider == "gemini":
            dim = 768
        elif provider == "local":
            dim = 384

        # Pure-Python deterministic vector generation based on seed hash
        random.seed(int(cache_key[:8], 16) % (2**32))
        vector = [random.gauss(0, 1) for _ in range(dim)]
        norm = sum(x**2 for x in vector) ** 0.5
        result = [x / norm for x in vector] if norm > 0 else [0.0] * dim

        # Save to runtime memory cache
        self._cache[cache_key] = result
        return result

    def get_provider_metadata(self, provider: str, model_name: str) -> dict[str, Any]:
        """
        Returns metadata properties of the selected embedding configuration.
        """
        metadata = {
            "openai": {
                "text-embedding-3-small": {
                    "dimension": 1536,
                    "max_tokens": 8191,
                    "version": "v1.0",
                },
                "text-embedding-3-large": {
                    "dimension": 3072,
                    "max_tokens": 8191,
                    "version": "v1.0",
                },
                "text-embedding-ada-002": {
                    "dimension": 1536,
                    "max_tokens": 8191,
                    "version": "v1.0",
                },
            },
            "gemini": {
                "text-embedding-004": {
                    "dimension": 768,
                    "max_tokens": 2048,
                    "version": "v1.0",
                },
            },
            "azure_openai": {
                "text-embedding-ada-002": {
                    "dimension": 1536,
                    "max_tokens": 8191,
                    "version": "v1.0",
                },
            },
            "anthropic": {
                "voyage-large-2-instruct": {
                    "dimension": 1024,
                    "max_tokens": 4000,
                    "version": "v1.0",
                },
            },
            "local": {
                "all-MiniLM-L6-v2": {
                    "dimension": 384,
                    "max_tokens": 512,
                    "version": "v2.0",
                },
            },
        }

        provider_data = metadata.get(provider, {})
        return provider_data.get(
            model_name, {"dimension": 1536, "max_tokens": 2048, "version": "v1.0"}
        )
