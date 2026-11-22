"""RAG Retriever executing tenant-isolated and authorization-filtered vector search."""

from __future__ import annotations

import logging
import math
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.models.rag_document import RAGDocument, RAGDocumentChunk, RAGDocumentVersion
from app.modules.ai.rag.embedder import RAGEmbedder

logger = logging.getLogger("vertexerp.ai.rag.retriever")


class RetrievedChunk:
    """A retrieved chunk candidate with vector score and document metadata."""

    def __init__(
        self,
        chunk_id: uuid.UUID,
        document_id: uuid.UUID,
        document_title: str,
        version_id: uuid.UUID,
        version_number: int,
        chunk_index: int,
        content: str,
        section_heading: str | None,
        vector_score: float,
        metadata: dict[str, Any],
        access_level: str,
        allowed_departments: list[str],
        allowed_roles: list[str],
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.document_title = document_title
        self.version_id = version_id
        self.version_number = version_number
        self.chunk_index = chunk_index
        self.content = content
        self.section_heading = section_heading
        self.vector_score = vector_score
        self.metadata = metadata
        self.access_level = access_level
        self.allowed_departments = allowed_departments
        self.allowed_roles = allowed_roles


class RAGRetriever:
    """Retrieves document chunks using vector cosine similarity and RBAC filtering."""

    def __init__(self, embedder: RAGEmbedder | None = None):
        self.embedder = embedder or RAGEmbedder()

    @staticmethod
    def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two float vectors."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
        norm_a = math.sqrt(sum(a * a for a in vec1))
        norm_b = math.sqrt(sum(b * b for b in vec2))

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return max(-1.0, min(1.0, dot_product / (norm_a * norm_b)))

    @staticmethod
    def is_user_authorized_for_document(
        doc_access_level: str,
        doc_allowed_roles: list[str],
        doc_allowed_departments: list[str],
        user_roles: set[str],
        user_department: str | None = None,
    ) -> bool:
        """Evaluate if user is permitted to retrieve chunks from this document."""
        # TenantAdmin and OrgAdmin bypass fine-grained document tags
        if "TenantAdmin" in user_roles or "OrgAdmin" in user_roles:
            return True

        # Check access level
        level = (doc_access_level or "INTERNAL").upper()
        if level == "RESTRICTED":
            # Must explicitly match role or department
            role_match = bool(set(doc_allowed_roles).intersection(user_roles)) or (
                "*" in doc_allowed_roles
            )
            dept_match = (user_department and user_department in doc_allowed_departments) or (
                "*" in doc_allowed_departments
            )
            return role_match and dept_match

        if level == "CONFIDENTIAL":
            # Executives/CFO/HRManager/Auditor or matching roles/depts
            privileged = {"Executive", "ChiefFinancialOfficer", "HRManager", "Auditor"}
            if user_roles.intersection(privileged):
                return True
            role_match = bool(set(doc_allowed_roles).intersection(user_roles)) or (
                "*" in doc_allowed_roles
            )
            dept_match = (user_department and user_department in doc_allowed_departments) or (
                "*" in doc_allowed_departments
            )
            return role_match and dept_match

        # INTERNAL and PUBLIC: Check department and role constraints if explicitly defined
        if "*" not in doc_allowed_departments and (
            not user_department or user_department not in doc_allowed_departments
        ):
            return False

        return bool("*" in doc_allowed_roles or user_roles.intersection(set(doc_allowed_roles)))

    async def retrieve_candidates(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        query: str,
        top_k: int = 15,
        user_roles: set[str] | None = None,
        user_department: str | None = None,
        access_level_filter: str | None = None,
        tags_filter: list[str] | None = None,
    ) -> list[RetrievedChunk]:
        """Retrieve and rank chunks for a tenant query enforcing RBAC."""
        roles = user_roles or {"StandardUser"}

        # 1. Embed query vector
        query_vector = await self.embedder.embed_single_query(query)

        # 2. Query database for active document chunks strictly belonging to THIS tenant
        stmt = (
            select(RAGDocumentChunk, RAGDocument, RAGDocumentVersion)
            .join(RAGDocument, RAGDocumentChunk.document_id == RAGDocument.id)
            .join(RAGDocumentVersion, RAGDocumentChunk.version_id == RAGDocumentVersion.id)
            .where(
                RAGDocumentChunk.tenant_id == tenant_id,
                RAGDocument.tenant_id == tenant_id,
                RAGDocument.is_active.is_(True),
                RAGDocumentVersion.is_active.is_(True),
            )
        )

        if access_level_filter:
            stmt = stmt.where(RAGDocument.access_level == access_level_filter)

        dialect_name = session.bind.dialect.name if session.bind is not None else ""
        if dialect_name == "postgresql":
            stmt = stmt.where(RAGDocumentChunk.embedding.is_not(None)).order_by(
                RAGDocumentChunk.embedding.cosine_distance(query_vector)
            ).limit(max(top_k * 10, top_k))
        else:
            stmt = stmt.limit(max(top_k * 10, top_k))

        result = await session.execute(stmt)
        rows = result.all()

        candidates: list[RetrievedChunk] = []

        for chunk, doc, version in rows:
            # 3. Apply Tag filtering if requested
            if tags_filter:
                doc_tags = set(doc.tags or [])
                if not any(t in doc_tags for t in tags_filter):
                    continue

            # 4. Zero-Trust Authorization check
            is_allowed = self.is_user_authorized_for_document(
                doc_access_level=doc.access_level,
                doc_allowed_roles=doc.allowed_roles or ["*"],
                doc_allowed_departments=doc.allowed_departments or ["*"],
                user_roles=roles,
                user_department=user_department,
            )
            if not is_allowed:
                continue

            # 5. Compute Cosine Similarity
            embedding = chunk.embedding if chunk.embedding is not None else chunk.embedding_json
            if not embedding:
                continue

            sim_score = self._cosine_similarity(query_vector, embedding)

            candidates.append(
                RetrievedChunk(
                    chunk_id=chunk.id,
                    document_id=doc.id,
                    document_title=doc.title,
                    version_id=version.id,
                    version_number=version.version_number,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    section_heading=chunk.section_heading,
                    vector_score=round(sim_score, 4),
                    metadata=chunk.metadata_json or {},
                    access_level=doc.access_level,
                    allowed_departments=doc.allowed_departments or ["*"],
                    allowed_roles=doc.allowed_roles or ["*"],
                )
            )

        # Sort by vector cosine similarity descending
        candidates.sort(key=lambda x: x.vector_score, reverse=True)
        return candidates[:top_k]
