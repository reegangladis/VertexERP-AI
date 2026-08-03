"""017_final_circular_foreign_keys_and_performance

Revision ID: k7k700l700fh
Revises: j6j600k600fg
Create Date: 2026-08-04 00:38:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'k7k700l700fh'
down_revision: Union[str, None] = 'j6j600k600fg'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Circular Foreign Keys via ALTER TABLE ADD COLUMN IF NOT EXISTS
    circular_fks = [
        ("organizations", "created_by", "users", "id"),
        ("users", "manager_id", "users", "id"),
        ("employees", "manager_id", "employees", "id"),
        ("departments", "manager_id", "employees", "id"),
        ("branches", "manager_id", "employees", "id"),
        ("work_centers", "manager_id", "employees", "id"),
    ]

    for tbl, col, target_tbl, target_col in circular_fks:
        sql = f"""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='{tbl}') AND 
               EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='{target_tbl}') THEN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='{tbl}' AND column_name='{col}'
                ) THEN
                    ALTER TABLE {tbl} ADD COLUMN {col} UUID NULL REFERENCES {target_tbl}({target_col}) ON DELETE SET NULL;
                END IF;
            END IF;
        END $$;
        """
        op.execute(sql)

    # 2. Performance Composite & Query Indexes with column existence check
    indexes = [
        ("idx_users_org_status", "users", ["organization_id", "status"]),
        ("idx_employees_org_dept", "employees", ["organization_id", "department_id"]),
        ("idx_leads_org_status", "leads", ["organization_id", "status"]),
        ("idx_sales_orders_status", "sales_orders", ["status"]),
        ("idx_purchase_orders_status", "purchase_orders", ["status"]),
        ("idx_journal_entries_date", "journal_entries", ["entry_date"]),
        ("idx_production_orders_status", "production_orders", ["status"]),
        ("idx_rag_chat_messages_session", "rag_chat_messages", ["session_id", "created_at"]),
        ("idx_system_metrics_name_recorded", "system_metrics", ["metric_name", "recorded_at"]),
    ]

    for idx_name, tbl, cols in indexes:
        cols_str = ", ".join(cols)
        # Check first column existence
        first_col = cols[0]
        sql = f"""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='{tbl}' AND column_name='{first_col}'
            ) THEN
                EXECUTE 'CREATE INDEX IF NOT EXISTS {idx_name} ON {tbl} ({cols_str})';
            END IF;
        END $$;
        """
        op.execute(sql)


def downgrade() -> None:
    pass
