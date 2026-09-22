"""RAG Service orchestrating document lifecycle, versioning, search, and generation."""

from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.ai.models.rag_document import (
    RAGDocument,
    RAGDocumentVersion,
    RAGIngestionJob,
)
from app.modules.ai.models.usage import AIUsageLog
from app.modules.ai.rag.generator import RAGGenerator
from app.modules.ai.rag.ingestion_worker import RAGIngestionWorker, rag_worker
from app.modules.ai.rag.reranker import RAGReranker
from app.modules.ai.rag.retriever import RAGRetriever
from app.modules.ai.schemas.rag import (
    RAGDocumentCreate,
    RAGDocumentVersionCreate,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSearchRequest,
    RAGSearchResponse,
)

logger = logging.getLogger("vertexerp.ai.rag.service")


class RAGService:
    """Core RAG Domain Service managing documents, versions, ingestion jobs, search, and QA generation."""

    def __init__(
        self,
        retriever: RAGRetriever | None = None,
        reranker: RAGReranker | None = None,
        generator: RAGGenerator | None = None,
        worker: RAGIngestionWorker | None = None,
    ):
        self.retriever = retriever or RAGRetriever()
        self.reranker = reranker or RAGReranker()
        self.generator = generator or RAGGenerator()
        self.worker = worker or rag_worker

    @staticmethod
    def _compute_checksum(content: str) -> str:
        """Compute SHA-256 hex digest for document content verification."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    async def create_document(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        payload: RAGDocumentCreate,
        eager: bool = False,
    ) -> tuple[RAGDocument, RAGIngestionJob]:
        """Upload and create a new knowledge document with Version 1 and dispatch ingestion."""
        checksum = self._compute_checksum(payload.raw_content)
        file_size = len(payload.raw_content.encode("utf-8"))

        # 1. Create Document Master Record
        doc = RAGDocument(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            organization_id=organization_id,
            title=payload.title,
            description=payload.description,
            file_type=payload.file_type,
            file_size_bytes=file_size,
            access_level=payload.access_level.value,
            allowed_departments=payload.allowed_departments,
            allowed_roles=payload.allowed_roles,
            tags=payload.tags,
            metadata_json=payload.metadata_json,
            is_active=True,
            created_by=user_id,
        )
        session.add(doc)
        await session.flush()

        # 2. Create Initial Version (v1)
        version = RAGDocumentVersion(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            document_id=doc.id,
            version_number=1,
            changelog="Initial document creation",
            raw_content=payload.raw_content,
            checksum=checksum,
            is_active=True,
            created_by=user_id,
        )
        session.add(version)
        await session.flush()

        # 3. Create Ingestion Job in PENDING state
        job = RAGIngestionJob(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            organization_id=organization_id,
            document_id=doc.id,
            version_id=version.id,
            status="PENDING",
            retry_count=0,
            max_retries=3,
            dead_letter=False,
            created_by=user_id,
        )
        session.add(job)
        await session.flush()

        # 4. Dispatch Async Ingestion or Eager Execution
        if eager:
            await self.worker.process_job(job.id, session=session)
        else:
            self.worker.enqueue_job(job.id)

        return doc, job

    async def create_document_version(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        document_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        payload: RAGDocumentVersionCreate,
        eager: bool = False,
    ) -> tuple[RAGDocumentVersion, RAGIngestionJob]:
        """Create a new version for an existing document and trigger async ingestion."""
        # 1. Verify Document exists and belongs to tenant
        doc_stmt = select(RAGDocument).where(
            RAGDocument.id == document_id,
            RAGDocument.tenant_id == tenant_id,
        )
        doc_res = await session.execute(doc_stmt)
        doc = doc_res.scalar_one_or_none()
        if not doc:
            raise ValueError(f"Document {document_id} not found.")

        # 2. Find latest version number
        latest_ver_stmt = select(
            func.coalesce(func.max(RAGDocumentVersion.version_number), 0)
        ).where(
            RAGDocumentVersion.document_id == document_id,
            RAGDocumentVersion.tenant_id == tenant_id,
        )
        ver_res = await session.execute(latest_ver_stmt)
        next_ver = ver_res.scalar_one() + 1

        # 3. Set prior active versions to inactive
        stmt_deact = select(RAGDocumentVersion).where(
            RAGDocumentVersion.document_id == document_id,
            RAGDocumentVersion.tenant_id == tenant_id,
        )
        prior_vers = (await session.execute(stmt_deact)).scalars().all()
        for pv in prior_vers:
            pv.is_active = False

        # 4. Create New Version
        checksum = self._compute_checksum(payload.raw_content)
        new_version = RAGDocumentVersion(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            document_id=document_id,
            version_number=next_ver,
            changelog=payload.changelog or f"Version {next_ver} update",
            raw_content=payload.raw_content,
            checksum=checksum,
            is_active=True,
            created_by=user_id,
        )
        new_version.document = doc
        session.add(new_version)
        await session.flush()

        # 5. Create Ingestion Job
        job = RAGIngestionJob(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            organization_id=organization_id,
            document_id=document_id,
            version_id=new_version.id,
            status="PENDING",
            retry_count=0,
            max_retries=3,
            dead_letter=False,
            created_by=user_id,
        )
        session.add(job)
        await session.flush()

        # 6. Dispatch
        if eager:
            await self.worker.process_job(job.id, session=session)
        else:
            self.worker.enqueue_job(job.id)

        return new_version, job

    async def get_document(
        self, session: AsyncSession, tenant_id: uuid.UUID, document_id: uuid.UUID
    ) -> RAGDocument | None:
        """Fetch single document by ID with tenant isolation."""
        stmt = (
            select(RAGDocument)
            .options(
                selectinload(RAGDocument.versions),
                selectinload(RAGDocument.chunks),
                selectinload(RAGDocument.jobs),
            )
            .where(
                RAGDocument.id == document_id,
                RAGDocument.tenant_id == tenant_id,
            )
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def list_documents(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        access_level: str | None = None,
        tag: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[RAGDocument], int]:
        """List documents for tenant with filtering and pagination."""
        base_stmt = select(RAGDocument).where(
            RAGDocument.tenant_id == tenant_id,
            RAGDocument.is_active.is_(True),
        )

        if access_level:
            base_stmt = base_stmt.where(RAGDocument.access_level == access_level)

        if search:
            base_stmt = base_stmt.where(RAGDocument.title.ilike(f"%{search}%"))

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total_count = (await session.execute(count_stmt)).scalar_one()

        docs_stmt = (
            base_stmt.options(
                selectinload(RAGDocument.versions),
                selectinload(RAGDocument.chunks),
                selectinload(RAGDocument.jobs),
            )
            .order_by(RAGDocument.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        docs = (await session.execute(docs_stmt)).scalars().all()

        if tag:
            docs = [d for d in docs if d.tags and tag in d.tags]

        return docs, total_count

    async def delete_document(
        self, session: AsyncSession, tenant_id: uuid.UUID, document_id: uuid.UUID
    ) -> bool:
        """Soft-delete or purge document and associated chunks."""
        doc = await self.get_document(session, tenant_id, document_id)
        if not doc:
            return False

        doc.is_active = False
        doc.updated_at = datetime.now(UTC)
        await session.flush()
        return True

    async def get_ingestion_job(
        self, session: AsyncSession, tenant_id: uuid.UUID, job_id: uuid.UUID
    ) -> RAGIngestionJob | None:
        """Retrieve ingestion job status for tenant."""
        stmt = select(RAGIngestionJob).where(
            RAGIngestionJob.id == job_id,
            RAGIngestionJob.tenant_id == tenant_id,
        )
        res = await session.execute(stmt)
        return res.scalar_one_or_none()

    async def retry_ingestion_job(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        job_id: uuid.UUID,
        force_reset: bool = True,
        eager: bool = False,
    ) -> RAGIngestionJob:
        """Retry a failed or dead-letter ingestion job."""
        job = await self.get_ingestion_job(session, tenant_id, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found.")

        if force_reset:
            job.retry_count = 0

        job.status = "PENDING"
        job.dead_letter = False
        job.dead_letter_reason = None
        job.error_message = None
        job.updated_at = datetime.now(UTC)
        await session.flush()

        if eager:
            await self.worker.process_job(job.id, session=session)
        else:
            self.worker.enqueue_job(job.id)

        return job

    async def search_knowledge(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        payload: RAGSearchRequest,
        user_roles: set[str] | None = None,
        user_department: str | None = None,
    ) -> RAGSearchResponse:
        """Vector retrieval and hybrid reranking returning top-K chunks."""
        start_time = datetime.now(UTC)

        candidates = await self.retriever.retrieve_candidates(
            session=session,
            tenant_id=tenant_id,
            query=payload.query,
            top_k=payload.top_k * 3,
            user_roles=user_roles,
            user_department=user_department,
            access_level_filter=payload.access_level_filter.value
            if payload.access_level_filter
            else None,
            tags_filter=payload.tags_filter,
        )

        ranked_results = self.reranker.rerank(
            query=payload.query,
            candidates=candidates,
            top_k=payload.top_k,
            min_score=payload.min_score,
        )

        elapsed_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000.0

        return RAGSearchResponse(
            query=payload.query,
            total_results=len(ranked_results),
            results=ranked_results,
            latency_ms=round(elapsed_ms, 2),
        )

    async def query_knowledge(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        organization_id: uuid.UUID,
        user_id: uuid.UUID | None,
        payload: RAGQueryRequest,
        user_roles: set[str] | None = None,
        user_department: str | None = None,
    ) -> RAGQueryResponse:
        """End-to-end grounded RAG generation with structured citations and telemetry."""
        # 1. Retrieve & Rerank Chunks
        search_req = RAGSearchRequest(
            query=payload.query,
            top_k=payload.top_k,
            min_score=0.0,
        )
        search_resp = await self.search_knowledge(
            session=session,
            tenant_id=tenant_id,
            payload=search_req,
            user_roles=user_roles,
            user_department=user_department,
        )

        # 2. Generate Grounded Response with Citations
        query_resp = await self.generator.generate_grounded_answer(
            query=payload.query,
            ranked_chunks=search_resp.results,
            provider=payload.provider,
            model=payload.model,
            temperature=payload.temperature,
        )

        # 3. Log AI Usage Telemetry
        usage_log = AIUsageLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            organization_id=organization_id,
            user_id=user_id,
            operation_type="RAG_QUERY",
            provider=query_resp.provider_used,
            model=query_resp.model_used,
            prompt_tokens=query_resp.prompt_tokens,
            completion_tokens=query_resp.completion_tokens,
            total_tokens=query_resp.total_tokens,
            cost_usd=query_resp.cost_usd,
            latency_ms=int(query_resp.latency_ms),
            status="SUCCESS",
        )
        session.add(usage_log)
        await session.flush()

        return query_resp


# Singleton RAG service instance
rag_service = RAGService()
