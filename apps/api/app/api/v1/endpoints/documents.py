import os
import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.models.document import OrganizationDocument
from app.models.user import User
from app.repositories.org_mgmt import DocumentRepository
from app.schemas.org_mgmt import DocumentResponse
from app.schemas.response import APIResponse
from app.services.org_mgmt import DocumentService
from app.utils.response import standard_json_response

router = APIRouter()


async def get_document_service(db: AsyncSession = Depends(get_db_session)):
    return DocumentService(DocumentRepository(db))


@router.get("", response_model=APIResponse[list[DocumentResponse]])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    doc_type: str | None = None,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    stmt = select(OrganizationDocument).where(
        OrganizationDocument.organization_id == current_user.organization_id,
        OrganizationDocument.is_deleted == False,
    )
    if doc_type:
        stmt = stmt.where(OrganizationDocument.type == doc_type)
    if search:
        stmt = stmt.where(OrganizationDocument.name.ilike(f"%{search}%"))

    stmt = stmt.order_by(OrganizationDocument.name.asc()).offset(skip).limit(limit)
    res = await service.repository.db.execute(stmt)
    docs = list(res.scalars().all())

    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Documents retrieved successfully",
        data=[DocumentResponse.model_validate(d) for d in docs],
    )


@router.post("/upload", response_model=APIResponse[DocumentResponse])
async def upload_document(
    name: str = Form(...),
    type: str = Form(...),  # policy, handbook, certificate, business_license
    provider: str = Form("local"),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")

    doc = await service.upload_document(
        org_id=current_user.organization_id,
        name=name,
        doc_type=type,
        file=file,
        provider=provider,
    )

    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Document uploaded successfully",
        data=DocumentResponse.model_validate(doc),
    )


@router.get("/{id}/download")
async def download_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    doc = await service.get(id)
    if not doc or doc.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.storage_provider != "local":
        raise HTTPException(
            status_code=400,
            detail=f"File is stored on remote provider: {doc.storage_provider}. Cloud download stub active.",
        )

    # Local file path validation
    full_path = os.path.join(service.upload_dir, os.path.basename(doc.file_path))
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Physical file not found on disk")

    return FileResponse(
        path=full_path,
        media_type=doc.mime_type or "application/octet-stream",
        filename=doc.name,
    )


@router.delete("/{id}", response_model=APIResponse[DocumentResponse])
async def delete_document(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: DocumentService = Depends(get_document_service),
):
    doc = await service.get(id)
    if not doc or doc.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="Document not found")

    # If local, clean up file
    if doc.storage_provider == "local":
        full_path = os.path.join(service.upload_dir, os.path.basename(doc.file_path))
        if os.path.exists(full_path):
            try:
                os.remove(full_path)
            except Exception:
                pass

    deleted = await service.delete(id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Document deleted successfully",
        data=DocumentResponse.model_validate(deleted),
    )
