"""MFA API endpoints for TOTP setup, verification, and recovery code management."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.infrastructure.database.session import get_db
from app.modules.audit.services.audit_service import AuditService
from app.modules.identity.api.dependencies import get_current_user
from app.modules.identity.models.mfa_setting import MfaSetting
from app.modules.identity.models.user import User
from app.modules.identity.repositories.user_repository import UserRepository
from app.modules.identity.schemas.auth import MfaSetupResponse, MfaVerifyRequest
from app.modules.identity.services.mfa_service import MfaService

router = APIRouter(prefix="/mfa", tags=["Multi-Factor Authentication"])


@router.post(
    "/setup",
    response_model=MfaSetupResponse,
    status_code=status.HTTP_200_OK,
    summary="Initialize TOTP MFA Enrollment",
)
async def setup_mfa(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MfaSetupResponse:
    """Generates a new RFC 6238 TOTP secret, encrypted database entry, and 8 recovery codes."""
    secret, encrypted_secret, otpauth_url, plain_recovery_codes, hashed_recovery_codes = (
        MfaService.setup_mfa(current_user.email)
    )

    user_repo = UserRepository(db)
    mfa_setting = await user_repo.get_mfa_setting(current_user.id)

    if not mfa_setting:
        mfa_setting = MfaSetting(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            secret_encrypted=encrypted_secret,
            recovery_codes_hashed=hashed_recovery_codes,
            is_enabled=False,
        )
        await user_repo.save_mfa_setting(mfa_setting)
    else:
        mfa_setting.secret_encrypted = encrypted_secret
        mfa_setting.recovery_codes_hashed = hashed_recovery_codes
        mfa_setting.is_enabled = False
        await db.flush()

    return MfaSetupResponse(
        secret=secret,
        otpauth_url=otpauth_url,
        recovery_codes=plain_recovery_codes,
    )


@router.post(
    "/verify",
    status_code=status.HTTP_200_OK,
    summary="Verify and Activate TOTP MFA",
)
async def verify_and_activate_mfa(
    req: MfaVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Validates the first TOTP code and marks MFA as activated on the account."""
    user_repo = UserRepository(db)
    mfa_setting = await user_repo.get_mfa_setting(current_user.id)

    if not mfa_setting:
        raise NotFoundException("MFA enrollment has not been initialized")

    is_valid = MfaService.verify_code(mfa_setting.secret_encrypted, req.code)
    if not is_valid:
        raise ValidationException("Invalid TOTP verification code")

    mfa_setting.is_enabled = True
    current_user.mfa_enabled = True
    await db.flush()

    await AuditService.log_security_event(
        session=db,
        event_type="MFA_ENABLED",
        description=f"MFA activated for user {current_user.email}",
        severity="INFO",
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )

    return {"message": "MFA has been successfully activated"}


@router.post(
    "/disable",
    status_code=status.HTTP_200_OK,
    summary="Disable TOTP MFA",
)
async def disable_mfa(
    req: MfaVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Disables MFA on the account after verifying the current TOTP code."""
    user_repo = UserRepository(db)
    mfa_setting = await user_repo.get_mfa_setting(current_user.id)

    if not mfa_setting or not mfa_setting.is_enabled:
        raise ValidationException("MFA is not enabled on this account")

    is_valid = MfaService.verify_code(mfa_setting.secret_encrypted, req.code)
    if not is_valid:
        raise ValidationException("Invalid TOTP verification code")

    mfa_setting.is_enabled = False
    current_user.mfa_enabled = False
    await db.flush()

    await AuditService.log_security_event(
        session=db,
        event_type="MFA_DISABLED",
        description=f"MFA disabled for user {current_user.email}",
        severity="WARNING",
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )

    return {"message": "MFA has been disabled"}
