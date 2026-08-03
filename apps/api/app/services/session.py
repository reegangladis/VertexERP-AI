import uuid

from app.models.session import Session
from app.repositories.session import RefreshTokenRepository, SessionRepository
from app.services.base import BaseService


class SessionService(BaseService[Session, SessionRepository]):
    def __init__(
        self,
        repository: SessionRepository,
        token_repo: RefreshTokenRepository,
    ):
        super().__init__(repository)
        self.token_repo = token_repo

    async def get_active_sessions(self, user_id: uuid.UUID) -> list[Session]:
        return await self.repository.get_active_sessions(user_id)

    async def revoke_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return await self.repository.revoke_session(session_id, user_id)

    async def revoke_all_sessions(self, user_id: uuid.UUID, except_session_id: uuid.UUID | None = None) -> int:
        return await self.repository.revoke_all_sessions(user_id, except_session_id)
