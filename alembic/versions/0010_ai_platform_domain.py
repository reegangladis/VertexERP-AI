"""0010_ai_platform_domain

Revision ID: 0010_ai_platform_domain
Revises: 0009_analytics_reporting_domain
Create Date: 2026-09-10 15:18:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0010_ai_platform_domain"
down_revision: str | None = "0009_analytics_reporting_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. AI Conversations
    # --------------------------------------------------------------------------
    op.create_table(
        "ai_conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(255), nullable=False, server_default="New Conversation"),
        sa.Column("domain_context", sa.String(32), nullable=False, server_default="GENERAL"),  # GENERAL, FINANCE, SALES, INVENTORY, MANUFACTURING, HR
        sa.Column("model_used", sa.String(64), nullable=False, server_default="gpt-4o"),
        sa.Column("total_prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_cost", sa.Numeric(12, 6), nullable=False, server_default="0.000000"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_ai_conversations_user_tenant",
        "ai_conversations",
        ["tenant_id", "user_id", "created_at"],
    )

    # --------------------------------------------------------------------------
    # 2. AI Messages
    # --------------------------------------------------------------------------
    op.create_table(
        "ai_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role", sa.String(32), nullable=False),  # system, user, assistant, tool
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("tool_calls", postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default=sa.text("'[]'")),
        sa.Column("tool_call_id", sa.String(128), nullable=True),
        sa.Column("name", sa.String(128), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost", sa.Numeric(12, 6), nullable=False, server_default="0.000000"),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_ai_messages_conv_created",
        "ai_messages",
        ["conversation_id", "created_at"],
    )

    # --------------------------------------------------------------------------
    # 3. AI Usage Logs
    # --------------------------------------------------------------------------
    op.create_table(
        "ai_usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_conversations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("operation_type", sa.String(32), nullable=False, server_default="CHAT_COMPLETION"),  # CHAT_COMPLETION, STREAMING, EMBEDDING, TOOL_CALL
        sa.Column("provider", sa.String(32), nullable=False),  # openai, anthropic, gemini, mock
        sa.Column("model", sa.String(64), nullable=False),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completion_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(12, 6), nullable=False, server_default="0.000000"),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(32), nullable=False, server_default="SUCCESS"),  # SUCCESS, FAILED, TIMEOUT, BLOCKED_GUARDRAIL
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_ai_usage_tenant_period",
        "ai_usage_logs",
        ["tenant_id", "created_at"],
    )

    # --------------------------------------------------------------------------
    # 4. AI Tool Executions
    # --------------------------------------------------------------------------
    op.create_table(
        "ai_tool_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_conversations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("message_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_messages.id", ondelete="SET NULL"), nullable=True),
        sa.Column("tool_name", sa.String(128), nullable=False, index=True),
        sa.Column("tool_category", sa.String(32), nullable=False, server_default="GENERAL"),
        sa.Column("is_mutation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("requires_confirmation", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("confirmation_status", sa.String(32), nullable=False, server_default="NOT_REQUIRED"),  # NOT_REQUIRED, PENDING_CONFIRMATION, CONFIRMED, REJECTED, EXPIRED
        sa.Column("confirmation_token", sa.String(128), nullable=True, index=True),
        sa.Column("arguments_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("execution_status", sa.String(32), nullable=False, server_default="SUCCESS"),  # SUCCESS, FAILED, DENIED
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("executed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_ai_tool_exec_lookup",
        "ai_tool_executions",
        ["tenant_id", "tool_name", "executed_at"],
    )


def downgrade() -> None:
    op.drop_table("ai_tool_executions")
    op.drop_table("ai_usage_logs")
    op.drop_table("ai_messages")
    op.drop_table("ai_conversations")
