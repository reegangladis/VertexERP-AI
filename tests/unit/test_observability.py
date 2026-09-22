"""Unit tests for Production Observability, Metrics, Tracing, PII Sanitization, and Audit Logging."""

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.audit import audit_logger
from app.core.context import set_correlation_id, set_tenant_id, set_user_id
from app.core.error_tracker import error_tracker
from app.core.logging import mask_sensitive_data, sanitize_string_value
from app.core.metrics import metrics_registry
from app.main import app


def test_pii_and_secret_masking():
    """Verify recursive key redaction and pattern scrubbing in log payloads."""
    # 1. Direct dictionary key redaction
    log_data = {
        "user_email": "admin@vertexerp.io",
        "password": "SuperSecretPassword123!",
        "access_token": "token_abc123",
        "nested": {
            "credit_card": "4111-2222-3333-4444",
            "api_key": "pk_test_samplekey1234567890abcdef12",
            "safe_field": "public_data",
        },
    }
    sanitized = mask_sensitive_data(None, "info", log_data)
    assert sanitized["password"] == "[REDACTED]"
    assert sanitized["access_token"] == "[REDACTED]"
    assert sanitized["nested"]["credit_card"] == "[REDACTED]"
    assert sanitized["nested"]["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["safe_field"] == "public_data"

    # 2. String inline pattern redaction
    raw_msg = (
        "User auth failed with token Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIn0.doNotLeakThisSecret and card 4111-2222-3333-4444 "
        "and SSN 123-45-6789 with api key pk_test_samplekey1234567890abcdef12"
    )
    scrubbed = sanitize_string_value(raw_msg)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in scrubbed
    assert "[JWT_REDACTED]" in scrubbed or "Bearer [REDACTED]" in scrubbed
    assert "4111-2222-3333-4444" not in scrubbed
    assert "[CARD_REDACTED]" in scrubbed
    assert "123-45-6789" not in scrubbed
    assert "[SSN_REDACTED]" in scrubbed
    assert "pk_test_samplekey1234567890abcdef12" not in scrubbed
    assert "[APIKEY_REDACTED]" in scrubbed


def test_metrics_registry_counters_and_histograms():
    """Verify metrics incrementing and Prometheus exposition formatting."""
    # Record test metrics
    metrics_registry.http_requests_total.inc(
        labels={"method": "GET", "path": "/test", "status": "200"}
    )
    metrics_registry.http_request_duration_seconds.observe(
        0.045, labels={"method": "GET", "path": "/test"}
    )
    metrics_registry.worker_jobs_processed_total.inc(
        labels={"job_type": "email", "status": "completed"}
    )
    metrics_registry.ai_tokens_consumed_total.inc(
        150, labels={"provider": "openai", "model": "gpt-4o", "type": "prompt"}
    )
    metrics_registry.ai_guardrail_blocks_total.inc(labels={"violation_type": "prompt_injection"})

    # Generate text
    prom_text = metrics_registry.generate_prometheus_text()
    assert "# HELP http_requests_total" in prom_text
    assert "# TYPE http_requests_total counter" in prom_text
    assert 'http_requests_total{method="GET",path="/test",status="200"}' in prom_text
    assert 'worker_jobs_processed_total{job_type="email",status="completed"}' in prom_text
    assert 'ai_tokens_consumed_total{model="gpt-4o",provider="openai",type="prompt"}' in prom_text
    assert 'ai_guardrail_blocks_total{violation_type="prompt_injection"}' in prom_text

    # Snapshot JSON
    snapshot = metrics_registry.get_snapshot_json()
    assert "app_version" in snapshot
    assert "environment" in snapshot


def test_audit_logger_event_capturing():
    """Verify structured audit logging and tenant filtering."""
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    set_correlation_id("test_corr_123")
    set_tenant_id(uuid.UUID(tenant_id))
    set_user_id(uuid.UUID(user_id))

    event = audit_logger.record(
        action="UPDATE",
        resource_type="SalesOrder",
        resource_id="SO-9988",
        status="SUCCESS",
        changes_summary={"discount": {"old": 0, "new": 10}},
    )

    assert event.action == "UPDATE"
    assert event.resource_type == "SalesOrder"
    assert event.resource_id == "SO-9988"
    assert event.tenant_id == tenant_id
    assert event.user_id == user_id
    assert event.correlation_id == "test_corr_123"

    # Retrieve events
    events = audit_logger.get_events(tenant_id=tenant_id)
    assert len(events) >= 1
    assert events[0]["resource_id"] == "SO-9988"


def test_error_tracker_and_fingerprinting():
    """Verify exception tracking, fingerprint calculation, and frequency aggregation."""
    try:
        raise ValueError("Invalid financial period dates provided")
    except ValueError as exc:
        fingerprint = error_tracker.record_error(
            exc=exc,
            path="/api/v1/finance/fiscal-periods",
            status_code=400,
            correlation_id="corr_err_999",
        )

    assert len(fingerprint) == 16
    recent = error_tracker.get_recent_errors(limit=5)
    assert len(recent) >= 1
    assert recent[0]["error_type"] == "ValueError"
    assert recent[0]["status_code"] == 400
    assert recent[0]["correlation_id"] == "corr_err_999"


@pytest.mark.asyncio
async def test_metrics_endpoint_and_correlation_middleware():
    """Verify HTTP requests inject correlation headers and GET /metrics outputs Prometheus data."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Test request without correlation header -> receives generated correlation ID
        res = await client.get("/health/live")
        assert res.status_code == 200
        assert "X-Correlation-ID" in res.headers
        assert "X-Request-ID" in res.headers
        assert res.headers["X-Correlation-ID"].startswith("req_")

        # 2. Test request with provided correlation header -> preserves client ID
        custom_id = "client_trace_88776655"
        res2 = await client.get("/health/live", headers={"X-Correlation-ID": custom_id})
        assert res2.status_code == 200
        assert res2.headers["X-Correlation-ID"] == custom_id
        assert res2.headers["X-Request-ID"] == custom_id

        # 3. Test Prometheus scraper endpoint
        metrics_res = await client.get("/metrics")
        assert metrics_res.status_code == 200
        assert "text/plain" in metrics_res.headers["Content-Type"]
        assert "http_requests_total" in metrics_res.text

        # 4. Test JSON metrics endpoint
        json_metrics_res = await client.get("/metrics/json")
        assert json_metrics_res.status_code == 200
        data = json_metrics_res.json()
        assert "app_version" in data
        assert "http" in data
