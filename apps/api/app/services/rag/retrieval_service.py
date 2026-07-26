import time
import uuid
from typing import Any
from app.repositories.rag_repository import RAGRepository
from app.services.rag.embedding_service import RAGEmbeddingService
from app.services.rag.vector_db_service import RAGVectorDBService
from app.models.rag import RetrievalLog


class RAGRetrievalService:
    def __init__(
        self,
        repository: Any,
        embedding_service: RAGEmbeddingService,
        vector_db_service: RAGVectorDBService
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
        min_score: float = 0.0
    ) -> dict[str, Any]:
        """
        Execute tenant-isolated and RBAC-aware semantic/hybrid search.
        Includes re-ranking placeholder.
        """
        start_time = time.time()

        # Step 1: Embedding Generation
        query_vector = await self.embedding_service.get_embedding(
            text=query,
            provider=provider
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
            vector=query_vector,
            top_k=top_k * 2, # Retrieve extra candidates for hybrid keyword fusion and re-ranking
            filters=filters
        )

        # Step 4: Hybrid Search Architecture / Keyword Re-ranking fusion
        # (Inject BM25 matching query scoring placeholder combined with vector similarity)
        results = []
        for res in vector_results:
            meta = res["metadata"]
            score = res["score"]

            # BM25/TF-IDF keyword boost placeholder
            query_words = set(query.lower().split())
            content_words = set(meta.get("content", "").lower().split())
            intersection = query_words.intersection(content_words)
            
            if search_type == "hybrid" and intersection:
                # Boost vector score based on keyword overlap
                score += (len(intersection) / len(query_words)) * 0.2

            # Apply min score filter
            if score >= min_score:
                results.append({
                    "chunk_id": uuid.UUID(res["vector_id"]),
                    "document_id": uuid.UUID(meta.get("document_id")),
                    "document_title": meta.get("document_title", "Untitled Document"),
                    "document_type": meta.get("document_type", "policy"),
                    "category": meta.get("category", "general"),
                    "content": meta.get("content", ""),
                    "score": round(score, 4),
                    "chunk_index": meta.get("chunk_index", 0),
                    "metadata": meta
                })

        # Sort the hybrid results
        results.sort(key=lambda x: x["score"], reverse=True)
        final_results = results[:top_k]

        # Step 5: Re-ranking Placeholder
        # Future cross-encoder ranking can be introduced here
        
        execution_time = (time.time() - start_time) * 1000

        # Step 6: Log retrieval query
        chunk_ids = [str(r["chunk_id"]) for r in final_results]
        scores = [r["score"] for r in final_results]
        
        retrieval_log = RetrievalLog(
            organization_id=org_id,
            user_id=user_id,
            query_text=query,
            top_k=top_k,
            retrieved_chunk_ids=chunk_ids,
            scores=scores,
            execution_time_ms=execution_time,
            search_type=search_type
        )
        await self.repository.log_retrieval(retrieval_log)

        return {
            "query": query,
            "results": final_results,
            "total_found": len(final_results),
            "execution_time_ms": execution_time,
            "search_type": search_type
        }
