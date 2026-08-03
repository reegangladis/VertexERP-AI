import uuid
from unittest.mock import MagicMock
import pytest
from fastapi import HTTPException

from app.models.ai_rag_copilot_v14 import (
    AIAgent,
    AIAgentRun,
    KnowledgeCollection,
    PromptTemplate,
    RAGChatMessage,
    RAGChatSession,
    RAGDocument,
)
from app.services.ai_rag_copilot import (
    AIAgentEngine,
    AIAnalyticsService,
    CopilotService,
    PromptEngine,
    RAGEngine,
)


def create_mock_execute_result(return_value=None, list_value=None):
    result = MagicMock()
    result.scalar_one_or_none.return_value = return_value
    result.scalars.return_value.all.return_value = list_value if list_value is not None else []
    return result


@pytest.mark.asyncio
async def test_knowledge_collection_and_ingestion(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    rag_engine = RAGEngine(mock_db_session)
    org_id = uuid.uuid4()

    from app.schemas.ai_rag_copilot import KnowledgeCollectionCreate, RAGDocumentCreate

    coll_payload = KnowledgeCollectionCreate(
        organization_id=org_id,
        name="Enterprise Financial Policies",
        description="Standard Operating Procedures for Procurement & Expenses",
    )

    coll_obj = KnowledgeCollection(
        id=uuid.uuid4(),
        organization_id=org_id,
        name=coll_payload.name,
        description=coll_payload.description,
        visibility="Internal",
        status="Active",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
    ]
    coll = await rag_engine.create_collection(coll_payload)
    assert coll is not None

    # Ingest document text
    doc_payload = RAGDocumentCreate(
        collection_id=coll_obj.id,
        document_name="Travel_Expense_Policy_2026.pdf",
        file_type="pdf",
        document_content="Employees can claim up to $150 per day for meals during international travel. Expense reports must be submitted within 30 days.",
    )

    doc_obj = RAGDocument(
        id=uuid.uuid4(),
        collection_id=coll_obj.id,
        document_name="Travel_Expense_Policy_2026.pdf",
        file_type="pdf",
        status="Processed",
        chunks=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # chunk insert
        create_mock_execute_result(doc_obj),  # get_with_chunks
    ]

    doc = await rag_engine.ingest_document(doc_payload)
    assert doc is not None
    assert doc.document_name == "Travel_Expense_Policy_2026.pdf"


@pytest.mark.asyncio
async def test_enterprise_copilot_chat(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    copilot_service = CopilotService(mock_db_session)
    org_id = uuid.uuid4()
    session_id = uuid.uuid4()

    from app.schemas.ai_rag_copilot import RAGChatMessageCreate, RAGChatSessionCreate

    session_payload = RAGChatSessionCreate(
        organization_id=org_id,
        session_name="Financial Policy Q&A",
        model_name="gpt-4o",
    )

    session_obj = RAGChatSession(
        id=session_id,
        organization_id=org_id,
        session_name="Financial Policy Q&A",
        model_name="gpt-4o",
        temperature=0.7,
        status="Active",
        messages=[],
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),
    ]
    session = await copilot_service.create_chat_session(session_payload)
    assert session is not None

    # Send chat message
    msg_payload = RAGChatMessageCreate(
        session_id=session_id,
        role="user",
        message="What is the meal expense limit for international travel?",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(session_obj),  # get session
        create_mock_execute_result(None),  # search chunks
    ]

    response_msg = await copilot_service.post_chat_message(msg_payload)
    assert response_msg is not None
    assert response_msg.role == "assistant"
    assert "VertexERP AI Copilot" in response_msg.message


@pytest.mark.asyncio
async def test_prompt_template_and_versioning(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    prompt_engine = PromptEngine(mock_db_session)

    from app.schemas.ai_rag_copilot import PromptTemplateCreate

    payload = PromptTemplateCreate(
        name="Financial Auditor Assistant",
        category="Finance",
        description="System prompt for compliance auditing",
        system_prompt="You are an expert enterprise auditor inspecting general ledger entries.",
    )

    prompt_obj = PromptTemplate(
        id=uuid.uuid4(),
        name=payload.name,
        category=payload.category,
        system_prompt=payload.system_prompt,
        status="Active",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(None),  # dup check
        create_mock_execute_result(None),  # insert version 1
    ]

    prompt = await prompt_engine.create_prompt_template(payload)
    assert prompt is not None
    assert prompt.name == "Financial Auditor Assistant"


@pytest.mark.asyncio
async def test_ai_agent_and_tool_execution(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None)
    agent_engine = AIAgentEngine(mock_db_session)
    org_id = uuid.uuid4()
    agent_id = uuid.uuid4()

    agent_obj = AIAgent(
        id=agent_id,
        organization_id=org_id,
        agent_name="Inventory Optimizer Agent",
        agent_type="Autonomous",
        system_prompt="Optimize reorder levels across regional warehouses.",
        model="gpt-4o",
        temperature=0.3,
        status="Active",
    )

    from app.schemas.ai_rag_copilot import AgentRunCreate

    run_payload = AgentRunCreate(
        agent_id=agent_id,
        input_text="Check stock levels for SKU-1002 in Warehouse A and optimize reorder quantity.",
    )

    mock_db_session.execute.side_effect = [
        create_mock_execute_result(agent_obj),  # get agent
    ]

    run_result = await agent_engine.run_agent(run_payload)
    assert run_result is not None
    assert run_result.status == "Completed"
    assert "Inventory Optimizer Agent" in run_result.output_text


@pytest.mark.asyncio
async def test_ai_analytics_dashboard_summary(mock_db_session):
    mock_db_session.execute.side_effect = None
    mock_db_session.execute.return_value = create_mock_execute_result(None, [])
    service = AIAnalyticsService(mock_db_session)
    org_id = uuid.uuid4()

    summary = await service.get_dashboard_summary(org_id)
    assert summary.total_documents >= 0
    assert summary.total_embeddings >= 0
    assert summary.active_chat_sessions >= 0
