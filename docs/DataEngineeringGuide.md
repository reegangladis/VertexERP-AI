# Enterprise Data Engineering Guide - VertexERP AI

## Overview
The **Enterprise Data Engineering Platform** in **VertexERP AI** processes, standardizes, enriches, and structures all ERP domain data (HR, CRM, Inventory, Finance, Manufacturing, Organization, and Identity) for:
- Business Intelligence & Operational Reporting
- Feature Store Ingestion & Machine Learning Feature Extraction
- AI Embeddings, Vector Search, and RAG Ingestion Pipeline
- Predictive Analytics & Demand Forecasting

---

## Technical Architecture

### 1. Data Lake Multi-Zone Abstraction
- **Raw Zone (`raw/`)**: Immutable raw landing zone for batch Parquet and streaming JSON files.
- **Processed Zone (`processed/`)**: Schema-validated, type-casted, and null-checked data objects.
- **Curated Zone (`curated/`)**: Aggregated business analytics datasets exported in Parquet/JSON formats.
- **Archive Zone (`archive/`)**: Cold storage point-in-time historical backups.

### 2. Data Warehouse Architecture (Star & Snowflake Schema)
- **Dimension Tables (SCD Type 2)**:
  - `dim_customers`: Customer dimension with `effective_date`, `expiration_date`, `is_current`, and `version` columns.
  - `dim_employees`: Employee dimension with historical department & salary tracking.
  - `dim_products`: Product dimension with historical cost/price versioning.
  - `dim_suppliers`: Supplier dimension with rating & payment terms history.
  - `dim_organizations`: Multi-tenant organization dimension.
  - `dim_dates`: Comprehensive date & time dimension.
- **Fact Tables**:
  - `fact_sales`: Revenue, quantity, discounts, and margins.
  - `fact_inventory`: Stock levels, reserved quantities, and warehouse valuations.
  - `fact_financials`: General ledger debit/credit balances.
  - `fact_manufacturing`: Units produced, scrap counts, and OEE %.
  - `fact_hr`: Attendance, worked hours, and payroll expenses.
  - `historical_snapshots`: Checksummed point-in-time warehouse audit snapshots.

---

## Data Quality & Master Data Management (MDM)
- **Automated Validation Rules**: Null checks, duplicate detection, referential integrity, and schema compliance.
- **MDM Golden Records**: Deduplication and confidence score matching for Customer, Employee, Product, Supplier, and Organization master records.

---

## Datasets
Pre-generated standard datasets in `datasets/`:
1. `employee_dataset.json`
2. `customer_dataset.json`
3. `inventory_dataset.json`
4. `financial_dataset.json`
5. `manufacturing_dataset.json`
6. `sales_dataset.json`
7. `supplier_dataset.json`
