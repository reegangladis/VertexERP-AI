"""0007_finance_accounting_domain

Revision ID: 0007_finance_accounting_domain
Revises: 0006_inventory_procurement
Create Date: 2026-09-08 10:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0007_finance_accounting_domain"
down_revision: str | None = "0006_inventory_procurement"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # --------------------------------------------------------------------------
    # 1. Chart of Accounts
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("account_type", sa.String(32), nullable=False),  # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
        sa.Column("account_category", sa.String(64), nullable=False, server_default="CURRENT_ASSET"),
        sa.Column("parent_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("is_reconciled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("is_deleted", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_fin_accounts_tenant_org_code"),
    )

    # --------------------------------------------------------------------------
    # 2. Fiscal Years and Fiscal Periods
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_fiscal_years",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_fin_fiscal_years_tenant_org_code"),
    )

    op.create_table(
        "fin_fiscal_periods",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("fiscal_year_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_fiscal_years.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("period_number", sa.Integer(), nullable=False),
        sa.Column("period_name", sa.String(64), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_locked", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_closed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "fiscal_year_id", "period_number", name="uq_fin_fiscal_periods_tenant_org_fy_period"),
    )

    # --------------------------------------------------------------------------
    # 3. Financial Customers and Vendors (Parties)
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_customers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("tax_id", sa.String(64), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(64), nullable=True),
        sa.Column("credit_limit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("ar_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("payment_terms_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_fin_customers_tenant_org_code"),
    )

    op.create_table(
        "fin_vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("code", sa.String(32), nullable=False, index=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("tax_id", sa.String(64), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(64), nullable=True),
        sa.Column("ap_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("payment_terms_days", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "code", name="uq_fin_vendors_tenant_org_code"),
    )

    # --------------------------------------------------------------------------
    # 4. Journal Entries and Journal Lines
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_journal_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("entry_number", sa.String(64), nullable=False, index=True),
        sa.Column("entry_date", sa.Date(), nullable=False),
        sa.Column("posting_date", sa.Date(), nullable=False),
        sa.Column("fiscal_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_fiscal_periods.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("entry_type", sa.String(32), nullable=False, server_default="STANDARD"),  # STANDARD, ADJUSTING, CLOSING, REVERSAL
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),  # DRAFT, POSTED, REVERSED, CANCELLED
        sa.Column("reference_type", sa.String(64), nullable=True),  # INVOICE, BILL, PAYMENT, BANK, MANUAL
        sa.Column("reference_id", sa.String(64), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("exchange_rate", sa.Numeric(12, 6), nullable=False, server_default="1.000000"),
        sa.Column("total_debit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_credit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("posted_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reversed_by_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "entry_number", name="uq_fin_journal_entries_tenant_org_number"),
    )

    op.create_table(
        "fin_journal_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("line_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("debit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("credit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("currency_debit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("currency_credit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("partner_type", sa.String(32), nullable=True),  # CUSTOMER, VENDOR, EMPLOYEE
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("cost_center_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cost_centers.id", ondelete="SET NULL"), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.CheckConstraint("debit >= 0", name="chk_fin_journal_lines_debit_positive"),
        sa.CheckConstraint("credit >= 0", name="chk_fin_journal_lines_credit_positive"),
    )

    # --------------------------------------------------------------------------
    # 5. General Ledger
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_general_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("journal_line_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_lines.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("posting_date", sa.Date(), nullable=False, index=True),
        sa.Column("fiscal_period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_fiscal_periods.id", ondelete="RESTRICT"), nullable=True, index=True),
        sa.Column("debit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("credit", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("balance_after", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
    )

    # --------------------------------------------------------------------------
    # 6. Sales Invoices (Accounts Receivable)
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("invoice_number", sa.String(64), nullable=False, index=True),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_customers.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("exchange_rate", sa.Numeric(12, 6), nullable=False, server_default="1.000000"),
        sa.Column("subtotal_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("amount_paid", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("amount_due", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),  # DRAFT, POSTED, PARTIALLY_PAID, PAID, CANCELLED
        sa.Column("ar_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("posted_journal_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "invoice_number", name="uq_fin_invoices_tenant_org_number"),
    )

    op.create_table(
        "fin_invoice_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_invoices.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("inv_products.id", ondelete="SET NULL"), nullable=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 4), nullable=False, server_default="1.0000"),
        sa.Column("unit_price", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_rate", sa.Numeric(6, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("line_total", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
    )

    # --------------------------------------------------------------------------
    # 7. Vendor Bills (Accounts Payable)
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_bills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("bill_number", sa.String(64), nullable=False, index=True),
        sa.Column("vendor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_vendors.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("vendor_invoice_ref", sa.String(128), nullable=True),
        sa.Column("bill_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("exchange_rate", sa.Numeric(12, 6), nullable=False, server_default="1.000000"),
        sa.Column("subtotal_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("total_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("amount_paid", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("amount_due", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),  # DRAFT, POSTED, PARTIALLY_PAID, PAID, CANCELLED
        sa.Column("ap_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=True),
        sa.Column("posted_journal_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "bill_number", name="uq_fin_bills_tenant_org_number"),
    )

    op.create_table(
        "fin_bill_lines",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_bills.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("description", sa.String(255), nullable=False),
        sa.Column("expense_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("quantity", sa.Numeric(12, 4), nullable=False, server_default="1.0000"),
        sa.Column("unit_price", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_rate", sa.Numeric(6, 4), nullable=False, server_default="0.0000"),
        sa.Column("tax_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("line_total", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
    )

    # --------------------------------------------------------------------------
    # 8. Bank Accounts and Bank Transactions
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_bank_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("account_name", sa.String(128), nullable=False),
        sa.Column("account_number", sa.String(64), nullable=False),
        sa.Column("bank_name", sa.String(128), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("gl_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_accounts.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("current_balance", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "account_number", name="uq_fin_bank_accounts_tenant_org_number"),
    )

    op.create_table(
        "fin_bank_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_bank_accounts.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("transaction_date", sa.Date(), nullable=False),
        sa.Column("value_date", sa.Date(), nullable=False),
        sa.Column("transaction_type", sa.String(32), nullable=False),  # DEPOSIT, WITHDRAWAL, TRANSFER_IN, TRANSFER_OUT, FEE, INTEREST
        sa.Column("amount", sa.Numeric(16, 4), nullable=False),
        sa.Column("balance_after", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("reference", sa.String(128), nullable=True),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_reconciled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("journal_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
    )

    # --------------------------------------------------------------------------
    # 9. Payments and Allocations
    # --------------------------------------------------------------------------
    op.create_table(
        "fin_payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("payment_number", sa.String(64), nullable=False, index=True),
        sa.Column("payment_type", sa.String(32), nullable=False),  # RECEIPT (Customer), DISBURSEMENT (Vendor)
        sa.Column("partner_type", sa.String(32), nullable=False),  # CUSTOMER, VENDOR
        sa.Column("partner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("payment_date", sa.Date(), nullable=False),
        sa.Column("payment_method", sa.String(32), nullable=False, server_default="BANK"),  # BANK, CASH, WIRE, CHECK, CARD
        sa.Column("bank_account_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_bank_accounts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("amount", sa.Numeric(16, 4), nullable=False),
        sa.Column("allocated_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("unallocated_amount", sa.Numeric(16, 4), nullable=False, server_default="0.0000"),
        sa.Column("status", sa.String(32), nullable=False, server_default="DRAFT"),  # DRAFT, POSTED, CANCELLED
        sa.Column("posted_journal_entry_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_journal_entries.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reference", sa.String(128), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
        sa.UniqueConstraint("tenant_id", "organization_id", "payment_number", name="uq_fin_payments_tenant_org_number"),
    )

    op.create_table(
        "fin_payment_allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="RESTRICT"), nullable=False, index=True),
        sa.Column("payment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_payments.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_invoices.id", ondelete="CASCADE"), nullable=True),
        sa.Column("bill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fin_bills.id", ondelete="CASCADE"), nullable=True),
        sa.Column("allocated_amount", sa.Numeric(16, 4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.clock_timestamp()),
    )


def downgrade() -> None:
    op.drop_table("fin_payment_allocations")
    op.drop_table("fin_payments")
    op.drop_table("fin_bank_transactions")
    op.drop_table("fin_bank_accounts")
    op.drop_table("fin_bill_lines")
    op.drop_table("fin_bills")
    op.drop_table("fin_invoice_lines")
    op.drop_table("fin_invoices")
    op.drop_table("fin_general_ledger")
    op.drop_table("fin_journal_lines")
    op.drop_table("fin_journal_entries")
    op.drop_table("fin_vendors")
    op.drop_table("fin_customers")
    op.drop_table("fin_fiscal_periods")
    op.drop_table("fin_fiscal_years")
    op.drop_table("fin_accounts")
