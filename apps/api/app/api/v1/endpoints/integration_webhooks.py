import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.integration_repository import IntegrationRepository
from app.services.webhook_engine import WebhookEngine
from app.models.integration import Webhook, WebhookEvent, IntegrationAudit
from app.schemas.integration import (
    WebhookCreate,
    WebhookUpdate,
    WebhookOut,
    WebhookEventOut,
    WebhookDispatchTest,
)

router = APIRouter()
webhook_engine = WebhookEngine()


@router.get("/webhooks", response_model=List[WebhookOut])
async def list_webhooks(db: AsyncSession = Depends(get_db)):
    """List registered webhooks."""
    repo = IntegrationRepository(db)
    return await repo.list_webhooks()


@router.post("/webhooks", response_model=WebhookOut, status_code=status.HTTP_201_CREATED)
async def create_webhook(payload: WebhookCreate, db: AsyncSession = Depends(get_db)):
    """Register a new webhook endpoint with HMAC secret key generation."""
    repo = IntegrationRepository(db)
    secret_key = payload.secret_key or webhook_engine.generate_secret()

    webhook = Webhook(
        name=payload.name,
        target_url=payload.target_url,
        secret_key=secret_key,
        signature_header=payload.signature_header,
        events=payload.events,
        is_active=payload.is_active,
        retry_limit=payload.retry_limit,
        timeout_seconds=payload.timeout_seconds,
        headers=payload.headers,
        description=payload.description,
    )
    saved = await repo.create_webhook(webhook)

    await repo.log_audit(
        IntegrationAudit(
            action="webhook_registered",
            resource_type="webhook",
            resource_id=str(saved.id),
            performed_by="admin",
            details={"name": saved.name, "target_url": saved.target_url},
        )
    )
    return saved


@router.get("/webhooks/{webhook_id}/events", response_model=List[WebhookEventOut])
async def list_webhook_events(webhook_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """List historical delivery events for a webhook."""
    repo = IntegrationRepository(db)
    return await repo.list_webhook_events(webhook_id)


@router.post("/webhooks/{webhook_id}/dispatch-test", response_model=Dict[str, Any])
async def test_dispatch_webhook(
    webhook_id: uuid.UUID,
    payload: WebhookDispatchTest,
    db: AsyncSession = Depends(get_db),
):
    """Executes a test webhook delivery dispatch with HMAC signing."""
    repo = IntegrationRepository(db)
    webhook = await repo.get_webhook_by_id(webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")

    dispatch_res = webhook_engine.dispatch_webhook(
        target_url=webhook.target_url,
        secret_key=webhook.secret_key,
        event_type=payload.event_type,
        payload=payload.payload,
        signature_header_name=webhook.signature_header,
    )

    # Save event log
    evt = WebhookEvent(
        webhook_id=webhook.id,
        event_type=payload.event_type,
        payload=payload.payload,
        status=dispatch_res["status"],
        http_status=dispatch_res["http_status"],
        attempt_count=1,
        latency_ms=dispatch_res["latency_ms"],
    )
    await repo.create_webhook_event(evt)
    return dispatch_res


@router.post("/verify-signature")
async def verify_signature(
    secret: str,
    payload_str: str,
    signature_header: str,
):
    """Verifies HMAC SHA256 webhook signature."""
    valid = webhook_engine.verify_signature(secret, payload_str, signature_header)
    return {"valid": valid}
