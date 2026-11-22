import { apiClient } from "@/lib/api-client";
import {
  Account,
  BankAccount,
  BankTransaction,
  BalanceSheetResponse,
  Bill,
  CustomerParty,
  FiscalPeriod,
  FiscalYear,
  Invoice,
  JournalEntry,
  Payment,
  ProfitLossResponse,
  TrialBalanceResponse,
  VendorParty,
} from "../types";

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export const financeApi = {
  // Chart of Accounts
  getAccounts: (params?: { account_type?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.account_type) q.set("account_type", params.account_type);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<Account>>(`/finance/accounts/?${q.toString()}`);
  },
  createAccount: (data: Partial<Account>) =>
    apiClient<Account>("/finance/accounts/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getAccount: (id: string) => apiClient<Account>(`/finance/accounts/${id}`),

  // Fiscal Years & Periods
  getFiscalYears: () => apiClient<PaginatedResponse<FiscalYear>>("/finance/fiscal/years"),
  createFiscalYear: (data: Partial<FiscalYear>) =>
    apiClient<FiscalYear>("/finance/fiscal/years", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getFiscalPeriods: (params?: { fiscal_year_id?: string }) => {
    const q = new URLSearchParams();
    if (params?.fiscal_year_id) q.set("fiscal_year_id", params.fiscal_year_id);
    return apiClient<PaginatedResponse<FiscalPeriod>>(`/finance/fiscal/periods?${q.toString()}`);
  },
  createFiscalPeriod: (data: Partial<FiscalPeriod>) =>
    apiClient<FiscalPeriod>("/finance/fiscal/periods", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  lockFiscalPeriod: (periodId: string) =>
    apiClient<FiscalPeriod>(`/finance/fiscal/periods/${periodId}/lock`, {
      method: "POST",
    }),
  unlockFiscalPeriod: (periodId: string) =>
    apiClient<FiscalPeriod>(`/finance/fiscal/periods/${periodId}/unlock`, {
      method: "POST",
    }),

  // Customers & Vendors
  getCustomers: () => apiClient<PaginatedResponse<CustomerParty>>("/finance/parties/customers"),
  createCustomer: (data: Partial<CustomerParty>) =>
    apiClient<CustomerParty>("/finance/parties/customers", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getVendors: () => apiClient<PaginatedResponse<VendorParty>>("/finance/parties/vendors"),
  createVendor: (data: Partial<VendorParty>) =>
    apiClient<VendorParty>("/finance/parties/vendors", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Double-Entry Journals
  getJournalEntries: (params?: { status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<JournalEntry>>(`/finance/journals/?${q.toString()}`);
  },
  createJournalEntry: (data: Partial<JournalEntry>) =>
    apiClient<JournalEntry>("/finance/journals/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  postJournalEntry: (id: string) =>
    apiClient<JournalEntry>(`/finance/journals/${id}/post`, {
      method: "POST",
    }),
  reverseJournalEntry: (id: string, notes?: string) =>
    apiClient<JournalEntry>(`/finance/journals/${id}/reverse`, {
      method: "POST",
      body: JSON.stringify({ notes }),
    }),

  // Invoices (AR)
  getInvoices: (params?: { status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<Invoice>>(`/finance/invoices/?${q.toString()}`);
  },
  createInvoice: (data: Partial<Invoice>) =>
    apiClient<Invoice>("/finance/invoices/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  postInvoice: (id: string) =>
    apiClient<Invoice>(`/finance/invoices/${id}/post`, {
      method: "POST",
    }),

  // Vendor Bills (AP)
  getBills: (params?: { status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<Bill>>(`/finance/bills/?${q.toString()}`);
  },
  createBill: (data: Partial<Bill>) =>
    apiClient<Bill>("/finance/bills/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  postBill: (id: string) =>
    apiClient<Bill>(`/finance/bills/${id}/post`, {
      method: "POST",
    }),

  // Payments
  getPayments: (params?: { payment_type?: string; status?: string; page?: number; page_size?: number }) => {
    const q = new URLSearchParams();
    if (params?.payment_type) q.set("payment_type", params.payment_type);
    if (params?.status) q.set("status", params.status);
    if (params?.page) q.set("page", params.page.toString());
    if (params?.page_size) q.set("page_size", params.page_size.toString());
    return apiClient<PaginatedResponse<Payment>>(`/finance/payments/?${q.toString()}`);
  },
  createPayment: (data: Partial<Payment>) =>
    apiClient<Payment>("/finance/payments/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  postPayment: (id: string) =>
    apiClient<Payment>(`/finance/payments/${id}/post`, {
      method: "POST",
    }),

  // Bank Accounts & Transactions
  getBankAccounts: () => apiClient<PaginatedResponse<BankAccount>>("/finance/banks/accounts"),
  createBankAccount: (data: Partial<BankAccount>) =>
    apiClient<BankAccount>("/finance/banks/accounts", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getBankTransactions: (accountId: string) =>
    apiClient<PaginatedResponse<BankTransaction>>(`/finance/banks/accounts/${accountId}/transactions`),

  // Financial Reports
  getTrialBalance: (asOfDate?: string) => {
    const q = new URLSearchParams();
    if (asOfDate) q.set("as_of_date", asOfDate);
    return apiClient<TrialBalanceResponse>(`/finance/reports/trial-balance?${q.toString()}`);
  },
  getBalanceSheet: (asOfDate?: string) => {
    const q = new URLSearchParams();
    if (asOfDate) q.set("as_of_date", asOfDate);
    return apiClient<BalanceSheetResponse>(`/finance/reports/balance-sheet?${q.toString()}`);
  },
  getProfitLoss: (startDate?: string, endDate?: string) => {
    const q = new URLSearchParams();
    if (startDate) q.set("start_date", startDate);
    if (endDate) q.set("end_date", endDate);
    return apiClient<ProfitLossResponse>(`/finance/reports/profit-loss?${q.toString()}`);
  },
};
