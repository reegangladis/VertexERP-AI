"""Prometheus & Diagnostic Telemetry Endpoints."""

from typing import Any

from fastapi import APIRouter, Response

from app.core.metrics import metrics_registry

router = APIRouter(tags=["Metrics & Observability"])


@router.get(
    "/metrics",
    summary="Prometheus Metrics Scraper Endpoint",
    description="Exposes application, database, worker, and AI telemetry in standard Prometheus text format.",
    response_class=Response,
)
async def get_prometheus_metrics() -> Response:
    """Returns application metrics formatted for Prometheus scraping."""
    content = metrics_registry.generate_prometheus_text()
    return Response(
        content=content,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@router.get(
    "/metrics/json",
    summary="JSON Telemetry Snapshot",
    description="Returns a structured JSON summary snapshot of active metrics.",
)
async def get_json_metrics() -> dict[str, Any]:
    """Returns a lightweight JSON snapshot of key metrics."""
    return metrics_registry.get_snapshot_json()
