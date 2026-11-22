"""Dedicated worker for batch vector embeddings generation."""

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.rag.embedder import RAGEmbedder
from app.modules.jobs.models.job import BackgroundJob
from app.modules.jobs.workers.base import BaseWorker

logger = logging.getLogger("vertexerp.jobs.embeddings")


class EmbeddingsWorker(BaseWorker):
    """Worker responsible for batch embedding generation across ERP entities."""

    job_type: str = "embeddings"

    async def process(
        self,
        job: BackgroundJob,
        payload: dict[str, Any],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """
        Batch generate embeddings for catalog items, knowledge chunks, or CRM descriptions.
        """
        entity_type = payload.get("entity_type", "generic")
        texts: list[str] = payload.get("texts", [])
        items: list[dict[str, Any]] = payload.get("items", [])

        if not texts and not items:
            raise ValueError("No 'texts' or 'items' provided for embeddings generation")

        if payload.get("simulate_error") and (job.retry_count + 1) < payload.get(
            "fail_until_attempt", payload.get("fail_until_retry", 999)
        ):
            raise ConnectionResetError("Simulated OpenAI embedding API rate limit 429")

        input_texts = texts if texts else [item.get("content", "") for item in items]

        # Generate vectors using RAGEmbedder
        embedder = RAGEmbedder()
        vectors, total_tokens, cost_usd = await embedder.embed_texts(input_texts)

        dim = len(vectors[0]) if vectors else 1536

        logger.info(
            "Generated %d embeddings for entity_type='%s' (dim=%d, tokens=%d, cost=$%.6f)",
            len(vectors),
            entity_type,
            dim,
            total_tokens,
            cost_usd,
        )

        return {
            "entity_type": entity_type,
            "total_embeddings": len(vectors),
            "vector_dimension": dim,
            "estimated_tokens": total_tokens,
            "sample_vector_preview": vectors[0][:5] if vectors else [],
        }
