"""RAG Indexer for transactional persistence of chunks and vector embeddings."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models.rag_document import RAGDocumentChunk
from app.modules.ai.rag.chunker import ChunkItem

logger = logging.getLogger("vertexerp.ai.rag.indexer")


class RAGIndexer:
    """Stores and indexes document chunks with vector embeddings in the database."""

    @staticmethod
    async def index_chunks(
        session: AsyncSession,
        tenant_id: uuid.UUID,
        document_id: uuid.UUID,
        version_id: uuid.UUID,
        chunks: list[ChunkItem],
        embeddings: list[list[float]],
        additional_metadata: dict[str, Any] | None = None,
    ) -> list[RAGDocumentChunk]:
        """Index a list of chunks and their embeddings transactionally."""
        if len(chunks) != len(embeddings):
            raise ValueError(
                f"Chunks count ({len(chunks)}) does not match embeddings count ({len(embeddings)})"
            )

        extra_meta = additional_metadata or {}

        # 1. Clear any pre-existing chunks for this document version
        stmt = delete(RAGDocumentChunk).where(
            RAGDocumentChunk.tenant_id == tenant_id,
            RAGDocumentChunk.document_id == document_id,
            RAGDocumentChunk.version_id == version_id,
        )
        await session.execute(stmt)

        # 2. Build and persist chunk entities
        chunk_entities: list[RAGDocumentChunk] = []
        for chunk, emb in zip(chunks, embeddings, strict=False):
            merged_meta = {**chunk.metadata, **extra_meta}
            entity = RAGDocumentChunk(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                document_id=document_id,
                version_id=version_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                token_count=chunk.token_count,
                char_count=chunk.char_count,
                section_heading=chunk.section_heading,
                embedding=emb,
                embedding_json=emb,
                metadata_json=merged_meta,
            )
            session.add(entity)
            chunk_entities.append(entity)

        await session.flush()
        logger.info(
            f"Successfully indexed {len(chunk_entities)} chunks for doc {document_id} v{version_id} (tenant {tenant_id})"
        )
        return chunk_entities
