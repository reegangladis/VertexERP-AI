export type AccountType = "ASSET" | "LIABILITY" | "EQUITY" | "REVENUE" | "EXPENSE";

export type AccountCategory =
  | "CURRENT_ASSET"
  | "NON_CURRENT_ASSET"
  | "CURRENT_LIABILITY"
  | "NON_CURRENT_LIABILITY"
  | "EQUITY"
  | "OPERATING_REVENUE"
  | "NON_OPERATING_REVENUE"
  | "OPERATING_EXPENSE"
  | "COST_OF_GOODS_SOLD"
  | "TAX_EXPENSE";

export interface Account {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  account_type: AccountType;
  account_category: AccountCategory;
  parent_account_id?: string | null;
  currency: string;
  is_reconciled: boolean;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface FiscalYear {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  start_date: string;
  end_date: string;
  is_closed: boolean;
  version: number;
  periods?: FiscalPeriod[];
  created_at: string;
  updated_at: string;
}

export interface FiscalPeriod {
  id: string;
  tenant_id: string;
  organization_id: string;
  fiscal_year_id: string;
  period_number: number;
  period_name: string;
  start_date: string;
  end_date: string;
  is_locked: boolean;
  is_closed: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CustomerParty {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  tax_id?: string | null;
  email?: string | null;
  phone?: string | null;
  credit_limit: string;
  ar_account_id?: string | null;
  payment_terms_days: number;
  is_active: boolean;
  created_at: string;
}

export interface VendorParty {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  tax_id?: string | null;
  email?: string | null;
  phone?: string | null;
  ap_account_id?: string | null;
  payment_terms_days: number;
  is_active: boolean;
  created_at: string;
}

export interface JournalLine {
  id?: string;
  account_id: string;
  debit: string | number;
  credit: string | number;
  currency?: string;
  partner_type?: string | null;
  partner_id?: string | null;
  description?: string | null;
  cost_center_id?: string | null;
  line_number?: number;
}

export interface JournalEntry {
  id: string;
  tenant_id: string;
  organization_id: string;
  entry_number: string;
  entry_date: string;
  posting_date: string;
  fiscal_period_id?: string | null;
  entry_type: "STANDARD" | "REVERSAL" | "CLOSING" | "ADJUSTING";
  status: "DRAFT" | "POSTED" | "REVERSED" | "CANCELLED";
  reference_type?: string | null;
  reference_id?: string | null;
  currency: string;
  exchange_rate: string;
  total_debit: string;
  total_credit: string;
  notes?: string | null;
  lines: JournalLine[];
  created_at: string;
  updated_at: string;
}

export interface InvoiceLine {
  id?: string;
  description: string;
  account_id: string;
  quantity: string | number;
  unit_price: string | number;
  tax_rate?: string | number;
  tax_amount?: string | number;
  line_total?: string | number;
}

export interface Invoice {
  id: string;
  tenant_id: string;
  organization_id: string;
  invoice_number: string;
  customer_id: string;
  issue_date: string;
  due_date: string;
  currency: string;
  subtotal_amount: string;
  tax_amount: string;
  total_amount: string;
  amount_paid: string;
  amount_due: string;
  status: "DRAFT" | "POSTED" | "PARTIALLY_PAID" | "PAID" | "CANCELLED";
  ar_account_id?: string | null;
  posted_journal_entry_id?: string | null;
  notes?: string | null;
  lines: InvoiceLine[];
  created_at: string;
  updated_at: string;
}

export interface BillLine {
  id?: string;
  description: string;
  expense_account_id: string;
  quantity: string | number;
  unit_price: string | number;
  tax_rate?: string | number;
  tax_amount?: string | number;
  line_total?: string | number;
}

export interface Bill {
  id: string;
  tenant_id: string;
  organization_id: string;
  bill_number: string;
  vendor_id: string;
  vendor_invoice_ref?: string | null;
  bill_date: string;
  due_date: string;
  currency: string;
  subtotal_amount: string;
  tax_amount: string;
  total_amount: string;
  amount_paid: string;
  amount_due: string;
  status: "DRAFT" | "POSTED" | "PARTIALLY_PAID" | "PAID" | "CANCELLED";
  ap_account_id?: string | null;
  posted_journal_entry_id?: string | null;
  notes?: string | null;
  lines: BillLine[];
  created_at: string;
  updated_at: string;
}

export interface PaymentAllocation {
  id?: string;
  invoice_id?: string | null;
  bill_id?: string | null;
  allocated_amount: string | number;
}

export interface Payment {
  id: string;
  tenant_id: string;
  organization_id: string;
  payment_number: string;
  payment_type: "RECEIPT" | "DISBURSEMENT";
  partner_type: "CUSTOMER" | "VENDOR";
  partner_id: string;
  payment_date: string;
  payment_method: string;
  bank_account_id?: string | null;
  currency: string;
  amount: string;
  allocated_amount: string;
  unallocated_amount: string;
  status: "DRAFT" | "POSTED" | "CANCELLED";
  posted_journal_entry_id?: string | null;
  reference?: string | null;
  notes?: string | null;
  allocations: PaymentAllocation[];
  created_at: string;
  updated_at: string;
}

export interface BankAccount {
  id: string;
  tenant_id: string;
  organization_id: string;
  account_name: string;
  account_number: string;
  bank_name: string;
  currency: string;
  gl_account_id: string;
  current_balance: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface BankTransaction {
  id: string;
  tenant_id: string;
  organization_id: string;
  bank_account_id: string;
  transaction_date: string;
  value_date: string;
  transaction_type: string;
  amount: string;
  balance_after: string;
  reference?: string | null;
  description?: string | null;
  is_reconciled: boolean;
  created_at: string;
}

// Financial Reporting Types
export interface TrialBalanceLine {
  account_id: string;
  account_code: string;
  account_name: string;
  account_type: string;
  debit_total: string;
  credit_total: string;
  net_debit: string;
  net_credit: string;
}

export interface TrialBalanceResponse {
  as_of_date: string;
  lines: TrialBalanceLine[];
  total_debit: string;
  total_credit: string;
  is_balanced: boolean;
}

export interface BalanceSheetLine {
  account_id: string;
  account_code: string;
  account_name: string;
  account_category: string;
  balance: string;
}

export interface BalanceSheetCategorySection {
  category: string;
  lines: BalanceSheetLine[];
  subtotal: string;
}

export interface BalanceSheetResponse {
  as_of_date: string;
  assets: BalanceSheetCategorySection[];
  liabilities: BalanceSheetCategorySection[];
  equity: BalanceSheetCategorySection[];
  total_assets: string;
  total_liabilities: string;
  total_equity: string;
  total_liabilities_and_equity: string;
  is_balanced: boolean;
}

export interface ProfitLossLine {
  account_id: string;
  account_code: string;
  account_name: string;
  account_category: string;
  amount: string;
}

export interface ProfitLossResponse {
  start_date: string;
  end_date: string;
  revenues: ProfitLossLine[];
  expenses: ProfitLossLine[];
  total_revenue: string;
  total_expense: string;
  net_income: string;
}
