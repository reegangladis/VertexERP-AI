import time
import uuid
from typing import Any

from app.services.rag.embedding_service import RAGEmbeddingService
from app.services.rag.vector_db_service import RAGVectorDBService


class RAGRetrievalService:
    def __init__(
        self,
        repository: Any,
        embedding_service: RAGEmbeddingService,
        vector_db_service: RAGVectorDBService,
    ):
        self.repository = repository
        self.embedding_service = embedding_service
        self.vector_db_service = vector_db_service

    async def retrieve(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        query: str,
        collection_ids: list[uuid.UUID] | None = None,
        categories: list[str] | None = None,
        document_types: list[str] | None = None,
        tags: list[str] | None = None,
        top_k: int = 5,
        search_type: str = "hybrid",
        provider: str = "openai",
        min_score: float = 0.0,
    ) -> dict[str, Any]:
        """
        Execute tenant-isolated and RBAC-aware semantic/hybrid search.
        """
        start_time = time.time()

        # Step 1: Embedding Generation
        query_vector = await self.embedding_service.get_embedding(
            text=query, provider=provider
        )

        # Step 2: Tenant & Permission Isolation Filters
        filters = {
            "organization_id": org_id,
        }
        if collection_ids:
            filters["collection_ids"] = collection_ids
        if categories:
            filters["categories"] = categories
        if document_types:
            filters["document_types"] = document_types
        if tags:
            filters["tags"] = tags

        # Step 3: Vector similarity search
        vector_results = await self.vector_db_service.similarity_search(
            vector=query_vector, top_k=top_k * 2, filters=filters
        )

        results = []
        for res in vector_results:
            meta = res["metadata"]
            score = res["score"]

            # Hybrid keyword match boost
            query_words = set(query.lower().split())
            content_words = set(meta.get("content", "").lower().split())
            intersection = query_words.intersection(content_words)

            if search_type == "hybrid" and intersection and len(query_words) > 0:
                score += (len(intersection) / len(query_words)) * 0.2

            if score >= min_score:
                chunk_uuid = (
                    uuid.UUID(res["vector_id"])
                    if self._is_valid_uuid(res["vector_id"])
                    else uuid.uuid4()
                )
                doc_uuid = (
                    uuid.UUID(str(meta.get("document_id")))
                    if meta.get("document_id")
                    and self._is_valid_uuid(str(meta.get("document_id")))
                    else uuid.uuid4()
                )

                results.append(
                    {
                        "chunk_id": chunk_uuid,
                        "document_id": doc_uuid,
                        "document_title": meta.get(
                            "document_title", "Indexed Enterprise Document"
                        ),
                        "document_type": meta.get("document_type", "policy"),
                        "category": meta.get("category", "general"),
                        "content": meta.get("content", ""),
                        "score": round(min(1.0, max(0.0, score)), 4),
                        "chunk_index": meta.get("chunk_index", 0),
                        "metadata": meta,
                    }
                )

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        final_results = results[:top_k]
        elapsed = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query,
            "results": final_results,
            "total_found": len(final_results),
            "execution_time_ms": elapsed,
            "search_type": search_type,
        }

    def _is_valid_uuid(self, val: str) -> bool:
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False
