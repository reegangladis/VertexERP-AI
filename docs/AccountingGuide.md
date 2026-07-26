# VertexERP AI - Double-Entry Accounting Guide

## Architectural Principles

VertexERP AI enforces strict double-entry bookkeeping rules based on financial accounting standards (GAAP & IFRS).

---

## Normal Account Balances & Ledger Rules

| Account Type | Normal Balance | Increase Direction | Decrease Direction |
| :--- | :--- | :--- | :--- |
| **Assets** | Debit | Debit (+) | Credit (-) |
| **Liabilities** | Credit | Credit (+) | Debit (-) |
| **Equity** | Credit | Credit (+) | Debit (-) |
| **Income / Revenue** | Credit | Credit (+) | Debit (-) |
| **Expenses** | Debit | Debit (+) | Credit (-) |

---

## Automated Transaction GL Workflows

### 1. Customer Sales Invoice
When a Customer Invoice is issued:
- **Debit**: Accounts Receivable (1100)
- **Credit**: Sales / Services Revenue (4000)

### 2. Customer Payment Receipt
When payment is received against an Invoice:
- **Debit**: Bank Account (1020)
- **Credit**: Accounts Receivable (1100)

### 3. Supplier Vendor Bill
When a Supplier Bill is received:
- **Debit**: Expense / Inventory Account (5100)
- **Credit**: Accounts Payable (2000)

### 4. Supplier Vendor Disbursement
When payment is issued for a Supplier Bill:
- **Debit**: Accounts Payable (2000)
- **Credit**: Bank Account (1020)

### 5. Employee Expense Reimbursement
When an employee expense claim is reimbursed:
- **Debit**: Operating Expense Account (5100)
- **Credit**: Operating Bank Account (1020)
