import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.models.observability import Alert, ApplicationLog, SystemMetric, Trace
from app.schemas.observability import (
    AlertUpdate,
    SystemMetricCreate,
    TraceSpanCreate,
)
from app.services.observability_service import ObservabilityService


@pytest.mark.asyncio
async def test_record_metric():
    db_mock = AsyncMock()
    service = ObservabilityService(db_mock)
    org_id = uuid.uuid4()

    mock_metric = SystemMetric(
        id=uuid.uuid4(),
        organization_id=org_id,
        metric_name="cpu_usage",
        metric_type="gauge",
        value=72.5,
        labels={"host": "host-1"},
    )
    service.repo.create_metric = AsyncMock(return_value=mock_metric)
    service.repo.get_alerts = AsyncMock(return_value=[])

    metric_in = SystemMetricCreate(
        metric_name="cpu_usage",
        metric_type="gauge",
        value=72.5,
        labels={"host": "host-1"},
    )
    res = await service.record_metric(org_id, metric_in)

    assert res.metric_name == "cpu_usage"
    assert res.value == 72.5
    assert service.repo.create_metric.called


@pytest.mark.asyncio
async def test_metric_threshold_breach_alert():
    db_mock = AsyncMock()
    service = ObservabilityService(db_mock)
    org_id = uuid.uuid4()

    mock_metric = SystemMetric(
        id=uuid.uuid4(),
        organization_id=org_id,
        metric_name="cpu_usage",
        metric_type="gauge",
        value=92.0,  # Breaches 85% limit
        labels={"host": "host-1"},
    )
    service.repo.create_metric = AsyncMock(return_value=mock_metric)
    service.repo.get_alerts = AsyncMock(return_value=[])
    service.create_alert = AsyncMock()

    metric_in = SystemMetricCreate(
        metric_name="cpu_usage",
        metric_type="gauge",
        value=92.0,
        labels={"host": "host-1"},
    )
    await service.record_metric(org_id, metric_in)

    assert service.create_alert.called


@pytest.mark.asyncio
async def test_search_logs():
    db_mock = AsyncMock()
    service = ObservabilityService(db_mock)
    org_id = uuid.uuid4()

    mock_logs = [
        ApplicationLog(
            id=uuid.uuid4(),
            organization_id=org_id,
            service_name="rest-api",
            log_level="ERROR",
            message="Internal database conflict error",
            timestamp=datetime.now(UTC),
        )
    ]
    service.repo.get_logs = AsyncMock(return_value=(mock_logs, 1))

    logs, count = await service.search_logs(
        org_id, keyword="conflict", page=1, page_size=10
    )

    assert count == 1
    assert logs[0].log_level == "ERROR"
    assert "conflict" in logs[0].message
    assert service.repo.get_logs.called


@pytest.mark.asyncio
async def test_record_trace_span():
    db_mock = AsyncMock()
    service = ObservabilityService(db_mock)
    org_id = uuid.uuid4()

    mock_span = Trace(
        id=uuid.uuid4(),
        organization_id=org_id,
        trace_id="tr-111",
        span_id="sp-1",
        parent_span_id=None,
        name="SQL Select",
        service_name="finance-service",
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC),
        duration_ms=45.5,
        status="success",
    )
    service.repo.create_trace_span = AsyncMock(return_value=mock_span)

    span_in = TraceSpanCreate(
        trace_id="tr-111",
        span_id="sp-1",
        name="SQL Select",
        service_name="finance-service",
        start_time=datetime.now(UTC),
        end_time=datetime.now(UTC),
        duration_ms=45.5,
        status="success",
    )
    res = await service.record_trace_span(org_id, span_in)

    assert res.trace_id == "tr-111"
    assert res.duration_ms == 45.5
    assert service.repo.create_trace_span.called


@pytest.mark.asyncio
async def test_acknowledge_alert_status():
    db_mock = AsyncMock()
    service = ObservabilityService(db_mock)
    org_id = uuid.uuid4()
    alert_id = uuid.uuid4()

    mock_alert = Alert(
        id=alert_id,
        organization_id=org_id,
        rule_name="High Latency",
        metric_name="api_latency",
        threshold=2000.0,
        comparison_operator=">",
        status="active",
        severity="warning",
    )
    service.repo.get_alert_by_id = AsyncMock(return_value=mock_alert)
    service.repo.update_alert = AsyncMock(side_effect=lambda a: a)
    service.repo.create_alert_history = AsyncMock()

    update_payload = AlertUpdate(status="acknowledged")
    res = await service.update_alert(
        org_id, alert_id, update_payload, "sre.engineer@vertex.ai"
    )

    assert res.status == "acknowledged"
    assert res.acknowledged_by == "sre.engineer@vertex.ai"
    assert service.repo.create_alert_history.called
