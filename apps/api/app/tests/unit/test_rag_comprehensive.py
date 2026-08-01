import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.schemas.rag import KnowledgeCollectionCreate, RAGDocumentCreate, RetrievalRequest, PromptChatRequest
from app.services.rag_service import RAGService
from app.services.rag.ingestion_service import RAGIngestionService
from app.services.rag.embedding_service import RAGEmbeddingService
from app.services.rag.vector_db_service import RAGVectorDBService
from app.services.rag.retrieval_service import RAGRetrievalService
from app.services.rag.rag_pipeline_service import RAGPipelineService
from app.models.rag import KnowledgeCollection, RAGDocument, DocumentVersion, DocumentChunk, EmbeddingMetadata, RAGChatSession, RAGChatMessage


@pytest.mark.asyncio
async def test_ingestion_parsing_and_chunking():
    ingestion = RAGIngestionService()

    file_content = b"VertexERP AI is an enterprise Resource Planning platform. It integrates Finance, CRM, HR, Inventory, and Manufacturing modules with RAG intelligence."
    chunks = await ingestion.parse_and_chunk(
        file_content=file_content,
        file_name="enterprise_overview.txt",
        mime_type="text/plain",
        chunk_size=10,
        chunk_overlap=2
    )

    assert len(chunks) > 0
    assert "content" in chunks[0]
    assert chunks[0]["token_count"] > 0
    assert chunks[0]["language"] == "en"


@pytest.mark.asyncio
async def test_embedding_generation_and_caching():
    embedding_service = RAGEmbeddingService()

    vec1 = await embedding_service.get_embedding(
        text="Enterprise RAG Vector Embedding Test",
        provider="openai",
        model_name="text-embedding-3-small"
    )

    assert len(vec1) == 1536

    # Test cache hit
    vec2 = await embedding_service.get_embedding(
        text="Enterprise RAG Vector Embedding Test",
        provider="openai",
        model_name="text-embedding-3-small"
    )

    assert vec1 == vec2


@pytest.mark.asyncio
async def test_faiss_vector_db_and_hybrid_retrieval():
    vector_db = RAGVectorDBService()
    embedding_service = RAGEmbeddingService()
    retrieval_service = RAGRetrievalService(None, embedding_service, vector_db)

    org_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    vector_id = str(uuid.uuid4())

    text_sample = "Financial policy requires all expense reports to be submitted within 30 days."
    vec = await embedding_service.get_embedding(text_sample, provider="openai")

    await vector_db.insert_vector(
        vector_id=vector_id,
        vector=vec,
        metadata={
            "document_id": str(doc_id),
            "document_title": "Financial Expense Policy",
            "document_type": "policy",
            "category": "finance",
            "organization_id": str(org_id),
            "content": text_sample,
            "chunk_index": 0
        }
    )

    # Search with filters
    res = await retrieval_service.retrieve(
        org_id=org_id,
        user_id=uuid.uuid4(),
        query="expense report submission policy",
        top_k=5,
        search_type="hybrid"
    )

    assert res["total_found"] > 0
    assert res["results"][0]["document_title"] == "Financial Expense Policy"
    assert res["results"][0]["score"] > 0.0


@pytest.mark.asyncio
async def test_rag_pipeline_answer_and_citations():
    vector_db = RAGVectorDBService()
    embedding_service = RAGEmbeddingService()
    retrieval_service = RAGRetrievalService(None, embedding_service, vector_db)
    pipeline = RAGPipelineService(retrieval_service)

    org_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    vector_id = str(uuid.uuid4())

    text_sample = "Safety compliance rule: Eye protection is mandatory in manufacturing zone B."
    vec = await embedding_service.get_embedding(text_sample, provider="openai")

    await vector_db.insert_vector(
        vector_id=vector_id,
        vector=vec,
        metadata={
            "document_id": str(doc_id),
            "document_title": "Manufacturing Safety Guidelines",
            "document_type": "guideline",
            "category": "manufacturing",
            "organization_id": str(org_id),
            "content": text_sample,
            "chunk_index": 0
        }
    )

    output = await pipeline.answer_query(
        org_id=org_id,
        user_id=uuid.uuid4(),
        query="What eye protection is required?",
        top_k=3
    )

    assert "answer" in output
    assert len(output["citations"]) > 0
    assert output["citations"][0]["document_title"] == "Manufacturing Safety Guidelines"
