"""0015_schema_alignment_and_feedbacks

Revision ID: 0015_schema_alignment
Revises: 0014_pgvector_hnsw_indexes
Create Date: 2026-09-19 17:15:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0015_schema_alignment"
down_revision: str | None = "0014_pgvector_hnsw_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Align api_keys table columns
    op.add_column("api_keys", sa.Column("rate_limit_rpm", sa.Integer(), server_default="60", nullable=False))
    op.add_column(
        "api_keys",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.clock_timestamp(),
            nullable=False,
        ),
    )
    op.add_column("api_keys", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("api_keys", sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False))

    # 2. Align branches table columns
    op.add_column("branches", sa.Column("address_line1", sa.String(length=255), server_default="", nullable=False))
    op.add_column("branches", sa.Column("address_line2", sa.String(length=255), nullable=True))
    op.add_column("branches", sa.Column("city", sa.String(length=64), server_default="", nullable=False))
    op.add_column("branches", sa.Column("state", sa.String(length=64), server_default="", nullable=False))
    op.add_column("branches", sa.Column("postal_code", sa.String(length=32), server_default="", nullable=False))
    op.add_column("branches", sa.Column("country", sa.String(length=3), server_default="USA", nullable=False))
    op.add_column("branches", sa.Column("version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("branches", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # 3. Align departments table columns
    op.add_column(
        "departments",
        sa.Column(
            "parent_department_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("departments.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("departments", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "departments",
        sa.Column(
            "manager_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column("departments", sa.Column("version", sa.Integer(), server_default="1", nullable=False))
    op.add_column("departments", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    # 4. Create interview_feedbacks table if not exists
    op.create_table(
        "interview_feedbacks",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interview_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("interviewer_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("rating", sa.Integer(), server_default="3", nullable=False),
        sa.Column("score", sa.Numeric(precision=4, scale=2), server_default="0.0", nullable=False),
        sa.Column("strengths", sa.Text(), nullable=True),
        sa.Column("weaknesses", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.String(length=32), server_default="HIRE", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.clock_timestamp(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name="pk_interview_feedbacks"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["interview_id"], ["interview_schedules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["interviewer_id"], ["users.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_interview_feedbacks_tenant_org",
        "interview_feedbacks",
        ["tenant_id", "organization_id"],
    )

    # Enable RLS on interview_feedbacks
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("ALTER TABLE interview_feedbacks ENABLE ROW LEVEL SECURITY;")
        op.execute("ALTER TABLE interview_feedbacks FORCE ROW LEVEL SECURITY;")
        op.execute("""
            CREATE POLICY interview_feedbacks_tenant_isolation_policy ON interview_feedbacks
            AS RESTRICTIVE
            USING (
                tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
                OR current_setting('app.is_superuser', true) = 'true'
            )
            WITH CHECK (
                tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid
                OR current_setting('app.is_superuser', true) = 'true'
            );
        """)


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP POLICY IF EXISTS interview_feedbacks_tenant_isolation_policy ON interview_feedbacks;")
    op.drop_table("interview_feedbacks")

    op.drop_column("departments", "deleted_at")
    op.drop_column("departments", "version")
    op.drop_column("departments", "manager_user_id")
    op.drop_column("departments", "description")
    op.drop_column("departments", "parent_department_id")

    op.drop_column("branches", "deleted_at")
    op.drop_column("branches", "version")
    op.drop_column("branches", "country")
    op.drop_column("branches", "postal_code")
    op.drop_column("branches", "state")
    op.drop_column("branches", "city")
    op.drop_column("branches", "address_line2")
    op.drop_column("branches", "address_line1")

    op.drop_column("api_keys", "is_deleted")
    op.drop_column("api_keys", "deleted_at")
    op.drop_column("api_keys", "updated_at")
    op.drop_column("api_keys", "rate_limit_rpm")
