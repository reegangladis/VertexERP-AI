# Employee Lifecycle Operational Workflow

This document details the software states, data schemas, and pipeline transitions mapping the employee lifecycle in **VertexERP AI**.

---

## 1. Candidate Recruitment
*   **Job Positions**: Jobs are published with description specifications, department associations, and requirements text at `/hr/recruitment`.
*   **Applications Stage**: Candidates apply, mapping applicants inside the hiring pipeline stage tracker:
    $$\text{applied} \to \text{screening} \to \text{interview} \to \text{offer} \to \text{hired} / \text{rejected}$$
*   **Interviews**: Interviews are scheduled with interviewer panels list and rating scale metrics.

---

## 2. Onboarding Workflow
Upon changing candidate application stage to `hired`, onboarding checklists trigger:
*   **Profile Setup**: Creation of standard employee profiles (employee code, department, branch, manager).
*   **Profile Documentation**: Requesting document uploads (Resumes, Passports, NDA acknowledgements) at `/hr/documents`.
*   **IT Asset Placeholder**: Asset allocation checks.
*   **Welcome Kit**: Dispatch verification.

---

## 3. Operations & Performance
Once active, employee data links into:
*   **Time & Attendance**: Checking in/out triggers lateness calculations based on calendar shifts, break deductions, and overtime calculations.
*   **Leaves requests**: Balance checkers verify that the employee has remaining leave limits before submitting requests.
*   **Goals & Reviews**: Manager reviewer scorecards and peer comments evaluate performance cycles.
*   **L&D Training**: Employees progress through certification courses.

---

## 4. Payroll Setup
Before pay cycle calculations:
*   Salary structures define basic base pay, allowances configurations, PF deductions, and health benefit packages.

---

## 5. Offboarding Termination
*   Update status to `terminated` at `/hr/employees`.
*   Assign `date_terminated` parameter logging.
*   Retain historic telemetry data for AI attrition risk analytics.
