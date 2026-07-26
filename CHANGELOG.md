# Changelog - VertexERP AI

All notable changes to the **VertexERP AI** project will be documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [0.8.0] - 2026-07-26 (Phase 8 - Manufacturing & Production Intelligence Platform)

### Added
- **Product Structure**: Finished Goods, Semi-Finished Goods, Raw Materials, Product Families, and Product Versions.
- **Bill of Materials (BOM)**: Multi-Level BOM tree hierarchy, version control, component scrap factors %, cost rollup calculation engine, and BOM approval workflow (`DRAFT`, `APPROVED`).
- **Routings & Operations**: Manufacturing operation sequences, setup time, machine time, labor time, standard cycle times, and hourly cost rates.
- **Work Centers & Machines**: Plant layout work centers, shift calendars, daily capacity hours, and machine fleet inventory with operational status indicators (`OPERATIONAL`, `MAINTENANCE`, `BREAKDOWN`).
- **Production Orders**: Order scheduling, priority management, start/end dates, material reservation checks, and progress tracking.
- **Shop Floor Execution**: Operator execution log interface, good output recording, scrap tracking, and material consumption logging.
- **Quality Control**: Inspection lots, parameter test results, pass/fail decisions, and corrective action records.
- **Maintenance & Downtime**: Breakdown service tickets, technician dispatch, preventive maintenance schedules, and machine downtime tracking.
- **MRP Engine**: Material Requirement Planning calculation engine generating raw material procurement recommendations, planned production recommendations, and work center capacity planning.
- **Manufacturing Dashboard**: Enterprise dashboard with OEE gauges, machine telemetry status, OEE utilization bars, and quality pass rates.
- **AI Readiness**: Integrated `health_score`, `predicted_failure_date`, `failure_risk_index`, and `sensor_telemetry_summary` placeholders across database models and API schemas.

---

## [0.7.0] - 2026-07-26 (Phase 7 - Finance & Accounting Intelligence Platform)


### Added
- **Chart of Accounts**: Hierarchical account tree (Assets, Liabilities, Equity, Income, Expenses), opening balances, running balance logic, and CSV export.
- **General Ledger Engine**: Double-entry journal vouchers, automatic GL posting from operational events, single-click reversals, running balances, and fiscal period closures.
- **Accounts Receivable (AR)**: Sales invoice issuance, customer payment receipts, and AR aging buckets.
- **Accounts Payable (AP)**: Supplier bill recording, vendor disbursements, and AP aging buckets.
- **Banking & Cash**: Bank account master, transaction log, and interactive bank statement reconciliation.
- **Expense Claims**: Employee expense claim submission, approval workflows, receipt metadata, and GL reimbursement posting.
- **Budget Management**: Annual & departmental budgets with real-time budget vs actual progress tracking.
- **Tax Engine**: Jurisdiction tax profiles, GST/VAT rates, and tax reporting.
- **Fixed Assets**: Asset register, straight-line depreciation calculation, and asset disposal.
- **Statutory Financial Reports**: Trial Balance, Balance Sheet, Profit & Loss Statement, Cash Flow Statement, AR/AP Aging.
- **AI Readiness Schema**: Integrated `ai_risk_score`, `ai_anomaly_flag`, `ai_fraud_score`, `ai_default_risk` fields across models.

---

## [0.6.0] - 2026-07-26 (Sprint 1.6 - Inventory & Warehouse Intelligence)

### Added
- **Backend Endpoints for Units & Brands**: Developed listing routes `GET /api/v1/inventory/products/units` and `GET /api/v1/inventory/products/brands` to serve catalog parameters.
- **Frontend Page Integration & Fixes**: Patched tuple destructuring issues, updated unit lists selection, and resolved Axios state mapping issues in `Products.tsx`.
- **Sidebar & Interface Polish**: Updated active layouts footer status to indicate Phase 6 platform integration.
- **Automated Tests**: Formed the Vitest unit test suite `InventoryDashboard.test.tsx` ensuring 100% test completeness and verification.

---

## [0.3.0] - 2026-07-24 (Sprint 1.3 - Enterprise Foundation Completion)

### Added
- **Design System Styles**: Added `variables.css` centralizing spacing, typography, elevations, and HSL colors for Dark/Light modes.
- **Global Context Stores**: Set up React Context Providers in the `store/` directory:
  - `ThemeProvider` for Dark/Light class toggles.
  - `UIProvider` managing Sidebar expand/collapse states and Modal controls.
  - `NotificationProvider` handling generic toast alert notifications.
  - `SettingsProvider` governing API base URLs and feature flags.
- **Axios client wrapper**: Configured `apiClient.ts` with custom request interceptors generating `X-Request-ID` tracing tokens, and response interceptors mapping server errors.
- **Error Boundaries**: Implemented a global React `ErrorBoundary` displaying formatted details during UI rendering failures.
- **Static Route Pages**: Created 404 (Not Found), 500 (Internal Error), Maintenance, and Unauthorized fallback screens.
- **Vitest Testing**: Formed Vitest JSDOM environment in `apps/web/` and wrote tests for `ThemeToggle`, `LandingPage`, and `NotFound` pages.
- **GitHub Configurations**: Created CODEOWNERS files, Dependabot schedules, issue bug/feature template worksheets, pull request templates, and branching strategies.

### Changed
- **TS Strict Mode**: Set `"strict": true` in `tsconfig.app.json`.
- **Ruff Linting**: Configured `pyproject.toml` with `isort` settings to group imports natively.
- **Docker Health Checks**: Added container healthchecks to `Dockerfile.web` and updated `docker-compose.yml` to check container health.

---

## [0.2.0] - 2026-07-24 (Sprint 1.2 - Enterprise Backend Foundation)

### Added
- **Custom Exceptions**: Formed custom exception classes (`NotFoundException`, `ValidationException`, `ConflictException`, etc.) mapping directly to standard HTTP status codes.
- **Standardized API Responses**: Serialized all endpoint data payloads inside a generic response envelope.
- **Logging separations**: Configured multi-destination logging sending console logs to stdout, and operational logs to separate rotating file targets (`app.log`, `error.log`, `access.log`).
- **ASGI Middlewares**: Registered Request ID tracers (`X-Request-ID`), process time calculations (`X-Process-Time`), security headers, and HTTP request access auditors.
- **Database Model Mixins**: Added UUID primary keys, timezone-aware UTC timestamps, and soft deletion mixins.
- **Redis connection client**: Developed connection pool controllers supporting ping healthchecks and automatic JSON serialization/deserialization.
- **Generic Abstractions**: Developed BaseRepository and BaseService classes containing reusable CRUD queries, dynamic filter/sorting mappings, and hooks.
- **Pytest Reorganization**: Restructured test cases into `unit/` and `integration/` suites.

---

## [0.1.0] - 2026-07-24 (Sprint 1.1 - Project Foundation)

### Added
- **Project Structure**: Set up monorepo workspaces containing modular directories: `apps/api` (FastAPI) and `apps/web` (React 19).
- **FastAPI backend**: Configured Uvicorn, routes prefixing, and health check endpoints.
- **Database migrations**: Configured Alembic and PostgreSQL engines.
- **Frontend SPA**: Configured React with Vite and Tailwind CSS.
- **DevOps**: Wrote multi-stage `Dockerfile.api` and `Dockerfile.web` environments coordinated in `docker-compose.yml`.
