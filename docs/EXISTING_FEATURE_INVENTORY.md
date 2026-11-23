# VertexERP AI — Existing Feature Inventory & Classification

## 1. Feature Classification Matrix

| Feature Domain | Existing Status | Problems & Architectural Deficiencies | Transformation Decision |
| :--- | :--- | :--- | :--- |
| **Authentication & Session** | WORKING | Session check works; cookie security and token rotation present in backend. | **Retain & Extend**: Retain argon2 + JWT; connect frontend `api-client` cleanly. |
| **Role-Based Access Control (RBAC)** | WORKING | Backend permissions enum is comprehensive; frontend permission guards exist. | **Retain & Improve**: Add role matrix for Business Head, Sales Rep, Employee. |
| **Multi-Tenancy & PostgreSQL RLS** | WORKING | Tenant isolation enforced in session and migrations (0013_enforce_postgresql_rls). | **Retain & Verify**: Ensure all new models include `tenant_id` and `organization_id`. |
| **Employee Directory & Profiles** | PARTIALLY WORKING | Backend endpoints exist; UI lacked full view/edit modals and emergency contacts. | **Improve**: Build comprehensive employee profile tabs and directory search. |
| **Attendance & Punch In/Out** | PARTIALLY WORKING | Backend endpoints exist; missing greytHR-style punch widget, calendar, regularization. | **Improve**: Implement calendar grid, real-time punch widget, regularization. |
| **Leave Management** | PARTIALLY WORKING | Backend models and API exist; frontend lacked leave balance cards and visual approvals. | **Improve**: Add leave balance cards, leave application modal, and approval timeline. |
| **Payroll & Payslips** | PARTIALLY WORKING | Backend salary components and payroll run endpoints exist; UI was basic table. | **Improve**: Add payslip PDF-style breakdown view and Decimal calculation verification. |
| **Recruitment & Applicant Pipeline** | PARTIALLY WORKING | Requisition and applicant models exist; resume parsing was not hooked up. | **Improve**: Integrate AI Resume Intelligence and stage advancement. |
| **Performance Management** | PARTIALLY WORKING | Goals and reviews models exist; lacked employee goal submission flow. | **Improve**: Integrate goal tracking and annual review forms. |
| **CRM Leads Management** | PARTIALLY WORKING | Backend model exists; frontend lacked lead conversion wizard and activity logging. | **Improve**: Create Lead management view with conversion to Account/Contact/Deal. |
| **CRM Accounts & Contacts** | PARTIALLY WORKING | Backend models exist; missing from frontend navigation and pages. | **Improve**: Implement full Accounts and Contacts directory with relationship views. |
| **CRM Opportunities & Kanban** | PARTIALLY WORKING | Deal model has stages and values; missing interactive Kanban pipeline board. | **Improve**: Build Salesforce-style Kanban pipeline with stage update actions. |
| **Quotations & Sales Orders** | PARTIALLY WORKING | Backend quotation and order models exist; missing quote generator and PDF export. | **Improve**: Build quote creation modal with line items, tax, and order conversion. |
| **Finance & Invoicing** | PARTIALLY WORKING | Backend invoice and payment endpoints exist; lacked payment status visual cards. | **Improve**: Add customer invoice tracking and revenue KPIs. |
| **Centralized Approvals Workflow** | NOT IMPLEMENTED | Approvals were scattered across individual modules without a unified inbox. | **Implement**: Build shared Workflow & Approval Engine with unified inbox. |
| **AI Copilot** | WORKING | Backend tool router and streaming exists; frontend chat drawer needed refinements. | **Improve**: Connect context-aware ERP query tools with user permission checks. |
| **RAG Knowledge Base** | WORKING | pgvector document chunking and vector search implemented; citations need UI tags. | **Improve**: Connect citation links and policy search in ESS portal. |
| **Machine Learning Engine** | NOT IMPLEMENTED | No trained scikit-learn models or inference endpoints were present in backend. | **Implement**: Add Lead Scoring, Attrition Risk, and Sales Forecasting ML services. |
| **AI Resume Intelligence** | NOT IMPLEMENTED | Applicant model had resume URL but no semantic skill extraction or matching. | **Implement**: Add NLP skill extraction and job-to-resume matching engine. |
| **Manufacturing & MRP** | WORKING (REDUNDANT) | Full BOM, routing, work orders exist but clutter primary product experience. | **Defer / Hide**: Remove from primary navigation while keeping models for safety. |
| **Procurement & Warehousing** | WORKING (REDUNDANT) | Inventory and purchase order models exist but distract from HRMS/CRM vision. | **Defer / Hide**: Remove from primary navigation; maintain underlying code. |

---

## 2. Classification Summary
- **WORKING**: Authentication, Multi-tenant RLS, Core RBAC, Database Sessions, AI RAG Base.
- **PARTIALLY WORKING**: HR Employees, Attendance, Leaves, Payroll, CRM Leads & Deals, Finance Invoices, AI Copilot.
- **NOT IMPLEMENTED**: Unified Workflow & Approval Inbox, Machine Learning (Lead Scoring, Attrition Risk), AI Resume Intelligence, Sales Forecasting, Dual-Workspace Navigation.
- **DEFERRED / HIDDEN**: Manufacturing, Heavy Warehousing, Procurement (de-emphasized from navigation, kept in codebase).
