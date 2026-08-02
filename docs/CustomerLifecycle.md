# Customer Lifecycle Operational Workflow

This document details the software states, data schemas, and pipeline transitions mapping the customer lifecycle in **VertexERP AI**.

---

## 1. Lead Capture & Scoring
*   **Capture**: Leads are captured via Website forms or Referral networks, mapping source channels.
*   **AI Lead Scoring**: Leads are automatically graded using source codes (e.g. Website = 80, Referral = 95, Cold Call = 25).
*   **Qualification**: Convert lead state to `qualified` once contact details are verified.

---

## 2. Customer & Contact Conversion
*   **Account profile**: Qualified leads are converted into Customer accounts (`business` or `individual` type).
*   **Contact directory**: Bind account managers, job titles, departments, and communication preferences.
*   **Notes & Documents**: Log agreements, resumes, or client briefs.

---

## 3. Opportunity Proposal & Quotations
*   **Staging**: Track opportunities inside sales pipelines:
    $$\text{qualification} \to \text{proposal} \to \text{negotiation} \to \text{closed\_won} / \text{closed\_lost}$$
*   **Deal Contract**: Define amount values and probability percentages.
*   **Quotation Versioning**: Draft quotations and save draft file paths.

---

## 4. Activities & Case Support
*   **Interactions**: Log tasks, meetings, calls, and email timelines.
*   **Tickets Case Registry**: File support tickets, assign categories (billing, technical, features), priority levels (low, medium, high, critical), and save resolution logs.

---

## 5. Marketing Campaigns
*   Track marketing campaigns (Email, SMS, Social), budget limits, and expected returns.
