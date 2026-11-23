# VertexERP AI — Comprehensive Testing Strategy

## 1. Testing Pyramid & Verification Gates
The VertexERP AI test suite follows an enterprise pyramid structure:

```
          / \
         / E2E \        (End-to-end full business flows)
        /-------\
       / Integration \  (API endpoints, DB sessions, RLS isolation)
      /---------------\
     /   Unit Tests    \ (Pure domain logic, Decimal math, PII masking)
    /-------------------\
```

---

## 2. Test Suites Catalog

### 2.1. Backend Tests (`tests/`)
- **Unit Tests (`tests/unit/`)**:
  - `test_config.py`: Environment validation, fail-closed configuration in production.
  - `test_backup_recovery.py`: AES-256 backup encryption, tamper detection, GFS retention.
  - `test_logging.py` & `test_observability.py`: PII redaction, Prometheus metrics, error fingerprinting.
  - `test_security.py`: Password hashing, token generation, security headers.
- **Security Tests (`tests/security/`)**:
  - `test_authentication.py`: Login, token refresh, logout.
  - `test_cross_tenant_isolation.py`: Cross-tenant data leakage prevention.
  - `test_rbac_permissions.py`: Role permission matrix enforcement.
  - `test_mfa.py`: Multi-factor authentication flows.
- **Domain Tests (`tests/hr/`, `tests/crm/`, `tests/finance/`, `tests/ai/`)**:
  - `test_attendance_domain.py`: Punch-in/out, hours calculation, regularization.
  - `test_leave_domain.py`: Accruals, balance deduction, approval transitions.
  - `test_payroll_domain.py`: Salary component math, payroll run generation.
  - `test_crm_domain.py`: Lead conversion, opportunity stage updates.
  - `test_ai_platform.py` & `test_rag_pipeline.py`: Copilot tools, pgvector search, citations.

### 2.2. Frontend Tests (`frontend/src/tests/`)
- `vite-config.test.ts`: Build and alias configuration.
- `core-and-e2e.test.tsx`: App shell, navigation, auth store state.
- `hr-pages.test.tsx`: HR pages rendering, attendance actions, leave modals.
- `finance-pages.test.tsx`: Invoices, journal tables, salary views.
- `ai-pages.test.tsx`: Copilot chat drawer, knowledge base documents.

---

## 3. End-to-End Business Flow Scenarios
1. **Complete HR Flow**:
   - Organization Admin creates employee record.
   - Employee logs into Employee Self-Service portal.
   - Employee clocks in, takes a break, and clocks out.
   - Employee submits leave request.
   - HR Manager reviews and approves leave in Tasks & Approvals.
   - HR processes monthly payroll run and generates payslip.
   - Employee views detailed payslip breakdown in ESS portal.

2. **Complete CRM Flow**:
   - Sales representative registers a new Lead.
   - System calculates AI lead score.
   - Representative logs follow-up call activity.
   - Lead qualifies and converts into Account, Contact, and Opportunity.
   - Representative drags Opportunity across Kanban pipeline to "Closed Won".
   - Sales quotation is generated with Decimal line items.
   - Quotation converts to Sales Order and customer invoice.

3. **Complete AI & RAG Flow**:
   - HR uploads official Employee Handbook document.
   - Background worker parses, chunks, and creates pgvector embeddings.
   - Employee asks Copilot: "What is our company annual leave policy?"
   - Copilot retrieves relevant chunks and responds with grounded facts and verifiable source citations.
