import uuid
from datetime import UTC, datetime
from typing import Any


class MessageQueueService:
    """Enterprise Message Queue Service supporting Producer/Consumer patterns, Retry Policies, and Message Tracking."""

    def __init__(self):
        # Queues: {queue_name: List[Dict[str, Any]]}
        self._queues: dict[str, list[dict[str, Any]]] = {
            "inventory_sync_queue": [],
            "email_notifications_queue": [],
            "payroll_processing_queue": [],
        }
        self._dlq: list[dict[str, Any]] = []

    def enqueue_message(
        self,
        queue_name: str,
        payload: dict[str, Any],
        max_retries: int = 3,
        message_id: str | None = None,
    ) -> dict[str, Any]:
        """Publishes a new message into the target queue."""
        if queue_name not in self._queues:
            self._queues[queue_name] = []

        msg_id = message_id or f"msg_{uuid.uuid4().hex[:12]}"
        now = datetime.now(UTC)

        msg_record = {
            "id": uuid.uuid4(),
            "queue_name": queue_name,
            "message_id": msg_id,
            "payload": payload,
            "status": "pending",
            "attempt_count": 0,
            "max_retries": max_retries,
            "consumer_id": None,
            "error_details": None,
            "processed_at": None,
            "created_at": now,
        }

        self._queues[queue_name].append(msg_record)
        return msg_record

    def dequeue_message(
        self, queue_name: str, consumer_id: str
    ) -> dict[str, Any] | None:
        """Consumes a pending message from the queue."""
        queue = self._queues.get(queue_name, [])
        for msg in queue:
            if msg["status"] == "pending":
                msg["status"] = "processing"
                msg["consumer_id"] = consumer_id
                msg["attempt_count"] += 1
                return msg
        return None

    def ack_message(self, queue_name: str, message_id: str) -> bool:
        """Acknowledges successful message processing."""
        queue = self._queues.get(queue_name, [])
        for msg in queue:
            if msg["message_id"] == message_id:
                msg["status"] = "completed"
                msg["processed_at"] = datetime.now(UTC)
                return True
        return False

    def nack_message(
        self, queue_name: str, message_id: str, error_details: str
    ) -> bool:
        """Negative acknowledgment. Triggers retry or routes to DLQ if max retries exceeded."""
        queue = self._queues.get(queue_name, [])
        for msg in queue:
            if msg["message_id"] == message_id:
                msg["error_details"] = error_details
                if msg["attempt_count"] >= msg["max_retries"]:
                    msg["status"] = "dlq"
                    self._dlq.append(msg)
                else:
                    msg["status"] = "pending"
                return True
        return False

    def get_queue_stats(self) -> list[dict[str, Any]]:
        """Returns statistics on queue depths and message statuses."""
        stats = []
        for q_name, msgs in self._queues.items():
            pending = sum(1 for m in msgs if m["status"] == "pending")
            processing = sum(1 for m in msgs if m["status"] == "processing")
            completed = sum(1 for m in msgs if m["status"] == "completed")
            failed = sum(1 for m in msgs if m["status"] in ("failed", "dlq"))
            stats.append(
                {
                    "queue_name": q_name,
                    "depth": pending + processing,
                    "pending": pending,
                    "processing": processing,
                    "completed": completed,
                    "failed": failed,
                }
            )
        return stats
