import uuid
from datetime import datetime
from typing import Any, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.rag_repository import RAGRepository
from app.models.rag import (
    KnowledgeCollection,
    RAGDocument,
    DocumentVersion,
    DocumentChunk,
    EmbeddingMetadata,
    RAGChatSession,
    RAGChatMessage,
    RAGFeedback,
)
from app.schemas.rag import (
    KnowledgeCollectionCreate,
    KnowledgeCollectionUpdate,
    RAGDocumentCreate,
    RAGDocumentUpdate,
    FeedbackCreate,
)
from app.services.rag.ingestion_service import RAGIngestionService
from app.services.rag.embedding_service import RAGEmbeddingService
from app.services.rag.vector_db_service import RAGVectorDBService
from app.services.rag.retrieval_service import RAGRetrievalService
from app.services.rag.rag_pipeline_service import RAGPipelineService


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = RAGRepository(db)
        self.ingestion_service = RAGIngestionService()
        self.embedding_service = RAGEmbeddingService()
        self.vector_db_service = RAGVectorDBService()
        self.retrieval_service = RAGRetrievalService(
            repository=self.repository,
            embedding_service=self.embedding_service,
            vector_db_service=self.vector_db_service
        )
        self.pipeline_service = RAGPipelineService(self.retrieval_service)

    # ==================== Collections ====================
    async def create_collection(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        schema: KnowledgeCollectionCreate
    ) -> KnowledgeCollection:
        slug = schema.name.lower().replace(" ", "-")
        collection = KnowledgeCollection(
            organization_id=org_id,
            name=schema.name,
            slug=slug,
            description=schema.description,
            category=schema.category,
            tags=schema.tags,
            is_public=schema.is_public,
            metadata_json=schema.metadata_json,
            created_by=user_id
        )
        return await self.repository.create_collection(collection)

    async def get_collection(self, collection_id: uuid.UUID, org_id: uuid.UUID) -> KnowledgeCollection | None:
        return await self.repository.get_collection(collection_id, org_id)

    async def list_collections(self, org_id: uuid.UUID, category: str | None = None) -> Sequence[KnowledgeCollection]:
        return await self.repository.list_collections(org_id, category)

    async def delete_collection(self, collection_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        return await self.repository.delete_collection(collection_id, org_id)

    # ==================== Documents ====================
    async def upload_document(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        schema: RAGDocumentCreate,
        file_content: bytes
    ) -> RAGDocument:
        # Create Document record
        doc = RAGDocument(
            organization_id=org_id,
            collection_id=schema.collection_id,
            title=schema.title,
            file_name=schema.file_name,
            file_path=schema.file_path,
            file_size=schema.file_size,
            mime_type=schema.mime_type,
            document_type=schema.document_type,
            format=schema.format,
            language=schema.language,
            category=schema.category,
            tags=schema.tags,
            current_version=1,
            status="processing",
            approval_status=schema.approval_status,
            retention_days=schema.retention_days,
            metadata_json=schema.metadata_json,
            created_by=user_id,
            updated_by=user_id
        )
        created_doc = await self.repository.create_document(doc)

        # Create Version record
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()
        version = DocumentVersion(
            document_id=created_doc.id,
            version_number=1,
            file_path=schema.file_path,
            file_size=schema.file_size,
            file_hash=file_hash,
            metadata_json=schema.metadata_json,
            created_by=user_id
        )
        created_version = await self.repository.create_version(version)

        # Ingest and create chunks
        chunks = await self.ingestion_service.parse_and_chunk(
            file_content=file_content,
            file_name=schema.file_name,
            mime_type=schema.mime_type
        )

        db_chunks = []
        for c in chunks:
            chunk = DocumentChunk(
                document_id=created_doc.id,
                version_id=created_version.id,
                chunk_index=c["chunk_index"],
                content=c["content"],
                clean_content=c["clean_content"],
                token_count=c["token_count"],
                word_count=c["word_count"],
                chunk_hash=c["chunk_hash"],
                language=c["language"],
                metadata_json=c["metadata_json"]
            )
            db_chunks.append(chunk)

        saved_chunks = await self.repository.create_chunks(db_chunks)

        # Generate Embeddings & Insert into Vector DB
        for sc in saved_chunks:
            vector = await self.embedding_service.get_embedding(
                text=sc.content,
                provider="openai"
            )
            vector_id = str(sc.id)

            # Save Embedding Metadata
            emb_meta = EmbeddingMetadata(
                chunk_id=sc.id,
                provider="openai",
                model_name="text-embedding-3-small",
                vector_id=vector_id,
                dimension=len(vector),
                status="indexed"
            )
            await self.repository.save_embedding_metadata(emb_meta)

            # Insert into Vector DB
            await self.vector_db_service.insert_vector(
                vector_id=vector_id,
                vector=vector,
                metadata={
                    "document_id": str(created_doc.id),
                    "document_title": created_doc.title,
                    "document_type": created_doc.document_type,
                    "category": created_doc.category,
                    "collection_id": str(created_doc.collection_id) if created_doc.collection_id else None,
                    "organization_id": str(org_id),
                    "tags": created_doc.tags,
                    "chunk_index": sc.chunk_index,
                    "content": sc.content
                }
            )

        # Update Document status to indexed
        created_doc.status = "indexed"
        await self.db.flush()

        return created_doc

    async def get_document(self, document_id: uuid.UUID, org_id: uuid.UUID) -> RAGDocument | None:
        return await self.repository.get_document(document_id, org_id)

    async def list_documents(
        self,
        org_id: uuid.UUID,
        collection_id: uuid.UUID | None = None,
        category: str | None = None,
        document_type: str | None = None,
        status: str | None = None,
        search_query: str | None = None,
    ) -> Sequence[RAGDocument]:
        return await self.repository.list_documents(
            org_id=org_id,
            collection_id=collection_id,
            category=category,
            document_type=document_type,
            status=status,
            search_query=search_query
        )

    async def delete_document(self, document_id: uuid.UUID, org_id: uuid.UUID) -> bool:
        return await self.repository.delete_document(document_id, org_id)

    # ==================== Retrieval / Search ====================
    async def search(
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
        return await self.retrieval_service.retrieve(
            org_id=org_id,
            user_id=user_id,
            query=query,
            collection_ids=collection_ids,
            categories=categories,
            document_types=document_types,
            tags=tags,
            top_k=top_k,
            search_type=search_type,
            provider=provider,
            min_score=min_score
        )

    # ==================== RAG Chat ====================
    async def create_chat_session(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str = "New Conversation"
    ) -> RAGChatSession:
        session = RAGChatSession(
            organization_id=org_id,
            user_id=user_id,
            title=title,
            is_pinned=False
        )
        return await self.repository.create_chat_session(session)

    async def get_chat_session(self, session_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID) -> RAGChatSession | None:
        return await self.repository.get_chat_session(session_id, org_id, user_id)

    async def list_chat_sessions(self, org_id: uuid.UUID, user_id: uuid.UUID) -> Sequence[RAGChatSession]:
        return await self.repository.list_chat_sessions(org_id, user_id)

    async def send_chat_message(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        session_id: uuid.UUID,
        query: str,
        collection_ids: list[uuid.UUID] | None = None,
        provider: str = "openai",
        model_name: str = "gpt-4o",
        temperature: float = 0.7,
        top_k: int = 5,
        search_type: str = "hybrid"
    ) -> tuple[RAGChatMessage, RAGChatMessage]:
        # Fetch session
        session = await self.get_chat_session(session_id, org_id, user_id)
        if not session:
            raise ValueError("Chat session not found")

        history = []
        for msg in session.messages[-10:]:
            history.append({
                "role": msg.role,
                "content": msg.content
            })

        user_message = RAGChatMessage(
            session_id=session_id,
            role="user",
            content=query
        )
        user_msg = await self.repository.add_chat_message(user_message)

        pipeline_output = await self.pipeline_service.answer_query(
            org_id=org_id,
            user_id=user_id,
            query=query,
            session_id=session_id,
            chat_history=history,
            collection_ids=collection_ids,
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            top_k=top_k,
            search_type=search_type
        )

        assistant_message = RAGChatMessage(
            session_id=session_id,
            role="assistant",
            content=pipeline_output["answer"],
            prompt_tokens=pipeline_output["prompt_tokens"],
            completion_tokens=pipeline_output["completion_tokens"],
            citations=pipeline_output["citations"]
        )
        assistant_msg = await self.repository.add_chat_message(assistant_message)

        session.updated_at = datetime.utcnow()
        await self.db.flush()

        return user_msg, assistant_msg

    async def toggle_pin_session(self, session_id: uuid.UUID, org_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.repository.toggle_pin_session(session_id, org_id, user_id)

    # ==================== Feedback ====================
    async def submit_feedback(
        self,
        org_id: uuid.UUID,
        user_id: uuid.UUID,
        schema: FeedbackCreate
    ) -> RAGFeedback:
        feedback = RAGFeedback(
            organization_id=org_id,
            user_id=user_id,
            chat_message_id=schema.chat_message_id,
            chunk_id=schema.chunk_id,
            rating=schema.rating,
            feedback_type=schema.feedback_type,
            comments=schema.comments,
            metadata_json=schema.metadata_json
        )
        return await self.repository.add_feedback(feedback)
