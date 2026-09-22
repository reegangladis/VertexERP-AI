"""0008_manufacturing_mrp_domain

Revision ID: 0008_manufacturing_mrp_domain
Revises: 0007_finance_accounting_domain
Create Date: 2026-09-08 12:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0008_manufacturing_mrp_domain"
down_revision: str | None = "0007_finance_accounting_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. Work Centers
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_work_centers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("work_center_type", sa.String(32), nullable=False, server_default="MACHINING"),  # MACHINING, ASSEMBLY, PACKAGING, TESTING
        sa.Column("capacity_per_day_hours", sa.Numeric(10, 2), nullable=False, server_default="8.00"),
        sa.Column("cost_per_hour", sa.Numeric(12, 4), nullable=False, server_default="50.0000"),
        sa.Column("overhead_cost_per_hour", sa.Numeric(12, 4), nullable=False, server_default="20.0000"),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),  # ACTIVE, MAINTENANCE, INACTIVE
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_mfg_work_center_tenant_code"),
    )

    # --------------------------------------------------------------------------
    # 2. Machines / Equipment
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_machines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("work_center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_work_centers.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("serial_number", sa.String(64), nullable=True),
        sa.Column("hourly_cost", sa.Numeric(12, 4), nullable=False, server_default="30.0000"),
        sa.Column("status", sa.String(32), nullable=False, server_default="OPERATIONAL"),  # OPERATIONAL, MAINTENANCE, DOWN
        sa.Column("last_maintenance_date", sa.Date(), nullable=True),
        sa.Column("next_maintenance_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_mfg_machine_tenant_code"),
    )

    # --------------------------------------------------------------------------
    # 3. Manufacturing Routings
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_routings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("version", sa.String(16), nullable=False, server_default="1.0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_mfg_routing_tenant_code"),
    )

    # --------------------------------------------------------------------------
    # 4. Routing Operations
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_routing_operations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("routing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_routings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("operation_name", sa.String(128), nullable=False),
        sa.Column("work_center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_work_centers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("preferred_machine_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_machines.id", ondelete="SET NULL"), nullable=True),
        sa.Column("setup_time_hours", sa.Numeric(10, 2), nullable=False, server_default="0.50"),
        sa.Column("run_time_per_unit_hours", sa.Numeric(10, 4), nullable=False, server_default="0.1000"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("routing_id", "sequence", name="uq_mfg_routing_operation_seq"),
    )

    # --------------------------------------------------------------------------
    # 5. Bills of Materials (BOM)
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_boms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("routing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_routings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False, server_default="1.0000"),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_units_of_measure.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),  # DRAFT, ACTIVE, ARCHIVED
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "code", name="uq_mfg_bom_tenant_code"),
    )

    # --------------------------------------------------------------------------
    # 6. BOM Versions
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_bom_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("bom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_boms.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("version_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("revision_notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="ACTIVE"),  # DRAFT, ACTIVE, SUPERSEDED, ARCHIVED
        sa.Column("effective_from_date", sa.Date(), nullable=True),
        sa.Column("effective_to_date", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("bom_id", "version_number", name="uq_mfg_bom_version_num"),
    )

    # --------------------------------------------------------------------------
    # 7. BOM Components / Line Items
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_bom_components",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("bom_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_bom_versions.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("component_product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("uom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_units_of_measure.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("scrap_percentage", sa.Numeric(5, 2), nullable=False, server_default="0.00"),
        sa.Column("operation_sequence", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --------------------------------------------------------------------------
    # 8. Production Orders (Manufacturing Orders / MO)
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_production_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("order_number", sa.String(64), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("bom_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_boms.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("bom_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_bom_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("routing_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_routings.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_sales_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm_sales_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("planned_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("produced_quantity", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("rejected_quantity", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("scrap_quantity", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("target_warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("planned_start_date", sa.Date(), nullable=False),
        sa.Column("planned_due_date", sa.Date(), nullable=False),
        sa.Column("actual_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="PLANNED", index=True),  # PLANNED, CONFIRMED, IN_PROGRESS, COMPLETED, CANCELLED
        sa.Column("priority", sa.String(16), nullable=False, server_default="MEDIUM"),  # LOW, MEDIUM, HIGH, URGENT
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_cost", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "order_number", name="uq_mfg_production_order_tenant_num"),
    )

    # --------------------------------------------------------------------------
    # 9. Work Orders (Operations Execution)
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_work_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("operation_name", sa.String(128), nullable=False),
        sa.Column("work_center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_work_centers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("machine_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_machines.id", ondelete="SET NULL"), nullable=True),
        sa.Column("planned_duration_hours", sa.Numeric(10, 2), nullable=False, server_default="1.00"),
        sa.Column("actual_duration_hours", sa.Numeric(10, 2), nullable=False, server_default="0.00"),
        sa.Column("technician_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="PENDING"),  # PENDING, IN_PROGRESS, PAUSED, COMPLETED, CANCELLED
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("hourly_rate", sa.Numeric(12, 4), nullable=False, server_default="50.0000"),
        sa.Column("total_labor_cost", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --------------------------------------------------------------------------
    # 10. Material Consumptions (Deducts Raw Materials from Inventory Ledger)
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_material_consumptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("planned_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("consumed_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_cost", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("stock_movement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_stock_movements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("batch_number", sa.String(64), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("consumed_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --------------------------------------------------------------------------
    # 11. Production Outputs (Adds Finished Goods into Inventory Ledger)
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_production_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("target_warehouse_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_warehouses.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("location_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("produced_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("unit_manufacturing_cost", sa.Numeric(14, 4), nullable=False),
        sa.Column("total_manufacturing_cost", sa.Numeric(16, 4), nullable=False),
        sa.Column("stock_movement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_stock_movements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("batch_number", sa.String(64), nullable=True),
        sa.Column("serial_number", sa.String(64), nullable=True),
        sa.Column("output_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --------------------------------------------------------------------------
    # 12. Production Scraps
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_production_scraps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("scrap_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("scrap_reason", sa.String(64), nullable=False, server_default="DEFECTIVE_RAW_MATERIAL"),
        sa.Column("unit_cost", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_scrap_cost", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("stock_movement_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_stock_movements.id", ondelete="SET NULL"), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("recorded_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --------------------------------------------------------------------------
    # 13. Quality Inspections
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_quality_inspections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("inspection_number", sa.String(64), nullable=False, index=True),
        sa.Column("production_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_production_orders.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_work_orders.id", ondelete="SET NULL"), nullable=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("inspection_type", sa.String(32), nullable=False, server_default="FINAL_ASSEMBLY"),  # RECEIVING, IN_PROCESS, FINAL_ASSEMBLY
        sa.Column("inspected_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("passed_quantity", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("failed_quantity", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("result", sa.String(32), nullable=False, server_default="PASSED"),  # PENDING, PASSED, FAILED, CONDITIONALLY_PASSED
        sa.Column("inspector_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("inspection_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("defect_reason", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="COMPLETED"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "inspection_number", name="uq_mfg_quality_inspection_tenant_num"),
    )

    # --------------------------------------------------------------------------
    # 14. MRP Runs
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_mrp_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("run_number", sa.String(64), nullable=False, index=True),
        sa.Column("planning_horizon_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("status", sa.String(32), nullable=False, server_default="COMPLETED"),  # RUNNING, COMPLETED, FAILED
        sa.Column("run_date", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("total_items_planned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_purchase_requests_generated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_production_orders_generated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("execution_log", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("tenant_id", "run_number", name="uq_mfg_mrp_run_tenant_num"),
    )

    # --------------------------------------------------------------------------
    # 15. MRP Planned Orders
    # --------------------------------------------------------------------------
    op.create_table(
        "mfg_mrp_planned_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("mrp_run_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mfg_mrp_runs.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("order_type", sa.String(32), nullable=False),  # MANUFACTURE, PURCHASE
        sa.Column("gross_requirement", sa.Numeric(14, 4), nullable=False),
        sa.Column("on_hand_stock", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("scheduled_receipts", sa.Numeric(14, 4), nullable=False, server_default="0.0000"),
        sa.Column("net_requirement", sa.Numeric(14, 4), nullable=False),
        sa.Column("planned_quantity", sa.Numeric(14, 4), nullable=False),
        sa.Column("order_date", sa.Date(), nullable=False),
        sa.Column("required_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="PLANNED"),  # PLANNED, CONVERTED, IGNORED
        sa.Column("converted_doc_type", sa.String(32), nullable=True),  # PRODUCTION_ORDER, PURCHASE_REQUEST
        sa.Column("converted_doc_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("mfg_mrp_planned_orders")
    op.drop_table("mfg_mrp_runs")
    op.drop_table("mfg_quality_inspections")
    op.drop_table("mfg_production_scraps")
    op.drop_table("mfg_production_outputs")
    op.drop_table("mfg_material_consumptions")
    op.drop_table("mfg_work_orders")
    op.drop_table("mfg_production_orders")
    op.drop_table("mfg_bom_components")
    op.drop_table("mfg_bom_versions")
    op.drop_table("mfg_boms")
    op.drop_table("mfg_routing_operations")
    op.drop_table("mfg_routings")
    op.drop_table("mfg_machines")
    op.drop_table("mfg_work_centers")
