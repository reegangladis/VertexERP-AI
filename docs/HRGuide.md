# HR Platform Setup Guide

This guide describes how to configure branch settings, calendars, shifts, and import data into the **HR Intelligence Platform** module in VertexERP AI.

---

## 1. Prerequisites Configuration
Before managing employee profiles, ensure you have set up:
1.  **Branch Locations**: Set up physical branches (e.g. Headquarters, Logistics hubs) at `/org/branches` and office locations at `/org/locations`.
2.  **Departments & Divisions**: Define target departments (e.g. Engineering, Sales) with allocated division budgets at `/org/departments`.
3.  **Job Designations**: Define corporate job grade tiers (e.g. Director, Engineer) and reporting authority scale numbers at `/org/designations`.

---

## 2. Business Calendar & Shift Patterns
Configure the business calendar at `/org/calendar` to map shift hours:
*   Standard shifts are configured with default hours (e.g. 09:00 to 17:00).
*   Specify active working days (e.g. Monday-Friday) and register holidays list (e.g. New Year's, Christmas).
*   Attendance tracking evaluates punch-ins after the calendar start time threshold (e.g. 09:15 AM) as "Late arrival".

---

## 3. Seeding Corporate HR Structure
The easiest way to review the system is to use the **HR Intelligence Cockpit** dashboard at `/hr/dashboard`:
1.  Click the **Seed HR Structure** button on the top right.
2.  This automatically populates 6 active employee records matching system users, emergency contacts, leaves balances, salary configurations, recruitment pipeline stages, and test attendance punch logs.
