import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any


class EventBus:
    """Enterprise Event Bus Engine with Topic Management, DLQ, and Event Replay capabilities."""

    def __init__(self):
        # Active topics: {topic_name: schema_or_meta}
        self._topics: dict[str, dict[str, Any]] = {
            "erp.order.created": {
                "retention_hours": 168,
                "consumers": ["finance_service", "warehouse_service"],
            },
            "crm.lead.updated": {
                "retention_hours": 168,
                "consumers": ["marketing_automation"],
            },
            "system.audit.log": {
                "retention_hours": 720,
                "consumers": ["observability_service"],
            },
        }
        # In-memory log of published events: List[Dict[str, Any]]
        self._event_store: list[dict[str, Any]] = []
        # Dead Letter Queue: List[Dict[str, Any]]
        self._dlq: list[dict[str, Any]] = []
        # In-memory event subscribers: {topic_name: List[Callable]}
        self._subscribers: dict[str, list[Callable]] = {}

    def create_topic(
        self,
        topic_name: str,
        retention_hours: int = 168,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Creates or updates a topic definition."""
        topic_info = {
            "name": topic_name,
            "retention_hours": retention_hours,
            "description": description or "",
            "created_at": datetime.now(UTC).isoformat(),
        }
        self._topics[topic_name] = topic_info
        return topic_info

    def list_topics(self) -> list[dict[str, Any]]:
        """Returns list of registered topics."""
        return [{"name": name, **meta} for name, meta in self._topics.items()]

    def subscribe(self, topic_name: str, handler: Callable):
        """Subscribes a callback handler to a specific topic."""
        if topic_name not in self._subscribers:
            self._subscribers[topic_name] = []
        self._subscribers[topic_name].append(handler)

    def publish_event(
        self,
        topic_name: str,
        payload: dict[str, Any],
        headers: dict[str, Any] | None = None,
        partition_key: str | None = None,
    ) -> dict[str, Any]:
        """Publishes an event to a topic, notifying subscribers and logging to event store."""
        event_id = f"evt_{uuid.uuid4().hex[:12]}"
        now = datetime.now(UTC)

        event_record = {
            "event_id": event_id,
            "topic_name": topic_name,
            "payload": payload,
            "headers": headers or {},
            "partition_key": partition_key,
            "status": "published",
            "is_replayed": False,
            "published_at": now.isoformat(),
        }

        self._event_store.append(event_record)

        # Notify subscribers
        subscribers = self._subscribers.get(topic_name, [])
        for sub in subscribers:
            try:
                sub(event_record)
            except Exception as ex:
                # Route to DLQ on handler failure
                self.route_to_dlq(event_record, reason=str(ex))

        return event_record

    def route_to_dlq(self, event_record: dict[str, Any], reason: str) -> None:
        """Routes failed message to Dead Letter Queue."""
        dlq_entry = {
            **event_record,
            "dlq_status": "dead_lettered",
            "failure_reason": reason,
            "dlq_routed_at": datetime.now(UTC).isoformat(),
        }
        self._dlq.append(dlq_entry)

    def get_dlq_messages(self, topic_name: str | None = None) -> list[dict[str, Any]]:
        """Retrieves messages in DLQ."""
        if topic_name:
            return [msg for msg in self._dlq if msg.get("topic_name") == topic_name]
        return self._dlq

    def replay_events(
        self,
        topic_name: str,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Replays historical events from the event store for a given topic."""
        matching_events = [
            e for e in self._event_store if e["topic_name"] == topic_name
        ]
        replayed_records = []

        for evt in matching_events[:limit]:
            replay_record = {
                **evt,
                "event_id": f"rpl_{uuid.uuid4().hex[:10]}",
                "is_replayed": True,
                "original_event_id": evt["event_id"],
                "replayed_at": datetime.now(UTC).isoformat(),
            }
            replayed_records.append(replay_record)

        return replayed_records
