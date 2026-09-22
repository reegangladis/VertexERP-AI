"""Comprehensive Test Suite for Background Processing & Asynchronous Workers in VertexERP AI V2.

Covers:
1. Job Idempotency deduplication.
2. Job Retries & Jittered Exponential Backoff.
3. Dead-Letter Queue (DLQ) transitions upon max retry exhaustion.
4. Execution Timeout enforcement via asyncio.wait_for.
5. Distributed Tracing Correlation ID & ContextVars propagation.
6. Non-blocking HTTP endpoints (HTTP 202 Accepted).
7. Dedicated Worker: Email (Templates, Deliveries, Attachments).
8. Dedicated Worker: Document Ingestion (RAG integration).
9. Dedicated Worker: Embeddings (Batch vector generation).
10. Dedicated Worker: Reports (GL Balance Sheet, Inventory Valuation, CSV/JSON artifacts).
11. Dedicated Worker: Notifications (Multi-channel in-app, push, slack).
12. Dedicated Worker: Scheduled Jobs (Inventory scans, balance checks).
13. Dedicated Worker: Integrations (HMAC-SHA256 signatures, partner sync).
14. Strict Cross-Tenant Isolation (Tenant A vs Tenant B).
15. Recurring Cron Scheduler evaluation & job spawning.
"""

import asyncio
import hashlib
import hmac
import json
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import get_correlation_id
from app.core.permissions import PermissionCode
from app.modules.ai.models.rag_document import RAGDocument, RAGDocumentChunk, RAGDocumentVersion
from app.modules.identity.services.jwt_service import JwtService
from app.modules.jobs.engine.executor import JobExecutor
from app.modules.jobs.engine.scheduler import CronScheduler
from app.modules.jobs.models.job import (
    BackgroundJob,
    JobExecutionLog,
    JobSchedule,
    JobStatus,
    JobType,
)
from app.modules.jobs.schemas.job import (
    JobCreateRequest,
)
from app.modules.jobs.services.job_service import job_service
from app.modules.jobs.workers.integrations_worker import IntegrationsWorker
from app.modules.jobs.workers.registry import worker_registry
from app.modules.organization.models.organization import Organization
from app.modules.organization.models.tenant import Tenant


@pytest.fixture
async def job_test_env(db_session: AsyncSession):
    """Setup multi-tenant test fixtures for Tenant A and Tenant B."""
    tenant_a = Tenant(
        id=uuid.uuid4(),
        name="Vertex Global Industries",
        slug=f"vertex-{uuid.uuid4().hex[:6]}",
    )
    db_session.add(tenant_a)
    await db_session.flush()

    org_a = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        name="Vertex HQ North America",
        legal_name="Vertex Global Inc",
        tax_identifier="US-123456789",
        base_currency="USD",
    )
    db_session.add(org_a)
    await db_session.flush()

    tenant_b = Tenant(
        id=uuid.uuid4(),
        name="Quantum Manufacturing Corp",
        slug=f"quantum-{uuid.uuid4().hex[:6]}",
    )
    db_session.add(tenant_b)
    await db_session.flush()

    org_b = Organization(
        id=uuid.uuid4(),
        tenant_id=tenant_b.id,
        name="Quantum EMEA Logistics",
        legal_name="Quantum EMEA Ltd",
        tax_identifier="GB-987654321",
        base_currency="EUR",
    )
    db_session.add(org_b)
    await db_session.flush()

    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()

    return {
        "tenant_a": tenant_a,
        "org_a": org_a,
        "user_a_id": user_a_id,
        "tenant_b": tenant_b,
        "org_b": org_b,
        "user_b_id": user_b_id,
    }


def _create_token(
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    org_id: uuid.UUID,
    permissions: list[str],
) -> str:
    """Generate signed JWT token for API tests."""
    token, _, _ = JwtService.create_access_token(
        user_id=user_id,
        tenant_id=tenant_id,
        organization_id=org_id,
        roles=["TenantAdmin"],
        permissions=permissions,
        session_id=uuid.uuid4(),
    )
    return token


# ==============================================================================
# 1. Idempotency Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_job_idempotency_deduplication(job_test_env, db_session: AsyncSession):
    """Enqueuing duplicate requests with the same idempotency key returns the existing job."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    idempotency_key = f"idemp-invoice-send-{uuid.uuid4().hex[:8]}"

    req = JobCreateRequest(
        job_type=JobType.EMAIL.value,
        job_name="Send Invoice #1001",
        payload={"recipient": "billing@client.com", "template": "invoice_ready"},
        idempotency_key=idempotency_key,
    )

    # First dispatch
    job1 = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=False,
    )

    # Second dispatch with identical idempotency_key
    job2 = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=False,
    )

    assert job1.id == job2.id
    assert job1.idempotency_key == idempotency_key


# ==============================================================================
# 2. Retries & Exponential Backoff Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_job_retries_and_exponential_backoff(job_test_env, db_session: AsyncSession):
    """Simulated transient failure increments retry_count and sets future scheduled_at with backoff."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    req = JobCreateRequest(
        job_type=JobType.EMAIL.value,
        job_name="Transient Failure Email Test",
        payload={"recipient": "user@domain.com", "simulate_error": True, "fail_until_retry": 2},
        max_retries=3,
        backoff_base_seconds=2.0,
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=False,
    )

    # Execute attempt 1 (fails due to simulate_error)
    job_after_1 = await JobExecutor.execute_job(db_session, job.id)
    assert job_after_1.retry_count == 1
    assert job_after_1.status == JobStatus.QUEUED.value
    assert job_after_1.scheduled_at is not None
    assert job_after_1.scheduled_at > datetime.now(UTC)

    # Verify execution log was recorded
    logs_stmt = select(JobExecutionLog).where(JobExecutionLog.job_id == job.id)
    logs_res = await db_session.execute(logs_stmt)
    logs = list(logs_res.scalars().all())
    assert len(logs) == 1
    assert logs[0].attempt_number == 1
    assert logs[0].status == "FAILED"
    assert "Simulated SMTP" in logs[0].error_message

    # Execute attempt 2 (now succeeds because fail_until_retry == 2)
    job_after_2 = await JobExecutor.execute_job(db_session, job.id)
    assert job_after_2.status == JobStatus.COMPLETED.value
    assert job_after_2.result_json["status"] == "DELIVERED"

    # Verify second execution log
    logs_res_2 = await db_session.execute(logs_stmt)
    logs_2 = list(logs_res_2.scalars().all())
    assert len(logs_2) == 2
    assert logs_2[1].attempt_number == 2
    assert logs_2[1].status == "COMPLETED"


# ==============================================================================
# 3. Dead-Letter Queue (DLQ) Exhaustion Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_job_dead_letter_queue_exhaustion(job_test_env, db_session: AsyncSession):
    """Job exceeding max_retries transitions to DEAD_LETTER status."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    req = JobCreateRequest(
        job_type=JobType.EMAIL.value,
        job_name="Permanent Failure Job",
        payload={"recipient": "fail@domain.com", "simulate_error": True, "fail_until_retry": 999},
        max_retries=2,
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=False,
    )

    # Attempt 1
    await JobExecutor.execute_job(db_session, job.id)
    assert job.retry_count == 1
    assert not job.is_dead_letter

    # Attempt 2 (Exhausts max_retries=2)
    await JobExecutor.execute_job(db_session, job.id)
    assert job.retry_count == 2
    assert job.status == JobStatus.DEAD_LETTER.value
    assert job.is_dead_letter is True
    assert "Exhausted maximum retry limit of 2" in job.dead_letter_reason


# ==============================================================================
# 4. Timeout Enforcement Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_job_timeout_enforcement(job_test_env, db_session: AsyncSession):
    """Long-running job exceeding timeout_seconds is cancelled and handled gracefully."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    # We test timeout with timeout_seconds=1 on a slow operation
    job = BackgroundJob(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        job_type=JobType.INTEGRATIONS.value,
        job_name="Timeout Test Job",
        payload_json={"target": "slow_service"},
        timeout_seconds=1,
        max_retries=1,
        created_by=user_a_id,
    )
    db_session.add(job)
    await db_session.flush()

    # Mock worker process to sleep for 3 seconds
    class SlowWorker(IntegrationsWorker):
        async def process(self, job: BackgroundJob, payload: dict[str, Any], session: AsyncSession):
            await asyncio.sleep(3.0)
            return {"status": "SUCCESS"}

    worker_registry.register(SlowWorker())

    try:
        updated_job = await JobExecutor.execute_job(db_session, job.id)
        assert updated_job.status == JobStatus.DEAD_LETTER.value
        assert updated_job.is_dead_letter is True
        assert "timed out after 1 seconds" in updated_job.error_message
    finally:
        # Restore standard IntegrationsWorker
        worker_registry.register(IntegrationsWorker())


# ==============================================================================
# 5. Correlation ID & Distributed Tracing
# ==============================================================================
@pytest.mark.asyncio
async def test_job_correlation_id_propagation(job_test_env, db_session: AsyncSession):
    """Correlation ID propagates into execution contextvars and execution logs."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    custom_corr_id = "corr-distributed-trace-9999"

    req = JobCreateRequest(
        job_type=JobType.EMAIL.value,
        job_name="Tracing Test Email",
        payload={"recipient": "admin@tenant.com", "template": "welcome"},
        correlation_id=custom_corr_id,
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=True,
    )

    assert job.status == JobStatus.COMPLETED.value
    assert job.correlation_id == custom_corr_id
    assert get_correlation_id() == custom_corr_id


# ==============================================================================
# 6. Non-Blocking HTTP 202 REST Endpoint Tests
# ==============================================================================
@pytest.mark.asyncio
async def test_non_blocking_http_endpoint(
    job_test_env,
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    """POST /api/v1/jobs returns HTTP 202 Accepted immediately without blocking."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    all_perms = [
        PermissionCode.JOBS_READ.value,
        PermissionCode.JOBS_WRITE.value,
        PermissionCode.JOBS_CANCEL.value,
        PermissionCode.JOBS_RETRY.value,
        PermissionCode.JOBS_SCHEDULES_MANAGE.value,
    ]
    token = _create_token(user_a_id, tenant_a.id, org_a.id, all_perms)

    payload = {
        "job_type": "reports",
        "job_name": "Fiscal Year End Balance Sheet",
        "priority": 1,
        "payload": {"report_type": "balance_sheet", "format": "json"},
        "idempotency_key": f"idemp-rep-{uuid.uuid4().hex[:8]}",
        "timeout_seconds": 120,
    }

    resp = await async_client.post(
        "/api/v1/jobs",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 202
    data = resp.json()
    assert data["job_name"] == "Fiscal Year End Balance Sheet"
    assert data["status"] == "PENDING"
    assert data["priority"] == 1
    job_id = data["id"]

    # Check that job is queryable via GET /api/v1/jobs/{job_id}
    detail_resp = await async_client.get(
        f"/api/v1/jobs/{job_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["id"] == job_id
    assert detail_data["payload_json"]["report_type"] == "balance_sheet"


# ==============================================================================
# 7. Dedicated Worker: Email Templates & Deliveries
# ==============================================================================
@pytest.mark.asyncio
async def test_email_worker_templates(job_test_env, db_session: AsyncSession):
    """EmailWorker renders invoice_ready, order_confirmation, welcome, and alert templates."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    templates_to_test = [
        ("invoice_ready", {"invoice_number": "INV-2026-001", "total_amount": "14500.00"}),
        ("order_confirmation", {"order_number": "SO-8899"}),
        ("welcome", {"user_name": "Alice Cooper"}),
        ("alert", {"message": "Critical server storage threshold exceeded"}),
    ]

    for tmpl, data in templates_to_test:
        req = JobCreateRequest(
            job_type=JobType.EMAIL.value,
            job_name=f"Email Test: {tmpl}",
            payload={"recipient": "client@enterprise.com", "template": tmpl, "template_data": data},
        )
        job = await job_service.create_and_enqueue_job(
            session=db_session,
            tenant_id=tenant_a.id,
            organization_id=org_a.id,
            user_id=user_a_id,
            payload=req,
            eager=True,
        )

        assert job.status == JobStatus.COMPLETED.value
        assert job.result_json["template"] == tmpl
        assert job.result_json["status"] == "DELIVERED"
        assert "message_id" in job.result_json


# ==============================================================================
# 8. Dedicated Worker: Document Ingestion (RAG Integration)
# ==============================================================================
@pytest.mark.asyncio
async def test_document_ingestion_worker(job_test_env, db_session: AsyncSession):
    """DocumentIngestionWorker processes raw content into parsed, cleaned, embedded chunks."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    # 1. Create document and version
    doc = RAGDocument(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        title="VertexERP Background Architecture Guide",
        file_type="markdown",
        created_by=user_a_id,
    )
    db_session.add(doc)
    await db_session.flush()

    raw_markdown = """# Architecture Overview
VertexERP AI uses asynchronous workers to prevent blocking HTTP endpoints.

## Worker Responsibilities
Email, Document Ingestion, Embeddings, Reports, Notifications, Scheduled Jobs, and Integrations.
"""
    checksum = hashlib.sha256(raw_markdown.encode()).hexdigest()
    version = RAGDocumentVersion(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        document_id=doc.id,
        version_number=1,
        raw_content=raw_markdown,
        checksum=checksum,
        created_by=user_a_id,
    )
    db_session.add(version)
    await db_session.flush()

    # 2. Trigger Document Ingestion Worker
    req = JobCreateRequest(
        job_type=JobType.DOCUMENT_INGESTION.value,
        job_name="Ingest RAG Doc",
        payload={"document_id": str(doc.id), "version_id": str(version.id), "chunk_size": 200},
    )
    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=True,
    )

    assert job.status == JobStatus.COMPLETED.value
    assert job.result_json["chunks_indexed"] > 0

    # Verify chunks exist in DB
    chunks_stmt = select(RAGDocumentChunk).where(RAGDocumentChunk.version_id == version.id)
    chunks_res = await db_session.execute(chunks_stmt)
    chunks = list(chunks_res.scalars().all())
    assert len(chunks) == job.result_json["chunks_indexed"]


# ==============================================================================
# 9. Dedicated Worker: Embeddings (Batch Vector Generation)
# ==============================================================================
@pytest.mark.asyncio
async def test_embeddings_worker(job_test_env, db_session: AsyncSession):
    """EmbeddingsWorker generates batch vector embeddings for product catalog items."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    catalog_texts = [
        "Industrial CNC Milling Machine 5-Axis with coolant delivery",
        "Hydraulic Press Brake 150 Ton with safety laser guard",
        "High-Speed Rotary Screw Air Compressor 50 HP",
    ]

    req = JobCreateRequest(
        job_type=JobType.EMBEDDINGS.value,
        job_name="Generate Product Catalog Embeddings",
        payload={"entity_type": "products", "texts": catalog_texts},
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=True,
    )

    assert job.status == JobStatus.COMPLETED.value
    assert job.result_json["total_embeddings"] == 3
    assert job.result_json["vector_dimension"] == 1536
    assert len(job.result_json["sample_vector_preview"]) == 5


# ==============================================================================
# 10. Dedicated Worker: Reports (GL Balance Sheet & Inventory Valuation)
# ==============================================================================
@pytest.mark.asyncio
async def test_reports_worker(job_test_env, db_session: AsyncSession):
    """ReportsWorker generates structured JSON and CSV report artifacts."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    # 1. JSON Balance sheet
    req_json = JobCreateRequest(
        job_type=JobType.REPORTS.value,
        job_name="Generate GL Balance Sheet JSON",
        payload={"report_type": "balance_sheet", "format": "json"},
    )
    job_json = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req_json,
        eager=True,
    )
    assert job_json.status == JobStatus.COMPLETED.value
    assert job_json.result_json["report_type"] == "balance_sheet"
    assert job_json.result_json["summary"]["total_assets"] == 955000.00

    # 2. CSV Inventory valuation
    req_csv = JobCreateRequest(
        job_type=JobType.REPORTS.value,
        job_name="Generate Inventory Valuation CSV",
        payload={"report_type": "inventory_valuation", "format": "csv"},
    )
    job_csv = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req_csv,
        eager=True,
    )
    assert job_csv.status == JobStatus.COMPLETED.value
    assert job_csv.result_json["format"] == "csv"
    assert job_csv.result_json["file_size_bytes"] > 0


# ==============================================================================
# 11. Dedicated Worker: Notifications (Multi-Channel Dispatch)
# ==============================================================================
@pytest.mark.asyncio
async def test_notifications_worker(job_test_env, db_session: AsyncSession):
    """NotificationsWorker delivers multi-channel in-app and push alerts."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    req = JobCreateRequest(
        job_type=JobType.NOTIFICATIONS.value,
        job_name="Dispatch PO Approval Alert",
        payload={
            "channel": "in_app",
            "title": "Purchase Order Approval Required",
            "message": "PO #9924 exceeds $50,000 threshold and requires CFO approval.",
            "user_id": str(user_a_id),
            "category": "approval_request",
            "action_url": "/procurement/orders/PO-9924",
        },
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=True,
    )

    assert job.status == JobStatus.COMPLETED.value
    assert job.result_json["channel"] == "in_app"
    assert job.result_json["status"] == "DELIVERED"
    assert job.result_json["notification_id"].startswith("notif_")


# ==============================================================================
# 12. Dedicated Worker: Scheduled Jobs Maintenance
# ==============================================================================
@pytest.mark.asyncio
async def test_scheduled_jobs_worker(job_test_env, db_session: AsyncSession):
    """ScheduledJobsWorker runs automated maintenance operations."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    req = JobCreateRequest(
        job_type=JobType.SCHEDULED_JOBS.value,
        job_name="Run Periodic Inventory Reorder Scan",
        payload={"task_name": "inventory_reorder_level_scan"},
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=True,
    )

    assert job.status == JobStatus.COMPLETED.value
    assert job.result_json["task_name"] == "inventory_reorder_level_scan"
    assert job.result_json["statistics"]["reorder_alerts_generated"] == 3


# ==============================================================================
# 13. Dedicated Worker: Integrations & Webhook HMAC Signing
# ==============================================================================
@pytest.mark.asyncio
async def test_integrations_worker_hmac(job_test_env, db_session: AsyncSession):
    """IntegrationsWorker computes HMAC-SHA256 signature for outbound partner webhooks."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    secret = "shopify_partner_signing_secret_key"
    data = {"order_id": "SO-1002", "total": 1250.00, "currency": "USD"}

    req = JobCreateRequest(
        job_type=JobType.INTEGRATIONS.value,
        job_name="Dispatch Shopify Order Sync",
        payload={
            "target": "shopify",
            "endpoint_url": "https://partner.shopify.com/api/v1/orders/sync",
            "event_type": "order.created",
            "data": data,
            "signing_secret": secret,
        },
    )

    job = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=True,
    )

    assert job.status == JobStatus.COMPLETED.value
    assert job.result_json["target"] == "shopify"
    assert job.result_json["http_status"] == 200

    # Verify signature independently
    expected_sig = hmac.new(
        secret.encode("utf-8"),
        json.dumps(data, sort_keys=True).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    assert job.result_json["signature_sha256"] == f"sha256={expected_sig}"


# ==============================================================================
# 14. Strict Cross-Tenant Isolation
# ==============================================================================
@pytest.mark.asyncio
async def test_cross_tenant_isolation_jobs(
    job_test_env,
    async_client: AsyncClient,
    db_session: AsyncSession,
):
    """Tenant B cannot view, query, or retry Tenant A's background jobs."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    tenant_b = job_test_env["tenant_b"]
    org_b = job_test_env["org_b"]
    user_b_id = job_test_env["user_b_id"]

    all_perms = [
        PermissionCode.JOBS_READ.value,
        PermissionCode.JOBS_WRITE.value,
        PermissionCode.JOBS_RETRY.value,
    ]
    _create_token(user_a_id, tenant_a.id, org_a.id, all_perms)
    token_b = _create_token(user_b_id, tenant_b.id, org_b.id, all_perms)

    # 1. Create Job in Tenant A
    req = JobCreateRequest(
        job_type=JobType.REPORTS.value,
        job_name="Confidential Tenant A Financial Audit",
        payload={"confidential": True},
    )
    job_a = await job_service.create_and_enqueue_job(
        session=db_session,
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        user_id=user_a_id,
        payload=req,
        eager=False,
    )

    # 2. Tenant B attempts to fetch Tenant A's job -> 404 NOT FOUND
    resp_b = await async_client.get(
        f"/api/v1/jobs/{job_a.id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp_b.status_code == 404

    # 3. Tenant B attempts to retry Tenant A's job -> 404 NOT FOUND
    retry_b = await async_client.post(
        f"/api/v1/jobs/{job_a.id}/retry",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert retry_b.status_code == 404

    # 4. Tenant B lists jobs -> should not contain Tenant A's job
    list_b = await async_client.get(
        "/api/v1/jobs",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert list_b.status_code == 200
    items_b = list_b.json()["items"]
    assert all(item["id"] != str(job_a.id) for item in items_b)


# ==============================================================================
# 15. Cron Scheduler Evaluation & Periodic Job Spawning
# ==============================================================================
@pytest.mark.asyncio
async def test_cron_scheduler_evaluation(job_test_env, db_session: AsyncSession):
    """CronScheduler evaluates active schedules and enqueues matured job instances."""
    tenant_a = job_test_env["tenant_a"]
    org_a = job_test_env["org_a"]
    user_a_id = job_test_env["user_a_id"]

    sched = JobSchedule(
        id=uuid.uuid4(),
        tenant_id=tenant_a.id,
        organization_id=org_a.id,
        name="Hourly Inventory Valuation Sync",
        job_type=JobType.REPORTS.value,
        cron_expression="0 * * * *",
        payload_template={"report_type": "inventory_valuation"},
        is_enabled=True,
        next_run_at=datetime.now(UTC) - timedelta(minutes=10),  # Matured
        created_by=user_a_id,
    )
    db_session.add(sched)
    await db_session.flush()

    # Evaluate schedules
    triggered_jobs = await CronScheduler.evaluate_schedules(db_session, tenant_id=tenant_a.id)

    assert len(triggered_jobs) == 1
    triggered_job = triggered_jobs[0]
    assert triggered_job.job_type == JobType.REPORTS.value
    assert "Hourly Inventory Valuation Sync" in triggered_job.job_name

    # Check schedule updated next_run_at into future
    assert sched.last_run_at is not None
    assert sched.next_run_at is not None
    assert sched.next_run_at > datetime.now(UTC)


@pytest.mark.asyncio
async def test_worker_healthcheck(tmp_path, monkeypatch):
    """Verifies that worker check_health correctly detects valid and stale heartbeats."""
    from app.worker import check_health, get_heartbeat_path

    heartbeat_file = tmp_path / "worker_heartbeat.json"
    monkeypatch.setattr("app.worker.get_heartbeat_path", lambda: heartbeat_file)

    # 1. No heartbeat file exists -> unhealthy
    assert check_health() is False

    # 2. Fresh healthy heartbeat -> healthy
    heartbeat_file.write_text(
        json.dumps({"status": "healthy", "timestamp": datetime.now(UTC).timestamp(), "concurrency": 4}),
        encoding="utf-8",
    )
    assert check_health(max_age_seconds=30.0) is True

    # 3. Unhealthy status reported -> unhealthy
    heartbeat_file.write_text(
        json.dumps({"status": "unhealthy", "timestamp": datetime.now(UTC).timestamp(), "error": "failed"}),
        encoding="utf-8",
    )
    assert check_health() is False

    # 4. Stale heartbeat (older than max_age_seconds) -> unhealthy
    heartbeat_file.write_text(
        json.dumps({"status": "healthy", "timestamp": (datetime.now(UTC) - timedelta(seconds=60)).timestamp()}),
        encoding="utf-8",
    )
    assert check_health(max_age_seconds=30.0) is False
