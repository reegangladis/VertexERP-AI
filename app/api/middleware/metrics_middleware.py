"""HTTP Metrics Collection Middleware for Prometheus and SLO Tracking."""

import re
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import metrics_registry

# Regex to normalize UUIDs and numeric IDs to prevent metric cardinality explosion
_RE_UUID = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
_RE_NUMERIC_ID = re.compile(r"/\d+(?=/|$)")


def normalize_metric_path(path: str) -> str:
    """Normalizes parameterized URL paths to prevent high Prometheus label cardinality."""
    path = _RE_UUID.sub("{id}", path)
    path = _RE_NUMERIC_ID.sub("/{id}", path)
    return path


class MetricsMiddleware(BaseHTTPMiddleware):
    """
    Measures HTTP request execution duration, status codes, and in-flight gauges.
    Automatically updates the global metrics_registry.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Ignore Prometheus scraper scraping itself from skewing latency metrics
        if request.url.path == "/metrics":
            return await call_next(request)

        method = request.method
        normalized_path = normalize_metric_path(request.url.path)
        labels = {"method": method, "path": normalized_path}

        metrics_registry.http_requests_in_progress.inc(labels={"method": method})
        start_time = time.perf_counter()

        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.perf_counter() - start_time
            metrics_registry.http_requests_in_progress.dec(labels={"method": method})

            total_labels = {
                "method": method,
                "path": normalized_path,
                "status": str(status_code),
            }
            metrics_registry.http_requests_total.inc(labels=total_labels)
            metrics_registry.http_request_duration_seconds.observe(duration, labels=labels)
