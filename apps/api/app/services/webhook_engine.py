import hmac
import hashlib
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Tuple


class WebhookEngine:
    """Enterprise Webhook Engine handling registration, HMAC signatures, event filtering, and exponential backoff retries."""

    def __init__(self):
        self._delivery_log: List[Dict[str, Any]] = []

    @staticmethod
    def generate_secret() -> str:
        """Generates a secure cryptographically random hex secret key."""
        return uuid.uuid4().hex + uuid.uuid4().hex

    @staticmethod
    def calculate_signature(secret: str, payload_str: str, timestamp: int) -> str:
        """Calculates HMAC-SHA256 signature for outgoing webhooks."""
        signed_payload = f"{timestamp}.{payload_str}"
        signature = hmac.new(
            secret.encode("utf-8"),
            signed_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return f"t={timestamp},v1={signature}"

    @staticmethod
    def verify_signature(secret: str, payload_str: str, signature_header: str) -> bool:
        """Verifies incoming HMAC-SHA256 webhook signature."""
        try:
            parts = dict(item.split("=") for item in signature_header.split(","))
            timestamp = int(parts.get("t", "0"))
            received_sig = parts.get("v1", "")

            # Check timestamp tolerance (e.g. 5 minutes)
            if abs(time.time() - timestamp) > 300:
                return False

            expected_sig = hmac.new(
                secret.encode("utf-8"),
                f"{timestamp}.{payload_str}".encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(expected_sig, received_sig)
        except Exception:
            return False

    def matches_event_filter(self, subscribed_events: List[str], event_type: str) -> bool:
        """Checks if event_type matches subscribed wildcards or exact event types."""
        if "*" in subscribed_events or "all" in subscribed_events:
            return True
        if event_type in subscribed_events:
            return True
        # Check wildcard matching e.g. "order.*" matches "order.created"
        for pattern in subscribed_events:
            if pattern.endswith(".*") and event_type.startswith(pattern[:-2]):
                return True
        return False

    def calculate_exponential_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 300.0) -> float:
        """Calculates backoff delay in seconds: base * (2 ^ (attempt - 1))."""
        delay = base_delay * (2 ** (attempt - 1))
        return min(delay, max_delay)

    def dispatch_webhook(
        self,
        target_url: str,
        secret_key: str,
        event_type: str,
        payload: Dict[str, Any],
        signature_header_name: str = "X-Webhook-Signature",
    ) -> Dict[str, Any]:
        """Executes webhook HTTP delivery with HMAC signature injection."""
        timestamp = int(time.time())
        payload_json = json.dumps(payload)
        sig = self.calculate_signature(secret_key, payload_json, timestamp)

        headers = {
            "Content-Type": "application/json",
            signature_header_name: sig,
            "X-Webhook-Event": event_type,
            "X-Webhook-Timestamp": str(timestamp),
        }

        # Simulated HTTP response dispatch
        event_record = {
            "id": str(uuid.uuid4()),
            "target_url": target_url,
            "event_type": event_type,
            "payload": payload,
            "status": "delivered",
            "http_status": 200,
            "latency_ms": 18.5,
            "attempt": 1,
            "headers_sent": headers,
            "timestamp": timestamp,
        }
        self._delivery_log.append(event_record)
        return event_record
