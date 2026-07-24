import uuid
from datetime import datetime, timedelta, UTC
from app.services.base import BaseService
from app.models.session import Session, RefreshToken
from app.repositories.session import SessionRepository, RefreshTokenRepository, TrustedDeviceRepository

def parse_user_agent(user_agent: str) -> tuple[str, str]:
    """Extracts Browser name and OS name from User-Agent string."""
    ua = user_agent.lower()
    browser = "Other"
    if "chrome" in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua:
        browser = "Safari"
    elif "edge" in ua:
        browser = "Edge"
        
    os = "Other"
    if "windows" in ua:
        os = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os = "macOS"
    elif "linux" in ua:
        os = "Linux"
    elif "android" in ua:
        os = "Android"
    elif "iphone" in ua or "ipad" in ua:
        os = "iOS"
        
    return browser, os

class SessionService(BaseService[Session, SessionRepository]):
    def __init__(self, repository: SessionRepository, trusted_repo: TrustedDeviceRepository):
        super().__init__(repository)
        self.trusted_repo = trusted_repo

    async def get_active_by_user(self, user_id: uuid.UUID) -> list[Session]:
        return await self.repository.get_active_by_user(user_id)

    async def create_session(
        self,
        user_id: uuid.UUID,
        ip_address: str,
        user_agent: str,
        expire_minutes: int = 30
    ) -> Session:
        browser, os = parse_user_agent(user_agent)
        expires_at = datetime.now(UTC) + timedelta(minutes=expire_minutes)
        
        session_in = {
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "device_info": f"{browser} ({os})",
            "is_active": True,
            "expires_at": expires_at
        }
        return await self.repository.create(session_in)

    async def revoke_session(self, session_id: uuid.UUID) -> None:
        session = await self.repository.get(session_id)
        if session:
            session.is_active = False
            await self.repository.update(session, {"is_active": False})

    async def revoke_all_user_sessions(self, user_id: uuid.UUID) -> None:
        await self.repository.revoke_all_user_sessions(user_id)
