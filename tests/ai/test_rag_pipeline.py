"""Comprehensive Test Suite for Production RAG (Retrieval-Augmented Generation) in VertexERP AI V2.

Covers:
1. Document Upload, Versioning (v1 -> v2), Checksum Verification, and Metadata.
2. Step-by-Step Pipeline: Parse -> Clean -> Chunk -> Embed -> Index.
3. Asynchronous Ingestion Pipeline with Job States (PENDING, PROCESSING, COMPLETED, FAILED).
4. Ingestion Failures, Retry Loops, and Dead-Letter Queue (DLQ) Handling.
5. Vector Cosine Similarity Search and Hybrid Reranking (Semantic + Lexical BM25 + Header Boost).
6. Grounded Answer Generation with In-line Citations [Doc: ..., v..., Chunk: ...] and Structured Citation Extraction.
7. Rigorous Multi-Tenant Cross-Tenant Retrieval Isolation Defense.
8. User Authorization, Access Level (PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED), and Department-level Filtering.
9. AI Copilot Tool Integration (`query_knowledge_base`).
10. FastAPI REST Endpoints Integration.
"""

import uuid
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.modules.ai.models.rag_document import (
    RAGDocumentVersion,
)
from app.modules.ai.rag.chunker import RAGChunker
from app.modules.ai.rag.cleaner import RAGCleaner
from app.modules.ai.rag.embedder import RAGEmbedder
from app.modules.ai.rag.indexer import RAGIndexer
from app.modules.ai.rag.ingestion_worker import RAGIngestionWorker
from app.modules.ai.rag.parser import RAGParser
from app.modules.ai.rag.rag_service import rag_service
from app.modules.ai.schemas.rag import (
    RAGAccessLevel,
    RAGDocumentCreate,
    RAGDocumentVersionCreate,
    RAGQueryRequest,
    RAGSearchRequest,
)
from app.modules.ai.tools.registry import erp_tool_registry
from app.modules.identity.services.jwt_service import JwtService
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def rag_test_env(db_session: AsyncSession):
    """Sets up a comprehensive multi-tenant test environment with Tenant A and Tenant B."""
    # Tenant A
    tenant_a = Tenant(
        id=uuid.uuid4(),
        name="Apex Industrial Dynamics",
        slug=f"apex-{uuid.uuid4().hex[:6]}",
    )
    db_session.add(tenant_a)
    await db_session.flush()

    org_a = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        name="Apex HQ North America",
        legal_name="Apex Corp",
        tax_identifier="US-999000111",
        base_currency="USD",
    )
    db_session.add(org_a)
    await db_session.flush()

    # Tenant B
    tenant_b = Tenant(
        id=uuid.uuid4(),
        name="Zenith Global Logistics",
        slug=f"zenith-{uuid.uuid4().hex[:6]}",
    )
    db_session.add(tenant_b)
    await db_session.flush()

    org_b = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        name="Zenith Logistics EMEA",
        legal_name="Zenith EMEA Ltd",
        tax_identifier="GB-555444333",
        base_currency="EUR",
    )
    db_session.add(org_b)
    await db_session.flush()

    # Users
    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()

    return {
        "tenant_a": tenant_a,
        "org_a": org_a,
        "user_a_id": user_a_id,
        "tenant_b": tenant_b,
        "org_b": org_b,
        "user_b_id": user_b_id,
    }


def _create_jwt_token(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    org_id: uuid.UUID,
    roles: list[str],
    permissions: list[str],
) -> str:
    """Generate mock signed JWT for API tests."""
    token, _, _ = JwtService.create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        organization_id=org_id,
        roles=roles,
        permissions=permissions,
        session_id=uuid.uuid4(),
    )
    return token


# ------------------------------------------------------------------------------
# 1. Document Upload & Versioning Tests
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_document_upload_and_versioning(rag_test_env, db_session: AsyncSession):
    """Test document creation, checksum calculation, versioning v1 -> v2, and active flags."""
    env = rag_test_env
    tenant_a_id = env["tenant_a"].id
    org_a_id = env["org_a"].id
    user_a_id = env["user_a_id"]

    raw_v1 = "# Warehouse Stock Transfer SOP\n\nAll transfers require supervisor approval."
    create_payload = RAGDocumentCreate(
        title="Warehouse Stock Transfer Policy",
        description="Standard operating procedure for moving stock between warehouses.",
        raw_content=raw_v1,
        file_type="markdown",
        access_level=RAGAccessLevel.INTERNAL,
        tags=["inventory", "sop", "warehouses"],
    )

    doc, job = await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_a_id,
        organization_id=org_a_id,
        user_id=user_a_id,
        payload=create_payload,
        eager=True,
    )
    doc_id = doc.id

    v1_stmt = select(RAGDocumentVersion).where(
        RAGDocumentVersion.document_id == doc_id,
        RAGDocumentVersion.tenant_id == tenant_a_id,
    )
    v1_res = (await db_session.execute(v1_stmt)).scalars().all()
    assert len(v1_res) == 1
    assert v1_res[0].version_number == 1
    assert v1_res[0].is_active is True
    assert v1_res[0].checksum == rag_service._compute_checksum(raw_v1)
    assert job.status == "COMPLETED"

    # Create Version 2
    raw_v2 = "# Warehouse Stock Transfer SOP v2\n\nTransfers exceeding 100 units require Plant Manager approval."
    v2_payload = RAGDocumentVersionCreate(
        raw_content=raw_v2,
        changelog="Added Plant Manager approval rule for transfers > 100 units",
    )

    v2, job2 = await rag_service.create_document_version(
        session=db_session,
        tenant_id=tenant_a_id,
        document_id=doc_id,
        organization_id=org_a_id,
        user_id=user_a_id,
        payload=v2_payload,
        eager=True,
    )

    assert v2.version_number == 2
    assert v2.is_active is True
    assert v2.changelog == "Added Plant Manager approval rule for transfers > 100 units"
    assert job2.status == "COMPLETED"

    # Verify all versions in database for this document
    all_v_stmt = (
        select(RAGDocumentVersion)
        .where(
            RAGDocumentVersion.document_id == doc_id,
            RAGDocumentVersion.tenant_id == tenant_a_id,
        )
        .order_by(RAGDocumentVersion.version_number.asc())
    )
    all_versions = (await db_session.execute(all_v_stmt)).scalars().all()
    assert len(all_versions) == 2
    assert all_versions[0].version_number == 1
    assert all_versions[0].is_active is False
    assert all_versions[1].version_number == 2
    assert all_versions[1].is_active is True


# ------------------------------------------------------------------------------
# 2. Pipeline Stages: Parse -> Clean -> Chunk -> Embed -> Index
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rag_pipeline_stages(rag_test_env, db_session: AsyncSession):
    """Verify each discrete pipeline stage from raw text to indexed chunk entities."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id

    raw_text = """## Section 1: Pre-Production Check
\x00\x08Inspect all raw titanium ingots for cracks.

## Section 2: Post-Production Inspection
Measure dimensional tolerance with micrometers (±0.005mm).
"""

    # Stage 1: Parse
    sections = RAGParser.parse_document(raw_text, file_type="markdown")
    assert len(sections) == 2
    assert sections[0].heading == "Section 1: Pre-Production Check"
    assert sections[1].heading == "Section 2: Post-Production Inspection"

    # Stage 2: Clean
    cleaned = RAGCleaner.clean_text(sections[0].content)
    assert "\x00" not in cleaned
    assert "titanium ingots" in cleaned

    # Stage 3: Chunk
    chunker = RAGChunker(chunk_size_tokens=100, chunk_overlap_tokens=10)
    chunks = chunker.chunk_document(
        raw_text, file_type="markdown", doc_metadata={"doc_id": "test-123"}
    )
    assert len(chunks) >= 2
    for c in chunks:
        assert c.token_count > 0
        assert c.char_count > 0
        assert c.section_heading is not None

    # Stage 4: Embed
    embedder = RAGEmbedder()
    chunk_texts = [c.content for c in chunks]
    embeddings, total_tokens, cost = await embedder.embed_texts(chunk_texts)
    assert len(embeddings) == len(chunks)
    assert len(embeddings[0]) == 1536  # 1536-dimensional vectors
    assert total_tokens > 0

    # Stage 5: Index
    dummy_doc_id = uuid.uuid4()
    dummy_ver_id = uuid.uuid4()
    indexer = RAGIndexer()
    indexed_chunks = await indexer.index_chunks(
        session=db_session,
        tenant_id=tenant_id,
        document_id=dummy_doc_id,
        version_id=dummy_ver_id,
        chunks=chunks,
        embeddings=embeddings,
    )
    assert len(indexed_chunks) == len(chunks)
    assert indexed_chunks[0].embedding_json is not None


# ------------------------------------------------------------------------------
# 3. Asynchronous Ingestion Worker & Job State Progression
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_async_ingestion_jobs_and_states(rag_test_env, db_session: AsyncSession):
    """Test job state transitions PENDING -> PROCESSING -> COMPLETED with metrics tracking."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    doc_payload = RAGDocumentCreate(
        title="Procurement Guidelines",
        raw_content="Purchase requests exceeding $5,000 require CFO sign-off.",
        file_type="text",
        access_level=RAGAccessLevel.INTERNAL,
    )

    doc, job = await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=doc_payload,
        eager=False,  # Enqueued in PENDING state
    )

    assert job.status == "PENDING"

    # Now execute worker
    worker = RAGIngestionWorker()
    processed_job = await worker.process_job(job.id, session=db_session)

    assert processed_job.status == "COMPLETED"
    assert processed_job.completed_at is not None
    assert processed_job.metrics_json["chunk_count"] >= 1
    assert processed_job.metrics_json["total_tokens"] > 0
    assert "duration_ms" in processed_job.metrics_json


# ------------------------------------------------------------------------------
# 4. Retries & Dead-Letter Queue (DLQ) Handling
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_ingestion_retries_and_dead_letter(rag_test_env, db_session: AsyncSession):
    """Verify that transient failures trigger retry backoff, and exhausting retries moves job to dead-letter state."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    doc_payload = RAGDocumentCreate(
        title="Flaky Ingestion Test Doc",
        raw_content="Some test content to trigger simulated embedding failure.",
        file_type="text",
    )

    doc, job = await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=doc_payload,
        eager=False,
    )

    worker = RAGIngestionWorker()

    # Simulate failure on embedding step
    with patch.object(
        worker.embedder, "embed_texts", side_effect=RuntimeError("AI Gateway Timeout 504")
    ):
        # Attempt 1
        j1 = await worker.process_job(job.id, session=db_session)
        assert j1.retry_count == 1
        assert j1.status == "PENDING"
        assert j1.dead_letter is False
        assert "AI Gateway Timeout" in j1.error_message

        # Attempt 2
        j2 = await worker.process_job(job.id, session=db_session)
        assert j2.retry_count == 2
        assert j2.status == "PENDING"
        assert j2.dead_letter is False

        # Attempt 3 (Exhausts max_retries = 3)
        j3 = await worker.process_job(job.id, session=db_session)
        assert j3.retry_count == 3
        assert j3.status == "FAILED"
        assert j3.dead_letter is True
        assert "Max retries (3) exhausted" in j3.dead_letter_reason

    # Test Job Retry Recovery
    retried_job = await rag_service.retry_ingestion_job(
        session=db_session,
        tenant_id=tenant_id,
        job_id=job.id,
        force_reset=True,
        eager=True,
    )
    assert retried_job.status == "COMPLETED"
    assert retried_job.dead_letter is False
    assert retried_job.retry_count == 0


# ------------------------------------------------------------------------------
# 5. Vector Search & Hybrid Reranking
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_vector_search_and_reranking(rag_test_env, db_session: AsyncSession):
    """Verify semantic vector search combined with BM25 lexical reranker returns top chunks."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    content = """# Production Routing Manual

## Machine Calibration
Calibrate 5-axis CNC machines every Monday morning before shift starts.

## Emergency Stop Protocol
Press the red emergency button on console panel in case of coolant leak.
"""
    doc_payload = RAGDocumentCreate(
        title="Machining SOPs",
        raw_content=content,
        file_type="markdown",
        access_level=RAGAccessLevel.INTERNAL,
    )

    await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=doc_payload,
        eager=True,
    )

    search_req = RAGSearchRequest(
        query="When should CNC machines be calibrated?",
        top_k=3,
    )

    search_resp = await rag_service.search_knowledge(
        session=db_session,
        tenant_id=tenant_id,
        payload=search_req,
    )

    assert search_resp.total_results >= 1
    top_hit = search_resp.results[0]
    assert "CNC machines" in top_hit.content
    assert top_hit.composite_score > 0.0
    assert top_hit.vector_score > 0.0


# ------------------------------------------------------------------------------
# 6. Grounded Generation & In-line Structured Citations
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rag_generation_and_structured_citations(rag_test_env, db_session: AsyncSession):
    """Test end-to-end grounded RAG generation, inline citation markers, and telemetry logging."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    policy_content = """# Employee Travel & Expense Policy

## Meal Allowance
Employees on official business trips are entitled to a daily per-diem meal allowance of $75.
"""
    await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=RAGDocumentCreate(
            title="Travel Expense Policy",
            raw_content=policy_content,
            file_type="markdown",
        ),
        eager=True,
    )

    query_req = RAGQueryRequest(
        query="What is the daily meal allowance for business travel?",
        top_k=3,
    )

    resp = await rag_service.query_knowledge(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=query_req,
    )

    assert resp.query == "What is the daily meal allowance for business travel?"
    assert len(resp.answer) > 0
    assert resp.retrieved_chunks_count >= 1
    assert len(resp.citations) >= 1

    top_cite = resp.citations[0]
    assert top_cite.document_title == "Travel Expense Policy"
    assert top_cite.version_number == 1
    assert len(top_cite.snippet) > 0


# ------------------------------------------------------------------------------
# 7. Rigorous Cross-Tenant Isolation Defense
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cross_tenant_isolation_rigorous(rag_test_env, db_session: AsyncSession):
    """Explicitly verify that Tenant A cannot retrieve, search, or cite Tenant B's documents."""
    env = rag_test_env
    tenant_a_id = env["tenant_a"].id
    org_a_id = env["org_a"].id
    user_a_id = env["user_a_id"]

    tenant_b_id = env["tenant_b"].id
    org_b_id = env["org_b"].id
    user_b_id = env["user_b_id"]

    # Ingest Document into Tenant A
    doc_a_payload = RAGDocumentCreate(
        title="Apex Secret Propulsion Blueprint",
        raw_content="Project Quantum: Ionic thruster reactor architecture for aerospace satellites.",
        file_type="text",
        access_level=RAGAccessLevel.INTERNAL,
    )
    doc_a, _ = await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_a_id,
        organization_id=org_a_id,
        user_id=user_a_id,
        payload=doc_a_payload,
        eager=True,
    )

    # Ingest Document into Tenant B
    doc_b_payload = RAGDocumentCreate(
        title="Zenith Maritime Logistics Route 2026",
        raw_content="Vessel Alpha container schedule from Rotterdam to Singapore maritime corridor.",
        file_type="text",
        access_level=RAGAccessLevel.INTERNAL,
    )
    doc_b, _ = await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_b_id,
        organization_id=org_b_id,
        user_id=user_b_id,
        payload=doc_b_payload,
        eager=True,
    )

    # 1. Tenant B searches using Tenant A's exact secret keyword
    tenant_b_search = await rag_service.search_knowledge(
        session=db_session,
        tenant_id=tenant_b_id,
        payload=RAGSearchRequest(query="Project Quantum Ionic thruster aerospace blueprint"),
    )
    for result in tenant_b_search.results:
        assert result.document_id != doc_a.id
        assert "Ionic thruster" not in result.content

    # 2. Tenant A searches using Tenant B's maritime keywords
    tenant_a_search = await rag_service.search_knowledge(
        session=db_session,
        tenant_id=tenant_a_id,
        payload=RAGSearchRequest(query="Vessel Alpha Rotterdam Singapore maritime corridor"),
    )
    for result in tenant_a_search.results:
        assert result.document_id != doc_b.id
        assert "Vessel Alpha" not in result.content

    # 3. Direct document ID query across tenants
    cross_doc = await rag_service.get_document(
        session=db_session,
        tenant_id=tenant_b_id,
        document_id=doc_a.id,  # Trying to fetch Tenant A doc using Tenant B credentials
    )
    assert cross_doc is None


# ------------------------------------------------------------------------------
# 8. User Authorization & Access Level Filtering
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_user_authorization_and_permission_filtering(rag_test_env, db_session: AsyncSession):
    """Verify that CONFIDENTIAL and RESTRICTED documents enforce role/department boundaries."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    # Ingest Confidential Executive Doc
    exec_doc_payload = RAGDocumentCreate(
        title="M&A Acquisition Strategy 2027",
        raw_content="Apex intends to acquire Robotics Co for $45M in cash and stock.",
        access_level=RAGAccessLevel.CONFIDENTIAL,
        allowed_roles=["Executive", "ChiefFinancialOfficer"],
        allowed_departments=["Executive", "Finance"],
    )
    await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=exec_doc_payload,
        eager=True,
    )

    # Standard User query -> Expect 0 results
    std_search = await rag_service.search_knowledge(
        session=db_session,
        tenant_id=tenant_id,
        payload=RAGSearchRequest(query="Robotics Co acquisition"),
        user_roles={"StandardUser"},
        user_department="Warehouse",
    )
    assert len(std_search.results) == 0

    # Executive User query -> Expect top match
    exec_search = await rag_service.search_knowledge(
        session=db_session,
        tenant_id=tenant_id,
        payload=RAGSearchRequest(query="Robotics Co acquisition"),
        user_roles={"Executive"},
        user_department="Executive",
    )
    assert len(exec_search.results) >= 1
    assert "M&A Acquisition Strategy" in exec_search.results[0].document_title


# ------------------------------------------------------------------------------
# 9. AI Copilot Tool Integration (`query_knowledge_base`)
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rag_copilot_tool_integration(rag_test_env, db_session: AsyncSession):
    """Verify QueryKnowledgeBaseTool executes properly within ERPToolRegistry."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    # Create safety manual
    await rag_service.create_document(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        payload=RAGDocumentCreate(
            title="Factory Safety Protocol",
            raw_content="All personnel on shop floor must wear steel-toed boots and ANSI safety goggles.",
        ),
        eager=True,
    )

    tool = erp_tool_registry.get_tool("query_knowledge_base")
    assert tool is not None
    assert tool.name == "query_knowledge_base"
    assert tool.is_mutation is False

    tool_result = await tool.execute(
        session=db_session,
        tenant_id=tenant_id,
        organization_id=org_id,
        user_id=user_id,
        parameters={"query": "safety goggles requirement", "top_k": 2},
    )

    assert tool_result["total_matches"] >= 1
    assert "Factory Safety Protocol" in tool_result["results"][0]["document_title"]


# ------------------------------------------------------------------------------
# 10. FastAPI REST Endpoints Integration
# ------------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_rag_rest_api_endpoints(async_client: AsyncClient, rag_test_env):
    """Verify HTTP REST endpoints for documents, search, QA query, and deletion."""
    env = rag_test_env
    tenant_id = env["tenant_a"].id
    org_id = env["org_a"].id
    user_id = env["user_a_id"]

    token = _create_jwt_token(
        user_id=user_id,
        tenant_id=tenant_id,
        org_id=org_id,
        roles=["TenantAdmin"],
        permissions=[
            PermissionCode.AI_RAG_DOCUMENTS_READ.value,
            PermissionCode.AI_RAG_DOCUMENTS_WRITE.value,
            PermissionCode.AI_RAG_DOCUMENTS_DELETE.value,
            PermissionCode.AI_RAG_QUERY.value,
            PermissionCode.AI_COPILOT_USE.value,
        ],
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Tenant-ID": str(tenant_id),
        "X-Organization-ID": str(org_id),
    }

    # 1. Create Document via POST
    create_resp = await async_client.post(
        "/api/v1/ai/rag/documents?eager=true",
        headers=headers,
        json={
            "title": "API Onboarding Handbook",
            "description": "API test doc",
            "raw_content": "# Welcome\n\nNew hires receive 20 days paid annual leave.",
            "file_type": "markdown",
            "access_level": "INTERNAL",
            "tags": ["hr", "handbook"],
        },
    )
    assert create_resp.status_code == 201
    create_data = create_resp.json()
    doc_id = create_data["document_id"]
    assert create_data["job_status"] == "COMPLETED"

    # 2. List Documents via GET
    list_resp = await async_client.get(
        "/api/v1/ai/rag/documents",
        headers=headers,
    )
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1

    # 3. Get Document Details
    detail_resp = await async_client.get(
        f"/api/v1/ai/rag/documents/{doc_id}",
        headers=headers,
    )
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["title"] == "API Onboarding Handbook"
    assert len(detail_data["versions"]) == 1

    # 4. Search Knowledge via POST /search
    search_resp = await async_client.post(
        "/api/v1/ai/rag/search",
        headers=headers,
        json={"query": "annual leave days", "top_k": 3},
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["total_results"] >= 1

    # 5. Query Knowledge via POST /query
    query_resp = await async_client.post(
        "/api/v1/ai/rag/query",
        headers=headers,
        json={"query": "How many days of paid leave do new hires get?", "top_k": 3},
    )
    assert query_resp.status_code == 200
    query_data = query_resp.json()
    assert len(query_data["answer"]) > 0
    assert len(query_data["citations"]) >= 1

    # 6. Delete Document via DELETE
    del_resp = await async_client.delete(
        f"/api/v1/ai/rag/documents/{doc_id}",
        headers=headers,
    )
    assert del_resp.status_code == 200
