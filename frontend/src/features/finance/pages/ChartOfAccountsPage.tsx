import React, { useEffect, useState } from "react";
import {
  Layers,
  Plus,
  Search,
  CheckCircle2,
  FolderTree,
  Filter,
  DollarSign,
  AlertCircle,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { Account, AccountType, AccountCategory } from "../types";

export const ChartOfAccountsPage: React.FC = () => {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedType, setSelectedType] = useState<string>("ALL");
  const [showModal, setShowModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    code: "",
    name: "",
    account_type: "ASSET" as AccountType,
    account_category: "CURRENT_ASSET" as AccountCategory,
    currency: "USD",
  });

  const loadAccounts = async () => {
    try {
      setLoading(true);
      const res = await financeApi.getAccounts({ page: 1, page_size: 200 });
      setAccounts(res.items || []);
    } catch (err: any) {
      setErrorMsg("Failed to load chart of accounts.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAccounts();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    try {
      await financeApi.createAccount(formData);
      setShowModal(false);
      setFormData({
        code: "",
        name: "",
        account_type: "ASSET",
        account_category: "CURRENT_ASSET",
        currency: "USD",
      });
      loadAccounts();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create account.");
    }
  };

  const filteredAccounts = accounts.filter((acc) => {
    const matchesSearch =
      acc.code.toLowerCase().includes(search.toLowerCase()) ||
      acc.name.toLowerCase().includes(search.toLowerCase());
    const matchesType = selectedType === "ALL" || acc.account_type === selectedType;
    return matchesSearch && matchesType;
  });

  const typeColor = (type: AccountType) => {
    switch (type) {
      case "ASSET":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "LIABILITY":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      case "EQUITY":
        return "bg-purple-500/10 text-purple-400 border-purple-500/20";
      case "REVENUE":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20";
      case "EXPENSE":
        return "bg-amber-500/10 text-amber-400 border-amber-500/20";
      default:
        return "bg-slate-700 text-slate-300";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-emerald-600/20 border border-emerald-500/30 text-emerald-400">
              <Layers className="w-6 h-6" />
            </span>
            Chart of Accounts (COA)
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            General ledger master accounts categorized by Assets, Liabilities, Equity, Revenue, and Expenses.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition shadow-lg shadow-emerald-600/20"
        >
          <Plus className="w-4 h-4" />
          Add Ledger Account
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search account code or title..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {["ALL", "ASSET", "LIABILITY", "EQUITY", "REVENUE", "EXPENSE"].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedType === type
                  ? "bg-emerald-600 text-white shadow-sm"
                  : "bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/50"
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Accounts Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 font-medium border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4">Account Code</th>
                <th className="px-6 py-4">Account Name</th>
                <th className="px-6 py-4">Classification Type</th>
                <th className="px-6 py-4">Category Section</th>
                <th className="px-6 py-4">Currency</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    Loading accounts...
                  </td>
                </tr>
              ) : filteredAccounts.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    No matching accounts found.
                  </td>
                </tr>
              ) : (
                filteredAccounts.map((acc) => (
                  <tr key={acc.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{acc.code}</td>
                    <td className="px-6 py-4 font-medium text-white">{acc.name}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex px-2.5 py-1 rounded-md text-xs font-semibold border ${typeColor(acc.account_type)}`}>
                        {acc.account_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-xs text-slate-400 font-mono">{acc.account_category}</td>
                    <td className="px-6 py-4 font-mono text-xs">{acc.currency}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400">
                        <CheckCircle2 className="w-3 h-3" /> Active
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Account Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Plus className="w-5 h-5 text-emerald-400" />
              Create Ledger Account
            </h3>

            {errorMsg && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {errorMsg}
              </div>
            )}

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Account Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 1010"
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Account Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Petty Cash"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Type</label>
                  <select
                    value={formData.account_type}
                    onChange={(e) => setFormData({ ...formData, account_type: e.target.value as AccountType })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                  >
                    <option value="ASSET">ASSET</option>
                    <option value="LIABILITY">LIABILITY</option>
                    <option value="EQUITY">EQUITY</option>
                    <option value="REVENUE">REVENUE</option>
                    <option value="EXPENSE">EXPENSE</option>
                  </select>
                </div>

                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Category</label>
                  <select
                    value={formData.account_category}
                    onChange={(e) => setFormData({ ...formData, account_category: e.target.value as AccountCategory })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-emerald-500"
                  >
                    <option value="CURRENT_ASSET">CURRENT_ASSET</option>
                    <option value="NON_CURRENT_ASSET">NON_CURRENT_ASSET</option>
                    <option value="CURRENT_LIABILITY">CURRENT_LIABILITY</option>
                    <option value="NON_CURRENT_LIABILITY">NON_CURRENT_LIABILITY</option>
                    <option value="EQUITY">EQUITY</option>
                    <option value="OPERATING_REVENUE">OPERATING_REVENUE</option>
                    <option value="NON_OPERATING_REVENUE">NON_OPERATING_REVENUE</option>
                    <option value="OPERATING_EXPENSE">OPERATING_EXPENSE</option>
                    <option value="COST_OF_GOODS_SOLD">COST_OF_GOODS_SOLD</option>
                  </select>
                </div>
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
                  className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-semibold transition"
                >
                  Save Account
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
