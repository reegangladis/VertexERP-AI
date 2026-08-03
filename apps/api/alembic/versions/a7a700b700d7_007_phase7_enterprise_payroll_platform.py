"""007_phase7_enterprise_payroll_platform

Revision ID: a7a700b700d7
Revises: f6f600a600c6
Create Date: 2026-08-03 12:06:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a7a700b700d7'
down_revision: Union[str, None] = 'f6f600a600c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. salary_components
    op.create_table(
        'salary_components',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('component_type', sa.String(length=50), nullable=False),
        sa.Column('calculation_type', sa.String(length=50), nullable=False, server_default='flat'),
        sa.Column('taxable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('affects_pf', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('affects_esi', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_salary_components_code'), 'salary_components', ['code'], unique=False)
    op.create_index(op.f('ix_salary_components_id'), 'salary_components', ['id'], unique=False)
    op.create_index(op.f('ix_salary_components_organization_id'), 'salary_components', ['organization_id'], unique=False)

    # 2. salary_structures
    op.create_table(
        'salary_structures',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_salary_structures_code'), 'salary_structures', ['code'], unique=False)
    op.create_index(op.f('ix_salary_structures_id'), 'salary_structures', ['id'], unique=False)
    op.create_index(op.f('ix_salary_structures_organization_id'), 'salary_structures', ['organization_id'], unique=False)

    # 3. salary_structure_components
    op.create_table(
        'salary_structure_components',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('salary_structure_id', sa.Uuid(), nullable=False),
        sa.Column('salary_component_id', sa.Uuid(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('percentage', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('formula', sa.String(length=255), nullable=True),
        sa.Column('sequence', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['salary_component_id'], ['salary_components.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['salary_structure_id'], ['salary_structures.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_salary_structure_components_id'), 'salary_structure_components', ['id'], unique=False)
    op.create_index(op.f('ix_salary_structure_components_salary_component_id'), 'salary_structure_components', ['salary_component_id'], unique=False)
    op.create_index(op.f('ix_salary_structure_components_salary_structure_id'), 'salary_structure_components', ['salary_structure_id'], unique=False)

    # 4. employee_salary_assignments
    op.create_table(
        'employee_salary_assignments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('salary_structure_id', sa.Uuid(), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.Column('gross_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ctc', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['salary_structure_id'], ['salary_structures.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_salary_assignments_employee_id'), 'employee_salary_assignments', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_salary_assignments_id'), 'employee_salary_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_employee_salary_assignments_salary_structure_id'), 'employee_salary_assignments', ['salary_structure_id'], unique=False)

    # 5. payroll_periods
    op.create_table(
        'payroll_periods',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('organization_id', sa.Uuid(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Open'),
        sa.Column('locked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payroll_periods_id'), 'payroll_periods', ['id'], unique=False)
    op.create_index(op.f('ix_payroll_periods_organization_id'), 'payroll_periods', ['organization_id'], unique=False)

    # 6. payroll_runs
    op.create_table(
        'payroll_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('payroll_period_id', sa.Uuid(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_by', sa.Uuid(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Draft'),
        sa.Column('employees_processed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['payroll_period_id'], ['payroll_periods.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['processed_by'], ['employees.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payroll_runs_id'), 'payroll_runs', ['id'], unique=False)
    op.create_index(op.f('ix_payroll_runs_payroll_period_id'), 'payroll_runs', ['payroll_period_id'], unique=False)

    # 7. payslips
    op.create_table(
        'payslips',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('payroll_run_id', sa.Uuid(), nullable=False),
        sa.Column('gross_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_earnings', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('total_deductions', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('net_salary', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('generated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Draft'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payslips_employee_id'), 'payslips', ['employee_id'], unique=False)
    op.create_index(op.f('ix_payslips_id'), 'payslips', ['id'], unique=False)
    op.create_index(op.f('ix_payslips_payroll_run_id'), 'payslips', ['payroll_run_id'], unique=False)

    # 8. payslip_items
    op.create_table(
        'payslip_items',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('payslip_id', sa.Uuid(), nullable=False),
        sa.Column('salary_component_id', sa.Uuid(), nullable=True),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('component_type', sa.String(length=50), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['payslip_id'], ['payslips.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['salary_component_id'], ['salary_components.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payslip_items_id'), 'payslip_items', ['id'], unique=False)
    op.create_index(op.f('ix_payslip_items_payslip_id'), 'payslip_items', ['payslip_id'], unique=False)

    # 9. reimbursements
    op.create_table(
        'reimbursements',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('submitted_date', sa.Date(), nullable=False),
        sa.Column('approved_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Pending'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reimbursements_employee_id'), 'reimbursements', ['employee_id'], unique=False)
    op.create_index(op.f('ix_reimbursements_id'), 'reimbursements', ['id'], unique=False)

    # 10. employee_loans
    op.create_table(
        'employee_loans',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('loan_type', sa.String(length=100), nullable=False),
        sa.Column('principal_amount', sa.Float(), nullable=False),
        sa.Column('remaining_amount', sa.Float(), nullable=False),
        sa.Column('emi_amount', sa.Float(), nullable=False),
        sa.Column('interest_rate', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='Active'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_loans_employee_id'), 'employee_loans', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_loans_id'), 'employee_loans', ['id'], unique=False)

    # 11. payroll_adjustments
    op.create_table(
        'payroll_adjustments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('employee_id', sa.Uuid(), nullable=False),
        sa.Column('adjustment_type', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('payroll_period_id', sa.Uuid(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['payroll_period_id'], ['payroll_periods.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payroll_adjustments_employee_id'), 'payroll_adjustments', ['employee_id'], unique=False)
    op.create_index(op.f('ix_payroll_adjustments_id'), 'payroll_adjustments', ['id'], unique=False)

    # 12. payroll_audit_logs
    op.create_table(
        'payroll_audit_logs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('payroll_run_id', sa.Uuid(), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('performed_by', sa.Uuid(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('remarks', sa.String(length=500), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['payroll_run_id'], ['payroll_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performed_by'], ['employees.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payroll_audit_logs_id'), 'payroll_audit_logs', ['id'], unique=False)
    op.create_index(op.f('ix_payroll_audit_logs_payroll_run_id'), 'payroll_audit_logs', ['payroll_run_id'], unique=False)


def downgrade() -> None:
    op.drop_table('payroll_audit_logs')
    op.drop_table('payroll_adjustments')
    op.drop_table('employee_loans')
    op.drop_table('reimbursements')
    op.drop_table('payslip_items')
    op.drop_table('payslips')
    op.drop_table('payroll_runs')
    op.drop_table('payroll_periods')
    op.drop_table('employee_salary_assignments')
    op.drop_table('salary_structure_components')
    op.drop_table('salary_structures')
    op.drop_table('salary_components')
