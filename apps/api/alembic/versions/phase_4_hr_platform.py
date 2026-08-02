"""Phase 4 HR Platform Migration — payroll_runs and payslips tables.

Revision ID: phase_4_hr_platform
Revises: phase_2_org_platform
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sqa
import sqlalchemy.dialects.postgresql as psql

# revision identifiers
revision = 'phase_4_hr_platform'
down_revision = 'phase_2_org_platform'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. payroll_runs table
    op.create_table(
        'payroll_runs',
        sqa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sqa.Column('organization_id', psql.UUID(as_uuid=True), sqa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('period_month', sqa.Integer(), nullable=False),
        sqa.Column('period_year', sqa.Integer(), nullable=False),
        sqa.Column('status', sqa.String(length=50), nullable=False, server_default='draft'),
        sqa.Column('total_gross', sqa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sqa.Column('total_deductions', sqa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sqa.Column('total_net', sqa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sqa.Column('processed_at', sqa.DateTime(timezone=True), nullable=True),
        sqa.Column('created_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('updated_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('deleted_at', sqa.DateTime(timezone=True), nullable=True),
        sqa.Column('is_deleted', sqa.Boolean(), server_default='false', nullable=False),
    )

    # 2. payslips table
    op.create_table(
        'payslips',
        sqa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sqa.Column('payroll_run_id', psql.UUID(as_uuid=True), sqa.ForeignKey('payroll_runs.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('employee_id', psql.UUID(as_uuid=True), sqa.ForeignKey('employees.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('base_salary', sqa.Numeric(15, 2), nullable=False),
        sqa.Column('total_allowances', sqa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sqa.Column('total_deductions', sqa.Numeric(15, 2), nullable=False, server_default='0.00'),
        sqa.Column('net_salary', sqa.Numeric(15, 2), nullable=False),
        sqa.Column('allowances_breakdown', psql.JSONB(astext_type=sqa.Text()), nullable=True),
        sqa.Column('deductions_breakdown', psql.JSONB(astext_type=sqa.Text()), nullable=True),
        sqa.Column('status', sqa.String(length=50), nullable=False, server_default='generated'),
        sqa.Column('created_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('updated_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('deleted_at', sqa.DateTime(timezone=True), nullable=True),
        sqa.Column('is_deleted', sqa.Boolean(), server_default='false', nullable=False),
    )

def downgrade() -> None:
    op.drop_table('payslips')
    op.drop_table('payroll_runs')
