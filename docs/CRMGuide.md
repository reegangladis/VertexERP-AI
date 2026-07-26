# CRM Platform Configuration Guide

This guide describes how to configure lead sources, customer accounts, sales opportunities, and import records into the **CRM Intelligence Platform** module in VertexERP AI.

---

## 1. Initial Setup Parameters
Before tracking deal opportunities:
1.  **Lead Sources**: Configure channels (e.g. Web, Cold Call, Referral) at `/crm/leads`.
2.  **Customer Accounts**: Set up business client profile details at `/crm/customers`.
3.  **Contacts Mapping**: Register primary and secondary contact emails and job titles linked to accounts.

---

## 2. Sales Pipeline Stages
Map your sales pipeline stages at `/crm/pipeline`:
*   Standard opportunities transition from `qualification` to `proposal` then `negotiation`.
*   Close deals as `won` or `lost` at `/crm/deals`, logging won/lost reason statements for review.

---

## 3. Activities & timelines
Track customer interactions at `/crm/activities`:
*   Create follow-up tasks, assign priorities, and log due dates.
*   Schedule alignment meetings and log meeting URLs.

---

## 4. Seeding CRM Telemetry Data
Use the **CRM Intelligence Cockpit** dashboard at `/crm/dashboard`:
1.  Click the **Seed CRM Structure** button on the top right.
2.  This automatically populates lead channels, customer accounts, primary contacts, deal opportunities, Quotation versions, support tickets, and campaigns budget parameters.
