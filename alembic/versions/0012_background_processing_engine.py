"""0012_background_processing_engine

Revision ID: 0012_background_processing
Revises: 0011_rag_knowledge_domain
Create Date: 2026-09-10 16:12:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0012_background_processing"
down_revision: str | None = "0011_rag_knowledge_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. Background Jobs
    # --------------------------------------------------------------------------
    op.create_table(
        "background_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("job_type", sa.String(64), nullable=False, index=True),
        sa.Column("job_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING", index=True),  # PENDING, QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED, DEAD_LETTER
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),  # 0=NORMAL, 1=HIGH, 2=CRITICAL
        sa.Column("idempotency_key", sa.String(128), nullable=True),
        sa.Column("correlation_id", sa.String(128), nullable=True, index=True),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("backoff_base_seconds", sa.Float(), nullable=False, server_default="2.0"),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="60"),
        sa.Column("is_dead_letter", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("dead_letter_reason", sa.Text(), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_jobs_tenant_idemp",
        "background_jobs",
        ["tenant_id", "idempotency_key"],
    )
    op.create_index(
        "idx_jobs_tenant_status_created",
        "background_jobs",
        ["tenant_id", "status", "created_at"],
    )

    # --------------------------------------------------------------------------
    # 2. Job Execution Logs
    # --------------------------------------------------------------------------
    op.create_table(
        "job_execution_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("background_jobs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),  # RUNNING, COMPLETED, FAILED, TIMEOUT
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_ms", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("worker_id", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_job_logs_job_attempt",
        "job_execution_logs",
        ["job_id", "attempt_number"],
    )

    # --------------------------------------------------------------------------
    # 3. Job Schedules (Recurring Cron Tasks)
    # --------------------------------------------------------------------------
    op.create_table(
        "job_schedules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("cron_expression", sa.String(64), nullable=False),
        sa.Column("payload_template", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_job_schedules_tenant_enabled",
        "job_schedules",
        ["tenant_id", "is_enabled"],
    )


def downgrade() -> None:
    op.drop_table("job_schedules")
    op.drop_table("job_execution_logs")
    op.drop_table("background_jobs")
