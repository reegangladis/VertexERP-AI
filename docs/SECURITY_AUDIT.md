# VertexERP AI — Security Audit & Hardening Specification

## 1. Security Architecture Assessment

### 1.1. Tenant Isolation & PostgreSQL Row-Level Security
- **Enforcement Mechanism**: The multi-tenant architecture uses a shared database with discriminator columns (`tenant_id`, `organization_id`) reinforced by PostgreSQL Row-Level Security (RLS).
- **Session Context**: Every database connection sets `app.current_tenant_id` at transaction start. Queries that do not supply a matching `tenant_id` return zero rows by design.
- **Superuser Flag**: Superuser context (`app.is_superuser = true`) is strictly reserved for administrative background jobs and initial tenant provisioning.

### 1.2. Authentication & Credential Storage
- **Password Hashing**: Enforced using `argon2-cffi` with high memory/time cost parameters (Argon2id).
- **JWT Protection**: Signed with `HS256` using minimum 32-character secrets (`JWT_SECRET_KEY`).
- **Token Storage**: HttpOnly, Secure, SameSite cookies are preferred in production to protect against XSS token theft.
- **Revocation**: Token blacklist maintained in Redis with automated TTL expiration matching JWT lifetime.

### 1.3. Authorization & Privilege Escalation Defenses
- **RBAC**: Handled on the backend through `PermissionCode` dependencies.
- **Fail-Closed Principle**: Any missing permission raises HTTP 403 Forbidden. Frontend navigation checks never replace backend validation.
- **Cross-Tenant Access Checks**: Verified in integration tests (`tests/security/test_cross_tenant_isolation.py`).

### 1.4. AI & LLM Execution Safety
- **No Unrestricted SQL**: The AI Copilot is strictly isolated from raw SQL generation or execution.
- **Predefined Tools**: Copilot interacts exclusively through predefined, statically typed tool functions (`app/modules/ai/tools/`).
- **Authorization Guard**: Tools inherit the authenticated user's permissions. If an employee asks for another employee's salary, the tool fails with an authorization error.
- **Human-in-the-Loop Confirmation**: Irreversible mutations (e.g., approving payroll, deleting records) require explicit user confirmation.

### 1.5. Data Protection & PII Masking
- **Sensitive Fields**: Employee bank details, tax IDs, and salaries are masked in standard API endpoints and application logs.
- **Logging Sanitization**: Structured logger runs automated regex scrubs to redact JWTs, passwords, credit card numbers, and SSNs.
