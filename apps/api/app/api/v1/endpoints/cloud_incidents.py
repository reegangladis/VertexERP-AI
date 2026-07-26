import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.cloud_release_repository import CloudReleaseRepository
from app.services.incident_management_service import IncidentManagementService
from app.models.cloud_release import IncidentReport
from app.schemas.cloud_release import IncidentCreate, IncidentOut

router = APIRouter()
inc_service = IncidentManagementService()


@router.post("/log", response_model=IncidentOut, status_code=status.HTTP_201_CREATED)
async def log_incident(
    payload: IncidentCreate,
    db: AsyncSession = Depends(get_db),
):
    """Logs an operational incident and assigns an on-call SRE engineer."""
    repo = CloudReleaseRepository(db)
    res = inc_service.log_incident(
        payload.title,
        payload.severity,
        payload.affected_services,
        payload.root_cause,
    )

    inc = IncidentReport(
        incident_number=res["incident_number"],
        title=res["title"],
        severity=res["severity"],
        status=res["status"],
        affected_services=res["affected_services"],
        mttr_minutes=res["mttr_minutes"],
        root_cause=res["root_cause"],
        runbook_executed=res["runbook_executed"],
        assigned_oncall=res["assigned_oncall"],
    )
    return await repo.create_incident(inc)


@router.get("/list", response_model=List[IncidentOut])
async def list_incidents(
    severity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List operational incidents."""
    repo = CloudReleaseRepository(db)
    return await repo.list_incidents(severity=severity)


@router.get("/mttr")
async def get_mttr_summary():
    """Returns MTTR SLA metrics."""
    return inc_service.get_mttr_summary()
