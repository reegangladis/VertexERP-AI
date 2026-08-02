from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.crm_mgmt import CampaignRepository
from app.schemas.crm_mgmt import CampaignCreate, CampaignResponse
from app.schemas.response import APIResponse
from app.utils.response import standard_json_response

router = APIRouter()


@router.get("", response_model=APIResponse[list[CampaignResponse]])
async def list_campaigns(
    current_user: User = Depends(get_current_user), db=Depends(get_db_session)
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = CampaignRepository(db)
    campaigns = await repo.get_by_org(current_user.organization_id)
    return standard_json_response(
        status_code=status.HTTP_200_OK,
        success=True,
        message="Campaigns retrieved successfully",
        data=campaigns,
    )


@router.post("", response_model=APIResponse[CampaignResponse])
async def create_campaign(
    payload: CampaignCreate,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db_session),
):
    if not current_user.organization_id:
        raise HTTPException(status_code=400, detail="User not bound to organization")
    repo = CampaignRepository(db)
    campaign = await repo.create(
        {"organization_id": current_user.organization_id, **payload.dict()}
    )
    return standard_json_response(
        status_code=status.HTTP_201_CREATED,
        success=True,
        message="Campaign launched successfully",
        data=campaign,
    )
