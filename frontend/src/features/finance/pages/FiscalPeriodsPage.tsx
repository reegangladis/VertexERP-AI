import React, { useEffect, useState } from "react";
import {
  Lock,
  Unlock,
  Calendar,
  Plus,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ShieldAlert,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { FiscalPeriod, FiscalYear } from "../types";

export const FiscalPeriodsPage: React.FC = () => {
  const [years, setYears] = useState<FiscalYear[]>([]);
  const [periods, setPeriods] = useState<FiscalPeriod[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedYearId, setSelectedYearId] = useState<string>("");
  const [showYearModal, setShowYearModal] = useState(false);
  const [showPeriodModal, setShowPeriodModal] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Form States
  const [yearForm, setYearForm] = useState({
    code: "",
    name: "",
    start_date: "",
    end_date: "",
  });

  const [periodForm, setPeriodForm] = useState({
    period_number: 1,
    period_name: "",
    start_date: "",
    end_date: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [yearsRes, periodsRes] = await Promise.all([
        financeApi.getFiscalYears(),
        financeApi.getFiscalPeriods(),
      ]);
      const yrs = yearsRes.items || [];
      setYears(yrs);
      setPeriods(periodsRes.items || []);
      if (yrs.length > 0 && !selectedYearId) {
        setSelectedYearId(yrs[0].id);
      }
    } catch (err: any) {
      setErrorMsg("Failed to load fiscal calendar.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateYear = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeApi.createFiscalYear(yearForm);
      setShowYearModal(false);
      setYearForm({ code: "", name: "", start_date: "", end_date: "" });
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create fiscal year.");
    }
  };

  const handleCreatePeriod = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await financeApi.createFiscalPeriod({
        ...periodForm,
        fiscal_year_id: selectedYearId,
      });
      setShowPeriodModal(false);
      setPeriodForm({ period_number: 1, period_name: "", start_date: "", end_date: "" });
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to create fiscal period.");
    }
  };

  const handleToggleLock = async (period: FiscalPeriod) => {
    try {
      if (period.is_locked) {
        await financeApi.unlockFiscalPeriod(period.id);
      } else {
        await financeApi.lockFiscalPeriod(period.id);
      }
      loadData();
    } catch (err: any) {
      setErrorMsg(err.message || "Failed to update period lock status.");
    }
  };

  const currentYearPeriods = periods.filter((p) => p.fiscal_year_id === selectedYearId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-amber-500/20 border border-amber-500/30 text-amber-400">
              <Lock className="w-6 h-6" />
            </span>
            Fiscal Years & Period Locking Controls
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Enforce audit period closures and lock controls to prevent retroactive financial record posting.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowYearModal(true)}
            className="inline-flex items-center gap-2 px-3.5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition"
          >
            <Calendar className="w-4 h-4" />
            New Fiscal Year
          </button>
          <button
            onClick={() => setShowPeriodModal(true)}
            disabled={!selectedYearId}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold transition shadow-lg shadow-amber-600/20 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            Add Period
          </button>
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <ShieldAlert className="w-5 h-5 shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* Fiscal Year Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3 overflow-x-auto">
        {years.map((y) => (
          <button
            key={y.id}
            onClick={() => setSelectedYearId(y.id)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition flex items-center gap-2 ${
              selectedYearId === y.id
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                : "bg-slate-900/60 text-slate-400 hover:text-white border border-slate-800"
            }`}
          >
            <Calendar className="w-4 h-4" />
            {y.name} ({y.code})
          </button>
        ))}
      </div>

      {/* Periods Table */}
      <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-800/50 text-slate-400 font-medium border-b border-slate-800 text-xs uppercase tracking-wider">
              <tr>
                <th className="px-6 py-4">#</th>
                <th className="px-6 py-4">Period Name</th>
                <th className="px-6 py-4">Date Range</th>
                <th className="px-6 py-4">Lock Status</th>
                <th className="px-6 py-4">Closure Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50 text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    Loading fiscal periods...
                  </td>
                </tr>
              ) : currentYearPeriods.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-10 text-center text-slate-500">
                    No periods defined for this fiscal year.
                  </td>
                </tr>
              ) : (
                currentYearPeriods.map((p) => (
                  <tr key={p.id} className="hover:bg-slate-800/30 transition">
                    <td className="px-6 py-4 font-mono font-bold text-white">{p.period_number}</td>
                    <td className="px-6 py-4 font-medium text-white">{p.period_name}</td>
                    <td className="px-6 py-4 text-xs text-slate-400 font-mono">
                      {p.start_date} &rarr; {p.end_date}
                    </td>
                    <td className="px-6 py-4">
                      {p.is_locked ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <Lock className="w-3.5 h-3.5" /> LOCKED
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          <Unlock className="w-3.5 h-3.5" /> OPEN FOR POSTING
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {p.is_closed ? (
                        <span className="text-xs text-slate-400 font-medium">CLOSED</span>
                      ) : (
                        <span className="text-xs text-emerald-400 font-medium">ACTIVE</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleToggleLock(p)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-semibold border transition inline-flex items-center gap-1.5 ${
                          p.is_locked
                            ? "bg-slate-800 hover:bg-slate-700 text-emerald-300 border-slate-700"
                            : "bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border-rose-500/40"
                        }`}
                      >
                        {p.is_locked ? <Unlock className="w-3 h-3" /> : <Lock className="w-3 h-3" />}
                        {p.is_locked ? "Unlock Period" : "Lock Period"}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Fiscal Year Modal */}
      {showYearModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-amber-400" />
              Create Fiscal Year
            </h3>
            <form onSubmit={handleCreateYear} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Code</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. FY-2026"
                  value={yearForm.code}
                  onChange={(e) => setYearForm({ ...yearForm, code: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Year Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Fiscal Year 2026"
                  value={yearForm.name}
                  onChange={(e) => setYearForm({ ...yearForm, name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={yearForm.start_date}
                    onChange={(e) => setYearForm({ ...yearForm, start_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">End Date</label>
                  <input
                    type="date"
                    required
                    value={yearForm.end_date}
                    onChange={(e) => setYearForm({ ...yearForm, end_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowYearModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold transition"
                >
                  Create Year
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Fiscal Period Modal */}
      {showPeriodModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Plus className="w-5 h-5 text-amber-400" />
              Add Fiscal Period
            </h3>
            <form onSubmit={handleCreatePeriod} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Period Number</label>
                <input
                  type="number"
                  required
                  min="1"
                  max="16"
                  value={periodForm.period_number}
                  onChange={(e) => setPeriodForm({ ...periodForm, period_number: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400 block mb-1">Period Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Month 1 - January"
                  value={periodForm.period_name}
                  onChange={(e) => setPeriodForm({ ...periodForm, period_name: e.target.value })}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">Start Date</label>
                  <input
                    type="date"
                    required
                    value={periodForm.start_date}
                    onChange={(e) => setPeriodForm({ ...periodForm, start_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-400 block mb-1">End Date</label>
                  <input
                    type="date"
                    required
                    value={periodForm.end_date}
                    onChange={(e) => setPeriodForm({ ...periodForm, end_date: e.target.value })}
                    className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-white text-sm focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowPeriodModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-medium transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-semibold transition"
                >
                  Save Period
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
