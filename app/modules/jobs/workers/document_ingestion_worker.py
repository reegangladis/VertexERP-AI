"""Dedicated worker for asynchronous RAG Document parsing, chunking, and indexing."""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models.rag_document import (
    RAGDocument,
    RAGDocumentVersion,
    RAGIngestionJob,
)
from app.modules.ai.rag.chunker import RAGChunker
from app.modules.ai.rag.cleaner import RAGCleaner
from app.modules.ai.rag.embedder import RAGEmbedder
from app.modules.ai.rag.indexer import RAGIndexer
from app.modules.jobs.models.job import BackgroundJob
from app.modules.jobs.workers.base import BaseWorker

logger = logging.getLogger("vertexerp.jobs.document_ingestion")


class DocumentIngestionWorker(BaseWorker):
    """Worker responsible for parsing, cleaning, chunking, embedding, and indexing documents."""

    job_type: str = "document_ingestion"

    async def process(
        self,
        job: BackgroundJob,
        payload: dict[str, Any],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """Run end-to-end RAG document ingestion pipeline."""
        document_id_raw = payload.get("document_id")
        version_id_raw = payload.get("version_id")

        if not document_id_raw or not version_id_raw:
            raise ValueError("Missing document_id or version_id in ingestion job payload")

        document_id = uuid.UUID(str(document_id_raw))
        version_id = uuid.UUID(str(version_id_raw))

        # Check for simulated failure test hooks
        if payload.get("simulate_error") and (job.retry_count + 1) < payload.get(
            "fail_until_attempt", payload.get("fail_until_retry", 999)
        ):
            raise RuntimeError("Simulated RAG parsing model transient failure")

        # Load document and version
        stmt = select(RAGDocumentVersion).where(
            RAGDocumentVersion.id == version_id,
            RAGDocumentVersion.tenant_id == job.tenant_id,
        )
        res = await session.execute(stmt)
        version = res.scalar_one_or_none()
        if not version:
            raise ValueError(f"Version {version_id} not found in tenant {job.tenant_id}")

        doc_stmt = select(RAGDocument).where(
            RAGDocument.id == document_id,
            RAGDocument.tenant_id == job.tenant_id,
        )
        doc_res = await session.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()
        if not doc:
            raise ValueError(f"Document {document_id} not found in tenant {job.tenant_id}")

        # Step 1 & 2: Clean content
        cleaned_text = RAGCleaner.clean_text(version.raw_content)
        version.cleaned_content = cleaned_text

        # Step 3: Chunk document
        chunker = RAGChunker(
            chunk_size_tokens=payload.get("chunk_size", 400),
            chunk_overlap_tokens=payload.get("chunk_overlap", 50),
        )
        doc_meta = {
            "document_title": doc.title,
            "document_id": str(doc.id),
            "version_number": version.version_number,
            "access_level": doc.access_level,
            "tags": doc.tags or [],
        }
        chunks = chunker.chunk_document(
            raw_content=cleaned_text,
            file_type=doc.file_type,
            doc_metadata=doc_meta,
        )

        if not chunks:
            raise ValueError("No valid text chunks produced from document content.")

        # Step 4: Batch Embeddings
        embedder = RAGEmbedder()
        chunk_texts = [c.content for c in chunks]
        embeddings, total_tokens, embedding_cost = await embedder.embed_texts(chunk_texts)

        # Step 5: Index Chunks
        indexer = RAGIndexer()
        await indexer.index_chunks(
            session=session,
            tenant_id=job.tenant_id,
            document_id=document_id,
            version_id=version_id,
            chunks=chunks,
            embeddings=embeddings,
            additional_metadata={"organization_id": str(job.organization_id)},
        )

        indexed_count = len(chunks)

        # Sync linked RAGIngestionJob if provided
        rag_job_id_raw = payload.get("rag_job_id")
        if rag_job_id_raw:
            rag_job_id = uuid.UUID(str(rag_job_id_raw))
            r_job_stmt = select(RAGIngestionJob).where(
                RAGIngestionJob.id == rag_job_id,
                RAGIngestionJob.tenant_id == job.tenant_id,
            )
            r_job_res = await session.execute(r_job_stmt)
            r_job = r_job_res.scalar_one_or_none()
            if r_job:
                r_job.status = "COMPLETED"
                r_job.metrics_json = {
                    "total_chunks": indexed_count,
                    "cleaned_chars": len(cleaned_text),
                }

        await session.flush()

        logger.info(
            "Completed ingestion for doc=%s, version=%s (%d chunks indexed)",
            document_id,
            version_id,
            indexed_count,
        )

        return {
            "document_id": str(document_id),
            "version_id": str(version_id),
            "chunks_indexed": indexed_count,
            "raw_length": len(version.raw_content),
            "cleaned_length": len(cleaned_text),
        }
