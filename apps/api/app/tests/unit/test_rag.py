import pytest
import uuid
from app.services.rag.ingestion_service import RAGIngestionService
from app.services.rag.embedding_service import RAGEmbeddingService
from app.services.rag.vector_db_service import RAGVectorDBService
from app.services.rag.retrieval_service import RAGRetrievalService
from app.services.rag.rag_pipeline_service import RAGPipelineService


@pytest.mark.asyncio
async def test_rag_ingestion_parsing_and_chunking():
    ingestion = RAGIngestionService()
    file_content = b"VertexERP AI is a leading enterprise suite. It has high modularity. We love SOLID."
    
    chunks = await ingestion.parse_and_chunk(
        file_content=file_content,
        file_name="handbook.md",
        mime_type="text/markdown",
        chunk_size=5,
        chunk_overlap=1
    )
    
    assert len(chunks) > 0
    assert chunks[0]["chunk_index"] == 0
    assert "language" in chunks[0]
    assert chunks[0]["language"] == "en"
    assert chunks[0]["word_count"] > 0
    assert chunks[0]["token_count"] > 0


@pytest.mark.asyncio
async def test_rag_embedding_service():
    emb_service = RAGEmbeddingService()
    text = "Enterprise AI agent patterns"
    
    vec1 = await emb_service.get_embedding(text, provider="openai")
    vec2 = await emb_service.get_embedding(text, provider="openai")
    
    assert len(vec1) == 1536
    assert vec1 == vec2 # Cache matches same values
    
    # Try gemini dimension mapping
    vec_gemini = await emb_service.get_embedding(text, provider="gemini")
    assert len(vec_gemini) == 768


@pytest.mark.asyncio
async def test_rag_vector_db_and_retrieval():
    vector_db = RAGVectorDBService(provider="faiss")
    emb_service = RAGEmbeddingService()
    
    # Setup test vectors
    org_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    col_id = uuid.uuid4()
    
    content = "This document outlines employee leave rules and HR performance review instructions."
    vec = await emb_service.get_embedding(content)
    
    vector_id = str(uuid.uuid4())
    metadata = {
        "document_id": str(doc_id),
        "document_title": "HR Handbook 2026",
        "document_type": "handbook",
        "category": "hr",
        "collection_id": str(col_id),
        "organization_id": str(org_id),
        "tags": ["hr", "leaves"],
        "chunk_index": 0,
        "content": content
    }
    
    await vector_db.insert_vector(vector_id, vec, metadata)
    
    # Create Retrieval Service dependencies
    class MockRepo:
        async def log_retrieval(self, log):
            pass
            
    mock_repo = MockRepo()
    retrieval_service = RAGRetrievalService(
        repository=mock_repo,
        embedding_service=emb_service,
        vector_db_service=vector_db
    )
    
    # Search
    search_res = await retrieval_service.retrieve(
        org_id=org_id,
        user_id=uuid.uuid4(),
        query="leave rules",
        collection_ids=[col_id],
        top_k=2,
        search_type="hybrid"
    )
    
    assert search_res["total_found"] > 0
    assert search_res["results"][0]["document_title"] == "HR Handbook 2026"
    assert search_res["results"][0]["score"] > 0.0


@pytest.mark.asyncio
async def test_rag_pipeline_answering():
    vector_db = RAGVectorDBService(provider="faiss")
    emb_service = RAGEmbeddingService()
    
    org_id = uuid.uuid4()
    doc_id = uuid.uuid4()
    
    content = "The manufacturing specifications require operating heat under 75 degrees Celsius."
    vec = await emb_service.get_embedding(content)
    vector_id = str(uuid.uuid4())
    
    await vector_db.insert_vector(vector_id, vec, {
        "document_id": str(doc_id),
        "document_title": "Manufacturing Specs",
        "document_type": "manual",
        "category": "manufacturing",
        "organization_id": str(org_id),
        "chunk_index": 0,
        "content": content
    })
    
    class MockRepo:
        async def log_retrieval(self, log):
            pass
            
    retrieval_service = RAGRetrievalService(
        repository=MockRepo(),
        embedding_service=emb_service,
        vector_db_service=vector_db
    )
    
    pipeline = RAGPipelineService(retrieval_service)
    
    ans_res = await pipeline.answer_query(
        org_id=org_id,
        user_id=uuid.uuid4(),
        query="what heat operates manufacturing specs?",
        provider="gemini",
        model_name="gemini-1.5-pro"
    )
    
    assert "Manufacturing Specs" in ans_res["answer"]
    assert len(ans_res["citations"]) > 0
    assert ans_res["citations"][0]["document_title"] == "Manufacturing Specs"
