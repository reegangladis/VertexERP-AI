import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.integration_repository import IntegrationRepository
from app.services.message_queue import MessageQueueService
from app.models.integration import MessageQueueLog
from app.schemas.integration import QueueMessagePublish, QueueMessageOut

router = APIRouter()
queue_service = MessageQueueService()


@router.post("/enqueue", response_model=Dict[str, Any])
async def enqueue_message(payload: QueueMessagePublish, db: AsyncSession = Depends(get_db)):
    """Enqueues a new message into a queue."""
    repo = IntegrationRepository(db)
    msg = queue_service.enqueue_message(
        queue_name=payload.queue_name,
        payload=payload.payload,
        max_retries=payload.max_retries,
        message_id=payload.message_id,
    )

    log = MessageQueueLog(
        queue_name=payload.queue_name,
        message_id=msg["message_id"],
        payload=payload.payload,
        status="pending",
        max_retries=payload.max_retries,
    )
    await repo.create_queue_log(log)
    return msg


@router.post("/dequeue", response_model=Optional[Dict[str, Any]])
async def dequeue_message(
    queue_name: str = Query(...),
    consumer_id: str = Query("worker_1"),
):
    """Dequeues a pending message for processing."""
    msg = queue_service.dequeue_message(queue_name, consumer_id)
    if not msg:
        return {"status": "empty", "message": "No pending messages in queue"}
    return msg


@router.post("/ack")
async def ack_message(queue_name: str, message_id: str):
    """Acknowledges message completion."""
    success = queue_service.ack_message(queue_name, message_id)
    return {"acknowledged": success, "message_id": message_id}


@router.post("/nack")
async def nack_message(queue_name: str, message_id: str, error_details: str = "Processing error"):
    """Negative acknowledgment with error details (routes to DLQ on max retries)."""
    success = queue_service.nack_message(queue_name, message_id, error_details)
    return {"nacknowledged": success, "message_id": message_id}


@router.get("/stats")
async def get_queue_stats():
    """Returns queue depths and throughput metrics."""
    return queue_service.get_queue_stats()
