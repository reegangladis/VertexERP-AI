"""CRM API Router registering Leads, Deals, Customers, Quotations, and Orders."""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import PermissionCode
from app.infrastructure.database.session import get_db
from app.modules.crm.services.crm_service import CRMService
from app.modules.identity.api.dependencies import (
    get_current_organization_id,
    get_current_tenant_id,
    require_permission,
)

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.post(
    "/leads",
    response_model=dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_WRITE.value))],
)
async def create_lead(
    payload: dict[str, Any],
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    org_id: uuid.UUID = Depends(get_current_organization_id),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Capture a new sales lead."""
    service = CRMService(db)
    lead = await service.create_lead(
        tenant_id=tenant_id,
        organization_id=uuid.UUID(str(payload.get("organization_id", org_id))),
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        email=payload.get("email", ""),
        company_name=payload.get("company_name"),
        phone=payload.get("phone"),
        title=payload.get("title"),
        source=payload.get("source", "WEBSITE"),
    )
    return {
        "id": str(lead.id),
        "first_name": lead.first_name,
        "last_name": lead.last_name,
        "email": lead.email,
        "status": lead.status,
        "company_name": lead.company_name,
    }


@router.get(
    "/leads",
    response_model=list[dict[str, Any]],
    dependencies=[Depends(require_permission(PermissionCode.CRM_LEADS_READ.value))],
)
async def list_leads(
    tenant_id: uuid.UUID = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all leads for the tenant."""
    service = CRMService(db)
    leads = await service.repo.list_leads(tenant_id=tenant_id)
    return [
        {
            "id": str(l.id),
            "first_name": l.first_name,
            "last_name": l.last_name,
            "email": l.email,
            "status": l.status,
            "company_name": l.company_name,
        }
        for l in leads
    ]
