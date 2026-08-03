import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import PermissionChecker, get_db_session
from app.models.user import User
from app.repositories.ai_rag_copilot import (
    AIAgentRepository,
    ChatSessionRepository,
    KnowledgeCollectionRepository,
    PromptTemplateRepository,
    RAGDocumentRepository,
    ToolRegistryRepository,
)
from app.schemas.ai_rag_copilot import (
    AgentRunCreate,
    AgentRunResponse,
    AIAgentCreate,
    AIAgentResponse,
    AIDashboardSummary,
    KnowledgeCollectionCreate,
    KnowledgeCollectionResponse,
    PromptTemplateCreate,
    PromptTemplateResponse,
    RAGChatMessageCreate,
    RAGChatMessageResponse,
    RAGChatSessionCreate,
    RAGChatSessionResponse,
    RAGDocumentCreate,
    RAGDocumentResponse,
    ToolRegistryCreate,
    ToolRegistryResponse,
)
from app.services.ai_rag_copilot import (
    AIAgentEngine,
    AIAnalyticsService,
    CopilotService,
    PromptEngine,
    RAGEngine,
)

router = APIRouter()


# --- Knowledge Collections ---
@router.post("/ai/collections", response_model=KnowledgeCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: KnowledgeCollectionCreate,
    current_user: User = Depends(PermissionChecker("rag.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = RAGEngine(db)
    return await engine.create_collection(payload)


@router.get("/ai/collections", response_model=list[KnowledgeCollectionResponse])
async def list_collections(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("ai.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = KnowledgeCollectionRepository(db)
    return await repo.get_by_org(org_id)


# --- RAG Documents ---
@router.post("/ai/documents", response_model=RAGDocumentResponse, status_code=status.HTTP_201_CREATED)
async def ingest_document(
    payload: RAGDocumentCreate,
    current_user: User = Depends(PermissionChecker("document.upload")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = RAGEngine(db)
    return await engine.ingest_document(payload, current_user.id)


@router.get("/ai/documents", response_model=list[RAGDocumentResponse])
async def list_documents(
    collection_id: uuid.UUID | None = None,
    current_user: User = Depends(PermissionChecker("ai.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = RAGDocumentRepository(db)
    records, _ = await repo.get_multi(filters={"collection_id": collection_id} if collection_id else None)
    return records


# --- Enterprise Copilot Chat ---
@router.post("/ai/copilot/sessions", response_model=RAGChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    payload: RAGChatSessionCreate,
    current_user: User = Depends(PermissionChecker("ai.chat")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CopilotService(db)
    return await service.create_chat_session(payload)


@router.get("/ai/copilot/sessions", response_model=list[RAGChatSessionResponse])
async def list_chat_sessions(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("ai.chat")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ChatSessionRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/ai/copilot/chat", response_model=RAGChatMessageResponse)
async def send_copilot_message(
    payload: RAGChatMessageCreate,
    current_user: User = Depends(PermissionChecker("ai.chat")),
    db: AsyncSession = Depends(get_db_session),
):
    service = CopilotService(db)
    return await service.post_chat_message(payload)


# --- Prompt Templates ---
@router.post("/ai/prompts", response_model=PromptTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_prompt_template(
    payload: PromptTemplateCreate,
    current_user: User = Depends(PermissionChecker("prompt.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = PromptEngine(db)
    return await engine.create_prompt_template(payload)


@router.get("/ai/prompts", response_model=list[PromptTemplateResponse])
async def list_prompt_templates(
    current_user: User = Depends(PermissionChecker("ai.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = PromptTemplateRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- AI Agents & Tools ---
@router.post("/ai/agents", response_model=AIAgentResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_agent(
    payload: AIAgentCreate,
    current_user: User = Depends(PermissionChecker("agent.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = AIAgentEngine(db)
    return await engine.create_agent(payload)


@router.get("/ai/agents", response_model=list[AIAgentResponse])
async def list_ai_agents(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("ai.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = AIAgentRepository(db)
    return await repo.get_by_org(org_id)


@router.post("/ai/agents/run", response_model=AgentRunResponse)
async def run_ai_agent(
    payload: AgentRunCreate,
    current_user: User = Depends(PermissionChecker("agent.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = AIAgentEngine(db)
    return await engine.run_agent(payload)


@router.post("/ai/tools", response_model=ToolRegistryResponse, status_code=status.HTTP_201_CREATED)
async def register_tool(
    payload: ToolRegistryCreate,
    current_user: User = Depends(PermissionChecker("ai.manage")),
    db: AsyncSession = Depends(get_db_session),
):
    engine = AIAgentEngine(db)
    return await engine.register_tool(payload)


@router.get("/ai/tools", response_model=list[ToolRegistryResponse])
async def list_tools(
    current_user: User = Depends(PermissionChecker("ai.read")),
    db: AsyncSession = Depends(get_db_session),
):
    repo = ToolRegistryRepository(db)
    records, _ = await repo.get_multi()
    return records


# --- AI Dashboard ---
@router.get("/ai/dashboard", response_model=AIDashboardSummary)
async def get_ai_dashboard(
    org_id: uuid.UUID = Query(...),
    current_user: User = Depends(PermissionChecker("ai.read")),
    db: AsyncSession = Depends(get_db_session),
):
    service = AIAnalyticsService(db)
    return await service.get_dashboard_summary(org_id)
