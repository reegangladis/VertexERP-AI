"""phase 2 organization platform business units schema

Revision ID: phase_2_org_platform
Revises: 
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'phase_2_org_platform'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'business_units',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organization_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('slug', sa.String(), nullable=False),
        sa.Column('code', sa.String(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('manager_id', sa.UUID(), nullable=True),
        sa.Column('status', sa.String(), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_business_units_organization_id'), 'business_units', ['organization_id'], unique=False)
    op.create_index(op.f('ix_business_units_slug'), 'business_units', ['slug'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_business_units_slug'), table_name='business_units')
    op.drop_index(op.f('ix_business_units_organization_id'), table_name='business_units')
    op.drop_table('business_units')
