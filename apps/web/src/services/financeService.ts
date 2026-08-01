import { apiClient } from './apiClient';

export interface Account {
  id: string;
  organization_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  account_subtype?: string;
  parent_id?: string;
  currency: string;
  balance: number;
  opening_balance: number;
  is_active: boolean;
  is_system: boolean;
}

export interface JournalEntryLine {
  id?: string;
  account_id: string;
  debit: number;
  credit: number;
  description?: string;
}

export interface JournalEntry {
  id: string;
  organization_id: string;
  entry_number: string;
  entry_date: string;
  reference?: string;
  narration?: string;
  status: string;
  source_type: string;
  lines: JournalEntryLine[];
  created_at: string;
}

export interface CustomerInvoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  issue_date: string;
  due_date: string;
  subtotal: number;
  tax_total: number;
  total_amount: number;
  paid_amount: number;
  status: string;
  notes?: string;
  created_at: string;
}

export interface SupplierBill {
  id: string;
  bill_number: string;
  supplier_id: string;
  bill_date: string;
  due_date: string;
  subtotal: number;
  tax_total: number;
  total_amount: number;
  paid_amount: number;
  status: string;
  notes?: string;
  created_at: string;
}

export interface Payment {
  id: string;
  payment_number: string;
  payment_type: string;
  amount: number;
  payment_date: string;
  payment_method: string;
  reference?: string;
  status: string;
}

export interface BankAccount {
  id: string;
  account_name: string;
  bank_name: string;
  account_number: string;
  swift_code?: string;
  currency: string;
  current_balance: number;
}

export interface ExpenseCategory {
  id: string;
  name: string;
  code: string;
  is_active: boolean;
}

export interface ExpenseClaim {
  id: string;
  claim_number: string;
  employee_id: string;
  category_id: string;
  claim_date: string;
  amount: number;
  description: string;
  receipt_url?: string;
  status: string;
}

export interface Budget {
  id: string;
  name: string;
  fiscal_year: number;
  total_budgeted: number;
  status: string;
}

export interface TaxProfile {
  id: string;
  name: string;
  country: string;
  is_default: boolean;
}

export interface FixedAsset {
  id: string;
  asset_number: string;
  asset_name: string;
  purchase_date: string;
  purchase_cost: number;
  salvage_value: number;
  current_value: number;
  status: string;
}

export const financeService = {
  // Chart of Accounts
  getAccounts: async () => {
    const res = await apiClient.get('/api/v1/finance/accounts');
    return res.data.data as Account[];
  },
  createAccount: async (data: Partial<Account>) => {
    const res = await apiClient.post('/api/v1/finance/accounts', data);
    return res.data.data as Account;
  },

  // Journal Entries
  getJournalEntries: async () => {
    const res = await apiClient.get('/api/v1/finance/journal-entries');
    return res.data.data as JournalEntry[];
  },
  createJournalEntry: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/journal-entries', data);
    return res.data.data as JournalEntry;
  },
  postJournalEntry: async (id: string) => {
    const res = await apiClient.post(`/api/v1/finance/journal-entries/${id}/post`);
    return res.data.data as JournalEntry;
  },
  reverseJournalEntry: async (id: string) => {
    const res = await apiClient.post(`/api/v1/finance/journal-entries/${id}/reverse`);
    return res.data.data as JournalEntry;
  },

  // Invoices (AR)
  getInvoices: async () => {
    const res = await apiClient.get('/api/v1/finance/invoices');
    return res.data.data as CustomerInvoice[];
  },
  createInvoice: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/invoices', data);
    return res.data.data as CustomerInvoice;
  },

  // Bills (AP)
  getBills: async () => {
    const res = await apiClient.get('/api/v1/finance/bills');
    return res.data.data as SupplierBill[];
  },
  createBill: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/bills', data);
    return res.data.data as SupplierBill;
  },

  // Payments
  getPayments: async () => {
    const res = await apiClient.get('/api/v1/finance/payments');
    return res.data.data as Payment[];
  },
  createPayment: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/payments', data);
    return res.data.data as Payment;
  },

  // Banking
  getBankAccounts: async () => {
    const res = await apiClient.get('/api/v1/finance/bank-accounts');
    return res.data.data as BankAccount[];
  },
  createBankAccount: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/bank-accounts', data);
    return res.data.data as BankAccount;
  },
  reconcileBank: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/reconciliations', data);
    return res.data.data;
  },

  // Expenses
  getExpenseCategories: async () => {
    const res = await apiClient.get('/api/v1/finance/expense-categories');
    return res.data.data as ExpenseCategory[];
  },
  getExpenseClaims: async () => {
    const res = await apiClient.get('/api/v1/finance/expense-claims');
    return res.data.data as ExpenseClaim[];
  },
  createExpenseClaim: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/expense-claims', data);
    return res.data.data as ExpenseClaim;
  },
  approveExpenseClaim: async (id: string) => {
    const res = await apiClient.post(`/api/v1/finance/expense-claims/${id}/approve`);
    return res.data.data as ExpenseClaim;
  },
  reimburseExpenseClaim: async (id: string) => {
    const res = await apiClient.post(`/api/v1/finance/expense-claims/${id}/reimburse`);
    return res.data.data as ExpenseClaim;
  },

  // Budgets
  getBudgets: async () => {
    const res = await apiClient.get('/api/v1/finance/budgets');
    return res.data.data as Budget[];
  },
  createBudget: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/budgets', data);
    return res.data.data as Budget;
  },

  // Taxes
  getTaxProfiles: async () => {
    const res = await apiClient.get('/api/v1/finance/tax-profiles');
    return res.data.data as TaxProfile[];
  },
  createTaxProfile: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/tax-profiles', data);
    return res.data.data as TaxProfile;
  },

  // Account Deletion
  deleteAccount: async (id: string) => {
    const res = await apiClient.delete(`/api/v1/finance/accounts/${id}`);
    return res.data.data;
  },

  // Credit Notes & Debit Notes
  getCreditNotes: async () => {
    const res = await apiClient.get('/api/v1/finance/credit-notes');
    return res.data.data;
  },
  createCreditNote: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/credit-notes', data);
    return res.data.data;
  },
  getDebitNotes: async () => {
    const res = await apiClient.get('/api/v1/finance/debit-notes');
    return res.data.data;
  },
  createDebitNote: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/debit-notes', data);
    return res.data.data;
  },

  // Bank Transactions
  getBankTransactions: async (bankAccountId: string) => {
    const res = await apiClient.get(`/api/v1/finance/bank-accounts/${bankAccountId}/transactions`);
    return res.data.data;
  },

  // Dashboard Summary
  getDashboardSummary: async () => {
    const res = await apiClient.get('/api/v1/finance/dashboard/summary');
    return res.data.data;
  },

  // Fixed Assets
  getAssetCategories: async () => {
    const res = await apiClient.get('/api/v1/finance/asset-categories');
    return res.data.data as any[];
  },
  getFixedAssets: async () => {
    const res = await apiClient.get('/api/v1/finance/fixed-assets');
    return res.data.data as FixedAsset[];
  },
  createFixedAsset: async (data: any) => {
    const res = await apiClient.post('/api/v1/finance/fixed-assets', data);
    return res.data.data as FixedAsset;
  },
  disposeFixedAsset: async (id: string, disposalAmount: number) => {
    const res = await apiClient.post(`/api/v1/finance/fixed-assets/${id}/dispose?disposal_amount=${disposalAmount}`);
    return res.data.data as FixedAsset;
  },

  // Financial Reports
  getTrialBalance: async (asOf?: string) => {
    const query = asOf ? `?as_of=${asOf}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/trial-balance${query}`);
    return res.data.data;
  },
  getBalanceSheet: async (asOf?: string) => {
    const query = asOf ? `?as_of=${asOf}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/balance-sheet${query}`);
    return res.data.data;
  },
  getProfitLoss: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/profit-loss${query}`);
    return res.data.data;
  },
  getCashFlow: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/cash-flow${query}`);
    return res.data.data;
  },
  getAgingReport: async (type: 'RECEIVABLE' | 'PAYABLE' = 'RECEIVABLE') => {
    const res = await apiClient.get(`/api/v1/finance/reports/aging?report_type=${type}`);
    return res.data.data;
  },
  getGeneralLedgerReport: async (accountId: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ account_id: accountId });
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await apiClient.get(`/api/v1/finance/reports/general-ledger?${params.toString()}`);
    return res.data.data;
  },
  getTaxReport: async (asOf?: string) => {
    const query = asOf ? `?as_of=${asOf}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/tax${query}`);
    return res.data.data;
  },
  getExpenseReport: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/expense${query}`);
    return res.data.data;
  },
  getRevenueReport: async (startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const query = params.toString() ? `?${params.toString()}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/revenue${query}`);
    return res.data.data;
  },
  getBudgetReport: async (fiscalYear?: number) => {
    const query = fiscalYear ? `?fiscal_year=${fiscalYear}` : '';
    const res = await apiClient.get(`/api/v1/finance/reports/budget${query}`);
    return res.data.data;
  },
  searchFinance: async (query: string) => {
    const res = await apiClient.get(`/api/v1/finance/search?q=${encodeURIComponent(query)}`);
    return res.data.data;
  },
};

