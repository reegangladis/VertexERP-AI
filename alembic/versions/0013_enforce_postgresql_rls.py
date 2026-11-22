"""0013_enforce_postgresql_rls

Revision ID: 0013_enforce_postgresql_rls
Revises: 0012_background_processing
Create Date: 2026-09-13 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0013_enforce_postgresql_rls"
down_revision: str | None = "0012_background_processing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# List of all tenant-owned application tables requiring PostgreSQL RLS
TENANT_TABLES: list[str] = [
    # Organization & Identity
    "organizations",
    "tenant_memberships",
    "branches",
    "departments",
    "teams",
    "team_members",
    "designations",
    "business_units",
    "cost_centers",
    "locations",
    "work_calendars",
    "working_days",
    "holidays",
    "users",
    "user_credentials",
    "user_sessions",
    "user_roles",
    "mfa_settings",
    "api_keys",
    "audit_log_entries",
    "security_event_logs",
    # Human Resources
    "employees",
    "employee_profiles",
    "employee_addresses",
    "employee_bank_accounts",
    "employee_emergency_contacts",
    "employment_contracts",
    "salary_components",
    "salary_structures",
    "salary_structure_items",
    "employee_salary_assignments",
    "payroll_runs",
    "payslips",
    "payslip_lines",
    "leave_types",
    "leave_policies",
    "leave_balances",
    "leave_requests",
    "attendance_records",
    "attendance_regularizations",
    "shifts",
    "shift_assignments",
    "job_requisitions",
    "job_applicants",
    "interview_schedules",
    "interview_feedback",
    "job_offers",
    "onboarding_tasks",
    "performance_review_periods",
    "performance_reviews",
    "employee_goals",
    "training_courses",
    "course_modules",
    "course_enrollments",
    "employee_skills",
    "employee_certifications",
    "employee_documents",
    "employee_lifecycle_events",
    # CRM
    "crm_leads",
    "crm_contacts",
    "crm_customers",
    "crm_pipelines",
    "crm_pipeline_stages",
    "crm_deals",
    "crm_deal_stage_history",
    "crm_activities",
    "crm_notes",
    "crm_tasks",
    "crm_quotations",
    "crm_quotation_items",
    "crm_sales_orders",
    "crm_sales_order_items",
    # Inventory
    "inv_uom",
    "inv_categories",
    "inv_products",
    "inv_warehouses",
    "inv_locations",
    "inv_stock_balances",
    "inv_stock_movements",
    "inv_stock_transfers",
    "inv_stock_transfer_items",
    "inv_stock_adjustments",
    "inv_stock_adjustment_items",
    "inv_goods_receipts",
    "inv_goods_receipt_items",
    # Procurement
    "proc_suppliers",
    "proc_purchase_requests",
    "proc_purchase_request_items",
    "proc_purchase_orders",
    "proc_purchase_order_items",
    # Finance
    "fin_accounts",
    "fin_fiscal_years",
    "fin_fiscal_periods",
    "fin_journals",
    "fin_journal_lines",
    "fin_general_ledger",
    "fin_customer_parties",
    "fin_vendor_parties",
    "fin_invoices",
    "fin_invoice_lines",
    "fin_bills",
    "fin_bill_lines",
    "fin_bank_accounts",
    "fin_bank_transactions",
    "fin_payments",
    "fin_payment_allocations",
    # Manufacturing
    "mfg_work_centers",
    "mfg_machines",
    "mfg_routings",
    "mfg_routing_operations",
    "mfg_boms",
    "mfg_bom_versions",
    "mfg_bom_components",
    "mfg_production_orders",
    "mfg_work_orders",
    "mfg_material_consumptions",
    "mfg_production_outputs",
    "mfg_production_scraps",
    "mfg_quality_inspections",
    "mfg_mrp_runs",
    "mfg_mrp_planned_orders",
    # Analytics
    "analytics_reports",
    "analytics_dashboards",
    "analytics_dashboard_widgets",
    "analytics_kpi_definitions",
    "analytics_kpi_snapshots",
    "analytics_report_executions",
    # AI & RAG
    "ai_conversations",
    "ai_messages",
    "ai_tool_executions",
    "ai_usage_logs",
    "rag_documents",
    "rag_document_versions",
    "rag_document_chunks",
    "rag_ingestion_jobs",
    # Jobs
    "background_jobs",
    "job_execution_logs",
    "job_schedules",
]



def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    for table in inspector.get_table_names(schema="public"):
        if table == "alembic_version":
            continue
        columns = {column["name"] for column in inspector.get_columns(table, schema="public")}
        if "tenant_id" not in columns:
            continue

        policy_name = f"{table}_tenant_isolation_policy"
        op.execute(sa.text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY'))
        op.execute(sa.text(f'ALTER TABLE "{table}" FORCE ROW LEVEL SECURITY'))
        op.execute(sa.text(f'DROP POLICY IF EXISTS "{policy_name}" ON "{table}"'))
        policy_sql = (
            f'CREATE POLICY "{policy_name}" ON "{table}" '
            "USING (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid "
            "OR current_setting('app.is_superuser', true) = 'true') "
            "WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid "
            "OR current_setting('app.is_superuser', true) = 'true')"
        )
        op.execute(sa.text(policy_sql))

    op.execute(sa.text("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY"))
    op.execute(sa.text("ALTER TABLE tenants FORCE ROW LEVEL SECURITY"))
    op.execute(sa.text("DROP POLICY IF EXISTS tenants_isolation_policy ON tenants"))
    op.execute(
        sa.text(
            "CREATE POLICY tenants_isolation_policy ON tenants "
            "USING (id = NULLIF(current_setting('app.current_tenant_id', true), '')::uuid "
            "OR current_setting('app.is_superuser', true) = 'true') "
            "WITH CHECK (true)"
        )
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    inspector = sa.inspect(bind)
    for table in inspector.get_table_names(schema="public"):
        if table == "alembic_version":
            continue
        columns = {column["name"] for column in inspector.get_columns(table, schema="public")}
        if "tenant_id" not in columns:
            continue
        policy_name = f"{table}_tenant_isolation_policy"
        op.execute(sa.text(f'DROP POLICY IF EXISTS "{policy_name}" ON "{table}"'))
        op.execute(sa.text(f'ALTER TABLE "{table}" DISABLE ROW LEVEL SECURITY'))

    op.execute(sa.text("DROP POLICY IF EXISTS tenants_isolation_policy ON tenants"))
    op.execute(sa.text("ALTER TABLE tenants DISABLE ROW LEVEL SECURITY"))
