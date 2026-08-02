from fastapi import APIRouter

from app.schemas.cloud_release import FailoverTriggerRequest
from app.services.cloud_deployment_service import CloudDeploymentService

router = APIRouter()
deploy_service = CloudDeploymentService()


@router.get("/list")
async def list_cloud_regions():
    """List multi-region cloud infrastructure status across AWS, Azure, GCP, and Hybrid clouds."""
    return deploy_service.list_regions()


@router.post("/failover")
async def trigger_regional_failover(payload: FailoverTriggerRequest):
    """Triggers automated multi-region Geo-DNS failover from primary to secondary region."""
    return deploy_service.trigger_regional_failover(
        payload.primary_region,
        payload.secondary_region,
        payload.reason,
    )
