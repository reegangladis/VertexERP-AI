"""RAG Asynchronous Ingestion Pipeline Worker with retries and dead-letter handling."""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import async_session_factory
from app.modules.ai.models.rag_document import (
    RAGDocument,
    RAGDocumentVersion,
    RAGIngestionJob,
)
from app.modules.ai.rag.chunker import RAGChunker
from app.modules.ai.rag.cleaner import RAGCleaner
from app.modules.ai.rag.embedder import RAGEmbedder
from app.modules.ai.rag.indexer import RAGIndexer

logger = logging.getLogger("vertexerp.ai.rag.worker")


class RAGIngestionWorker:
    """Processes document ingestion jobs asynchronously with retry backoff and dead-letter handling."""

    def __init__(
        self,
        chunker: RAGChunker | None = None,
        embedder: RAGEmbedder | None = None,
        indexer: RAGIndexer | None = None,
    ):
        self.chunker = chunker or RAGChunker()
        self.embedder = embedder or RAGEmbedder()
        self.indexer = indexer or RAGIndexer()

    async def process_job(
        self,
        job_id: uuid.UUID,
        session: AsyncSession | None = None,
    ) -> RAGIngestionJob:
        """Execute the ingestion pipeline for a specific job."""
        if session is not None:
            return await self._execute_pipeline(job_id, session)
        else:
            async with async_session_factory() as new_session, new_session.begin():
                return await self._execute_pipeline(job_id, new_session)

    async def _execute_pipeline(
        self,
        job_id: uuid.UUID,
        session: AsyncSession,
    ) -> RAGIngestionJob:
        """Internal pipeline execution steps."""
        start_time = time.perf_counter()

        # 1. Fetch Job
        job_stmt = select(RAGIngestionJob).where(RAGIngestionJob.id == job_id)
        job_res = await session.execute(job_stmt)
        job = job_res.scalar_one_or_none()
        if not job:
            raise ValueError(f"Ingestion job {job_id} not found.")

        # 2. Transition state to PROCESSING
        job.status = "PROCESSING"
        job.updated_at = datetime.now(UTC)
        await session.flush()

        try:
            # 3. Load Document and Version
            ver_stmt = select(RAGDocumentVersion).where(
                RAGDocumentVersion.id == job.version_id,
                RAGDocumentVersion.tenant_id == job.tenant_id,
            )
            ver_res = await session.execute(ver_stmt)
            version = ver_res.scalar_one_or_none()
            if not version:
                raise ValueError(f"Document version {job.version_id} not found.")

            doc_stmt = select(RAGDocument).where(
                RAGDocument.id == job.document_id,
                RAGDocument.tenant_id == job.tenant_id,
            )
            doc_res = await session.execute(doc_stmt)
            document = doc_res.scalar_one_or_none()
            if not document:
                raise ValueError(f"Document {job.document_id} not found.")

            # 4. Clean and update cleaned_content
            cleaned_body = RAGCleaner.clean_text(version.raw_content)
            version.cleaned_content = cleaned_body

            # 5. Chunk document
            doc_meta = {
                "document_title": document.title,
                "document_id": str(document.id),
                "version_number": version.version_number,
                "access_level": document.access_level,
                "tags": document.tags or [],
            }
            chunks = self.chunker.chunk_document(
                raw_content=cleaned_body,
                file_type=document.file_type,
                doc_metadata=doc_meta,
            )

            if not chunks:
                raise ValueError("No valid text chunks could be produced from document content.")

            # 6. Batch Embeddings
            chunk_texts = [c.content for c in chunks]
            embeddings, total_tokens, embedding_cost = await self.embedder.embed_texts(chunk_texts)

            # 7. Index Chunks
            await self.indexer.index_chunks(
                session=session,
                tenant_id=job.tenant_id,
                document_id=job.document_id,
                version_id=job.version_id,
                chunks=chunks,
                embeddings=embeddings,
                additional_metadata={"organization_id": str(job.organization_id)},
            )

            # 8. Mark Job as COMPLETED
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            job.status = "COMPLETED"
            job.error_message = None
            job.completed_at = datetime.now(UTC)
            job.updated_at = datetime.now(UTC)
            job.metrics_json = {
                "chunk_count": len(chunks),
                "total_tokens": total_tokens,
                "embedding_cost_usd": embedding_cost,
                "duration_ms": duration_ms,
            }

            # Update document file size and updated_at
            document.file_size_bytes = len(version.raw_content.encode("utf-8"))
            document.updated_at = datetime.now(UTC)

            await session.flush()
            logger.info(
                f"Ingestion job {job_id} COMPLETED in {duration_ms}ms ({len(chunks)} chunks)."
            )
            return job

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            err_msg = str(exc)
            logger.error(f"Ingestion job {job_id} encountered error: {err_msg}", exc_info=True)

            job.retry_count += 1
            job.updated_at = datetime.now(UTC)

            if job.retry_count < job.max_retries:
                # Mark for retry
                job.status = "PENDING"
                job.error_message = f"Attempt {job.retry_count} failed: {err_msg}"
                logger.warning(
                    f"Job {job_id} will be retried (attempt {job.retry_count}/{job.max_retries})"
                )
            else:
                # Retries exhausted -> Dead-letter queue transition
                job.status = "FAILED"
                job.dead_letter = True
                job.dead_letter_reason = (
                    f"Max retries ({job.max_retries}) exhausted. Last error: {err_msg}"
                )
                job.error_message = err_msg
                job.completed_at = datetime.now(UTC)
                logger.error(f"Job {job_id} permanently moved to DEAD-LETTER state.")

            await session.flush()
            return job

    def enqueue_job(self, job_id: uuid.UUID) -> asyncio.Task:
        """Spawn background task for async execution without blocking HTTP request."""
        return asyncio.create_task(self.process_job(job_id))


# Singleton worker instance
rag_worker = RAGIngestionWorker()
