# Phase 4 Completion Report: HR Intelligence Platform

This report summarizes the design, database models, REST controllers, and user pages developed for **Phase 4 - HR Intelligence Platform** in VertexERP AI.

---

## 1. System Architecture & Boundaries

The module adheres to **Clean Architecture** boundaries, isolating database transactions, validation formats, and frontend states:
*   **Models Layer** (`apps/api/app/models/`): Maps entities for employees, profiles, attendance shift timestamps, leaves rules, payroll structure tiers, and recruitment stages.
*   **Repositories Layer** (`apps/api/app/repositories/`): Inherits abstract async queries from `BaseRepository`.
*   **Services Layer** (`apps/api/app/services/`): Enforces hierarchy loop parameters, evaluates leave balances before filing requests, and manages local uploads.
*   **Schemas Layer** (`apps/api/app/schemas/`): Restricts inputs using Pydantic validation structures.
*   **Controllers Layer** (`apps/api/app/api/v1/endpoints/`): Integrates REST routes, handles CSV imports/exports, and serves file attachments.

---

## 2. Relational Database Schema

Seventeen tables coordinate the HR module:
1.  `employees`: Core identity linking to branch, department, designation, and supervisor hierarchies.
2.  `employee_profiles`: Extends personal info (DOB, contact details, emergency contacts).
3.  `attendance`: Logs shift timing check-in/out timestamps and lateness flags.
4.  `leave_types`: Configures allocations.
5.  `leave_balances`: Tracks used, remaining, and allocated days.
6.  `leave_requests`: Stores date ranges, reasons, and approval status workflow.
7.  `salary_structures`: Establishes basic wage scales and benefits parameters.
8.  `recruitment_jobs`: Stores job postings.
9.  `candidates`: Tracks applicants.
10. `applications`: Tracks stages (`applied`, `screening`, `interview`, `offer`, `hired`).
11. `interviews`: Logs interviewer assignments and comments.
12. `performance_reviews`: Stores reviews and manager rating scorecards.
13. `goals`: Logs performance target KPIs.
14. `training_courses`: Tracks course options.
15. `training_records`: Logs progression rates.
16. `employee_documents`: Stores file references.
17. `employee_notes`: Holds private administrative comments.

---

## 3. Frontend Tiers

Ten user dashboards are integrated:
1.  **HR Dashboard** (`Dashboard.tsx`): Stat cards count active staff, today's punches, and pending leaves, rendering attrition telemetry charts using Recharts.
2.  **Employee Directory** (`EmployeeList.tsx`): Filterable datagrid with bulk CSV controls.
3.  **Employee Profile** (`EmployeeDetails.tsx`): Displays coordinates, files, and onboarding progress checklists.
4.  **Attendance Punch** (`Attendance.tsx`): check-in/out actions and shift logs.
5.  **Leave Console** (`LeaveManagement.tsx`): Balance panels and request routing controls.
6.  **Recruitment Pipeline** (`Recruitment.tsx`): Job creation modals and candidates directory.
7.  **Performance & Goals** (`Performance.tsx`): Progress gauge bars.
8.  **Training L&D** (`Training.tsx`): Course directories.
9.  **Documents Vault** (`Documents.tsx`): Metadata records.
10. **Payroll Settings** (`Payroll.tsx`): Structure setups.

---

## 4. Verification Check

All verification checkpoints have run and pass:
*   **Pytest backend tests**: Verified employee listings, validation errors, and check-in workflows.
*   **Vitest frontend tests**: Verified component title rendering.
*   **Vite build compilation**: Frontend bundles compile with zero typescript errors.

---

## 5. Future AI Integration Points

The data schema is structured to feed future machine learning engines:
*   **Attrition Risk Predictor**: Compares employee tenure, attendance checks, and manager reviews.
*   **Promotion Pipeline**: Evaluates designations, performance reviews, and goals completion rates.
*   **Salary Recommendations ML**: Tracks designation levels and salary settings.
