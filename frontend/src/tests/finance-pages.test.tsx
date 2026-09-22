import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { FinanceOverviewPage } from "@/features/finance/pages/FinanceOverviewPage";
import { ChartOfAccountsPage } from "@/features/finance/pages/ChartOfAccountsPage";
import { FiscalPeriodsPage } from "@/features/finance/pages/FiscalPeriodsPage";
import { JournalEntriesPage } from "@/features/finance/pages/JournalEntriesPage";
import { InvoicesPage } from "@/features/finance/pages/InvoicesPage";
import { BillsPage } from "@/features/finance/pages/BillsPage";
import { PaymentsPage } from "@/features/finance/pages/PaymentsPage";
import { BankAccountsPage } from "@/features/finance/pages/BankAccountsPage";
import { FinancialReportsPage } from "@/features/finance/pages/FinancialReportsPage";
import { useAuthStore } from "@/stores/auth-store";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Finance & Accounting Domain Frontend Pages", () => {
  beforeEach(() => {
    useAuthStore.getState().setAuth({
      userId: "u-fin-cfo",
      email: "cfo@vertexerp.io",
      fullName: "Chief Financial Officer",
      tenantId: "t-fin-001",
      organizationId: "org-001",
      roles: ["CFO", "SeniorAccountant"],
      permissions: [
        "finance:accounts:read",
        "finance:accounts:write",
        "finance:journals:read",
        "finance:journals:write",
        "finance:journals:post",
        "finance:journals:reverse",
        "finance:invoices:read",
        "finance:invoices:write",
        "finance:invoices:post",
        "finance:bills:read",
        "finance:bills:write",
        "finance:bills:post",
        "finance:payments:read",
        "finance:payments:write",
        "finance:payments:post",
        "finance:banks:read",
        "finance:banks:write",
        "finance:periods:read",
        "finance:periods:close",
        "finance:reports:read",
      ],
    });

    global.fetch = vi.fn().mockImplementation((url: string) => {
      // Trial Balance
      if (url.includes("/finance/reports/trial-balance")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            as_of_date: "2026-09-08",
            total_debit: "245000.50",
            total_credit: "245000.50",
            is_balanced: true,
            lines: [
              {
                account_id: "acc-1010",
                account_code: "1010",
                account_name: "Operating Cash Account",
                account_type: "ASSET",
                debit_total: "245000.50",
                credit_total: "0.00",
                net_debit: "245000.50",
                net_credit: "0.00",
              },
              {
                account_id: "acc-4000",
                account_code: "4000",
                account_name: "SaaS Revenue",
                account_type: "REVENUE",
                debit_total: "0.00",
                credit_total: "245000.50",
                net_debit: "0.00",
                net_credit: "245000.50",
              },
            ],
          }),
        });
      }

      // Balance Sheet
      if (url.includes("/finance/reports/balance-sheet")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            as_of_date: "2026-09-08",
            total_assets: "250000.00",
            total_liabilities: "50000.00",
            total_equity: "200000.00",
            total_liabilities_and_equity: "250000.00",
            is_balanced: true,
            assets: [
              {
                category: "Current Assets",
                subtotal: "250000.00",
                lines: [
                  {
                    account_id: "acc-1010",
                    account_code: "1010",
                    account_name: "Operating Cash Account",
                    account_category: "CURRENT_ASSET",
                    balance: "250000.00",
                  },
                ],
              },
            ],
            liabilities: [
              {
                category: "Current Liabilities",
                subtotal: "50000.00",
                lines: [
                  {
                    account_id: "acc-2000",
                    account_code: "2000",
                    account_name: "Accounts Payable",
                    account_category: "CURRENT_LIABILITY",
                    balance: "50000.00",
                  },
                ],
              },
            ],
            equity: [
              {
                category: "Equity",
                subtotal: "200000.00",
                lines: [
                  {
                    account_id: "acc-3000",
                    account_code: "3000",
                    account_name: "Retained Earnings",
                    account_category: "EQUITY",
                    balance: "200000.00",
                  },
                ],
              },
            ],
          }),
        });
      }

      // Profit & Loss
      if (url.includes("/finance/reports/profit-loss")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            start_date: "2026-01-01",
            end_date: "2026-09-08",
            total_revenue: "150000.00",
            total_expense: "40000.00",
            net_income: "110000.00",
            revenues: [
              {
                account_id: "acc-4000",
                account_code: "4000",
                account_name: "SaaS Subscription Revenue",
                account_category: "REVENUE",
                amount: "150000.00",
              },
            ],
            expenses: [
              {
                account_id: "acc-5000",
                account_code: "5000",
                account_name: "Cloud Server Hosting",
                account_category: "EXPENSE",
                amount: "40000.00",
              },
            ],
          }),
        });
      }

      // Accounts endpoints
      if (url.includes("/finance/accounts")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "acc-1010",
                code: "1010",
                name: "Operating Cash Account",
                account_type: "ASSET",
                account_category: "CURRENT_ASSET",
                currency: "USD",
                current_balance: "245000.50",
                is_reconciled: true,
                is_active: true,
              },
              {
                id: "acc-1100",
                code: "1100",
                name: "Accounts Receivable",
                account_type: "ASSET",
                account_category: "CURRENT_ASSET",
                currency: "USD",
                current_balance: "5000.00",
                is_reconciled: true,
                is_active: true,
              },
              {
                id: "acc-2000",
                code: "2000",
                name: "Accounts Payable",
                account_type: "LIABILITY",
                account_category: "CURRENT_LIABILITY",
                currency: "USD",
                current_balance: "1200.00",
                is_reconciled: true,
                is_active: true,
              },
              {
                id: "acc-4000",
                code: "4000",
                name: "SaaS Revenue",
                account_type: "REVENUE",
                account_category: "OPERATING_REVENUE",
                currency: "USD",
                current_balance: "150000.00",
                is_reconciled: false,
                is_active: true,
              },
              {
                id: "acc-5000",
                code: "5000",
                name: "Hosting & Server Expense",
                account_type: "EXPENSE",
                account_category: "OPERATING_EXPENSE",
                currency: "USD",
                current_balance: "40000.00",
                is_reconciled: false,
                is_active: true,
              },
            ],
            total: 5,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Fiscal Years endpoints
      if (url.includes("/finance/fiscal/years")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "fy-2026",
                code: "FY-2026",
                name: "FY 2026",
                start_date: "2026-01-01",
                end_date: "2026-12-31",
                is_closed: false,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Fiscal Periods endpoints
      if (url.includes("/finance/fiscal/periods")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "fp-2026-01",
                fiscal_year_id: "fy-2026",
                period_number: 1,
                period_name: "Jan 2026",
                start_date: "2026-01-01",
                end_date: "2026-01-31",
                is_locked: false,
                is_closed: false,
              },
              {
                id: "fp-2026-02",
                fiscal_year_id: "fy-2026",
                period_number: 2,
                period_name: "Feb 2026",
                start_date: "2026-02-01",
                end_date: "2026-02-28",
                is_locked: true,
                is_closed: false,
              },
            ],
            total: 2,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Journal Entries endpoints
      if (url.includes("/finance/journals")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "je-1",
                entry_number: "JE-2026-0001",
                entry_type: "STANDARD",
                posting_date: "2026-01-15",
                reference: "INV-001",
                notes: "Sales Invoice Revenue Posting",
                status: "POSTED",
                total_debit: "1500.00",
                total_credit: "1500.00",
                currency: "USD",
                lines: [
                  {
                    id: "jl-1",
                    account_id: "acc-1100",
                    account_code: "1100",
                    account_name: "Accounts Receivable",
                    description: "AR Debit",
                    debit: "1500.00",
                    credit: "0.00",
                  },
                  {
                    id: "jl-2",
                    account_id: "acc-4000",
                    account_code: "4000",
                    account_name: "SaaS Revenue",
                    description: "Revenue Credit",
                    debit: "0.00",
                    credit: "1500.00",
                  },
                ],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Customer Parties endpoints
      if (url.includes("/finance/parties/customers")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "pty-1",
                name: "Apex Global Corp",
                code: "CUST-001",
                email: "billing@apexglobal.com",
                tax_id: "US-998877",
                is_active: true,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Vendor Parties endpoints
      if (url.includes("/finance/parties/vendors")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "pty-2",
                name: "Cloud Hosting Providers Inc",
                code: "VEND-001",
                email: "accounts@cloudhost.com",
                tax_id: "US-112233",
                is_active: true,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Invoices endpoints
      if (url.includes("/finance/invoices")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "inv-1",
                invoice_number: "INV-2026-001",
                customer_id: "pty-1",
                customer_name: "Apex Global Corp",
                issue_date: "2026-01-10",
                due_date: "2026-02-10",
                currency: "USD",
                total_amount: "5000.00",
                amount_paid: "0.00",
                amount_due: "5000.00",
                status: "POSTED",
                lines: [],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Bills endpoints
      if (url.includes("/finance/bills")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "bill-1",
                bill_number: "BILL-2026-001",
                vendor_id: "pty-2",
                vendor_name: "Cloud Hosting Providers Inc",
                bill_date: "2026-01-12",
                due_date: "2026-02-12",
                currency: "USD",
                total_amount: "1200.00",
                amount_paid: "1200.00",
                amount_due: "0.00",
                status: "PAID",
                lines: [],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Payments endpoints
      if (url.includes("/finance/payments")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "pmt-1",
                payment_number: "PMT-2026-001",
                payment_type: "RECEIPT",
                payment_method: "BANK_TRANSFER",
                payment_date: "2026-01-15",
                amount: "5000.00",
                allocated_amount: "5000.00",
                unallocated_amount: "0.00",
                status: "POSTED",
                reference: "WIRE-9921",
                partner_name: "Apex Global Corp",
                allocations: [],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Bank Accounts endpoints
      if (url.includes("/finance/banks/accounts")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "bank-1",
                account_name: "Silicon Valley Operating Treasury",
                bank_name: "JPMorgan Chase",
                account_number: "CHASE-8899-001",
                routing_number: "021000021",
                currency: "USD",
                gl_account_id: "acc-1010",
                current_balance: "245000.50",
                is_active: true,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ items: [], total: 0 }),
      });
    });
  });

  it("renders Finance Overview dashboard with summary KPIs and metrics", async () => {
    renderWithProviders(<FinanceOverviewPage />);

    expect(screen.getByText("Finance & Accounting Operations")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Cash & Treasury Reserves")).toBeInTheDocument();
      expect(screen.getByText("Accounts Receivable (AR)")).toBeInTheDocument();
    });
  });

  it("renders Chart of Accounts with hierarchical category tabs and account listing", async () => {
    renderWithProviders(<ChartOfAccountsPage />);

    expect(screen.getByText("Chart of Accounts (COA)")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Operating Cash Account")).toBeInTheDocument();
      expect(screen.getByText("1010")).toBeInTheDocument();
      expect(screen.getByText("SaaS Revenue")).toBeInTheDocument();
    });
  });

  it("renders Fiscal Periods page with year and lock state indicators", async () => {
    renderWithProviders(<FiscalPeriodsPage />);

    expect(screen.getByText("Fiscal Years & Period Locking Controls")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/FY 2026/)).toBeInTheDocument();
      expect(screen.getByText("Jan 2026")).toBeInTheDocument();
      expect(screen.getByText("Feb 2026")).toBeInTheDocument();
    });
  });

  it("renders Journal Entries page with double-entry ledger listings", async () => {
    renderWithProviders(<JournalEntriesPage />);

    expect(screen.getByText("Double-Entry Journal Entries")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("JE-2026-0001")).toBeInTheDocument();
      expect(screen.getByText("Sales Invoice Revenue Posting")).toBeInTheDocument();
    });
  });

  it("renders Customer Invoices (AR) with status badges and actions", async () => {
    renderWithProviders(<InvoicesPage />);

    expect(screen.getByText("Sales Invoices (Accounts Receivable)")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("INV-2026-001")).toBeInTheDocument();
    });
  });

  it("renders Vendor Bills (AP) with payment status and actions", async () => {
    renderWithProviders(<BillsPage />);

    expect(screen.getByText("Vendor Bills (Accounts Payable)")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("BILL-2026-001")).toBeInTheDocument();
    });
  });

  it("renders Payments & Allocations page with inbound/outbound records", async () => {
    renderWithProviders(<PaymentsPage />);

    expect(screen.getByText("Payments & Document Allocations")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("PMT-2026-001")).toBeInTheDocument();
      expect(screen.getByText("BANK_TRANSFER")).toBeInTheDocument();
    });
  });

  it("renders Bank & Cash Accounts with balance trackers", async () => {
    renderWithProviders(<BankAccountsPage />);

    expect(screen.getByText("Bank & Treasury Accounts")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Silicon Valley Operating Treasury")).toBeInTheDocument();
      expect(screen.getByText("JPMorgan Chase")).toBeInTheDocument();
    });
  });

  it("renders Financial Reports with Trial Balance, Balance Sheet, and P&L tabs", async () => {
    renderWithProviders(<FinancialReportsPage />);

    expect(screen.getByText("Financial Statements & GAAP Reporting")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Operating Cash Account")).toBeInTheDocument();
      expect(screen.getByText("Total Ledger Activity")).toBeInTheDocument();
    });

    // Switch to Balance Sheet tab
    const balanceSheetTab = screen.getByRole("button", { name: /Balance Sheet/i });
    fireEvent.click(balanceSheetTab);

    await waitFor(() => {
      expect(screen.getByText("ASSETS")).toBeInTheDocument();
      expect(screen.getByText("LIABILITIES & EQUITY")).toBeInTheDocument();
    });

    // Switch to Profit & Loss tab
    const pnlTab = screen.getByRole("button", { name: /Profit & Loss/i });
    fireEvent.click(pnlTab);

    await waitFor(() => {
      expect(screen.getByText("Operating Revenues")).toBeInTheDocument();
      expect(screen.getByText("Operating Expenses")).toBeInTheDocument();
    });
  });
});
