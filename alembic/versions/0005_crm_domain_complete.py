"""0005_crm_domain_complete

Revision ID: 0005_crm_domain_complete
Revises: 0004_hr_domain_complete
Create Date: 2026-09-06 17:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005_crm_domain_complete"
down_revision: str | None = "0004_hr_domain_complete"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. CRM Customers (Accounts)
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("name", sa.String(128), nullable=False, index=True),
        sa.Column("customer_type", sa.String(32), nullable=False, server_default=sa.text("'CORPORATE'")),
        sa.Column("industry", sa.String(64), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("email", sa.String(255), nullable=True, index=True),
        sa.Column("tax_id", sa.String(64), nullable=True),
        sa.Column("billing_address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("shipping_address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("credit_limit", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("payment_terms", sa.String(64), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'ACTIVE'")),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 2. CRM Contacts
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_customers.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("first_name", sa.String(64), nullable=False),
        sa.Column("last_name", sa.String(64), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, index=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("mobile", sa.String(32), nullable=True),
        sa.Column("title", sa.String(64), nullable=True),
        sa.Column("department", sa.String(64), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 3. CRM Pipelines & Stages
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_pipelines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_default", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "crm_pipeline_stages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("pipeline_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_pipelines.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("stage_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("probability_pct", sa.Numeric(5, 2), server_default=sa.text("10.00"), nullable=False),
        sa.Column("stage_type", sa.String(32), nullable=False, server_default=sa.text("'OPEN'")),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 4. CRM Deals & Stage History
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_deals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("pipeline_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_pipelines.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("stage_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_pipeline_stages.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_customers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("title", sa.String(128), nullable=False, index=True),
        sa.Column("value", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("currency", sa.String(3), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("expected_close_date", sa.Date(), nullable=True),
        sa.Column("win_probability_pct", sa.Numeric(5, 2), server_default=sa.text("10.00"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'OPEN'"), nullable=False),
        sa.Column("lost_reason", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "crm_deal_stage_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_deals.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("from_stage_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_pipeline_stages.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("to_stage_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_pipeline_stages.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("changed_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("duration_in_stage_seconds", sa.Integer(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 5. CRM Leads
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("first_name", sa.String(64), nullable=False),
        sa.Column("last_name", sa.String(64), nullable=False),
        sa.Column("company_name", sa.String(128), nullable=True),
        sa.Column("email", sa.String(255), nullable=False, index=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("title", sa.String(64), nullable=True),
        sa.Column("source", sa.String(32), server_default=sa.text("'WEBSITE'"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'NEW'"), nullable=False),
        sa.Column("rating", sa.String(16), server_default=sa.text("'WARM'"), nullable=False),
        sa.Column("estimated_value", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("converted_customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_customers.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("converted_contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("converted_deal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_deals.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("converted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 6. CRM Quotations & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_quotations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_customers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_deals.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("quotation_number", sa.String(32), nullable=False, index=True),
        sa.Column("quotation_date", sa.Date(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("currency", sa.String(3), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_amount", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_amount", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("grand_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("terms_and_conditions", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("billing_address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("shipping_address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "crm_quotation_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("quotation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_quotations.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("item_type", sa.String(32), server_default=sa.text("'PRODUCT'"), nullable=False),
        sa.Column("item_code", sa.String(64), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_pct", sa.Numeric(5, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_pct", sa.Numeric(5, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 7. CRM Sales Orders & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_sales_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("quotation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_quotations.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_customers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_contacts.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("deal_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_deals.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("order_number", sa.String(32), nullable=False, index=True),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("currency", sa.String(3), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_amount", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_amount", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("grand_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("payment_terms", sa.String(64), nullable=True),
        sa.Column("shipping_method", sa.String(64), nullable=True),
        sa.Column("billing_address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("shipping_address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "crm_sales_order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("sales_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_sales_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("item_type", sa.String(32), server_default=sa.text("'PRODUCT'"), nullable=False),
        sa.Column("item_code", sa.String(64), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_pct", sa.Numeric(5, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_pct", sa.Numeric(5, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("sort_order", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 8. CRM Activities, Notes & Tasks
    # --------------------------------------------------------------------------
    op.create_table(
        "crm_activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("activity_type", sa.String(32), server_default=sa.text("'CALL'"), nullable=False),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("entity_type", sa.String(32), nullable=False, index=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("status", sa.String(32), server_default=sa.text("'PLANNED'"), nullable=False),
        sa.Column("priority", sa.String(16), server_default=sa.text("'MEDIUM'"), nullable=False),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("outcome", sa.Text(), nullable=True),
        sa.Column("location", sa.String(128), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "crm_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("entity_type", sa.String(32), nullable=False, index=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "crm_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("entity_type", sa.String(32), nullable=False, index=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("title", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.String(16), server_default=sa.text("'MEDIUM'"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'TODO'"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("crm_tasks")
    op.drop_table("crm_notes")
    op.drop_table("crm_activities")
    op.drop_table("crm_sales_order_items")
    op.drop_table("crm_sales_orders")
    op.drop_table("crm_quotation_items")
    op.drop_table("crm_quotations")
    op.drop_table("crm_leads")
    op.drop_table("crm_deal_stage_history")
    op.drop_table("crm_deals")
    op.drop_table("crm_pipeline_stages")
    op.drop_table("crm_pipelines")
    op.drop_table("crm_contacts")
    op.drop_table("crm_customers")
