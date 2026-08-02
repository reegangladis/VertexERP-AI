import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


# Security Audit Schemas
class SecurityAuditLogOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    event_type: str
    severity: str
    actor_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    endpoint_path: str | None = None
    details: dict[str, Any] | None = None
    action_taken: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


# Backup & Restore Schemas
class BackupJobCreate(BaseModel):
    job_name: str
    backup_type: str = "FULL"  # FULL, INCREMENTAL, DIFFERENTIAL


class BackupJobOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    job_name: str
    backup_type: str
    status: str
    size_bytes: int
    storage_location: str
    checksum_sha256: str
    duration_seconds: float
    error_message: str | None = None
    completed_at: datetime | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RestoreJobCreate(BaseModel):
    backup_job_id: uuid.UUID
    target_environment: str = "staging"


class RestoreJobOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    backup_job_id: uuid.UUID
    target_environment: str
    status: str
    rpo_achieved_minutes: float
    rto_achieved_minutes: float
    verification_details: dict[str, Any] | None = None
    executed_by: str
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Performance & Benchmark Schemas
class PerformanceReportOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    report_title: str
    period: str
    avg_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    throughput_rps: float
    redis_hit_ratio: float
    slow_queries_count: int
    recommendations: list[str] | None = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LoadTestRunRequest(BaseModel):
    test_name: str = "Enterprise 10k RPS Stress Test"
    concurrent_users: int = 250
    total_requests: int = 20000


class LoadTestResultOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    test_name: str
    concurrent_users: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    peak_rps: float
    avg_response_ms: float
    p99_response_ms: float
    status: str
    run_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Compliance Schemas
class ComplianceReportOut(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID | None = None
    framework: str
    overall_score: float
    passed_controls: int
    failed_controls: int
    control_details: dict[str, Any] | None = None
    audited_by: str
    audited_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GDPRDataDeletionRequest(BaseModel):
    user_email: str
    anonymize_audit_logs: bool = True
    delete_user_sessions: bool = True


# System Readiness Scorecard Schema
class SystemReadinessChecklist(BaseModel):
    security_hardening: bool = True
    csp_enforced: bool = True
    hsts_enabled: bool = True
    circuit_breakers_active: bool = True
    database_backups_verified: bool = True
    dr_rto_verified: bool = True
    soc2_compliance_score: float = 98.5
    system_status: str = "PRODUCTION_READY"
