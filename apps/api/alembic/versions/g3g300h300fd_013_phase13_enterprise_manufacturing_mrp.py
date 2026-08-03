"""013_phase13_enterprise_manufacturing_mrp

Revision ID: g3g300h300fd
Revises: f2f200g200fc
Create Date: 2026-08-04 00:14:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'g3g300h300fd'
down_revision: Union[str, None] = 'f2f200g200fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_table_if_not_exists(table_name: str, *columns_and_constraints, **kwargs):
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        op.create_table(table_name, *columns_and_constraints, **kwargs)


def upgrade() -> None:
    # 1. product_families
    create_table_if_not_exists(
        'product_families',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('family_name', sa.String(length=255), nullable=False),
        sa.Column('family_code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('family_code')
    )

    # 2. product_versions
    create_table_if_not_exists(
        'product_versions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('version_number', sa.String(length=50), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. bill_of_materials
    create_table_if_not_exists(
        'bill_of_materials',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('version_id', sa.Uuid(), nullable=True),
        sa.Column('bom_code', sa.String(length=100), nullable=False),
        sa.Column('revision', sa.String(length=50), nullable=False, server_default='Rev A'),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['version_id'], ['product_versions.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bom_code')
    )

    # 4. bom_items
    create_table_if_not_exists(
        'bom_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('bom_id', sa.Uuid(), nullable=False),
        sa.Column('raw_material_id', sa.Uuid(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('unit', sa.String(length=50), nullable=False, server_default='Pcs'),
        sa.Column('scrap_percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['bom_id'], ['bill_of_materials.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['raw_material_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 5. routings
    create_table_if_not_exists(
        'routings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('routing_code', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=1000), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('routing_code')
    )

    # 6. work_centers
    create_table_if_not_exists(
        'work_centers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('center_name', sa.String(length=255), nullable=False),
        sa.Column('center_code', sa.String(length=50), nullable=False),
        sa.Column('capacity', sa.Float(), nullable=False, server_default='100.0'),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('manager_uuid', sa.Uuid(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['manager_uuid'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('center_code')
    )

    # 7. routing_operations
    create_table_if_not_exists(
        'routing_operations',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('routing_id', sa.Uuid(), nullable=False),
        sa.Column('work_center_id', sa.Uuid(), nullable=False),
        sa.Column('operation_name', sa.String(length=255), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('setup_time_minutes', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('run_time_minutes', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['routing_id'], ['routings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 8. machines
    create_table_if_not_exists(
        'machines',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('work_center_id', sa.Uuid(), nullable=False),
        sa.Column('machine_name', sa.String(length=255), nullable=False),
        sa.Column('machine_code', sa.String(length=50), nullable=False),
        sa.Column('manufacturer', sa.String(length=255), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('installation_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Operational'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['work_center_id'], ['work_centers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('machine_code')
    )

    # 9. machine_maintenance
    create_table_if_not_exists(
        'machine_maintenance',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('machine_id', sa.Uuid(), nullable=False),
        sa.Column('maintenance_type', sa.String(length=50), nullable=False, server_default='Preventive'),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('completed_date', sa.Date(), nullable=True),
        sa.Column('cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Scheduled'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 10. machine_downtime
    create_table_if_not_exists(
        'machine_downtime',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('machine_id', sa.Uuid(), nullable=False),
        sa.Column('downtime_reason', sa.String(length=500), nullable=False),
        sa.Column('start_time', sa.DateTime(), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('duration_hours', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['machine_id'], ['machines.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 11. production_orders
    create_table_if_not_exists(
        'production_orders',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('production_number', sa.String(length=100), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('planned_quantity', sa.Float(), nullable=False),
        sa.Column('completed_quantity', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('scheduled_start', sa.Date(), nullable=False),
        sa.Column('scheduled_end', sa.Date(), nullable=False),
        sa.Column('actual_start', sa.Date(), nullable=True),
        sa.Column('actual_end', sa.Date(), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False, server_default='Medium'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Draft'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('production_number')
    )

    # 12. production_order_items
    create_table_if_not_exists(
        'production_order_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('raw_material_id', sa.Uuid(), nullable=False),
        sa.Column('required_quantity', sa.Float(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['raw_material_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 13. production_schedule
    create_table_if_not_exists(
        'production_schedule',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=False),
        sa.Column('planned_units', sa.Float(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 14. production_logs
    create_table_if_not_exists(
        'production_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('log_message', sa.String(length=1000), nullable=False),
        sa.Column('logged_at', sa.DateTime(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 15. material_consumption
    create_table_if_not_exists(
        'material_consumption',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('planned_quantity', sa.Float(), nullable=False),
        sa.Column('consumed_quantity', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('variance', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 16. finished_goods
    create_table_if_not_exists(
        'finished_goods',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('quantity_produced', sa.Float(), nullable=False),
        sa.Column('unit_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 17. quality_inspections
    create_table_if_not_exists(
        'quality_inspections',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('inspection_type', sa.String(length=50), nullable=False, server_default='In-Process'),
        sa.Column('inspector_id', sa.Uuid(), nullable=True),
        sa.Column('inspection_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Passed'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['inspector_id'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # 18. quality_results
    create_table_if_not_exists(
        'quality_results',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('inspection_id', sa.Uuid(), nullable=False),
        sa.Column('parameter_name', sa.String(length=100), nullable=False),
        sa.Column('measured_value', sa.String(length=100), nullable=False),
        sa.Column('is_passed', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['inspection_id'], ['quality_inspections.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 19. scrap_records
    create_table_if_not_exists(
        'scrap_records',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('product_id', sa.Uuid(), nullable=False),
        sa.Column('scrap_quantity', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 20. mrp_runs
    create_table_if_not_exists(
        'mrp_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('run_date', sa.Date(), nullable=False),
        sa.Column('planning_period', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='Completed'),
        sa.Column('processed_items', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 21. production_costs
    create_table_if_not_exists(
        'production_costs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('production_order_id', sa.Uuid(), nullable=False),
        sa.Column('material_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('labor_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('overhead_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_cost', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('(CURRENT_TIMESTAMP)')),
        sa.ForeignKeyConstraint(['production_order_id'], ['production_orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    pass
