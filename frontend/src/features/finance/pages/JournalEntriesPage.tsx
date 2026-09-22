import React, { useEffect, useState } from "react";
import {
  Scale,
  Plus,
  Search,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  Clock,
  Trash2,
  FileText,
  DollarSign,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { Account, JournalEntry, JournalLine } from "../types";

export const JournalEntriesPage: React.FC = () => {
  const [entries, setEntries] = useState<JournalEntry[]>([]);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [selectedStatus, setSelectedStatus] = useState<string>("ALL");
  const [showModal, setShowModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form State
  const [entryDate, setEntryDate] = useState(new Date().toISOString().split("T")[0]);
  const [notes, setNotes] = useState("");
  const [lines, setLines] = useState<Array<{ account_id: string; debit: string; credit: string; description: string }>>([
    { account_id: "", debit: "0", credit: "0", description: "" },
    { account_id: "", debit: "0", credit: "0", description: "" },
  ]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [entriesRes, accountsRes] = await Promise.all([
        financeApi.getJournalEntries({ page: 1, page_size: 100 }),
        financeApi.getAccounts({ page: 1, page_size: 200 }),
      ]);
      setEntries(entriesRes.items || []);
      setAccounts(accountsRes.items || []);
    } catch (err: any) {
      setErrorMsg("Failed to load journal entries.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalDebit = lines.reduce((acc, l) => acc + (parseFloat(l.debit) || 0), 0);
  const totalCredit = lines.reduce((acc, l) => acc + (parseFloat(l.credit) || 0), 0);
  const isBalanced = Math.abs(totalDebit - totalCredit) < 0.0001 && totalDebit > 0;

  const handleAddLine = () => {
    setLines([...lines, { account_id: "", debit: "0", credit: "0", description: "" }]);
  };

  const handleRemoveLine = (index: number) => {
    if (lines.length <= 2) return;
    setLines(lines.filter((_, idx) => idx !== index));
  };

  const handleCreateAndPost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isBalanced) {
      setErrorMsg(`Unbalanced Entry: Total Debits ($${totalDebit}) must equal Total Credits ($${totalCredit}).`);
      return;
    }
    setErrorMsg(null);
    try {
      const created = await financeApi.createJournalEntry({
        entry_date: entryDate,
        posting_date: entryDate,
        entry_type: "STANDARD",
        notes,
        lines: lines.map((l) => ({
          account_id: l.account_id,
          debit: parseFloat(l.debit) || 0,
          credit: parseFloat(l.credit) || 0,
          description: l.description,
        })),
      });

      // Post the entry immediately
      await financeApi.postJournalEntry(created.id);
      setShowModal(false);
      setNotes("");
      setLines([
        { account_id: "", debit: "0", credit: "0", description: "" },
        { account_id: "", debit: "0", credit: "0", description: "" },
      ]);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to post journal entry.");
    }
  };

  const handleReverse = async (entry: JournalEntry) => {
    if (!confirm(`Are you sure you want to reverse posted entry ${entry.entry_number}?`)) return;
    try {
      await financeApi.reverseJournalEntry(entry.id, `Reversal of ${entry.entry_number}`);
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to reverse journal entry.");
    }
  };

  const filteredEntries = entries.filter((e) => {
    const matchesSearch =
      e.entry_number.toLowerCase().includes(search.toLowerCase()) ||
      (e.notes || "").toLowerCase().includes(search.toLowerCase());
    const matchesStatus = selectedStatus === "ALL" || e.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-400">
              <Scale className="w-6 h-6" />
            </span>
            Double-Entry Journal Entries
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Immutable general ledger transactions strictly enforcing Total Debits = Total Credits.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold transition shadow-lg shadow-purple-600/20"
        >
          <Plus className="w-4 h-4" />
          Create Journal Entry
        </button>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search journal number or memo..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-purple-500"
          />
        </div>

        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {["ALL", "POSTED", "DRAFT", "REVERSED"].map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedStatus === status
                  ? "bg-purple-600 text-white shadow-sm"
                  : "bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/50"
              }`}
            >
              {status}
            </button>
          ))}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* Entries List */}
      <div className="space-y-4">
        {loading ? (
          <div className="p-12 text-center text-slate-500 bg-slate-900/60 rounded-2xl border border-slate-800">
            Loading journal entries...
          </div>
        ) : filteredEntries.length === 0 ? (
          <div className="p-12 text-center text-slate-500 bg-slate-900/60 rounded-2xl border border-slate-800">
            No journal entries found.
          </div>
        ) : (
          filteredEntries.map((entry) => (
            <div
              key={entry.id}
              className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 space-y-4 hover:border-slate-700 transition"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <span className="font-mono font-bold text-white text-base">{entry.entry_number}</span>
                  <span
                    className={`px-2.5 py-1 rounded-md text-xs font-semibold border ${
                      entry.status === "POSTED"
                        ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                        : entry.status === "REVERSED"
                        ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                        : "bg-slate-700 text-slate-300 border-slate-600"
                    }`}
                  >
                    {entry.status}
                  </span>
                  <span className="text-xs text-slate-400 font-mono">Date: {entry.posting_date}</span>
                </div>

                <div className="flex items-center gap-3">
                  <div className="text-right">
                    <span className="text-xs text-slate-400 block">Total Balanced Amount</span>
                    <span className="text-sm font-bold text-white font-mono">
                      ${Number(entry.total_debit).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>

                  {entry.status === "POSTED" && (
                    <button
                      onClick={() => handleReverse(entry)}
                      className="px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 transition flex items-center gap-1.5"
                    >
                      <RotateCcw className="w-3.5 h-3.5" />
                      Reverse Entry
                    </button>
                  )}
                </div>
              </div>

              {entry.notes && <p className="text-xs text-slate-400 italic">{entry.notes}</p>}

              {/* Lines Table */}
              <div className="rounded-xl bg-slate-800/40 border border-slate-800/80 overflow-hidden">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800/60 text-slate-400 font-medium border-b border-slate-800/80 uppercase tracking-wider">
                    <tr>
                      <th className="px-4 py-2.5">Account Code & Name</th>
                      <th className="px-4 py-2.5">Description</th>
                      <th className="px-4 py-2.5 text-right">Debit ($)</th>
                      <th className="px-4 py-2.5 text-right">Credit ($)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/40 font-mono">
                    {entry.lines.map((l, i) => {
                      const acct = accounts.find((a) => a.id === l.account_id);
                      return (
                        <tr key={i} className="hover:bg-slate-800/20">
                          <td className="px-4 py-2 text-slate-300 font-sans">
                            <span className="font-mono font-bold text-white mr-2">
                              {acct ? acct.code : "GL Account"}
                            </span>
                            {acct ? acct.name : ""}
                          </td>
                          <td className="px-4 py-2 text-slate-400 font-sans">{l.description || "-"}</td>
                          <td className="px-4 py-2 text-right font-medium text-emerald-400">
                            {Number(l.debit) > 0 ? Number(l.debit).toFixed(2) : "-"}
                          </td>
                          <td className="px-4 py-2 text-right font-medium text-purple-400">
                            {Number(l.credit) > 0 ? Number(l.credit).toFixed(2) : "-"}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Double-Entry Journal Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 shadow-2xl space-y-4 max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Scale className="w-5 h-5 text-purple-400" />
              New Double-Entry Journal Entry
            </h3>

            <form onSubmit={handleCreateAndPost} className="space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Posting Date</label>
                  <input
                    type="date"
                    required
                    value={entryDate}
                    onChange={(e) => setEntryDate(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Description / Memo</label>
                  <input
                    type="text"
                    placeholder="e.g. Monthly Accrual Adjustment"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              {/* Dynamic Lines */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-medium text-slate-400">Journal Lines (Debits must equal Credits)</label>
                  <button
                    type="button"
                    onClick={handleAddLine}
                    className="text-xs text-purple-400 hover:underline flex items-center gap-1 font-semibold"
                  >
                    <Plus className="w-3.5 h-3.5" /> Add Line
                  </button>
                </div>

                <div className="space-y-2">
                  {lines.map((line, idx) => (
                    <div key={idx} className="flex items-center gap-2 p-2.5 rounded-xl bg-slate-800/60 border border-slate-700/60">
                      <select
                        required
                        value={line.account_id}
                        onChange={(e) => {
                          const updated = [...lines];
                          updated[idx].account_id = e.target.value;
                          setLines(updated);
                        }}
                        className="flex-1 px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs focus:outline-none focus:border-purple-500"
                      >
                        <option value="">Select Account...</option>
                        {accounts.map((a) => (
                          <option key={a.id} value={a.id}>
                            {a.code} - {a.name} ({a.account_type})
                          </option>
                        ))}
                      </select>

                      <input
                        type="text"
                        placeholder="Line memo"
                        value={line.description}
                        onChange={(e) => {
                          const updated = [...lines];
                          updated[idx].description = e.target.value;
                          setLines(updated);
                        }}
                        className="w-40 px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs"
                      />

                      <div className="w-28">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="Debit"
                          value={line.debit}
                          onChange={(e) => {
                            const updated = [...lines];
                            updated[idx].debit = e.target.value;
                            if (parseFloat(e.target.value) > 0) updated[idx].credit = "0";
                            setLines(updated);
                          }}
                          className="w-full px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-emerald-400 font-mono text-xs text-right"
                        />
                      </div>

                      <div className="w-28">
                        <input
                          type="number"
                          step="0.01"
                          min="0"
                          placeholder="Credit"
                          value={line.credit}
                          onChange={(e) => {
                            const updated = [...lines];
                            updated[idx].credit = e.target.value;
                            if (parseFloat(e.target.value) > 0) updated[idx].debit = "0";
                            setLines(updated);
                          }}
                          className="w-full px-2.5 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-purple-400 font-mono text-xs text-right"
                        />
                      </div>

                      {lines.length > 2 && (
                        <button
                          type="button"
                          onClick={() => handleRemoveLine(idx)}
                          className="p-1.5 rounded-lg text-rose-400 hover:bg-rose-500/10"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>
                  ))}
                </div>

                {/* Balance Totals Footer */}
                <div className="flex items-center justify-between p-3 rounded-xl bg-slate-800 border border-slate-700">
                  <div className="flex items-center gap-2">
                    {isBalanced ? (
                      <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4" /> Entry is balanced
                      </span>
                    ) : (
                      <span className="text-xs font-semibold text-rose-400 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" /> Unbalanced by $
                        {Math.abs(totalDebit - totalCredit).toFixed(2)}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center gap-4 text-xs font-mono">
                    <span className="text-emerald-400">Debits: ${totalDebit.toFixed(2)}</span>
                    <span className="text-purple-400">Credits: ${totalCredit.toFixed(2)}</span>
                  </div>
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
                  disabled={!isBalanced}
                  className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-sm font-semibold transition disabled:opacity-50"
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
};
