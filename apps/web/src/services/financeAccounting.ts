import { apiClient } from './apiClient';

export interface Account {
  id: string;
  organization_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  currency: string;
  is_control_account: boolean;
  status: string;
  created_at: string;
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
  journal_number: string;
  posting_date: string;
  reference?: string;
  description: string;
  status: string;
  created_at: string;
  lines: JournalEntryLine[];
}

export interface CustomerInvoiceItem {
  id?: string;
  item_description: string;
  quantity: number;
  unit_price: number;
  tax_amount: number;
  total_price?: number;
}

export interface CustomerInvoice {
  id: string;
  customer_id: string;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  subtotal: number;
  tax: number;
  discount: number;
  grand_total: number;
  paid_amount: number;
  balance_due: number;
  status: string;
  created_at: string;
  items: CustomerInvoiceItem[];
}

export interface SupplierBill {
  id: string;
  supplier_id: string;
  bill_number: string;
  bill_date: string;
  due_date: string;
  subtotal: number;
  tax: number;
  discount: number;
  grand_total: number;
  paid_amount: number;
  balance_due: number;
  status: string;
  created_at: string;
}

export interface Payment {
  id: string;
  payment_reference: string;
  payment_type: string;
  payment_method: string;
  amount: number;
  payment_date: string;
  status: string;
  created_at: string;
}

export interface BankAccount {
  id: string;
  organization_id: string;
  bank_name: string;
  account_holder: string;
  account_number: string;
  currency: string;
  status: string;
  created_at: string;
}

export interface FinanceDashboardSummary {
  total_revenue: number;
  total_expenses: number;
  cash_flow: number;
  net_profit: number;
  outstanding_invoices_amount: number;
  outstanding_bills_amount: number;
  total_bank_balance: number;
  budget_usage_percentage: number;
}

export const financeAccountingService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<FinanceDashboardSummary> => {
    const res = await apiClient.get('/api/v1/finance/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // Accounts
  getAccounts: async (orgId: string): Promise<Account[]> => {
    const res = await apiClient.get('/api/v1/finance/accounts', { params: { org_id: orgId } });
    return res.data;
  },

  createAccount: async (data: Partial<Account>): Promise<Account> => {
    const res = await apiClient.post('/api/v1/finance/accounts', data);
    return res.data;
  },

  // Journal Entries
  getJournalEntries: async (orgId: string): Promise<JournalEntry[]> => {
    const res = await apiClient.get('/api/v1/finance/journal-entries', { params: { org_id: orgId } });
    return res.data;
  },

  createJournalEntry: async (data: any): Promise<JournalEntry> => {
    const res = await apiClient.post('/api/v1/finance/journal-entries', data);
    return res.data;
  },

  postJournalEntry: async (id: string): Promise<JournalEntry> => {
    const res = await apiClient.post(`/api/v1/finance/journal-entries/${id}/post`);
    return res.data;
  },

  // Invoices
  getInvoices: async (): Promise<CustomerInvoice[]> => {
    const res = await apiClient.get('/api/v1/finance/invoices');
    return res.data;
  },

  createInvoice: async (data: any): Promise<CustomerInvoice> => {
    const res = await apiClient.post('/api/v1/finance/invoices', data);
    return res.data;
  },

  downloadInvoicePdf: async (invNumber: string): Promise<string> => {
    const res = await apiClient.get(`/api/v1/finance/invoices/${invNumber}/download-pdf`, {
      responseType: 'text',
    });
    return res.data;
  },

  // Supplier Bills
  getSupplierBills: async (): Promise<SupplierBill[]> => {
    const res = await apiClient.get('/api/v1/finance/supplier-bills');
    return res.data;
  },

  createSupplierBill: async (data: any): Promise<SupplierBill> => {
    const res = await apiClient.post('/api/v1/finance/supplier-bills', data);
    return res.data;
  },

  // Payments
  getPayments: async (): Promise<Payment[]> => {
    const res = await apiClient.get('/api/v1/finance/payments');
    return res.data;
  },

  processPayment: async (data: any): Promise<Payment> => {
    const res = await apiClient.post('/api/v1/finance/payments', data);
    return res.data;
  },

  // Bank Accounts
  getBankAccounts: async (orgId: string): Promise<BankAccount[]> => {
    const res = await apiClient.get('/api/v1/finance/bank-accounts', { params: { org_id: orgId } });
    return res.data;
  },

  createBankAccount: async (data: Partial<BankAccount>): Promise<BankAccount> => {
    const res = await apiClient.post('/api/v1/finance/bank-accounts', data);
    return res.data;
  },
};
