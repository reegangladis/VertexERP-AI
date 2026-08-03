import uuid
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import generate_totp_secret, verify_totp_code
from app.models.user import MfaSetting, User
from app.schemas.mfa import MfaSecretResponse


class MfaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_mfa_setting(self, user_id: uuid.UUID) -> MfaSetting:
        stmt = select(MfaSetting).where(MfaSetting.user_id == user_id, MfaSetting.is_deleted == False)
        res = await self.db.execute(stmt)
        setting = res.scalar_one_or_none()
        if not setting:
            secret = generate_totp_secret()
            backup_codes = [uuid.uuid4().hex[:8] for _ in range(8)]
            setting = MfaSetting(
                user_id=user_id,
                totp_secret=secret,
                backup_codes=backup_codes,
                enabled=False,
                is_totp_confirmed=False,
            )
            self.db.add(setting)
            await self.db.commit()
            await self.db.refresh(setting)
        return setting

    async def generate_secret(self, user: User) -> MfaSecretResponse:
        setting = await self.get_or_create_mfa_setting(user.id)
        if not setting.totp_secret:
            setting.totp_secret = generate_totp_secret()
            await self.db.commit()

        qr_url = f"otpauth://totp/VertexERP:{user.email}?secret={setting.totp_secret}&issuer=VertexERP"
        return MfaSecretResponse(
            totp_secret=setting.totp_secret,
            qr_code_url=qr_url,
            backup_codes=setting.backup_codes or [],
        )

    async def verify_otp(self, user: User, code: str) -> bool:
        setting = await self.get_or_create_mfa_setting(user.id)
        if not setting.totp_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA secret not generated yet",
            )

        is_valid = verify_totp_code(setting.totp_secret, code)
        if not is_valid and setting.backup_codes and code in setting.backup_codes:
            setting.backup_codes.remove(code)
            is_valid = True

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP code",
            )

        if not setting.is_totp_confirmed:
            setting.is_totp_confirmed = True
            setting.enabled = True
            user.mfa_enabled = True
            await self.db.commit()
        return True

    async def enable_mfa(self, user: User) -> bool:
        setting = await self.get_or_create_mfa_setting(user.id)
        setting.enabled = True
        user.mfa_enabled = True
        await self.db.commit()
        return True

    async def disable_mfa(self, user: User) -> bool:
        setting = await self.get_or_create_mfa_setting(user.id)
        setting.enabled = False
        user.mfa_enabled = False
        await self.db.commit()
        return True
