"""0006_inventory_procurement_domain

Revision ID: 0006_inventory_procurement
Revises: 0005_crm_domain_complete
Create Date: 2026-09-07 18:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006_inventory_procurement"
down_revision: str | None = "0005_crm_domain_complete"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. Units of Measure
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_units_of_measure",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(16), nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("category", sa.String(32), server_default=sa.text("'COUNT'"), nullable=False),
        sa.Column("is_base_unit", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("conversion_factor", sa.Numeric(12, 6), server_default=sa.text("1.000000"), nullable=False),
        sa.Column("base_unit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_units_of_measure.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 2. Product Categories
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_product_categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_product_categories.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 3. Product Master
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("sku", sa.String(64), nullable=False, index=True),
        sa.Column("barcode", sa.String(64), nullable=True, index=True),
        sa.Column("name", sa.String(128), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_product_categories.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_units_of_measure.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("valuation_method", sa.String(32), server_default=sa.text("'AVERAGE_COST'"), nullable=False),
        sa.Column("cost_price", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("selling_price", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("reorder_point", sa.Numeric(12, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("reorder_quantity", sa.Numeric(12, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("safety_stock", sa.Numeric(12, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("min_order_qty", sa.Numeric(12, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("lead_time_days", sa.Integer(), server_default=sa.text("7"), nullable=False),
        sa.Column("is_stockable", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_purchasable", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("is_sellable", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("allow_negative_stock", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("custom_fields", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 4. Supplier Master
    # --------------------------------------------------------------------------
    op.create_table(
        "proc_suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False, index=True),
        sa.Column("contact_name", sa.String(128), nullable=True),
        sa.Column("email", sa.String(255), nullable=True, index=True),
        sa.Column("phone", sa.String(32), nullable=True),
        sa.Column("website", sa.String(255), nullable=True),
        sa.Column("tax_id", sa.String(64), nullable=True),
        sa.Column("currency", sa.String(3), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("payment_terms", sa.String(64), server_default=sa.text("'NET_30'"), nullable=True),
        sa.Column("lead_time_days", sa.Integer(), server_default=sa.text("7"), nullable=False),
        sa.Column("address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'ACTIVE'"), nullable=False),
        sa.Column("rating", sa.Numeric(3, 2), server_default=sa.text("5.00"), nullable=False),
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
    # 5. Warehouses & Locations
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_warehouses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("warehouse_type", sa.String(32), server_default=sa.text("'STANDARD'"), nullable=False),
        sa.Column("address", postgresql.JSONB, server_default=sa.text("'{}'"), nullable=False),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "inv_locations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("code", sa.String(64), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("aisle", sa.String(32), nullable=True),
        sa.Column("rack", sa.String(32), nullable=True),
        sa.Column("shelf", sa.String(32), nullable=True),
        sa.Column("bin", sa.String(32), nullable=True),
        sa.Column("location_type", sa.String(32), server_default=sa.text("'STORAGE'"), nullable=False),
        sa.Column("max_weight", sa.Numeric(12, 4), nullable=True),
        sa.Column("max_volume", sa.Numeric(12, 4), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 6. Stock Balances (Aggregated State Table)
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_stock_balances",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("quantity_on_hand", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("quantity_reserved", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("quantity_allocated", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("quantity_available", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("average_cost", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("total_value", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("last_movement_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.UniqueConstraint("tenant_id", "organization_id", "product_id", "warehouse_id", "location_id", name="uq_inv_stock_balance_dim"),
    )

    # --------------------------------------------------------------------------
    # 7. Stock Movements (Immutable Double-Entry / Audit Ledger)
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_stock_movements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("movement_number", sa.String(64), nullable=False, index=True),
        sa.Column("movement_type", sa.String(32), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("batch_number", sa.String(64), nullable=True, index=True),
        sa.Column("serial_number", sa.String(64), nullable=True, index=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("total_cost", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("reference_doc_type", sa.String(64), nullable=True, index=True),
        sa.Column("reference_doc_id", postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column("reference_doc_line_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("running_balance_qty", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("running_balance_cost", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False, index=True),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # --------------------------------------------------------------------------
    # 8. Purchase Requests & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "proc_purchase_requests",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("request_number", sa.String(64), nullable=False, index=True),
        sa.Column("requester_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("required_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("priority", sa.String(16), server_default=sa.text("'MEDIUM'"), nullable=False),
        sa.Column("estimated_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "proc_purchase_request_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_purchase_requests.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_units_of_measure.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity", sa.Numeric(14, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("estimated_unit_price", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("estimated_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
    )

    # --------------------------------------------------------------------------
    # 9. Purchase Orders & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "proc_purchase_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("po_number", sa.String(64), nullable=False, index=True),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_suppliers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("purchase_request_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_purchase_requests.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("expected_delivery_date", sa.Date(), nullable=True),
        sa.Column("payment_terms", sa.String(64), server_default=sa.text("'NET_30'"), nullable=True),
        sa.Column("currency", sa.String(3), server_default=sa.text("'USD'"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("subtotal", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_amount", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_amount", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("grand_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("shipping_terms", sa.String(64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "proc_purchase_order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_purchase_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_units_of_measure.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("quantity_ordered", sa.Numeric(14, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("quantity_received", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("quantity_billed", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("unit_price", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("discount_pct", sa.Numeric(5, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("tax_pct", sa.Numeric(5, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("line_total", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
    )

    # --------------------------------------------------------------------------
    # 10. Goods Receipts & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_goods_receipts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("receipt_number", sa.String(64), nullable=False, index=True),
        sa.Column("purchase_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_purchase_orders.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("supplier_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_suppliers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("receipt_date", sa.Date(), nullable=False),
        sa.Column("vendor_delivery_note", sa.String(128), nullable=True),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("received_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("posted_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "inv_goods_receipt_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("goods_receipt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_goods_receipts.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("po_item_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("proc_purchase_order_items.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("quantity_received", sa.Numeric(14, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("quantity_accepted", sa.Numeric(14, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("quantity_rejected", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("rejection_reason", sa.String(255), nullable=True),
        sa.Column("unit_cost", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("total_cost", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("batch_number", sa.String(64), nullable=True),
        sa.Column("serial_number", sa.String(64), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
    )

    # --------------------------------------------------------------------------
    # 11. Stock Transfers & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_stock_transfers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("transfer_number", sa.String(64), nullable=False, index=True),
        sa.Column("from_warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("to_warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("transfer_date", sa.Date(), nullable=False),
        sa.Column("expected_arrival_date", sa.Date(), nullable=True),
        sa.Column("shipped_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "inv_stock_transfer_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("transfer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_stock_transfers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("from_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("to_location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 4), server_default=sa.text("1.0000"), nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("total_cost", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("batch_number", sa.String(64), nullable=True),
    )

    # --------------------------------------------------------------------------
    # 12. Stock Adjustments & Items
    # --------------------------------------------------------------------------
    op.create_table(
        "inv_stock_adjustments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("adjustment_number", sa.String(64), nullable=False, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("reason", sa.String(64), server_default=sa.text("'INVENTORY_COUNT_DISCREPANCY'"), nullable=False),
        sa.Column("status", sa.String(32), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("adjustment_date", sa.Date(), nullable=False),
        sa.Column("requested_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("approved_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("version", sa.Integer(), server_default=sa.text("1"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.clock_timestamp(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    op.create_table(
        "inv_stock_adjustment_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("adjustment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_stock_adjustments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("system_quantity", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("counted_quantity", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("difference_quantity", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), server_default=sa.text("0.0000"), nullable=False),
        sa.Column("total_adjustment_value", sa.Numeric(14, 2), server_default=sa.text("0.00"), nullable=False),
        sa.Column("adjustment_type", sa.String(16), server_default=sa.text("'INCREASE'"), nullable=False),
        sa.Column("batch_number", sa.String(64), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("inv_stock_adjustment_items")
    op.drop_table("inv_stock_adjustments")
    op.drop_table("inv_stock_transfer_items")
    op.drop_table("inv_stock_transfers")
    op.drop_table("inv_goods_receipt_items")
    op.drop_table("inv_goods_receipts")
    op.drop_table("proc_purchase_order_items")
    op.drop_table("proc_purchase_orders")
    op.drop_table("proc_purchase_request_items")
    op.drop_table("proc_purchase_requests")
    op.drop_table("inv_stock_movements")
    op.drop_table("inv_stock_balances")
    op.drop_table("inv_locations")
    op.drop_table("inv_warehouses")
    op.drop_table("proc_suppliers")
    op.drop_table("inv_products")
    op.drop_table("inv_product_categories")
    op.drop_table("inv_units_of_measure")
