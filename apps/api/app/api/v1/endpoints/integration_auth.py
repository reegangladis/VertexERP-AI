import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, UTC
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.integration_repository import IntegrationRepository
from app.models.integration import APIKey, IntegrationAudit
from app.schemas.integration import APIKeyCreate, APIKeyOut

router = APIRouter()


@router.post("/api-keys", response_model=APIKeyOut, status_code=status.HTTP_201_CREATED)
async def create_api_key(payload: APIKeyCreate, db: AsyncSession = Depends(get_db)):
    """Generates a new secure API Key with prefix, hashed storage, and rate-limits."""
    repo = IntegrationRepository(db)

    prefix = "vx_live_"
    random_secret = secrets.token_urlsafe(32)
    raw_key = f"{prefix}{random_secret}"
    hashed_key = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    expires_at = None
    if payload.expires_in_days:
        expires_at = datetime.now(UTC) + timedelta(days=payload.expires_in_days)

    api_key = APIKey(
        name=payload.name,
        key_prefix=prefix,
        hashed_key=hashed_key,
        scopes=payload.scopes,
        rate_limit_rps=payload.rate_limit_rps,
        rate_limit_rpm=payload.rate_limit_rpm,
        status="active",
        expires_at=expires_at,
        created_by="system_admin",
    )
    saved = await repo.create_api_key(api_key)

    await repo.log_audit(
        IntegrationAudit(
            action="api_key_created",
            resource_type="api_key",
            resource_id=str(saved.id),
            performed_by="admin",
            details={"name": saved.name, "prefix": prefix, "scopes": payload.scopes},
        )
    )

    result = APIKeyOut.model_validate(saved)
    result.raw_key = raw_key
    return result


@router.get("/api-keys", response_model=List[APIKeyOut])
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    """List API keys."""
    repo = IntegrationRepository(db)
    return await repo.list_api_keys()


@router.post("/oauth/token")
async def issue_oauth_token(
    grant_type: str = Query("client_credentials"),
    client_id: str = Query(...),
    client_secret: str = Query(...),
):
    """Simulates OAuth 2.0 token endpoint for machine-to-machine client credentials grant."""
    if not client_id or not client_secret:
        raise HTTPException(status_code=400, detail="Invalid client credentials")

    token = f"vx_oauth_{secrets.token_urlsafe(24)}"
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "scope": "read write connectors:execute",
    }
