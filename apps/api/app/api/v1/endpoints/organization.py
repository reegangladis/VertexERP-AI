import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db_session, get_current_user, PermissionChecker
from app.schemas.organization import (
    OrganizationResponse,
    OrganizationUpdate,
    TenantSettingResponse,
    TenantSettingUpdate,
    SecuritySettingResponse,
    SecuritySettingUpdate,
)
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response
from app.models.user import User

router = APIRouter()

# Service resolvers
async def get_org_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.organization import OrganizationRepository, TenantSettingRepository, SecuritySettingRepository
    from app.services.organization import OrganizationService
    return OrganizationService(OrganizationRepository(db), TenantSettingRepository(db), SecuritySettingRepository(db))

async def get_tenant_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.organization import TenantSettingRepository
    from app.services.organization import TenantSettingService
    return TenantSettingService(TenantSettingRepository(db))

async def get_security_service(db: AsyncSession = Depends(get_db_session)):
    from app.repositories.organization import SecuritySettingRepository
    from app.services.organization import SecuritySettingService
    return SecuritySettingService(SecuritySettingRepository(db))

@router.get("/me", response_model=APIResponse[OrganizationResponse])
async def get_my_org(
    current_user: User = Depends(get_current_user),
    org_service = Depends(get_org_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    org = await org_service.get(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization details retrieved successfully",
        data=OrganizationResponse.model_validate(org)
    )

@router.put("/me", response_model=APIResponse[OrganizationResponse])
async def update_my_org(
    payload: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    org_service = Depends(get_org_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    org = await org_service.update(current_user.organization_id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Organization details updated successfully",
        data=OrganizationResponse.model_validate(org)
    )

@router.get("/me/tenant-settings", response_model=APIResponse[TenantSettingResponse])
async def get_tenant_settings(
    current_user: User = Depends(get_current_user),
    tenant_service = Depends(get_tenant_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings = await tenant_service.get_by_org_id(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Tenant settings retrieved",
        data=TenantSettingResponse.model_validate(settings)
    )

@router.put("/me/tenant-settings", response_model=APIResponse[TenantSettingResponse])
async def update_tenant_settings(
    payload: TenantSettingUpdate,
    current_user: User = Depends(get_current_user),
    tenant_service = Depends(get_tenant_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings_obj = await tenant_service.get_by_org_id(current_user.organization_id)
    updated = await tenant_service.update(settings_obj.id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Tenant settings updated successfully",
        data=TenantSettingResponse.model_validate(updated)
    )

@router.get("/me/security-settings", response_model=APIResponse[SecuritySettingResponse])
async def get_security_settings(
    current_user: User = Depends(get_current_user),
    security_service = Depends(get_security_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings = await security_service.get_by_org_id(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Security settings retrieved",
        data=SecuritySettingResponse.model_validate(settings)
    )

@router.put("/me/security-settings", response_model=APIResponse[SecuritySettingResponse])
async def update_security_settings(
    payload: SecuritySettingUpdate,
    current_user: User = Depends(get_current_user),
    security_service = Depends(get_security_service)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User is not associated with an organization")
        
    settings_obj = await security_service.get_by_org_id(current_user.organization_id)
    updated = await security_service.update(settings_obj.id, payload)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Security settings updated successfully",
        data=SecuritySettingResponse.model_validate(updated)
    )
