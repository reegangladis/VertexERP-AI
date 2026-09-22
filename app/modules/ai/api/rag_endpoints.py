"""API Endpoints for RAG Knowledge Base and Document Ingestion."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.ai.rag.rag_service import rag_service
from app.modules.ai.schemas.rag import (
    RAGDocumentChunkRead,
    RAGDocumentCreate,
    RAGDocumentDetailRead,
    RAGDocumentRead,
    RAGDocumentVersionCreate,
    RAGDocumentVersionRead,
    RAGIngestionJobRead,
    RAGJobRetryRequest,
    RAGQueryRequest,
    RAGQueryResponse,
    RAGSearchRequest,
    RAGSearchResponse,
)
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    get_current_user_claims,
    get_current_user_id,
    require_permission,
)

router = APIRouter(prefix="/rag", tags=["AI Knowledge & RAG"])


# ------------------------------------------------------------------------------
# Document Management Endpoints
# ------------------------------------------------------------------------------
@router.post(
    "/documents",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_WRITE.value))],
)
async def create_document(
    payload: RAGDocumentCreate,
    eager: bool = Query(False, description="Run ingestion synchronously for tests"),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Upload and create a new knowledge document and trigger async ingestion."""
    doc, job = await rag_service.create_document(
        session=db,
        tenant_id=tenant_id,
        organization_id=organization_id,
        user_id=user_id,
        payload=payload,
        eager=eager,
    )
    return {
        "message": "Document created and queued for ingestion.",
        "document_id": str(doc.id),
        "job_id": str(job.id),
        "job_status": job.status,
    }


@router.get(
    "/documents",
    response_model=dict[str, Any],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_READ.value))],
)
async def list_documents(
    access_level: str | None = None,
    tag: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """List knowledge base documents for tenant with filtering and pagination."""
    docs, total = await rag_service.list_documents(
        session=db,
        tenant_id=tenant_id,
        access_level=access_level,
        tag=tag,
        search=search,
        skip=skip,
        limit=limit,
    )

    items = []
    for d in docs:
        latest_job = d.jobs[0].status if d.jobs else "NONE"
        items.append(
            RAGDocumentRead(
                id=d.id,
                tenant_id=d.tenant_id,
                organization_id=d.organization_id,
                title=d.title,
                description=d.description,
                file_type=d.file_type,
                file_size_bytes=d.file_size_bytes,
                access_level=d.access_level,
                allowed_departments=d.allowed_departments or ["*"],
                allowed_roles=d.allowed_roles or ["*"],
                tags=d.tags or [],
                metadata_json=d.metadata_json or {},
                is_active=d.is_active,
                active_version=d.versions[0].version_number if d.versions else 1,
                total_chunks=len(d.chunks),
                latest_job_status=latest_job,
                created_at=d.created_at,
                updated_at=d.updated_at,
            )
        )

    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.get(
    "/documents/{document_id}",
    response_model=RAGDocumentDetailRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_READ.value))],
)
async def get_document_details(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Get detailed document information including version history and recent chunks."""
    doc = await rag_service.get_document(db, tenant_id=tenant_id, document_id=document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found in this tenant.",
        )

    versions = [
        RAGDocumentVersionRead(
            id=v.id,
            document_id=v.document_id,
            version_number=v.version_number,
            changelog=v.changelog,
            checksum=v.checksum,
            is_active=v.is_active,
            created_at=v.created_at,
        )
        for v in doc.versions
    ]

    chunks = [
        RAGDocumentChunkRead(
            id=c.id,
            document_id=c.document_id,
            version_id=c.version_id,
            chunk_index=c.chunk_index,
            content=c.content,
            token_count=c.token_count,
            char_count=c.char_count,
            section_heading=c.section_heading,
            metadata_json=c.metadata_json or {},
            created_at=c.created_at,
        )
        for c in doc.chunks[:20]
    ]

    latest_job = doc.jobs[0].status if doc.jobs else "NONE"

    return RAGDocumentDetailRead(
        id=doc.id,
        tenant_id=doc.tenant_id,
        organization_id=doc.organization_id,
        title=doc.title,
        description=doc.description,
        file_type=doc.file_type,
        file_size_bytes=doc.file_size_bytes,
        access_level=doc.access_level,
        allowed_departments=doc.allowed_departments or ["*"],
        allowed_roles=doc.allowed_roles or ["*"],
        tags=doc.tags or [],
        metadata_json=doc.metadata_json or {},
        is_active=doc.is_active,
        active_version=doc.versions[0].version_number if doc.versions else 1,
        total_chunks=len(doc.chunks),
        latest_job_status=latest_job,
        created_at=doc.created_at,
        updated_at=doc.updated_at,
        versions=versions,
        recent_chunks=chunks,
    )


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_DELETE.value))],
)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Deactivate or remove a document from the knowledge base."""
    deleted = await rag_service.delete_document(db, tenant_id=tenant_id, document_id=document_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {document_id} not found.",
        )
    return {"message": "Document successfully deleted."}


# ------------------------------------------------------------------------------
# Versioning Endpoints
# ------------------------------------------------------------------------------
@router.post(
    "/documents/{document_id}/versions",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_WRITE.value))],
)
async def create_document_version(
    document_id: uuid.UUID,
    payload: RAGDocumentVersionCreate,
    eager: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
):
    """Create a new version for an existing document and queue ingestion."""
    version, job = await rag_service.create_document_version(
        session=db,
        tenant_id=tenant_id,
        document_id=document_id,
        organization_id=organization_id,
        user_id=user_id,
        payload=payload,
        eager=eager,
    )
    return {
        "message": f"Version {version.version_number} created and queued for ingestion.",
        "version_id": str(version.id),
        "version_number": version.version_number,
        "job_id": str(job.id),
        "job_status": job.status,
    }


# ------------------------------------------------------------------------------
# Ingestion Job Endpoints
# ------------------------------------------------------------------------------
@router.get(
    "/jobs/{job_id}",
    response_model=RAGIngestionJobRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_READ.value))],
)
async def get_ingestion_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Check asynchronous ingestion job state, retry counts, and dead-letter status."""
    job = await rag_service.get_ingestion_job(db, tenant_id=tenant_id, job_id=job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )
    return RAGIngestionJobRead(
        id=job.id,
        tenant_id=job.tenant_id,
        organization_id=job.organization_id,
        document_id=job.document_id,
        version_id=job.version_id,
        status=job.status,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        error_message=job.error_message,
        dead_letter=job.dead_letter,
        dead_letter_reason=job.dead_letter_reason,
        metrics_json=job.metrics_json or {},
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
    )


@router.post(
    "/jobs/{job_id}/retry",
    response_model=RAGIngestionJobRead,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_DOCUMENTS_WRITE.value))],
)
async def retry_ingestion_job(
    job_id: uuid.UUID,
    payload: RAGJobRetryRequest | None = None,
    eager: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
):
    """Retry a failed or dead-lettered ingestion job."""
    force_reset = payload.force_reset if payload else True
    job = await rag_service.retry_ingestion_job(
        session=db,
        tenant_id=tenant_id,
        job_id=job_id,
        force_reset=force_reset,
        eager=eager,
    )
    return RAGIngestionJobRead(
        id=job.id,
        tenant_id=job.tenant_id,
        organization_id=job.organization_id,
        document_id=job.document_id,
        version_id=job.version_id,
        status=job.status,
        retry_count=job.retry_count,
        max_retries=job.max_retries,
        error_message=job.error_message,
        dead_letter=job.dead_letter,
        dead_letter_reason=job.dead_letter_reason,
        metrics_json=job.metrics_json or {},
        created_at=job.created_at,
        updated_at=job.updated_at,
        completed_at=job.completed_at,
    )


# ------------------------------------------------------------------------------
# Search & Grounded Generation Endpoints
# ------------------------------------------------------------------------------
@router.post(
    "/search",
    response_model=RAGSearchResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_QUERY.value))],
)
async def search_knowledge(
    payload: RAGSearchRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    claims: dict[str, Any] = Depends(get_current_user_claims),
):
    """Perform vector and hybrid search against tenant knowledge base with RBAC authorization."""
    user_roles: set[str] = set(claims.get("roles", []))
    user_dept = claims.get("department")

    return await rag_service.search_knowledge(
        session=db,
        tenant_id=tenant_id,
        payload=payload,
        user_roles=user_roles,
        user_department=user_dept,
    )


@router.post(
    "/query",
    response_model=RAGQueryResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_permission(PermissionCode.AI_RAG_QUERY.value))],
)
async def query_knowledge(
    payload: RAGQueryRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    organization_id: uuid.UUID = Depends(get_current_organization_id),
    user_id: uuid.UUID = Depends(get_current_user_id),
    claims: dict[str, Any] = Depends(get_current_user_claims),
):
    """Perform end-to-end grounded RAG answering with verifiable structured in-line citations."""
    user_roles: set[str] = set(claims.get("roles", []))
    user_dept = claims.get("department")

    return await rag_service.query_knowledge(
        session=db,
        tenant_id=tenant_id,
        organization_id=organization_id,
        user_id=user_id,
        payload=payload,
        user_roles=user_roles,
        user_department=user_dept,
    )
