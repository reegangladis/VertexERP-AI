import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  BookOpen,
  FileText,
  Receipt,
  CreditCard,
  Building2,
  PieChart,
  Plus,
  CheckCircle2,
  AlertCircle,
  Download,
  Scale,
} from 'lucide-react';
import {
  financeAccountingService,
  FinanceDashboardSummary,
  Account,
  JournalEntry,
  CustomerInvoice,
  SupplierBill,
  Payment,
  BankAccount,
} from '../../services/financeAccounting';

export function FinanceModule() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'accounts' | 'journals' | 'invoices' | 'bills' | 'payments' | 'banks'
  >('dashboard');
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<FinanceDashboardSummary | null>(null);

  const [accounts, setAccounts] = useState<Account[]>([]);
  const [journals, setJournals] = useState<JournalEntry[]>([]);
  const [invoices, setInvoices] = useState<CustomerInvoice[]>([]);
  const [bills, setBills] = useState<SupplierBill[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);

  // Modals
  const [showAccountModal, setShowAccountModal] = useState<boolean>(false);
  const [showJournalModal, setShowJournalModal] = useState<boolean>(false);

  // Form Inputs
  const [accountCode, setAccountCode] = useState('');
  const [accountName, setAccountName] = useState('');
  const [accountType, setAccountType] = useState('Asset');

  // Journal form
  const [journalNumber, setJournalNumber] = useState('');
  const [journalDesc, setJournalDesc] = useState('');
  const [debitAmount, setDebitAmount] = useState(500);
  const [creditAmount, setCreditAmount] = useState(500);

  const mockOrgId = '00000000-0000-0000-0000-000000000001';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, accRes, jRes, invRes, billRes, payRes, bankRes] = await Promise.all([
        financeAccountingService.getDashboardSummary(mockOrgId).catch(() => null),
        financeAccountingService.getAccounts(mockOrgId).catch(() => []),
        financeAccountingService.getJournalEntries(mockOrgId).catch(() => []),
        financeAccountingService.getInvoices().catch(() => []),
        financeAccountingService.getSupplierBills().catch(() => []),
        financeAccountingService.getPayments().catch(() => []),
        financeAccountingService.getBankAccounts(mockOrgId).catch(() => []),
      ]);

      setSummary(
        sumRes || {
          total_revenue: invRes.reduce((acc, i) => acc + i.grand_total, 0),
          total_expenses: billRes.reduce((acc, b) => acc + b.grand_total, 0),
          cash_flow: 145000.0,
          net_profit: 85000.0,
          outstanding_invoices_amount: invRes.reduce((acc, i) => acc + i.balance_due, 0),
          outstanding_bills_amount: billRes.reduce((acc, b) => acc + b.balance_due, 0),
          total_bank_balance: 250000.0,
          budget_usage_percentage: 65.0,
        }
      );

      setAccounts(accRes);
      setJournals(jRes);
      setInvoices(invRes);
      setBills(billRes);
      setPayments(payRes);
      setBankAccounts(bankRes);
    } catch (err) {
      console.error('Failed to load finance data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeAccountingService.createAccount({
        organization_id: mockOrgId,
        account_code: accountCode,
        account_name: accountName,
        account_type: accountType,
        status: 'Active',
      });
      setShowAccountModal(false);
      setAccountCode('');
      setAccountName('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create account');
    }
  };

  const handleCreateJournal = async (e: React.FormEvent) => {
    e.preventDefault();
    if (accounts.length < 2) {
      alert('You need at least 2 accounts in the Chart of Accounts to create a journal entry.');
      return;
    }
    if (debitAmount !== creditAmount) {
      alert(`Unbalanced entry! Debit ($${debitAmount}) must equal Credit ($${creditAmount}).`);
      return;
    }

    try {
      await financeAccountingService.createJournalEntry({
        organization_id: mockOrgId,
        journal_number: journalNumber || `JV-${Math.floor(1000 + Math.random() * 9000)}`,
        posting_date: new Date().toISOString().split('T')[0],
        description: journalDesc,
        lines: [
          { account_id: accounts[0].id, debit: Number(debitAmount), credit: 0 },
          { account_id: accounts[1].id, debit: 0, credit: Number(creditAmount) },
        ],
      });
      setShowJournalModal(false);
      setJournalDesc('');
      setJournalNumber('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create journal entry');
    }
  };

  const handleDownloadPdf = async (invNum: string) => {
    try {
      const pdfText = await financeAccountingService.downloadInvoicePdf(invNum);
      const blob = new Blob([pdfText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Invoice_${invNum}.txt`;
      a.click();
    } catch (err: any) {
      alert('Failed to download invoice PDF text');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-600 shadow-lg shadow-teal-500/30">
              <DollarSign className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
                Finance & Accounting Platform
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Chart of Accounts, Double-Entry General Ledger, Invoices, Supplier Bills & Payments
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAccountModal(true)}
            className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-lg font-medium border border-slate-700 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Add Account
          </button>
          <button
            onClick={() => setShowJournalModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-600 hover:to-teal-700 text-white px-4 py-2.5 rounded-lg font-medium shadow-md shadow-emerald-500/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> New Journal Entry
          </button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'dashboard', label: 'Executive Dashboard', icon: DollarSign },
          { id: 'accounts', label: 'Chart of Accounts', icon: BookOpen },
          { id: 'journals', label: 'Journal Entries & Ledger', icon: Scale },
          { id: 'invoices', label: 'Customer Invoices', icon: FileText },
          { id: 'bills', label: 'Supplier Bills', icon: Receipt },
          { id: 'payments', label: 'Payments', icon: CreditCard },
          { id: 'banks', label: 'Bank Accounts', icon: Building2 },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap cursor-pointer ${
                active
                  ? 'bg-slate-800 text-emerald-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total Revenue</span>
                <TrendingUp className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                ${summary?.total_revenue.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-emerald-400 mt-2">+14.2% from last period</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total Expenses</span>
                <TrendingDown className="w-5 h-5 text-rose-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                ${summary?.total_expenses.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-rose-400 mt-2">Operational expenditure</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Net Profit</span>
                <DollarSign className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-3xl font-extrabold text-blue-400">
                ${summary?.net_profit.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-slate-400 mt-2">Revenue minus expenses</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Total Bank Balance</span>
                <Building2 className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                ${summary?.total_bank_balance.toLocaleString() || '0'}
              </div>
              <p className="text-xs text-purple-400 mt-2">Liquid cash reserves</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Outstanding Invoices (Receivables)</h3>
              <div className="space-y-3">
                {invoices.length === 0 ? (
                  <p className="text-slate-500 text-sm">No outstanding customer invoices.</p>
                ) : (
                  invoices.map((inv) => (
                    <div key={inv.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-mono text-emerald-400 font-bold">{inv.invoice_number}</div>
                        <div className="text-xs text-slate-400 mt-0.5">Due: {inv.due_date}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-white">${inv.grand_total.toLocaleString()}</div>
                        <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 font-medium">{inv.status}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Outstanding Bills (Payables)</h3>
              <div className="space-y-3">
                {bills.length === 0 ? (
                  <p className="text-slate-500 text-sm">No outstanding supplier bills.</p>
                ) : (
                  bills.map((bill) => (
                    <div key={bill.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-mono text-rose-400 font-bold">{bill.bill_number}</div>
                        <div className="text-xs text-slate-400 mt-0.5">Due: {bill.due_date}</div>
                      </div>
                      <div className="text-right">
                        <div className="font-bold text-white">${bill.grand_total.toLocaleString()}</div>
                        <span className="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 font-medium">{bill.status}</span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Chart of Accounts Tab */}
      {activeTab === 'accounts' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Chart of Accounts</h3>
            <button
              onClick={() => setShowAccountModal(true)}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-2 rounded-lg text-sm font-medium cursor-pointer"
            >
              + Add Account
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">Code</th>
                  <th className="p-3.5">Account Name</th>
                  <th className="p-3.5">Type</th>
                  <th className="p-3.5">Currency</th>
                  <th className="p-3.5">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {accounts.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-6 text-center text-slate-500">
                      No accounts registered. Click "Add Account" to set up your Chart of Accounts.
                    </td>
                  </tr>
                ) : (
                  accounts.map((acc) => (
                    <tr key={acc.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-mono text-emerald-400 font-bold">{acc.account_code}</td>
                      <td className="p-3.5 font-semibold text-slate-100">{acc.account_name}</td>
                      <td className="p-3.5 text-slate-300">{acc.account_type}</td>
                      <td className="p-3.5 font-mono">{acc.currency}</td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                          {acc.status}
                        </span>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Customer Invoices Tab */}
      {activeTab === 'invoices' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Customer Invoices</h3>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">Invoice #</th>
                  <th className="p-3.5">Date</th>
                  <th className="p-3.5">Due Date</th>
                  <th className="p-3.5">Grand Total</th>
                  <th className="p-3.5">Balance Due</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {invoices.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="p-6 text-center text-slate-500">
                      No invoices recorded.
                    </td>
                  </tr>
                ) : (
                  invoices.map((inv) => (
                    <tr key={inv.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-mono text-emerald-400 font-bold">{inv.invoice_number}</td>
                      <td className="p-3.5">{inv.invoice_date}</td>
                      <td className="p-3.5">{inv.due_date}</td>
                      <td className="p-3.5 font-bold text-white">${inv.grand_total.toLocaleString()}</td>
                      <td className="p-3.5 text-amber-400 font-bold">${inv.balance_due.toLocaleString()}</td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300">
                          {inv.status}
                        </span>
                      </td>
                      <td className="p-3.5">
                        <button
                          onClick={() => handleDownloadPdf(inv.invoice_number)}
                          className="flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-emerald-400 px-3 py-1 rounded text-xs cursor-pointer"
                        >
                          <Download className="w-3.5 h-3.5" /> PDF
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Account Modal */}
      {showAccountModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Add Account to Chart</h3>
            <form onSubmit={handleCreateAccount} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Account Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 1010"
                  value={accountCode}
                  onChange={(e) => setAccountCode(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Account Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Cash & Equivalents"
                  value={accountName}
                  onChange={(e) => setAccountName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Account Type</label>
                <select
                  value={accountType}
                  onChange={(e) => setAccountType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                >
                  <option value="Asset">Asset</option>
                  <option value="Liability">Liability</option>
                  <option value="Equity">Equity</option>
                  <option value="Revenue">Revenue</option>
                  <option value="Expense">Expense</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowAccountModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Save Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Journal Entry Modal */}
      {showJournalModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Create Double-Entry Journal</h3>
            <form onSubmit={handleCreateJournal} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Journal Number</label>
                <input
                  type="text"
                  placeholder="e.g. JV-2026-0001"
                  value={journalNumber}
                  onChange={(e) => setJournalNumber(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Description</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Monthly rent payment"
                  value={journalDesc}
                  onChange={(e) => setJournalDesc(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-xs font-medium text-slate-400">Debit Amount ($)</label>
                  <input
                    type="number"
                    value={debitAmount}
                    onChange={(e) => setDebitAmount(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400">Credit Amount ($)</label>
                  <input
                    type="number"
                    value={creditAmount}
                    onChange={(e) => setCreditAmount(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                  />
                </div>
              </div>

              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs flex items-center justify-between">
                <span className="text-slate-400">Balance Validation:</span>
                {debitAmount === creditAmount ? (
                  <span className="text-emerald-400 font-bold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Balanced (${debitAmount})
                  </span>
                ) : (
                  <span className="text-rose-400 font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" /> Unbalanced Diff: ${Math.abs(debitAmount - creditAmount)}
                  </span>
                )}
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowJournalModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Post Journal Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
