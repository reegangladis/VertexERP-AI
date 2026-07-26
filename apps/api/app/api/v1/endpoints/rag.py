import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session, get_current_user
from app.models.user import User
from app.services.rag_service import RAGService
from app.schemas.rag import (
    KnowledgeCollectionCreate,
    KnowledgeCollectionResponse,
    RAGDocumentResponse,
    RetrievalRequest,
    RetrievalResponse,
    RAGChatSessionResponse,
    RAGChatMessageResponse,
    PromptChatRequest,
    ChatPromptResponse,
    FeedbackCreate,
    FeedbackResponse,
)

router = APIRouter()


# ==================== Collections ====================

@router.post("/collections", response_model=KnowledgeCollectionResponse, status_code=status.HTTP_201_CREATED)
async def create_collection(
    payload: KnowledgeCollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.create_collection(current_user.organization_id, current_user.id, payload)


@router.get("/collections", response_model=List[KnowledgeCollectionResponse])
async def list_collections(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.list_collections(current_user.organization_id, category)


@router.get("/collections/{collection_id}", response_model=KnowledgeCollectionResponse)
async def get_collection(
    collection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    collection = await service.get_collection(collection_id, current_user.organization_id)
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection(
    collection_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    success = await service.delete_collection(collection_id, current_user.organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Collection not found")


# ==================== Documents ====================

@router.post("/documents", response_model=RAGDocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    title: str = Form(...),
    collection_id: Optional[uuid.UUID] = Form(None),
    document_type: str = Form("policy"),
    category: str = Form("general"),
    tags: Optional[str] = Form(None), # comma-separated list of tags
    language: str = Form("en"),
    approval_status: str = Form("approved"),
    retention_days: Optional[int] = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    
    # Save the file content
    content = await file.read()
    
    # Parse tag list
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Mock file path/storage structure
    file_path = f"storage/rag/{current_user.organization_id}/{file.filename}"

    from app.schemas.rag import RAGDocumentCreate
    schema = RAGDocumentCreate(
        title=title,
        collection_id=collection_id,
        document_type=document_type,
        category=category,
        tags=tag_list,
        language=language,
        approval_status=approval_status,
        retention_days=retention_days,
        file_name=file.filename,
        file_path=file_path,
        file_size=len(content),
        mime_type=file.content_type or "text/plain",
        format=file.filename.split(".")[-1].lower() if "." in file.filename else "txt"
    )

    service = RAGService(db)
    return await service.upload_document(
        org_id=current_user.organization_id,
        user_id=current_user.id,
        schema=schema,
        file_content=content
    )


@router.get("/documents", response_model=List[RAGDocumentResponse])
async def list_documents(
    collection_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    document_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.list_documents(
        org_id=current_user.organization_id,
        collection_id=collection_id,
        category=category,
        document_type=document_type,
        status=status,
        search_query=search
    )


@router.get("/documents/{document_id}", response_model=RAGDocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    doc = await service.get_document(document_id, current_user.organization_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    success = await service.delete_document(document_id, current_user.organization_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")


# ==================== Retrieval ====================

@router.post("/retrieval/search", response_model=RetrievalResponse)
async def semantic_search(
    payload: RetrievalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.search(
        org_id=current_user.organization_id,
        user_id=current_user.id,
        query=payload.query,
        collection_ids=payload.collection_ids,
        categories=payload.categories,
        document_types=payload.document_types,
        tags=payload.tags,
        top_k=payload.top_k,
        search_type=payload.search_type,
        provider=payload.provider,
        min_score=payload.min_score
    )


# ==================== RAG Chat Sessions ====================

@router.post("/chat/sessions", response_model=RAGChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_chat_session(
    title: Optional[str] = "New Conversation",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.create_chat_session(current_user.organization_id, current_user.id, title)


@router.get("/chat/sessions", response_model=List[RAGChatSessionResponse])
async def list_chat_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.list_chat_sessions(current_user.organization_id, current_user.id)


@router.get("/chat/sessions/{session_id}", response_model=RAGChatSessionResponse)
async def get_chat_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    session = await service.get_chat_session(session_id, current_user.organization_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.get("/chat/sessions/{session_id}/messages", response_model=List[RAGChatMessageResponse])
async def get_chat_messages(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    session = await service.get_chat_session(session_id, current_user.organization_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session.messages


@router.post("/chat/sessions/{session_id}/messages", response_model=ChatPromptResponse)
async def send_chat_message(
    session_id: uuid.UUID,
    payload: PromptChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    user_msg, assistant_msg = await service.send_chat_message(
        org_id=current_user.organization_id,
        user_id=current_user.id,
        session_id=session_id,
        query=payload.query,
        collection_ids=payload.collection_ids,
        provider=payload.provider,
        model_name=payload.model_name,
        temperature=payload.temperature,
        top_k=payload.top_k,
        search_type=payload.search_type
    )
    return ChatPromptResponse(
        session_id=session_id,
        user_message=RAGChatMessageResponse.model_validate(user_msg),
        assistant_message=RAGChatMessageResponse.model_validate(assistant_msg)
    )


@router.post("/chat/sessions/{session_id}/pin", response_model=RAGChatSessionResponse)
async def toggle_pin_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    success = await service.toggle_pin_session(session_id, current_user.organization_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return await service.get_chat_session(session_id, current_user.organization_id, current_user.id)


# ==================== Feedback ====================

@router.post("/chat/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    service = RAGService(db)
    return await service.submit_feedback(current_user.organization_id, current_user.id, payload)
