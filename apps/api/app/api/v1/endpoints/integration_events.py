import uuid
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_db
from app.repositories.integration_repository import IntegrationRepository
from app.services.event_bus import EventBus
from app.models.integration import EventTopic, EventLog
from app.schemas.integration import (
    EventTopicCreate,
    EventTopicOut,
    EventPublishRequest,
    EventLogOut,
    EventReplayRequest,
)

router = APIRouter()
event_bus_service = EventBus()


@router.get("/topics", response_model=List[EventTopicOut])
async def list_event_topics(db: AsyncSession = Depends(get_db)):
    """List event topics."""
    repo = IntegrationRepository(db)
    return await repo.list_event_topics()


@router.post("/topics", response_model=EventTopicOut, status_code=status.HTTP_201_CREATED)
async def create_event_topic(payload: EventTopicCreate, db: AsyncSession = Depends(get_db)):
    """Create a new Event Bus topic."""
    repo = IntegrationRepository(db)
    topic = EventTopic(
        name=payload.name,
        description=payload.description,
        schema_json=payload.schema_json,
        retention_hours=payload.retention_hours,
        consumer_groups=payload.consumer_groups,
    )
    return await repo.create_event_topic(topic)


@router.post("/publish", response_model=Dict[str, Any])
async def publish_event(payload: EventPublishRequest, db: AsyncSession = Depends(get_db)):
    """Publishes an event to the Event Bus."""
    repo = IntegrationRepository(db)
    pub_res = event_bus_service.publish_event(
        topic_name=payload.topic_name,
        payload=payload.payload,
        headers=payload.headers,
        partition_key=payload.partition_key,
    )

    topic = await repo.get_topic_by_name(payload.topic_name)
    if topic:
        evt_log = EventLog(
            topic_id=topic.id,
            topic_name=payload.topic_name,
            event_id=pub_res["event_id"],
            payload=payload.payload,
            headers=payload.headers,
            status="published",
            partition_key=payload.partition_key,
        )
        await repo.create_event_log(evt_log)

    return pub_res


@router.get("/logs", response_model=List[EventLogOut])
async def list_event_logs(
    topic_name: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    """List event publication logs."""
    repo = IntegrationRepository(db)
    return await repo.list_event_logs(topic_name=topic_name, status=status_filter)


@router.post("/replay", response_model=List[Dict[str, Any]])
async def replay_events(payload: EventReplayRequest):
    """Replays historical events for a topic."""
    return event_bus_service.replay_events(topic_name=payload.topic_name, limit=payload.limit)


@router.get("/dlq", response_model=List[Dict[str, Any]])
async def get_dlq_events(topic_name: Optional[str] = Query(None)):
    """Retrieves messages in the Event Bus Dead Letter Queue (DLQ)."""
    return event_bus_service.get_dlq_messages(topic_name)
