# VertexERP AI - Financial Reports Guide

## Overview

Financial reporting in VertexERP AI provides statutory financial statements dynamically compiled from posted General Ledger entries.

---

## Available Financial Reports

### 1. Trial Balance Report
- **Endpoint**: `/api/v1/finance/reports/trial-balance`
- **Output**: Listing of all active GL accounts with accumulated debits, credits, and current balances. Asserts `Total Debits == Total Credits`.

### 2. Balance Sheet (Statement of Financial Position)
- **Endpoint**: `/api/v1/finance/reports/balance-sheet`
- **Output**:
  - `total_assets`
  - `total_liabilities`
  - `total_equity`
  - Validation check `is_balanced: Assets == (Liabilities + Equity)`

### 3. Profit & Loss Statement (Income Statement)
- **Endpoint**: `/api/v1/finance/reports/profit-loss`
- **Output**:
  - `total_revenue`
  - `total_expenses`
  - `net_profit = total_revenue - total_expenses`

### 4. Statement of Cash Flows
- **Endpoint**: `/api/v1/finance/reports/cash-flow`
- **Output**:
  - Operating Cash Flow
  - Investing Cash Flow
  - Financing Cash Flow
  - Net Cash Flow & Ending Cash Balance

### 5. Aging Reports (AR & AP)
- **Endpoint**: `/api/v1/finance/reports/aging?report_type=RECEIVABLE|PAYABLE`
- **Output**: Outstanding balances grouped into:
  - Current (0 - 30 days)
  - 31 - 60 days
  - 61 - 90 days
  - Over 90 days
