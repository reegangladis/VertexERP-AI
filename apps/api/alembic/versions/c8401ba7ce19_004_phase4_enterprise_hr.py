"""004_phase4_enterprise_hr

Revision ID: c8401ba7ce19
Revises: 30edc2461469
Create Date: 2026-08-03 02:21:03.113976

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8401ba7ce19'
down_revision: Union[str, None] = '30edc2461469'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. employees
    op.create_table('employees',
    sa.Column('organization_id', sa.Uuid(), nullable=False),
    sa.Column('department_id', sa.Uuid(), nullable=True),
    sa.Column('designation_id', sa.Uuid(), nullable=True),
    sa.Column('business_unit_id', sa.Uuid(), nullable=True),
    sa.Column('branch_id', sa.Uuid(), nullable=True),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.Column('employee_code', sa.String(), nullable=False),
    sa.Column('employee_number', sa.String(), nullable=True),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('middle_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('gender', sa.String(), nullable=True),
    sa.Column('date_of_birth', sa.DateTime(timezone=True), nullable=True),
    sa.Column('marital_status', sa.String(), nullable=True),
    sa.Column('blood_group', sa.String(), nullable=True),
    sa.Column('joining_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('confirmation_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('employment_type', sa.String(), nullable=False, server_default='full_time'),
    sa.Column('employment_status', sa.String(), nullable=False, server_default='active'),
    sa.Column('official_email', sa.String(), nullable=False),
    sa.Column('personal_email', sa.String(), nullable=True),
    sa.Column('official_phone', sa.String(), nullable=True),
    sa.Column('personal_phone', sa.String(), nullable=True),
    sa.Column('nationality', sa.String(), nullable=True),
    sa.Column('photo', sa.String(), nullable=True),
    sa.Column('manager_uuid', sa.Uuid(), nullable=True),
    sa.Column('manager_id', sa.Uuid(), nullable=True),
    sa.Column('status', sa.String(), nullable=False, server_default='active'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['branch_id'], ['branches.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['business_unit_id'], ['business_units.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['designation_id'], ['designations.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employees_branch_id'), 'employees', ['branch_id'], unique=False)
    op.create_index(op.f('ix_employees_business_unit_id'), 'employees', ['business_unit_id'], unique=False)
    op.create_index(op.f('ix_employees_department_id'), 'employees', ['department_id'], unique=False)
    op.create_index(op.f('ix_employees_designation_id'), 'employees', ['designation_id'], unique=False)
    op.create_index(op.f('ix_employees_employee_code'), 'employees', ['employee_code'], unique=False)
    op.create_index(op.f('ix_employees_id'), 'employees', ['id'], unique=False)
    op.create_index(op.f('ix_employees_official_email'), 'employees', ['official_email'], unique=False)
    op.create_index(op.f('ix_employees_organization_id'), 'employees', ['organization_id'], unique=False)
    op.create_index(op.f('ix_employees_user_id'), 'employees', ['user_id'], unique=False)

    # 2. employee_profiles
    op.create_table('employee_profiles',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('postal_code', sa.String(), nullable=True),
    sa.Column('linkedin', sa.String(), nullable=True),
    sa.Column('github', sa.String(), nullable=True),
    sa.Column('portfolio', sa.String(), nullable=True),
    sa.Column('biography', sa.String(), nullable=True),
    sa.Column('languages', sa.String(), nullable=True),
    sa.Column('hobbies', sa.String(), nullable=True),
    sa.Column('skills_summary', sa.String(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_profiles_employee_id'), 'employee_profiles', ['employee_id'], unique=True)
    op.create_index(op.f('ix_employee_profiles_id'), 'employee_profiles', ['id'], unique=False)

    # 3. employee_documents
    op.create_table('employee_documents',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('document_type', sa.String(), nullable=False),
    sa.Column('document_name', sa.String(), nullable=False),
    sa.Column('document_number', sa.String(), nullable=True),
    sa.Column('file_url', sa.String(), nullable=False),
    sa.Column('issued_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_documents_employee_id'), 'employee_documents', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_documents_id'), 'employee_documents', ['id'], unique=False)

    # 4. emergency_contacts
    op.create_table('emergency_contacts',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('contact_name', sa.String(), nullable=False),
    sa.Column('relationship', sa.String(), nullable=False),
    sa.Column('phone', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('address', sa.String(), nullable=True),
    sa.Column('priority', sa.Integer(), nullable=False, server_default='1'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_emergency_contacts_employee_id'), 'emergency_contacts', ['employee_id'], unique=False)
    op.create_index(op.f('ix_emergency_contacts_id'), 'emergency_contacts', ['id'], unique=False)

    # 5. employment_history
    op.create_table('employment_history',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('company', sa.String(), nullable=False),
    sa.Column('designation', sa.String(), nullable=True),
    sa.Column('department', sa.String(), nullable=True),
    sa.Column('joining_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('leaving_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reason', sa.String(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employment_history_employee_id'), 'employment_history', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employment_history_id'), 'employment_history', ['id'], unique=False)

    # 6. employee_skills
    op.create_table('employee_skills',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('skill_name', sa.String(), nullable=False),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('proficiency', sa.String(), nullable=False, server_default='intermediate'),
    sa.Column('years_of_experience', sa.Float(), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_skills_employee_id'), 'employee_skills', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_skills_id'), 'employee_skills', ['id'], unique=False)

    # 7. employee_certifications
    op.create_table('employee_certifications',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('certification_name', sa.String(), nullable=False),
    sa.Column('issuer', sa.String(), nullable=False),
    sa.Column('issue_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('credential_id', sa.String(), nullable=True),
    sa.Column('credential_url', sa.String(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_certifications_employee_id'), 'employee_certifications', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_certifications_id'), 'employee_certifications', ['id'], unique=False)

    # 8. employee_assets
    op.create_table('employee_assets',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('asset_name', sa.String(), nullable=False),
    sa.Column('asset_code', sa.String(), nullable=False),
    sa.Column('asset_type', sa.String(), nullable=True),
    sa.Column('assigned_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('returned_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.String(), nullable=False, server_default='assigned'),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_assets_employee_id'), 'employee_assets', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_assets_id'), 'employee_assets', ['id'], unique=False)

    # 9. employee_notes
    op.create_table('employee_notes',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('note', sa.String(), nullable=False),
    sa.Column('visibility', sa.String(), nullable=False, server_default='public'),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_notes_employee_id'), 'employee_notes', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_notes_id'), 'employee_notes', ['id'], unique=False)

    # 10. employee_timeline
    op.create_table('employee_timeline',
    sa.Column('employee_id', sa.Uuid(), nullable=False),
    sa.Column('event_type', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('event_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('created_by', sa.Uuid(), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_timeline_employee_id'), 'employee_timeline', ['employee_id'], unique=False)
    op.create_index(op.f('ix_employee_timeline_id'), 'employee_timeline', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('employee_timeline')
    op.drop_table('employee_notes')
    op.drop_table('employee_assets')
    op.drop_table('employee_certifications')
    op.drop_table('employee_skills')
    op.drop_table('employment_history')
    op.drop_table('emergency_contacts')
    op.drop_table('employee_documents')
    op.drop_table('employee_profiles')
    op.drop_table('employees')
