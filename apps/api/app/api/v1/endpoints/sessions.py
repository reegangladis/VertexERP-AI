import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_db_session
from app.models.user import User
from app.repositories.session import RefreshTokenRepository, SessionRepository
from app.schemas.session import SessionResponse
from app.services.session import SessionService

router = APIRouter()


def get_session_service(db: AsyncSession = Depends(get_db_session)) -> SessionService:
    return SessionService(SessionRepository(db), RefreshTokenRepository(db))


@router.get("", response_model=list[SessionResponse])
async def list_active_sessions(
    current_user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    return await service.get_active_sessions(current_user.id)


@router.delete("/{id}")
async def revoke_session(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    revoked = await service.revoke_session(id, current_user.id)
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
        )
    return {"message": "Session revoked successfully"}


@router.delete("")
async def revoke_all_sessions(
    current_user: User = Depends(get_current_user),
    service: SessionService = Depends(get_session_service),
):
    count = await service.revoke_all_sessions(current_user.id)
    return {"message": f"Revoked {count} sessions successfully"}
