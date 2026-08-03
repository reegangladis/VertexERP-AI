from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.schemas.mfa import MfaSecretResponse, MfaVerifyRequest
from app.services.mfa import MfaService

router = APIRouter()


def get_mfa_service(db: AsyncSession = Depends(get_db_session)) -> MfaService:
    return MfaService(db)


@router.post("/generate-secret", response_model=MfaSecretResponse)
async def generate_mfa_secret(
    current_user: User = Depends(get_current_user),
    service: MfaService = Depends(get_mfa_service),
):
    return await service.generate_secret(current_user)


@router.post("/verify")
async def verify_mfa_otp(
    data: MfaVerifyRequest,
    current_user: User = Depends(get_current_user),
    service: MfaService = Depends(get_mfa_service),
):
    await service.verify_otp(current_user, data.code)
    return {"message": "MFA code verified successfully"}


@router.post("/enable")
async def enable_mfa(
    current_user: User = Depends(get_current_user),
    service: MfaService = Depends(get_mfa_service),
):
    await service.enable_mfa(current_user)
    return {"message": "MFA enabled successfully"}


@router.post("/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_user),
    service: MfaService = Depends(get_mfa_service),
):
    await service.disable_mfa(current_user)
    return {"message": "MFA disabled successfully"}
