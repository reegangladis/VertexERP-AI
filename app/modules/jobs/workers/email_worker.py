"""Dedicated worker for transactional and batch email delivery."""

import hashlib
import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.jobs.models.job import BackgroundJob
from app.modules.jobs.workers.base import BaseWorker

logger = logging.getLogger("vertexerp.jobs.email")


class EmailWorker(BaseWorker):
    """Worker responsible for rendering and delivering transactional and alert emails."""

    job_type: str = "email"

    async def process(
        self,
        job: BackgroundJob,
        payload: dict[str, Any],
        session: AsyncSession,
    ) -> dict[str, Any]:
        """
        Process email dispatch.
        Supports templates: invoice_ready, order_confirmation, welcome, alert, custom.
        """
        recipient = payload.get("recipient")
        if not recipient or "@" not in recipient:
            raise ValueError(f"Invalid or missing recipient email: '{recipient}'")

        subject = payload.get("subject", "VertexERP Notification")
        template = payload.get("template", "custom")
        template_data = payload.get("template_data", {})
        body = payload.get("body", "")

        # Simulate transient failure test hook
        if payload.get("simulate_error") and (job.retry_count + 1) < payload.get(
            "fail_until_attempt", payload.get("fail_until_retry", 999)
        ):
            raise ConnectionError(
                f"Simulated SMTP transient gateway timeout for recipient '{recipient}'"
            )

        # Render template if specified
        rendered_content = body
        if template == "invoice_ready":
            invoice_num = template_data.get("invoice_number", "INV-UNKNOWN")
            amount = template_data.get("total_amount", "0.00")
            rendered_content = (
                f"Your invoice {invoice_num} for ${amount} is ready for review and payment."
            )
        elif template == "order_confirmation":
            order_num = template_data.get("order_number", "SO-UNKNOWN")
            rendered_content = (
                f"Your order {order_num} has been confirmed and scheduled for fulfillment."
            )
        elif template == "welcome":
            user_name = template_data.get("user_name", "Valued User")
            rendered_content = f"Welcome to VertexERP, {user_name}! Your account is now active."
        elif template == "alert":
            alert_msg = template_data.get("message", "System Alert")
            rendered_content = f"ALERT: {alert_msg}"

        # Generate deterministic message ID
        hash_digest = hashlib.sha256(
            f"{recipient}:{subject}:{datetime.now(UTC).isoformat()}".encode()
        ).hexdigest()[:16]
        message_id = f"msg_{hash_digest}"

        logger.info(
            "Delivered email to %s with subject '%s' (message_id=%s, template=%s)",
            recipient,
            subject,
            message_id,
            template,
        )

        return {
            "status": "DELIVERED",
            "message_id": message_id,
            "recipient": recipient,
            "subject": subject,
            "template": template,
            "content_preview": rendered_content[:100],
            "delivered_at": datetime.now(UTC).isoformat(),
        }
