import uuid
from typing import Sequence
from sqlalchemy import select, update, delete, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.rag import (
    KnowledgeCollection,
    RAGDocument,
    DocumentVersion,
    DocumentChunk,
    EmbeddingMetadata,
    RAGChatSession,
    RAGChatMessage,
    RetrievalLog,
    RAGFeedback,
)


class RAGRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== Collections ====================
    async def create_collection(self, collection: KnowledgeCollection) -> KnowledgeCollection:
        self.db.add(collection)
        await self.db.flush()
        await self.db.refresh(collection)
        return collection

    async def get_collection(self, collection_id: uuid.UUID, org_id: uuid.UUID) -> KnowledgeCollection | None:
        query = select(KnowledgeCollection).where(
            KnowledgeCollection.id == collection_id,
            KnowledgeCollection.organization_id == org_id,
            KnowledgeCollection.is_deleted == False,
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_collections(self, org_id: uuid.UUID, category: str | None = None) -> Sequence[KnowledgeCollection]:
        query = select(KnowledgeCollection).where(
            KnowledgeCollection.organization_id == org_id,
            KnowledgeCollection.is_deleted == False,
        )
        if category:
            query = query.where(KnowledgeCollection.category == category)
        query = query.order_by(KnowledgeCollection.name.asc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_collection(self, collection_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        collection = await self.get_collection(collection_id, org_id)
        if not collection:
            return False
        collection.is_deleted = True
        await self.db.flush()
        return True

    # ==================== Documents ====================
    async def create_document(self, document: RAGDocument) -> RAGDocument:
        self.db.add(document)
        await self.db.flush()
        await self.db.refresh(document)
        return document

    async def get_document(self, document_id: uuid.UUID, org_id: uuid.UUID) -> RAGDocument | None:
        query = (
            select(RAGDocument)
            .where(
                RAGDocument.id == document_id,
                RAGDocument.organization_id == org_id,
                RAGDocument.is_deleted == False,
            )
            .options(
                selectinload(RAGDocument.collection),
                selectinload(RAGDocument.versions),
                selectinload(RAGDocument.chunks),
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        org_id: uuid.UUID,
        collection_id: uuid.UUID | None = None,
        category: str | None = None,
        document_type: str | None = None,
        status: str | None = None,
        search_query: str | None = None,
    ) -> Sequence[RAGDocument]:
        query = select(RAGDocument).where(
            RAGDocument.organization_id == org_id,
            RAGDocument.is_deleted == False,
        )
        if collection_id:
            query = query.where(RAGDocument.collection_id == collection_id)
        if category:
            query = query.where(RAGDocument.category == category)
        if document_type:
            query = query.where(RAGDocument.document_type == document_type)
        if status:
            query = query.where(RAGDocument.status == status)
        if search_query:
            query = query.where(
                or_(
                    RAGDocument.title.ilike(f"%{search_query}%"),
                    RAGDocument.file_name.ilike(f"%{search_query}%"),
                )
            )
        query = query.order_by(RAGDocument.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_document(self, document_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        doc = await self.get_document(document_id, org_id)
        if not doc:
            return False
        doc.is_deleted = True
        await self.db.flush()
        return True

    # ==================== Document Versions ====================
    async def create_version(self, version: DocumentVersion) -> DocumentVersion:
        self.db.add(version)
        await self.db.flush()
        await self.db.refresh(version)
        return version

    async def get_versions(self, document_id: uuid.UUID) -> Sequence[DocumentVersion]:
        query = (
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version_number.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    # ==================== Document Chunks ====================
    async def create_chunks(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        self.db.add_all(chunks)
        await self.db.flush()
        return chunks

    async def get_chunks_for_document(self, document_id: uuid.UUID) -> Sequence[DocumentChunk]:
        query = (
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_chunks_by_ids(self, chunk_ids: list[uuid.UUID]) -> Sequence[DocumentChunk]:
        if not chunk_ids:
            return []
        query = select(DocumentChunk).where(DocumentChunk.id.in_(chunk_ids))
        result = await self.db.execute(query)
        return result.scalars().all()

    # ==================== Embeddings Metadata ====================
    async def save_embedding_metadata(self, metadata: EmbeddingMetadata) -> EmbeddingMetadata:
        self.db.add(metadata)
        await self.db.flush()
        await self.db.refresh(metadata)
        return metadata

    # ==================== Retrieval Logging ====================
    async def log_retrieval(self, log: RetrievalLog) -> RetrievalLog:
        self.db.add(log)
        await self.db.flush()
        return log

    # ==================== Chat Sessions & Messages ====================
    async def create_chat_session(self, session: RAGChatSession) -> RAGChatSession:
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_chat_session(self, session_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID) -> RAGChatSession | None:
        query = (
            select(RAGChatSession)
            .where(
                RAGChatSession.id == session_id,
                RAGChatSession.organization_id == org_id,
                RAGChatSession.user_id == user_id,
                RAGChatSession.is_deleted == False,
            )
            .options(selectinload(RAGChatSession.messages))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_chat_sessions(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Sequence[RAGChatSession]:
        query = (
            select(RAGChatSession)
            .where(
                RAGChatSession.organization_id == org_id,
                RAGChatSession.user_id == user_id,
                RAGChatSession.is_deleted == False,
            )
            .order_by(RAGChatSession.is_pinned.desc(), RAGChatSession.updated_at.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def add_chat_message(self, message: RAGChatMessage) -> RAGChatMessage:
        self.db.add(message)
        await self.db.flush()
        await self.db.refresh(message)
        return message

    async def toggle_pin_session(self, session_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        session = await self.get_chat_session(session_id, org_id, user_id)
        if not session:
            return False
        session.is_pinned = not session.is_pinned
        await self.db.flush()
        return True

    # ==================== Feedback ====================
    async def add_feedback(self, feedback: RAGFeedback) -> RAGFeedback:
        self.db.add(feedback)
        await self.db.flush()
        await self.db.refresh(feedback)
        return feedback
