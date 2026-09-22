import React, { useEffect, useState } from "react";
import {
  Building2,
  Plus,
  Search,
  CheckCircle2,
  AlertCircle,
  History,
  CreditCard,
  DollarSign,
  ArrowUpRight,
  ArrowDownLeft,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { Account, BankAccount, BankTransaction } from "../types";

export const BankAccountsPage: React.FC = () => {
  const [bankAccounts, setBankAccounts] = useState<BankAccount[]>([]);
  const [glAccounts, setGlAccounts] = useState<Account[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [transactions, setTransactions] = useState<BankTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingTx, setLoadingTx] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    account_name: "",
    account_number: "",
    bank_name: "",
    currency: "USD",
    gl_account_id: "",
  });

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const [bankRes, glRes] = await Promise.all([
        financeApi.getBankAccounts(),
        financeApi.getAccounts({ account_type: "ASSET", page: 1, page_size: 100 }),
      ]);
      const accounts = bankRes.items || [];
      setBankAccounts(accounts);
      setGlAccounts(glRes.items || []);
      if (accounts.length > 0 && !selectedAccountId) {
        setSelectedAccountId(accounts[0].id);
      }
    } catch (err: any) {
      setErrorMsg("Failed to load bank accounts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  useEffect(() => {
    if (!selectedAccountId) return;
    async function loadTx() {
      try {
        setLoadingTx(true);
        const res = await financeApi.getBankTransactions(selectedAccountId!);
        setTransactions(res.items || []);
      } catch (err: any) {
        // Transactions optional or empty
        setTransactions([]);
      } finally {
        setLoadingTx(false);
      }
    }
    loadTx();
  }, [selectedAccountId]);

  const handleCreateAccount = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.gl_account_id) {
      setErrorMsg("Please select a General Ledger account.");
      return;
    }
    setErrorMsg(null);
    try {
      await financeApi.createBankAccount(formData);
      setShowModal(false);
      setFormData({
        account_name: "",
        account_number: "",
        bank_name: "",
        currency: "USD",
        gl_account_id: "",
      });
      loadAccounts();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create bank account.");
    }
  };

  const selectedAccount = bankAccounts.find((a) => a.id === selectedAccountId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-teal-500/20 border border-teal-500/30 text-teal-400">
              <Building2 className="w-6 h-6" />
            </span>
            Bank & Treasury Accounts
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Cash management, treasury registers, and bank transaction ledgers.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold transition shadow-lg shadow-teal-600/20"
        >
          <Plus className="w-4 h-4" />
          Add Bank Account
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* Account Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-3 text-center py-8 text-slate-500">Loading bank accounts...</div>
        ) : bankAccounts.length === 0 ? (
          <div className="col-span-3 text-center py-8 text-slate-500">No bank accounts registered.</div>
        ) : (
          bankAccounts.map((account) => (
            <div
              key={account.id}
              onClick={() => setSelectedAccountId(account.id)}
              className={`p-5 rounded-2xl border cursor-pointer transition relative overflow-hidden ${
                selectedAccountId === account.id
                  ? "bg-slate-900 border-teal-500/50 shadow-lg shadow-teal-500/10 ring-1 ring-teal-500/30"
                  : "bg-slate-900/60 border-slate-800 hover:border-slate-700"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-teal-400 uppercase tracking-wider">
                  {account.bank_name}
                </span>
                <span className="p-1.5 rounded-lg bg-slate-800 border border-slate-700">
                  <CreditCard className="w-4 h-4 text-slate-300" />
                </span>
              </div>
              <h3 className="text-base font-bold text-white mb-1">{account.account_name}</h3>
              <p className="text-xs text-slate-400 font-mono mb-4">{account.account_number}</p>
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-400">Ledger Balance</span>
                <span className="text-lg font-extrabold text-white font-mono">
                  ${Number(account.current_balance).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Account Transactions Ledger */}
      {selectedAccount && (
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-white flex items-center gap-2">
                <History className="w-4 h-4 text-teal-400" />
                Transaction Ledger &bull; {selectedAccount.account_name}
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Bank transaction feed and clearing records for {selectedAccount.account_number}
              </p>
            </div>
          </div>

          <div className="rounded-xl bg-slate-800/40 border border-slate-800/80 overflow-hidden">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/60 text-slate-400 font-medium border-b border-slate-800/80 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3">Type</th>
                  <th className="px-5 py-3">Description / Ref</th>
                  <th className="px-5 py-3 text-right">Amount</th>
                  <th className="px-5 py-3 text-right">Running Balance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-slate-300">
                {loadingTx ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-8 text-center text-slate-500">
                      Loading transactions...
                    </td>
                  </tr>
                ) : transactions.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-8 text-center text-slate-500">
                      No transactions recorded for this account.
                    </td>
                  </tr>
                ) : (
                  transactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-slate-800/20">
                      <td className="px-5 py-3 font-mono text-xs text-slate-400">{tx.transaction_date}</td>
                      <td className="px-5 py-3">
                        <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                          {tx.transaction_type}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-xs text-white">
                        {tx.description || tx.reference || "Bank Transaction"}
                      </td>
                      <td
                        className={`px-5 py-3 font-mono text-xs text-right font-semibold ${
                          Number(tx.amount) >= 0 ? "text-emerald-400" : "text-rose-400"
                        }`}
                      >
                        {Number(tx.amount) >= 0 ? "+" : ""}${Number(tx.amount).toFixed(2)}
                      </td>
                      <td className="px-5 py-3 font-mono text-xs text-right text-white">
                        ${Number(tx.balance_after).toFixed(2)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Add Bank Account Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-teal-400" />
              Register Bank Account
            </h3>

            <form onSubmit={handleCreateAccount} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Bank Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. JPMorgan Chase"
                  value={formData.bank_name}
                  onChange={(e) => setFormData({ ...formData, bank_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Account Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Primary Operating Account"
                  value={formData.account_name}
                  onChange={(e) => setFormData({ ...formData, account_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Account Number / IBAN</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. US99-8821-4401"
                  value={formData.account_number}
                  onChange={(e) => setFormData({ ...formData, account_number: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Linked General Ledger Account</label>
                <select
                  required
                  value={formData.gl_account_id}
                  onChange={(e) => setFormData({ ...formData, gl_account_id: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-teal-500"
                >
                  <option value="">Select Cash / Bank GL Account...</option>
                  {glAccounts.map((a) => (
                    <option key={a.id} value={a.id}>
                      {a.code} - {a.name}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-sm font-semibold transition"
                >
                  Save Bank Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
