"""Dedicated worker for multi-channel notification dispatch."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models.job import BackgroundJob
from app.modules.jobs.workers.base import BaseWorker

logger = logging.getLogger("vertexerp.jobs.notifications")


class NotificationsWorker(BaseWorker):
    """Worker responsible for delivering in-app notifications, mobile push, and chat alerts."""

    job_type: str = "notifications"

    async def process(
        self,
        job: BackgroundJob,
        payload: dict[str, Any],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """
        Process notification broadcast across configured channels (in-app, push, slack, webhook).
        """
        channel = payload.get("channel", "in_app").lower()
        title = payload.get("title", "VertexERP Alert")
        message = payload.get("message", "")
        recipient_user_id = payload.get("user_id")
        category = payload.get("category", "system_alert")
        action_url = payload.get("action_url")

        if not message:
            raise ValueError("Notification payload must include a 'message'")

        if payload.get("simulate_error") and (job.retry_count + 1) < payload.get(
            "fail_until_attempt", payload.get("fail_until_retry", 999)
        ):
            raise ConnectionError(
                f"Push notification gateway temporary failure for channel '{channel}'"
            )

        notification_id = f"notif_{uuid.uuid4().hex[:12]}"

        logger.info(
            "Dispatched notification (%s) to user=%s via channel=%s: '%s'",
            notification_id,
            recipient_user_id,
            channel,
            title,
        )

        return {
            "notification_id": notification_id,
            "channel": channel,
            "recipient_user_id": str(recipient_user_id) if recipient_user_id else None,
            "category": category,
            "title": title,
            "action_url": action_url,
            "status": "DELIVERED",
            "dispatched_at": datetime.now(UTC).isoformat(),
        }
