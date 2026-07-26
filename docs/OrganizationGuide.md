# Organization Management Configuration Guide

This guide details the administrative setup and management procedures for **Phase 3 - Organization Management Platform**.

---

## 1. Quick Start: Seeding Enterprise Data

To verify database relationships, schemas, and interactive pages, a helper seeder is included.
1. Log in to the application and navigate to **Organization Console** (`/org/dashboard`).
2. Click **Seed Enterprise Structure**.
3. This will create:
    *   **Locations**: Regional Headquarters (office) and Warehouse Hub (warehouse).
    *   **Branches**: Dublin HQ and Dublin Hub Satellite.
    *   **Departments**: Engineering, HR, and Executive Office.
    *   **Teams**: Core Engineering team and HR Operations.
    *   **Designations**: CEO (L1), VP (L2), Director (L3), Manager (L4), Tech Lead (L5), Software Engineer (L6).
    *   **Reporting Hierarchy**: A 6-tier reporting structure matching the designations above.
    *   **Business Calendar**: Dublin active shift calendar, configuring Dublin working hours (Monday to Friday, 09:00 - 17:30) and local Irish holidays (e.g. St. Patrick's Day).

---

## 2. Managing Branches & Departments

### 2.1. Adding a Subdivision Branch
1. Navigate to **Branches** (`/org/branches`).
2. Click **Add Branch**.
3. Enter Branch details, matching slug identifiers, and default timezone registries (e.g. `Europe/Dublin`).
4. To import bulk branches, click **Bulk Upload CSV** and select a formatted branch list CSV.

### 2.2. Setting Up Departments & Budgets
1. Navigate to **Departments** (`/org/departments`).
2. Define department names and allocate budget placeholders (e.g. `$500,000` for Engineering operations).
3. Select an associated branch to map geographic accounting units.

---

## 3. Configuring Business Calendars

1. Navigate to **Business Calendar** (`/org/calendar`).
2. Select or create the fiscal calendar (e.g. `Irish Fiscal Calendar 2026`).
3. Under **Weekly Shift Pattern**, toggle working days and adjust daily shift start/end hours (e.g. 09:00 to 18:00).
4. Under **Holiday Directory**, append corporate or local public holidays specifying calendar dates.

---

## 4. Policy Handbooks & Settings

1. Navigate to **Org Settings** (`/org/settings`).
2. Under **Branding & Local**, set organization primary and secondary brand HEX colors (used to customize client portal branding colors) and timezones.
3. Under **Extensible Metadata**, configure custom parameters (e.g. tax identifier registration codes).
4. Under **Policy Handbooks**, upload corporate handbooks and business license documents. Files are stored securely locally or via mocked cloud providers.
