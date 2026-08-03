import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ai_rag_copilot_v14 import (
    AIAgent,
    AIAgentRun,
    DocumentChunk,
    Embedding,
    KnowledgeCollection,
    PromptTemplate,
    PromptVersion,
    RAGChatMessage,
    RAGChatSession,
    RAGDocument,
    RetrievalLog,
    ToolRegistry,
)
from app.repositories.base import BaseRepository


class KnowledgeCollectionRepository(BaseRepository[KnowledgeCollection]):
    def __init__(self, db: AsyncSession):
        super().__init__(KnowledgeCollection, db)

    async def find_by_name(self, org_id: uuid.UUID, name: str) -> KnowledgeCollection | None:
        stmt = select(KnowledgeCollection).where(
            KnowledgeCollection.organization_id == org_id,
            KnowledgeCollection.name == name,
            KnowledgeCollection.is_deleted == False,
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[KnowledgeCollection]:
        stmt = select(KnowledgeCollection).where(
            KnowledgeCollection.organization_id == org_id, KnowledgeCollection.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class RAGDocumentRepository(BaseRepository[RAGDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(RAGDocument, db)

    async def get_with_chunks(self, doc_id: uuid.UUID) -> RAGDocument | None:
        stmt = (
            select(RAGDocument)
            .options(selectinload(RAGDocument.chunks))
            .where(RAGDocument.id == doc_id, RAGDocument.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class DocumentChunkRepository(BaseRepository[DocumentChunk]):
    def __init__(self, db: AsyncSession):
        super().__init__(DocumentChunk, db)

    async def search_chunks_by_query(self, query: str, limit: int = 5) -> list[DocumentChunk]:
        # Basic keyword match fallback simulation for vector search
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.chunk_text.ilike(f"%{query}%"), DocumentChunk.is_deleted == False)
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ChatSessionRepository(BaseRepository[RAGChatSession]):
    def __init__(self, db: AsyncSession):
        super().__init__(RAGChatSession, db)

    async def get_with_messages(self, session_id: uuid.UUID) -> RAGChatSession | None:
        stmt = (
            select(RAGChatSession)
            .options(selectinload(RAGChatSession.messages))
            .where(RAGChatSession.id == session_id, RAGChatSession.is_deleted == False)
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def get_by_org(self, org_id: uuid.UUID) -> list[RAGChatSession]:
        stmt = select(RAGChatSession).where(
            RAGChatSession.organization_id == org_id, RAGChatSession.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ChatMessageRepository(BaseRepository[RAGChatMessage]):
    def __init__(self, db: AsyncSession):
        super().__init__(RAGChatMessage, db)


class PromptTemplateRepository(BaseRepository[PromptTemplate]):
    def __init__(self, db: AsyncSession):
        super().__init__(PromptTemplate, db)

    async def find_by_name(self, name: str) -> PromptTemplate | None:
        stmt = select(PromptTemplate).where(
            PromptTemplate.name == name, PromptTemplate.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class AIAgentRepository(BaseRepository[AIAgent]):
    def __init__(self, db: AsyncSession):
        super().__init__(AIAgent, db)

    async def get_by_org(self, org_id: uuid.UUID) -> list[AIAgent]:
        stmt = select(AIAgent).where(
            AIAgent.organization_id == org_id, AIAgent.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


class ToolRegistryRepository(BaseRepository[ToolRegistry]):
    def __init__(self, db: AsyncSession):
        super().__init__(ToolRegistry, db)

    async def find_by_name(self, name: str) -> ToolRegistry | None:
        stmt = select(ToolRegistry).where(
            ToolRegistry.tool_name == name, ToolRegistry.is_deleted == False
        )
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


class AIAgentRunRepository(BaseRepository[AIAgentRun]):
    def __init__(self, db: AsyncSession):
        super().__init__(AIAgentRun, db)
