import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.cloud_release_repository import CloudReleaseRepository
from app.services.cloud_deployment_service import CloudDeploymentService
from app.models.cloud_release import DeploymentHistory
from app.schemas.cloud_release import DeploymentTriggerRequest, DeploymentOut

router = APIRouter()
deploy_service = CloudDeploymentService()


@router.post("/trigger", response_model=DeploymentOut, status_code=status.HTTP_201_CREATED)
async def trigger_deployment(
    payload: DeploymentTriggerRequest,
    db: AsyncSession = Depends(get_db),
):
    """Triggers a Canary / Blue-Green cloud deployment across target environments."""
    repo = CloudReleaseRepository(db)
    res = deploy_service.trigger_canary_deployment(
        payload.environment_name,
        payload.version,
        payload.canary_traffic_percent,
    )

    dep = DeploymentHistory(
        environment_name=res["environment_name"],
        version=res["version"],
        strategy=res["strategy"],
        status=res["status"],
        canary_traffic_percent=res["canary_traffic_percent"],
        duration_seconds=res["duration_seconds"],
        deployed_by=res["deployed_by"],
    )
    return await repo.create_deployment(dep)


@router.get("/list", response_model=List[DeploymentOut])
async def list_deployments(
    environment: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """List historical cloud deployment runs."""
    repo = CloudReleaseRepository(db)
    return await repo.list_deployments(env_name=environment)


@router.get("/strategies")
async def get_deployment_strategies():
    """Returns deployment strategy specifications (Canary, Blue-Green, Rolling)."""
    return deploy_service.get_deployment_strategies_spec()
