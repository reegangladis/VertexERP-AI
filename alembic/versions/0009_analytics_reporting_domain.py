"""0009_analytics_reporting_domain

Revision ID: 0009_analytics_reporting_domain
Revises: 0008_manufacturing_mrp_domain
Create Date: 2026-09-08 17:35:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0009_analytics_reporting_domain"
down_revision: str | None = "0008_manufacturing_mrp_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. KPI Definitions Catalog
    # --------------------------------------------------------------------------
    op.create_table(
        "analytics_kpi_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(32), nullable=False, server_default="EXECUTIVE"),  # FINANCE, SALES, INVENTORY, MANUFACTURING, HR, EXECUTIVE
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("unit", sa.String(32), nullable=False, server_default="COUNT"),  # CURRENCY, PERCENTAGE, COUNT, RATIO, DAYS, HOURS
        sa.Column("target_value", sa.Numeric(16, 4), nullable=True),
        sa.Column("warning_threshold", sa.Numeric(16, 4), nullable=True),
        sa.Column("critical_threshold", sa.Numeric(16, 4), nullable=True),
        sa.Column("trend_direction", sa.String(32), nullable=False, server_default="HIGHER_IS_BETTER"),  # HIGHER_IS_BETTER, LOWER_IS_BETTER
        sa.Column("calculation_method", sa.String(32), nullable=False, server_default="REALTIME_SQL"),  # REALTIME_SQL, SNAPSHOT_ROLLUP
        sa.Column("required_permission", sa.String(64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_analytics_kpi_code"),
    )

    # --------------------------------------------------------------------------
    # 2. KPI Snapshots / Pre-Aggregated Rollups (Protects OLTP from Repeated Full Scans)
    # --------------------------------------------------------------------------
    op.create_table(
        "analytics_kpi_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("kpi_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics_kpi_definitions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("kpi_code", sa.String(64), nullable=False, index=True),
        sa.Column("period_type", sa.String(32), nullable=False, server_default="MONTHLY"),  # DAILY, WEEKLY, MONTHLY, QUARTERLY, YEARLY
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dimension_type", sa.String(32), nullable=False, server_default="OVERALL"),  # OVERALL, BRANCH, DEPARTMENT, WAREHOUSE, PRODUCT_CATEGORY
        sa.Column("dimension_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metric_value", sa.Numeric(18, 4), nullable=False, server_default="0.0000"),
        sa.Column("target_value", sa.Numeric(18, 4), nullable=True),
        sa.Column("variance_pct", sa.Numeric(8, 4), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ON_TRACK"),  # ON_TRACK, WARNING, CRITICAL
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_analytics_snapshot_lookup",
        "analytics_kpi_snapshots",
        ["tenant_id", "kpi_code", "period_type", "period_start"],
    )

    # --------------------------------------------------------------------------
    # 3. Configurable Dashboards
    # --------------------------------------------------------------------------
    op.create_table(
        "analytics_dashboards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("category", sa.String(32), nullable=False, server_default="EXECUTIVE"),  # EXECUTIVE, FINANCE, SALES, INVENTORY, MANUFACTURING, HR, CUSTOM
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("layout_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("required_permission", sa.String(64), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_analytics_dashboard_code"),
    )

    # --------------------------------------------------------------------------
    # 4. Dashboard Widgets
    # --------------------------------------------------------------------------
    op.create_table(
        "analytics_dashboard_widgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("dashboard_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics_dashboards.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("widget_type", sa.String(32), nullable=False, server_default="METRIC_CARD"),  # METRIC_CARD, LINE_CHART, BAR_CHART, DONUT_CHART, AREA_CHART, DATA_TABLE, GAUGE
        sa.Column("kpi_code", sa.String(64), nullable=True),
        sa.Column("data_source", sa.String(64), nullable=False),
        sa.Column("query_config", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("grid_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grid_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("grid_w", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("grid_h", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --------------------------------------------------------------------------
    # 5. Reporting Definitions
    # --------------------------------------------------------------------------
    op.create_table(
        "analytics_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(64), nullable=False, index=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("report_type", sa.String(64), nullable=False, server_default="EXECUTIVE_SUMMARY"),  # EXECUTIVE_SUMMARY, FINANCIAL_PERFORMANCE, SALES_COHORT, INVENTORY_AGING, MANUFACTURING_EFFICIENCY, HR_PAYROLL_METRICS
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("parameters_schema", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("required_permission", sa.String(64), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_analytics_report_code"),
    )

    # --------------------------------------------------------------------------
    # 6. Report Execution Audit Logs
    # --------------------------------------------------------------------------
    op.create_table(
        "analytics_report_executions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("report_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("analytics_reports.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("executed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("execution_time_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("result_summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("status", sa.String(32), nullable=False, server_default="COMPLETED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    # --------------------------------------------------------------------------
    # 7. Dedicated Analytical Indexes on Transactional Fact Tables
    # --------------------------------------------------------------------------
    # Safeguards OLTP query performance by enabling fast index scans for analytical time-series filters
    op.create_index("idx_fin_invoices_analytics", "fin_invoices", ["tenant_id", "organization_id", "status", "issue_date"])
    op.create_index("idx_fin_bills_analytics", "fin_bills", ["tenant_id", "organization_id", "status", "bill_date"])
    op.create_index("idx_inv_movements_analytics", "inv_stock_movements", ["tenant_id", "movement_type", "created_at"])
    op.create_index("idx_mfg_orders_analytics", "mfg_production_orders", ["tenant_id", "status", "planned_start_date"])
    op.create_index("idx_mfg_qc_analytics", "mfg_quality_inspections", ["tenant_id", "result", "inspection_date"])


def downgrade() -> None:
    op.drop_index("idx_mfg_qc_analytics", table_name="mfg_quality_inspections")
    op.drop_index("idx_mfg_orders_analytics", table_name="mfg_production_orders")
    op.drop_index("idx_inv_movements_analytics", table_name="inv_stock_movements")
    op.drop_index("idx_fin_bills_analytics", table_name="fin_bills")
    op.drop_index("idx_fin_invoices_analytics", table_name="fin_invoices")

    op.drop_table("analytics_report_executions")
    op.drop_table("analytics_reports")
    op.drop_table("analytics_dashboard_widgets")
    op.drop_table("analytics_dashboards")
    op.drop_index("idx_analytics_snapshot_lookup", table_name="analytics_kpi_snapshots")
    op.drop_table("analytics_kpi_snapshots")
    op.drop_table("analytics_kpi_definitions")
