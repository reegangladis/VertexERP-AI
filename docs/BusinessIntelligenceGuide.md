# VertexERP AI - Business Intelligence & Analytics Platform Guide

## Overview
Phase 9 delivers a complete enterprise **Business Intelligence & Analytics Platform** comparable to Power BI, Tableau, Looker, and SAP Analytics Cloud. It features a multi-tiered KPI Engine, Executive CEO Dashboards, Domain-Specific Analytics (HR, CRM, Inventory, Finance, Manufacturing), a Custom Report Builder, BI Dashboard Builder, and clean analytics layers prepared for future AI/ML integrations.

---

## Core Architecture & Key Modules

### 1. Enterprise KPI Framework
- **Scope Hierarchy**: Global, Organization, Department, and Branch scopes.
- **Target vs. Actual Calculation**: Dynamic formula evaluation comparing actual operational time-series values against defined performance targets.
- **Trend Directions**: Automated calculation of `UP`, `DOWN`, and `STABLE` indicators based on historical percentage variance thresholds.

### 2. Executive CEO Dashboard
- **Cross-Enterprise Metrics**: Unified visibility across gross revenue, operating expenses, net profit, profit margin %, total headcount, customer accounts, inventory valuation, overall plant OEE, and operating cash flow.
- **Interactive Visualizations**: Time-series revenue/expense trajectory bars, departmental performance share cards, and KPI trend meters.

### 3. Domain Analytics Engines
- **HR & Workforce**: Headcount growth, attendance efficiency %, leave category breakdown, L&D training completion rates, and top performer tracking.
- **CRM & Sales**: Lead conversion funnel stages, sales pipeline valuation, deal velocity, win rate %, and key customer revenue breakdown.
- **Inventory & Logistics**: Stock valuation, turnover ratio, warehouse space capacity load %, supplier OTIF scorecard rating, and stock aging schedule.
- **Finance & Accounting**: Revenue vs expense trends, budget utilization variance %, operating cash flow, and AR/AP aging schedules.
- **Manufacturing & Plant**: Overall Equipment Effectiveness (OEE %), machine fleet telemetry, shop floor quality inspection pass rates, and downtime breakdown.

---

## Database Schemas & Data Model
1. `analytics_dashboards`: Dashboard metadata, scope, and theme configuration.
2. `analytics_widgets`: Chart visualization configuration, query config, data sources, and grid coordinates.
3. `reports`: Custom report definitions, column schemas, and filter queries.
4. `saved_reports`: User saved report execution presets and snapshots.
5. `kpis`: KPI master records, targets, threshold boundaries, and formulas.
6. `kpi_values`: Time-series performance log entries.
7. `dashboard_layouts`: User-customized grid positions and widget placements.
8. `report_templates`: Pre-packaged system report templates.

---

## REST API Endpoints (`/api/v1/analytics/*`)
- `GET /analytics/dashboards/executive`: Fetch CEO summary analytics.
- `GET /analytics/hr`, `/crm`, `/inventory`, `/finance`, `/manufacturing`: Domain analytics aggregations.
- `GET /analytics/dashboards`, `POST /analytics/dashboards`: Manage dashboards and widgets.
- `GET /analytics/kpis`, `POST /analytics/kpis`, `POST /analytics/kpis/{id}/values`: Custom KPI Builder.
- `POST /analytics/reports/execute`: Dynamic tabular query execution with pagination and filtering.
- `POST /analytics/export`: Dataset export to CSV, JSON, or PDF preview.
- `GET /analytics/search`: Unified platform search across dashboards, reports, and KPIs.
