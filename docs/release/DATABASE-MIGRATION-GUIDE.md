# VertexERP AI V2 — Database Migration Operations Guide

---

## 1. Migration Architecture
VertexERP AI V2 manages relational PostgreSQL schema lifecycle via Alembic with asyncpg/psycopg database drivers.

### Migration Sequence Order
1. `0001_core_organization_tenants.py` - Core Tenants & Organizations
2. `0002_identity_rbac_users.py` - Identity, Users, Roles, MFA, Sessions
3. `0003_audit_logging.py` - Enterprise Audit Trail Ledger
4. `0004_human_resources_domain.py` - HR Employees, Attendance, Shifts
5. `0005_hr_leave_lifecycle_payroll.py` - Leave, Payroll, Performance, LMS
6. `0006_crm_sales_domain.py` - CRM Pipeline, Deals, Quotations
7. `0007_inventory_master_ledger.py` - Products, UoMs, Warehouses, Stock Ledger
8. `0008_procurement_po_receipts.py` - Suppliers, Purchase Orders, Receipts
9. `0009_finance_gl_double_entry.py` - Chart of Accounts, Journals, Ledger
10. `0010_manufacturing_mrp_domain.py` - Work Centers, BOMs, Production
11. `0011_rag_knowledge_domain.py` - RAG Documents & Metadata
12. `0012_analytics_reporting_kpi.py` - KPI Definitions, Dashboards
13. `0013_enforce_postgresql_rls.py` - PostgreSQL Row-Level Security & Policies
14. `0014_pgvector_hnsw_indexes.py` - pgvector Extension & HNSW Cosine Index

---

## 2. Executing Migrations

```bash
# Check current database revision
alembic current

# Upgrade to latest revision (head)
alembic upgrade head

# Generate a new auto-detected revision
alembic revision --autogenerate -m "description_of_change"

# Verify migration history
alembic history --verbose
```
