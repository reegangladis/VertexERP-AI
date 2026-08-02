from typing import Any


class VectorDBAdapter:
    async def insert(
        self, vector_id: str, vector: list[float], metadata: dict[str, Any]
    ) -> None:
        raise NotImplementedError()

    async def search(
        self, vector: list[float], top_k: int = 5, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        raise NotImplementedError()

    async def delete(self, vector_id: str) -> None:
        raise NotImplementedError()


class InMemoryFAISSAdapter(VectorDBAdapter):
    """
    An in-memory fallback index simulating FAISS vector searches with metadata filtering.
    """

    def __init__(self):
        self.vectors: dict[str, list[float]] = {}
        self.metadata: dict[str, dict[str, Any]] = {}

    async def insert(
        self, vector_id: str, vector: list[float], metadata: dict[str, Any]
    ) -> None:
        self.vectors[vector_id] = vector
        self.metadata[vector_id] = metadata

    async def search(
        self, vector: list[float], top_k: int = 5, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        if not self.vectors:
            return []

        results = []

        for vid, v in self.vectors.items():
            meta = self.metadata.get(vid, {})

            # Apply filters (Tenant Isolation & RBAC checks)
            if filters:
                match = True
                for fk, fv in filters.items():
                    if fv is None:
                        continue
                    if fk == "collection_ids":
                        str_fv = [str(x) for x in fv]
                        doc_col = meta.get("collection_id")
                        if doc_col and str(doc_col) not in str_fv:
                            match = False
                    elif fk == "organization_id":
                        if str(meta.get("organization_id")) != str(fv):
                            match = False
                    elif fk == "categories":
                        str_fv = [str(x).lower() for x in fv]
                        if str(meta.get("category", "")).lower() not in str_fv:
                            match = False
                    elif fk == "document_types":
                        str_fv = [str(x).lower() for x in fv]
                        if str(meta.get("document_type", "")).lower() not in str_fv:
                            match = False
                    elif fk == "tags":
                        str_fv = [str(x).lower() for x in fv]
                        meta_tags = [str(t).lower() for t in (meta.get("tags") or [])]
                        if not set(str_fv).intersection(set(meta_tags)):
                            match = False
                if not match:
                    continue

            # Pure-Python dot product calculation
            min_dim = min(len(vector), len(v))
            dot_product = sum(vector[i] * v[i] for i in range(min_dim))
            results.append(
                {"vector_id": vid, "score": float(dot_product), "metadata": meta}
            )

        # Sort by high similarity score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def delete(self, vector_id: str) -> None:
        self.vectors.pop(vector_id, None)
        self.metadata.pop(vector_id, None)


class RAGVectorDBService:
    def __init__(self, provider: str = "faiss"):
        self.provider = provider
        self._adapters: dict[str, VectorDBAdapter] = {
            "faiss": InMemoryFAISSAdapter(),
            "chroma": InMemoryFAISSAdapter(),
            "pgvector": InMemoryFAISSAdapter(),
        }

    def get_adapter(self) -> VectorDBAdapter:
        return self._adapters.get(self.provider, self._adapters["faiss"])

    async def insert_vector(
        self, vector_id: str, vector: list[float], metadata: dict[str, Any]
    ) -> None:
        await self.get_adapter().insert(vector_id, vector, metadata)

    async def similarity_search(
        self, vector: list[float], top_k: int = 5, filters: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return await self.get_adapter().search(vector, top_k, filters)

    async def delete_vector(self, vector_id: str) -> None:
        await self.get_adapter().delete(vector_id)
