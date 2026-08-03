import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.repositories.organization import (
    OrganizationMetadataRepository,
    OrganizationRepository,
    OrganizationSettingRepository,
    SecuritySettingRepository,
    TenantSettingRepository,
)
from app.schemas.org_metadata import (
    OrganizationMetadataResponse,
    OrganizationMetadataUpdate,
)
from app.schemas.org_setting import (
    OrganizationSettingResponse,
    OrganizationSettingUpdate,
)
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.schemas.security_setting import (
    SecuritySettingResponse,
    SecuritySettingUpdate,
)
from app.schemas.tenant_setting import TenantSettingResponse, TenantSettingUpdate
from app.services.organization import (
    OrganizationMetadataService,
    OrganizationService,
    OrganizationSettingService,
    SecuritySettingService,
    TenantSettingService,
)

router = APIRouter()


# Service dependencies
def get_org_service(db: AsyncSession = Depends(get_db_session)) -> OrganizationService:
    return OrganizationService(OrganizationRepository(db))


def get_tenant_service(db: AsyncSession = Depends(get_db_session)) -> TenantSettingService:
    return TenantSettingService(TenantSettingRepository(db))


def get_org_setting_service(db: AsyncSession = Depends(get_db_session)) -> OrganizationSettingService:
    return OrganizationSettingService(OrganizationSettingRepository(db))


def get_org_metadata_service(db: AsyncSession = Depends(get_db_session)) -> OrganizationMetadataService:
    return OrganizationMetadataService(OrganizationMetadataRepository(db))


def get_security_service(db: AsyncSession = Depends(get_db_session)) -> SecuritySettingService:
    return SecuritySettingService(SecuritySettingRepository(db))


# --- Organizations Endpoints ---

@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
async def create_organization(
    data: OrganizationCreate,
    service: OrganizationService = Depends(get_org_service),
):
    return await service.create_organization(data)


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    skip: int = 0,
    limit: int = 100,
    service: OrganizationService = Depends(get_org_service),
):
    items, _ = await service.get_multi(skip=skip, limit=limit)
    return items


@router.get("/{id}", response_model=OrganizationResponse)
async def get_organization(
    id: uuid.UUID,
    service: OrganizationService = Depends(get_org_service),
):
    org = await service.get(id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


@router.patch("/{id}", response_model=OrganizationResponse)
async def update_organization(
    id: uuid.UUID,
    data: OrganizationUpdate,
    service: OrganizationService = Depends(get_org_service),
):
    org = await service.update(id, data)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


@router.delete("/{id}", response_model=OrganizationResponse)
async def delete_organization(
    id: uuid.UUID,
    service: OrganizationService = Depends(get_org_service),
):
    org = await service.delete(id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found"
        )
    return org


# --- Tenant Settings ---

@router.get("/tenant-settings/{organization_id}", response_model=TenantSettingResponse)
async def get_tenant_settings(
    organization_id: uuid.UUID,
    service: TenantSettingService = Depends(get_tenant_service),
):
    return await service.get_by_org_id(organization_id)


@router.put("/tenant-settings/{organization_id}", response_model=TenantSettingResponse)
async def update_tenant_settings(
    organization_id: uuid.UUID,
    data: TenantSettingUpdate,
    service: TenantSettingService = Depends(get_tenant_service),
):
    return await service.update_by_org_id(organization_id, data)


# --- Organization Settings ---

@router.get("/organization-settings/{organization_id}", response_model=OrganizationSettingResponse)
async def get_organization_settings(
    organization_id: uuid.UUID,
    service: OrganizationSettingService = Depends(get_org_setting_service),
):
    return await service.get_by_org_id(organization_id)


@router.put("/organization-settings/{organization_id}", response_model=OrganizationSettingResponse)
async def update_organization_settings(
    organization_id: uuid.UUID,
    data: OrganizationSettingUpdate,
    service: OrganizationSettingService = Depends(get_org_setting_service),
):
    return await service.update_by_org_id(organization_id, data)


# --- Organization Metadata ---

@router.get("/organization-metadata/{organization_id}", response_model=OrganizationMetadataResponse)
async def get_organization_metadata(
    organization_id: uuid.UUID,
    service: OrganizationMetadataService = Depends(get_org_metadata_service),
):
    return await service.get_by_org_id(organization_id)


@router.put("/organization-metadata/{organization_id}", response_model=OrganizationMetadataResponse)
async def update_organization_metadata(
    organization_id: uuid.UUID,
    data: OrganizationMetadataUpdate,
    service: OrganizationMetadataService = Depends(get_org_metadata_service),
):
    return await service.update_by_org_id(organization_id, data)


# --- Security Settings ---

@router.get("/security-settings/{organization_id}", response_model=SecuritySettingResponse)
async def get_security_settings(
    organization_id: uuid.UUID,
    service: SecuritySettingService = Depends(get_security_service),
):
    return await service.get_by_org_id(organization_id)


@router.put("/security-settings/{organization_id}", response_model=SecuritySettingResponse)
async def update_security_settings(
    organization_id: uuid.UUID,
    data: SecuritySettingUpdate,
    service: SecuritySettingService = Depends(get_security_service),
):
    return await service.update_by_org_id(organization_id, data)
