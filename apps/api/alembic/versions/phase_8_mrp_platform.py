"""Phase 8 Manufacturing Resource Planning (MRP) Platform migration.

Revision ID: phase_8_mrp_platform
Revises: phase_6_inventory_platform
Create Date: 2026-07-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase_8_mrp_platform'
down_revision = 'phase_6_inventory_platform'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Product Families
    op.create_table(
        'product_families',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 2. Product Versions
    op.create_table(
        'product_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('version_number', sa.String(50), nullable=False, default='1.0'),
        sa.Column('revision_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('change_summary', sa.String(500), nullable=True),
        sa.Column('engineering_change_note', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 3. Bill of Materials
    op.create_table(
        'bill_of_materials',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('code', sa.String(100), nullable=False, index=True),
        sa.Column('version', sa.String(50), nullable=False, default='1.0'),
        sa.Column('status', sa.String(50), nullable=False, default='DRAFT'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('base_quantity', sa.Float(), nullable=False, default=1.0),
        sa.Column('total_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('approved_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('predicted_yield_rate', sa.Float(), nullable=True, default=98.5),
        sa.Column('optimal_batch_size', sa.Float(), nullable=True, default=100.0),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 4. BOM Items
    op.create_table(
        'bom_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('bom_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bill_of_materials.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('component_product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('parent_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bom_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('quantity', sa.Float(), nullable=False, default=1.0),
        sa.Column('unit_name', sa.String(50), nullable=False, default='PCS'),
        sa.Column('scrap_factor_percent', sa.Float(), nullable=False, default=0.0),
        sa.Column('unit_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('extended_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_alternative', sa.Boolean(), nullable=False, default=False),
        sa.Column('alternative_to_item_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bom_items.id', ondelete='SET NULL'), nullable=True),
        sa.Column('notes', sa.String(255), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 5. Routings
    op.create_table(
        'routings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('code', sa.String(100), nullable=False, index=True),
        sa.Column('version', sa.String(50), nullable=False, default='1.0'),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('total_standard_time_mins', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 6. Work Centers
    op.create_table(
        'work_centers',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('code', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('production_line', sa.String(100), nullable=True),
        sa.Column('category', sa.String(100), nullable=False, default='ASSEMBLY'),
        sa.Column('capacity_per_day_hours', sa.Float(), nullable=False, default=16.0),
        sa.Column('hourly_cost', sa.Float(), nullable=False, default=50.0),
        sa.Column('efficiency_percent', sa.Float(), nullable=False, default=95.0),
        sa.Column('shift_calendar', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='ACTIVE'),
        sa.Column('failure_risk_index', sa.Float(), nullable=True, default=0.05),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 7. Routing Operations
    op.create_table(
        'routing_operations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('routing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routings.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('work_centers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False, default=10),
        sa.Column('operation_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('setup_time_mins', sa.Float(), nullable=False, default=0.0),
        sa.Column('machine_time_mins', sa.Float(), nullable=False, default=0.0),
        sa.Column('labor_time_mins', sa.Float(), nullable=False, default=0.0),
        sa.Column('standard_time_mins', sa.Float(), nullable=False, default=0.0),
        sa.Column('hourly_rate', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 8. Machines
    op.create_table(
        'machines',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('work_centers.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('code', sa.String(50), nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('model_number', sa.String(100), nullable=True),
        sa.Column('serial_number', sa.String(100), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='OPERATIONAL'),
        sa.Column('hourly_cost', sa.Float(), nullable=False, default=75.0),
        sa.Column('capacity_units_per_hour', sa.Float(), nullable=False, default=100.0),
        sa.Column('health_score', sa.Float(), nullable=True, default=98.0),
        sa.Column('predicted_failure_date', sa.Date(), nullable=True),
        sa.Column('sensor_telemetry_summary', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 9. Production Orders
    op.create_table(
        'production_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('order_number', sa.String(100), nullable=False, index=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('bom_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('bill_of_materials.id', ondelete='SET NULL'), nullable=True),
        sa.Column('routing_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routings.id', ondelete='SET NULL'), nullable=True),
        sa.Column('warehouse_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('warehouses.id', ondelete='SET NULL'), nullable=True),
        sa.Column('planned_quantity', sa.Float(), nullable=False),
        sa.Column('completed_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('scrap_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.String(50), nullable=False, default='PLANNED'),
        sa.Column('priority', sa.String(50), nullable=False, default='MEDIUM'),
        sa.Column('planned_start_date', sa.Date(), nullable=False),
        sa.Column('planned_end_date', sa.Date(), nullable=False),
        sa.Column('actual_start_date', sa.Date(), nullable=True),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('material_reservation_status', sa.String(50), nullable=False, default='NOT_RESERVED'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('predicted_completion_delay_days', sa.Float(), nullable=True, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 10. Production Order Items
    op.create_table(
        'production_order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('production_orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('routing_operation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('routing_operations.id', ondelete='SET NULL'), nullable=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('work_centers.id', ondelete='CASCADE'), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False, default=10),
        sa.Column('operation_name', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='PENDING'),
        sa.Column('planned_hours', sa.Float(), nullable=False, default=0.0),
        sa.Column('actual_hours', sa.Float(), nullable=False, default=0.0),
        sa.Column('completed_qty', sa.Float(), nullable=False, default=0.0),
        sa.Column('scrap_qty', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 11. Production Logs
    op.create_table(
        'production_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('production_orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('work_centers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id', ondelete='SET NULL'), nullable=True),
        sa.Column('operator_name', sa.String(255), nullable=True),
        sa.Column('quantity_produced', sa.Float(), nullable=False, default=0.0),
        sa.Column('scrap_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('log_time', sa.DateTime(), nullable=False),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 12. Material Consumption
    op.create_table(
        'material_consumption',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('production_orders.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('reserved_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('consumed_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('scrap_quantity', sa.Float(), nullable=False, default=0.0),
        sa.Column('unit_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('batch_number', sa.String(100), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 13. Quality Inspections
    op.create_table(
        'quality_inspections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('inspection_number', sa.String(100), nullable=False, index=True),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('production_orders.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('lot_number', sa.String(100), nullable=True),
        sa.Column('inspector_name', sa.String(255), nullable=True),
        sa.Column('inspection_type', sa.String(50), nullable=False, default='IN_PROCESS'),
        sa.Column('status', sa.String(50), nullable=False, default='PENDING'),
        sa.Column('decision', sa.String(50), nullable=False, default='PENDING'),
        sa.Column('sample_size', sa.Integer(), nullable=False, default=5),
        sa.Column('passed_count', sa.Integer(), nullable=False, default=0),
        sa.Column('failed_count', sa.Integer(), nullable=False, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 14. Quality Results
    op.create_table(
        'quality_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('inspection_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('quality_inspections.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('parameter_name', sa.String(255), nullable=False),
        sa.Column('expected_value', sa.String(255), nullable=False),
        sa.Column('actual_value', sa.String(255), nullable=False),
        sa.Column('is_passed', sa.Boolean(), nullable=False, default=True),
        sa.Column('corrective_action', sa.String(500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 15. Maintenance Requests
    op.create_table(
        'maintenance_requests',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('ticket_number', sa.String(100), nullable=False, index=True),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('work_centers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('priority', sa.String(50), nullable=False, default='MEDIUM'),
        sa.Column('issue_type', sa.String(50), nullable=False, default='CORRECTIVE'),
        sa.Column('status', sa.String(50), nullable=False, default='OPEN'),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reported_by', sa.String(255), nullable=True),
        sa.Column('assigned_technician', sa.String(255), nullable=True),
        sa.Column('reported_at', sa.DateTime(), nullable=False),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 16. Maintenance Logs
    op.create_table(
        'maintenance_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('request_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('maintenance_requests.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('technician_name', sa.String(255), nullable=False),
        sa.Column('maintenance_date', sa.Date(), nullable=False),
        sa.Column('duration_hours', sa.Float(), nullable=False, default=1.0),
        sa.Column('work_done', sa.Text(), nullable=False),
        sa.Column('parts_replaced', sa.String(500), nullable=True),
        sa.Column('total_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 17. Machine Downtime
    op.create_table(
        'machine_downtime',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('machine_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('machines.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('work_center_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('work_centers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('production_order_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('production_orders.id', ondelete='SET NULL'), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Float(), nullable=False, default=0.0),
        sa.Column('reason_category', sa.String(100), nullable=False, default='UNPLANNED_BREAKDOWN'),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # 18. MRP Runs
    op.create_table(
        'mrp_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('run_number', sa.String(100), nullable=False, index=True),
        sa.Column('run_date', sa.DateTime(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='COMPLETED'),
        sa.Column('total_items_processed', sa.Integer(), nullable=False, default=0),
        sa.Column('suggestions_count', sa.Integer(), nullable=False, default=0),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('procurement_suggestions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('production_suggestions', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('capacity_planning', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )


def downgrade() -> None:
    op.drop_table('mrp_runs')
    op.drop_table('machine_downtime')
    op.drop_table('maintenance_logs')
    op.drop_table('maintenance_requests')
    op.drop_table('quality_results')
    op.drop_table('quality_inspections')
    op.drop_table('material_consumption')
    op.drop_table('production_logs')
    op.drop_table('production_order_items')
    op.drop_table('production_orders')
    op.drop_table('machines')
    op.drop_table('routing_operations')
    op.drop_table('work_centers')
    op.drop_table('routings')
    op.drop_table('bom_items')
    op.drop_table('bill_of_materials')
    op.drop_table('product_versions')
    op.drop_table('product_families')
