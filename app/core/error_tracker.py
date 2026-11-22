"""Application Error Tracking, Fingerprinting, and Diagnostic Aggregation Engine."""

import hashlib
import time
import traceback
from collections import deque
from dataclasses import asdict, dataclass
from typing import Any

from app.core.context import get_correlation_id, get_tenant_id
from app.core.metrics import metrics_registry


@dataclass
class ErrorEvent:
    fingerprint: str
    error_type: str
    message: str
    status_code: int
    path: str
    correlation_id: str
    tenant_id: str | None
    timestamp: float
    count: int = 1


class ErrorTracker:
    """In-memory error tracking and fingerprinting engine."""

    def __init__(self, max_history: int = 200) -> None:
        self.max_history = max_history
        self._recent_errors: deque[ErrorEvent] = deque(maxlen=max_history)
        self._fingerprint_counts: dict[str, int] = {}

    def _generate_fingerprint(self, exc: Exception, path: str, status_code: int) -> str:
        """Computes a deterministic hash from the exception type, top stack frame, and endpoint."""
        exc_type = exc.__class__.__name__
        tb = traceback.extract_tb(exc.__traceback__) if exc.__traceback__ else []
        top_frame = f"{tb[-1].filename}:{tb[-1].lineno}:{tb[-1].name}" if tb else "unknown:0"
        raw_key = f"{exc_type}|{status_code}|{path}|{top_frame}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def record_error(
        self,
        exc: Exception,
        path: str,
        status_code: int = 500,
        correlation_id: str | None = None,
        tenant_id: str | None = None,
    ) -> str:
        """Captures an error, updates metric counters, and stores diagnostic fingerprint."""
        corr_id = correlation_id or get_correlation_id() or "unknown"
        t_id = tenant_id or (str(get_tenant_id()) if get_tenant_id() else None)
        fingerprint = self._generate_fingerprint(exc, path, status_code)
        error_type = exc.__class__.__name__

        # Increment metrics
        metrics_registry.app_errors_total.inc(
            labels={
                "error_type": error_type,
                "status_code": str(status_code),
                "endpoint": path,
            }
        )

        # Update frequency
        self._fingerprint_counts[fingerprint] = self._fingerprint_counts.get(fingerprint, 0) + 1
        count = self._fingerprint_counts[fingerprint]

        event = ErrorEvent(
            fingerprint=fingerprint,
            error_type=error_type,
            message=str(exc),
            status_code=status_code,
            path=path,
            correlation_id=corr_id,
            tenant_id=t_id,
            timestamp=time.time(),
            count=count,
        )
        self._recent_errors.append(event)
        return fingerprint

    def get_recent_errors(self, limit: int = 50) -> list[dict[str, Any]]:
        """Returns the most recent error events."""
        events = list(self._recent_errors)[-limit:]
        return [asdict(e) for e in reversed(events)]

    def get_summary(self) -> dict[str, Any]:
        """Provides a statistical summary of tracked application errors."""
        return {
            "total_tracked": len(self._recent_errors),
            "unique_fingerprints": len(self._fingerprint_counts),
            "top_errors": sorted(
                self._fingerprint_counts.items(), key=lambda item: item[1], reverse=True
            )[:10],
        }


# Global Error Tracker Singleton
error_tracker = ErrorTracker()
