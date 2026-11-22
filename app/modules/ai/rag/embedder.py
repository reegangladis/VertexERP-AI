"""RAG Embedder generating vector embeddings via AIGateway."""

from __future__ import annotations

import logging

from app.modules.ai.gateway.gateway import ai_gateway
from app.modules.ai.schemas.gateway import EmbeddingRequest

logger = logging.getLogger("vertexerp.ai.rag.embedder")


class RAGEmbedder:
    """Batch vector embedding generator for RAG chunks and search queries."""

    def __init__(self, provider: str | None = None, model: str | None = None, batch_size: int = 32):
        self.provider = provider
        self.model = model
        self.batch_size = batch_size

    async def embed_texts(self, texts: list[str]) -> tuple[list[list[float]], int, float]:
        """Generate vector embeddings for a list of strings in batches.

        Returns:
            Tuple of (embeddings_list, total_tokens, cost_usd)
        """
        if not texts:
            return [], 0, 0.0

        all_embeddings: list[list[float]] = []
        total_tokens = 0
        total_cost = 0.0

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            req = EmbeddingRequest(
                input=batch,
                provider=self.provider,
                model=self.model,
            )
            resp = await ai_gateway.create_embeddings(req)

            # Sort items by index to guarantee input order preservation
            sorted_items = sorted(resp.data, key=lambda x: x.index)
            for item in sorted_items:
                all_embeddings.append(item.embedding)

            total_tokens += resp.usage.total_tokens
            total_cost += resp.cost_usd

        return all_embeddings, total_tokens, total_cost

    async def embed_single_query(self, query: str) -> list[float]:
        """Generate vector embedding for a single search query."""
        embeddings, _, _ = await self.embed_texts([query])
        if not embeddings:
            raise RuntimeError("Failed to generate embedding for query.")
        return embeddings[0]
