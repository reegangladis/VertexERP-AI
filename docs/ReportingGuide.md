# VertexERP AI - Report Builder & Export Engine Guide

## Overview
The **Enterprise Custom Report Builder** provides cross-module querying, filtering, saved preset snapshots, and export capabilities.

---

## Key Features

### 1. Dynamic Query & Filtering
- Select target business domain (`FINANCE`, `HR`, `CRM`, `INVENTORY`, `MANUFACTURING`).
- Apply multi-tenant filters: Organization, Branch, Department, Date Range, User, Product, Customer, and Warehouse.
- Pagination controls with custom page size limits.

### 2. Export & Printing Capabilities
- **CSV Export**: Direct downloadable comma-separated values file encoded in Base64.
- **JSON Export**: Structured raw payload export for external system ingestion.
- **Print Preview Placeholder**: Browser print preview mode optimized for landscape PDF rendering.

### 3. Saved Reports & Presets
- Save dynamic query parameter configurations with custom titles.
- Execution history tracking (`execution_count` and `last_executed_at`).
