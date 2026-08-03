"""006_phase6_enterprise_leave_management

Revision ID: f6f600a600c6
Revises: e5f500a500b5
Create Date: 2026-08-03 11:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f6f600a600c6'
down_revision: Union[str, None] = 'e5f500a500b5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. leave_types
    op.create_table(
        'leave_types',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=False, server_default='#3B82F6'),
        sa.Column('is_paid', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('allow_half_day', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('allow_negative_balance', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('max_days_per_year', sa.Float(), nullable=False, server_default='20.0'),
        sa.Column('carry_forward', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('carry_forward_limit', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_types_code'), 'leave_types', ['code'], unique=False)
    op.create_index(op.f('ix_leave_types_id'), 'leave_types', ['id'], unique=False)
    op.create_index(op.f('ix_leave_types_organization_id'), 'leave_types', ['organization_id'], unique=False)

    # 2. leave_policies
    op.create_table(
        'leave_policies',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('accrual_method', sa.String(length=50), nullable=False, server_default='annual'),
        sa.Column('approval_levels', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_policies_id'), 'leave_policies', ['id'], unique=False)
    op.create_index(op.f('ix_leave_policies_organization_id'), 'leave_policies', ['organization_id'], unique=False)

    # 3. leave_policy_assignments
    op.create_table(
        'leave_policy_assignments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('policy_id', sa.Uuid(), nullable=False),
        sa.Column('department_id', sa.Uuid(), nullable=True),
        sa.Column('designation_id', sa.Uuid(), nullable=True),
        sa.Column('employment_type', sa.String(length=50), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['designation_id'], ['designations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['policy_id'], ['leave_policies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_policy_assignments_id'), 'leave_policy_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_leave_policy_assignments_policy_id'), 'leave_policy_assignments', ['policy_id'], unique=False)

    # 4. leave_balances
    op.create_table(
        'leave_balances',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('leave_type_id', sa.Uuid(), nullable=False),
        sa.Column('available_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('used_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('pending_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('carry_forward_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('accrued_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('last_updated', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_balances_employee_id'), 'leave_balances', ['employee_id'], unique=False)
    op.create_index(op.f('ix_leave_balances_id'), 'leave_balances', ['id'], unique=False)
    op.create_index(op.f('ix_leave_balances_leave_type_id'), 'leave_balances', ['leave_type_id'], unique=False)

    # 5. leave_requests
    op.create_table(
        'leave_requests',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('leave_type_id', sa.Uuid(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('number_of_days', sa.Float(), nullable=False),
        sa.Column('is_half_day', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('half_day_session', sa.String(length=20), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('attachment_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_requests_employee_id'), 'leave_requests', ['employee_id'], unique=False)
    op.create_index(op.f('ix_leave_requests_end_date'), 'leave_requests', ['end_date'], unique=False)
    op.create_index(op.f('ix_leave_requests_id'), 'leave_requests', ['id'], unique=False)
    op.create_index(op.f('ix_leave_requests_leave_type_id'), 'leave_requests', ['leave_type_id'], unique=False)
    op.create_index(op.f('ix_leave_requests_start_date'), 'leave_requests', ['start_date'], unique=False)

    # 6. leave_approvals
    op.create_table(
        'leave_approvals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('leave_request_id', sa.Uuid(), nullable=False),
        sa.Column('approver_id', sa.Uuid(), nullable=False),
        sa.Column('approval_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('decision', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('remarks', sa.String(length=500), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['approver_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_request_id'], ['leave_requests.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_approvals_approver_id'), 'leave_approvals', ['approver_id'], unique=False)
    op.create_index(op.f('ix_leave_approvals_id'), 'leave_approvals', ['id'], unique=False)
    op.create_index(op.f('ix_leave_approvals_leave_request_id'), 'leave_approvals', ['leave_request_id'], unique=False)

    # 7. leave_accruals
    op.create_table(
        'leave_accruals',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('leave_type_id', sa.Uuid(), nullable=False),
        sa.Column('accrual_date', sa.Date(), nullable=False),
        sa.Column('days_added', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['leave_type_id'], ['leave_types.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leave_accruals_employee_id'), 'leave_accruals', ['employee_id'], unique=False)
    op.create_index(op.f('ix_leave_accruals_id'), 'leave_accruals', ['id'], unique=False)
    op.create_index(op.f('ix_leave_accruals_leave_type_id'), 'leave_accruals', ['leave_type_id'], unique=False)

    # 8. comp_offs
    op.create_table(
        'comp_offs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('attendance_record_id', sa.Uuid(), nullable=True),
        sa.Column('earned_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=False),
        sa.Column('days', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Available'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['attendance_record_id'], ['attendance_records.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comp_offs_employee_id'), 'comp_offs', ['employee_id'], unique=False)
    op.create_index(op.f('ix_comp_offs_id'), 'comp_offs', ['id'], unique=False)

    # 9. holiday_calendars
    op.create_table(
        'holiday_calendars',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_holiday_calendars_id'), 'holiday_calendars', ['id'], unique=False)
    op.create_index(op.f('ix_holiday_calendars_organization_id'), 'holiday_calendars', ['organization_id'], unique=False)

    # 10. holiday_events
    op.create_table(
        'holiday_events',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('calendar_id', sa.Uuid(), nullable=False),
        sa.Column('holiday_date', sa.Date(), nullable=False),
        sa.Column('holiday_name', sa.String(length=100), nullable=False),
        sa.Column('holiday_type', sa.String(length=50), nullable=False, server_default='national'),
        sa.Column('is_optional', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['calendar_id'], ['holiday_calendars.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_holiday_events_calendar_id'), 'holiday_events', ['calendar_id'], unique=False)
    op.create_index(op.f('ix_holiday_events_holiday_date'), 'holiday_events', ['holiday_date'], unique=False)
    op.create_index(op.f('ix_holiday_events_id'), 'holiday_events', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('holiday_events')
    op.drop_table('holiday_calendars')
    op.drop_table('comp_offs')
    op.drop_table('leave_accruals')
    op.drop_table('leave_approvals')
    op.drop_table('leave_requests')
    op.drop_table('leave_balances')
    op.drop_table('leave_policy_assignments')
    op.drop_table('leave_policies')
    op.drop_table('leave_types')
