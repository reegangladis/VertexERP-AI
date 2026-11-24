# VertexERP AI — API Design & REST Endpoint Specification

## 1. API Standards & Architecture
- **Base URI**: `/api/v1`
- **Protocol**: HTTPS / HTTP (RESTful JSON)
- **Response Format**: RFC 7807 Problem Details for errors; standardized JSON envelope for successes.
- **Authentication**: JWT Bearer token in `Authorization: Bearer <token>` or HttpOnly session cookie.
- **Correlation ID**: Injected `X-Correlation-ID` header on all requests and responses for distributed tracing.

---

## 2. API Domain Routers Summary

### 2.1. Authentication & Identity (`/api/v1/identity`)
- `POST /identity/auth/login` — User authentication, issues access & refresh tokens.
- `POST /identity/auth/logout` — Revokes session and clears auth cookies.
- `GET /identity/auth/me` — Fetches authenticated user profile, roles, and permissions.
- `POST /identity/auth/refresh` — Rotates refresh token and issues new access token.
- `GET /identity/users` — List organization users (Admin only).
- `GET /identity/roles` — List available system and custom roles.

### 2.2. Organization & Structure (`/api/v1/organization`)
- `GET /organization/organizations` — Organization details.
- `GET /organization/branches` — List company branches.
- `GET /organization/departments` — List departments and hierarchy.
- `GET /organization/designations` — List designations and job levels.
- `GET /organization/holidays` — List official public and company holidays.

### 2.3. Human Resources & ESS (`/api/v1/hr`)
- `GET /hr/employees` — List employees with search and department filtering.
- `POST /hr/employees` — Create new employee record.
- `GET /hr/employees/{id}` — Get detailed employee profile.
- `GET /hr/attendance/records` — Query attendance logs with date range and employee filter.
- `POST /hr/attendance/clock-in` — Employee punch-in (server timestamp).
- `POST /hr/attendance/clock-out` — Employee punch-out (calculates duration).
- `GET /hr/attendance/summary` — Monthly attendance stats (present, absent, leave, hours).
- `POST /hr/attendance/regularize` — Submit attendance regularization request.
- `GET /hr/leaves/balances/{employee_id}` — Get leave balances by type.
- `GET /hr/leaves/requests` — List leave requests (user or team scope).
- `POST /hr/leaves/requests` — Submit new leave request.
- `PUT /hr/leaves/requests/{id}/review` — Approve or reject leave request.
- `GET /hr/payroll/runs` — List monthly payroll execution runs.
- `POST /hr/payroll/runs` — Initiate new payroll processing run.
- `POST /hr/payroll/runs/{id}/process` — Calculate salary items for all active employees.
- `PUT /hr/payroll/runs/{id}/approve` — Approve payroll run for disbursement.
- `GET /hr/payroll/payslips/employee/{employee_id}` — List employee payslips.
- `GET /hr/payroll/payslips/{id}` — Detailed payslip breakdown.
- `GET /hr/recruitment/requisitions` — List open job positions.
- `GET /hr/recruitment/applicants` — List applicants with pipeline stage.
- `POST /hr/recruitment/applicants` — Register candidate.
- `PUT /hr/recruitment/applicants/{id}/stage` — Update candidate hiring stage.

### 2.4. Customer Relationship Management (`/api/v1/crm`)
- `GET /crm/leads` — Query leads with status, source, and search filters.
- `POST /crm/leads` — Create lead.
- `PUT /crm/leads/{id}` — Update lead details.
- `POST /crm/leads/{id}/convert` — Convert qualified lead into Account, Contact, and Deal.
- `GET /crm/customers` — List customer accounts.
- `POST /crm/customers` — Create customer account.
- `GET /crm/contacts` — List business contacts.
- `GET /crm/deals` — List opportunities (supports stage filtering for Kanban).
- `POST /crm/deals` — Create opportunity.
- `PUT /crm/deals/{id}/stage` — Update deal stage (moves Kanban column).
- `GET /crm/activities` — List calls, meetings, tasks, and follow-ups.
- `POST /crm/activities` — Log sales activity or schedule follow-up.
- `GET /crm/quotations` — List quotations.
- `POST /crm/quotations` — Create quotation with line items and taxes.
- `POST /crm/quotations/{id}/convert-order` — Convert quotation to sales order.
- `GET /crm/orders` — List sales orders.
- `GET /crm/dashboard/metrics` — Salesforce-inspired CRM dashboard metrics.

### 2.5. Shared Workflows & Approvals (`/api/v1/workflows`)
- `GET /workflows/inbox` — List pending approvals assigned to current user.
- `GET /workflows/requests` — List approval requests submitted by current user.
- `POST /workflows/{id}/action` — Execute approval action (`APPROVE`, `REJECT`, `RETURN`).
- `GET /workflows/{id}/history` — Get timeline of approval steps and comments.

### 2.6. Vertex AI Center (`/api/v1/ai`)
- `POST /ai/copilot/chat` — Contextual AI ERP Copilot conversation with tool execution.
- `POST /ai/copilot/confirm-action` — Human-in-the-loop confirmation for proposed actions.
- `GET /ai/rag/documents` — Search and filter knowledge documents.
- `POST /ai/rag/documents` — Upload and index company policies and handbooks.
- `POST /ai/rag/query` — RAG grounded query returning answer with verifiable citations.
- `POST /ai/ml/lead-scoring/predict` — Predict lead conversion probability and score.
- `POST /ai/ml/attrition-risk/predict` — Predict employee attrition risk score.
- `POST /ai/ml/sales-forecast` — Compute monthly and quarterly sales revenue forecasts.
- `POST /ai/resume/analyze` — Parse resume and calculate semantic match against job requirements.
