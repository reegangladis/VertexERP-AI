"""Phase 5 CRM Platform Migration — sales_orders table and quotation total_amount.

Revision ID: phase_5_crm_platform
Revises: phase_4_hr_platform
Create Date: 2026-07-29

"""
from alembic import op
import sqlalchemy as sqa
import sqlalchemy.dialects.postgresql as psql

# revision identifiers
revision = 'phase_5_crm_platform'
down_revision = 'phase_4_hr_platform'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # 1. Add total_amount to quotations if not exists
    op.add_column('quotations', sqa.Column('total_amount', sqa.Numeric(15, 2), server_default='0.00', nullable=False))

    # 2. Create sales_orders table
    op.create_table(
        'sales_orders',
        sqa.Column('id', psql.UUID(as_uuid=True), primary_key=True),
        sqa.Column('organization_id', psql.UUID(as_uuid=True), sqa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('customer_id', psql.UUID(as_uuid=True), sqa.ForeignKey('customers.id', ondelete='CASCADE'), nullable=False, index=True),
        sqa.Column('quotation_id', psql.UUID(as_uuid=True), sqa.ForeignKey('quotations.id', ondelete='SET NULL'), nullable=True),
        sqa.Column('order_number', sqa.String(length=100), nullable=False),
        sqa.Column('total_amount', sqa.Numeric(15, 2), server_default='0.00', nullable=False),
        sqa.Column('status', sqa.String(length=50), server_default='confirmed', nullable=False),
        sqa.Column('order_date', sqa.Date(), nullable=False),
        sqa.Column('created_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('updated_at', sqa.DateTime(timezone=True), server_default=sqa.func.now(), nullable=False),
        sqa.Column('deleted_at', sqa.DateTime(timezone=True), nullable=True),
        sqa.Column('is_deleted', sqa.Boolean(), server_default='false', nullable=False),
    )

def downgrade() -> None:
    op.drop_table('sales_orders')
    op.drop_column('quotations', 'total_amount')
