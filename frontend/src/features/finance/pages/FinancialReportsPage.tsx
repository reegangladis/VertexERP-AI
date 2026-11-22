import React, { useEffect, useState } from "react";
import {
  FileSpreadsheet,
  Scale,
  TrendingUp,
  PieChart,
  Calendar,
  CheckCircle2,
  AlertCircle,
  Download,
  Printer,
  ChevronRight,
} from "lucide-react";
import { financeApi } from "../api/financeApi";
import { BalanceSheetResponse, ProfitLossResponse, TrialBalanceResponse } from "../types";

export const FinancialReportsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"TB" | "BS" | "PL">("TB");
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split("T")[0]);
  const [startDate, setStartDate] = useState(
    new Date(new Date().getFullYear(), 0, 1).toISOString().split("T")[0]
  );
  const [endDate, setEndDate] = useState(new Date().toISOString().split("T")[0]);

  const [tb, setTb] = useState<TrialBalanceResponse | null>(null);
  const [bs, setBs] = useState<BalanceSheetResponse | null>(null);
  const [pl, setPl] = useState<ProfitLossResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const loadReport = async () => {
    try {
      setLoading(true);
      setErrorMsg(null);
      if (activeTab === "TB") {
        const res = await financeApi.getTrialBalance(asOfDate);
        setTb(res);
      } else if (activeTab === "BS") {
        const res = await financeApi.getBalanceSheet(asOfDate);
        setBs(res);
      } else if (activeTab === "PL") {
        const res = await financeApi.getProfitLoss(startDate, endDate);
        setPl(res);
      }
    } catch (err: any) {
      setErrorMsg("Failed to generate financial statement.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
  }, [activeTab, asOfDate, startDate, endDate]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-3">
            <span className="p-2 rounded-xl bg-purple-500/20 border border-purple-500/30 text-purple-400">
              <FileSpreadsheet className="w-6 h-6" />
            </span>
            Financial Statements & GAAP Reporting
          </h1>
          <p className="text-slate-400 text-sm mt-1">
            Real-time reporting generated directly from immutable general ledger postings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => window.print()}
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium transition"
          >
            <Printer className="w-4 h-4" />
            Print Statement
          </button>
        </div>
      </div>

      {/* Report Switcher & Date Controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between p-4 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveTab("TB")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === "TB"
                ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20"
                : "bg-slate-800/60 text-slate-400 hover:text-white border border-slate-700/50"
            }`}
          >
            <Scale className="w-4 h-4" /> Trial Balance
          </button>

          <button
            onClick={() => setActiveTab("BS")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === "BS"
                ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20"
                : "bg-slate-800/60 text-slate-400 hover:text-white border border-slate-700/50"
            }`}
          >
            <PieChart className="w-4 h-4" /> Balance Sheet
          </button>

          <button
            onClick={() => setActiveTab("PL")}
            className={`px-4 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 ${
              activeTab === "PL"
                ? "bg-purple-600 text-white shadow-lg shadow-purple-600/20"
                : "bg-slate-800/60 text-slate-400 hover:text-white border border-slate-700/50"
            }`}
          >
            <TrendingUp className="w-4 h-4" /> Profit & Loss
          </button>
        </div>

        {/* Date Selectors */}
        <div className="flex items-center gap-3">
          {activeTab === "PL" ? (
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
              <span>From:</span>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none"
              />
              <span>To:</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none"
              />
            </div>
          ) : (
            <div className="flex items-center gap-2 text-xs font-medium text-slate-400">
              <span>As of Date:</span>
              <input
                type="date"
                value={asOfDate}
                onChange={(e) => setAsOfDate(e.target.value)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white focus:outline-none"
              />
            </div>
          )}
        </div>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-sm flex items-center gap-3">
          <AlertCircle className="w-5 h-5 shrink-0" />
          {errorMsg}
        </div>
      )}

      {/* REPORT 1: TRIAL BALANCE */}
      {activeTab === "TB" && (
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white">Trial Balance</h2>
              <p className="text-xs text-slate-400 mt-0.5">As of {asOfDate} &bull; Currency: USD</p>
            </div>

            {tb && (
              <div
                className={`px-3 py-1.5 rounded-xl border text-xs font-bold flex items-center gap-2 ${
                  tb.is_balanced
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                }`}
              >
                {tb.is_balanced ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                {tb.is_balanced ? "TRIAL BALANCE BALANCED" : "UNBALANCED LEDGER DETECTED"}
              </div>
            )}
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-800/50 text-slate-400 font-medium border-b border-slate-800 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-5 py-3">Account Code</th>
                  <th className="px-5 py-3">Account Title</th>
                  <th className="px-5 py-3">Classification</th>
                  <th className="px-5 py-3 text-right">Debit Balance ($)</th>
                  <th className="px-5 py-3 text-right">Credit Balance ($)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40 text-slate-300 font-mono">
                {loading ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-10 text-center text-slate-500">
                      Computing trial balance from ledger...
                    </td>
                  </tr>
                ) : !tb || tb.lines.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-5 py-10 text-center text-slate-500">
                      No posted activity as of selected date.
                    </td>
                  </tr>
                ) : (
                  tb.lines.map((l) => (
                    <tr key={l.account_id} className="hover:bg-slate-800/20">
                      <td className="px-5 py-3 font-bold text-white">{l.account_code}</td>
                      <td className="px-5 py-3 font-sans text-white">{l.account_name}</td>
                      <td className="px-5 py-3 font-sans text-xs text-slate-400">{l.account_type}</td>
                      <td className="px-5 py-3 text-right font-semibold text-emerald-400">
                        {Number(l.net_debit) > 0 ? Number(l.net_debit).toFixed(2) : "-"}
                      </td>
                      <td className="px-5 py-3 text-right font-semibold text-purple-400">
                        {Number(l.net_credit) > 0 ? Number(l.net_credit).toFixed(2) : "-"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
              {tb && (
                <tfoot className="bg-slate-800/80 font-mono font-bold text-white border-t-2 border-slate-700">
                  <tr>
                    <td colSpan={3} className="px-5 py-4 font-sans uppercase text-xs tracking-wider text-slate-300">
                      Total Ledger Activity
                    </td>
                    <td className="px-5 py-4 text-right text-emerald-400 text-base">
                      ${Number(tb.total_debit).toFixed(2)}
                    </td>
                    <td className="px-5 py-4 text-right text-purple-400 text-base">
                      ${Number(tb.total_credit).toFixed(2)}
                    </td>
                  </tr>
                </tfoot>
              )}
            </table>
          </div>
        </div>
      )}

      {/* REPORT 2: BALANCE SHEET */}
      {activeTab === "BS" && (
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white">Balance Sheet (Statement of Financial Position)</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Assets = Liabilities + Equity &bull; As of {asOfDate}
              </p>
            </div>

            {bs && (
              <div
                className={`px-3 py-1.5 rounded-xl border text-xs font-bold flex items-center gap-2 ${
                  bs.is_balanced
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                    : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                }`}
              >
                {bs.is_balanced ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                {bs.is_balanced ? "ACCOUNTING EQUATION BALANCED" : "EQUATION IMBALANCE"}
              </div>
            )}
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-500">Computing balance sheet...</div>
          ) : !bs ? (
            <div className="text-center py-12 text-slate-500">No balance sheet data available.</div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Assets Section */}
              <div className="space-y-4">
                <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
                  <h3 className="text-base font-bold text-emerald-300">ASSETS</h3>
                  <span className="font-mono font-extrabold text-white text-base">
                    ${Number(bs.total_assets).toFixed(2)}
                  </span>
                </div>

                <div className="space-y-3">
                  {bs.assets.map((sec, i) => (
                    <div key={i} className="rounded-xl bg-slate-800/40 border border-slate-800 p-3 space-y-2">
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{sec.category}</p>
                      <div className="space-y-1 font-mono text-xs">
                        {sec.lines.map((l) => (
                          <div key={l.account_id} className="flex items-center justify-between text-slate-300">
                            <span className="font-sans">{l.account_name} ({l.account_code})</span>
                            <span className="text-white">${Number(l.balance).toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                      <div className="pt-2 border-t border-slate-700/60 flex justify-between text-xs font-mono font-bold text-emerald-400">
                        <span>Subtotal</span>
                        <span>${Number(sec.subtotal).toFixed(2)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Liabilities & Equity Section */}
              <div className="space-y-4">
                <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-between">
                  <h3 className="text-base font-bold text-purple-300">LIABILITIES & EQUITY</h3>
                  <span className="font-mono font-extrabold text-white text-base">
                    ${Number(bs.total_liabilities_and_equity).toFixed(2)}
                  </span>
                </div>

                {/* Liabilities */}
                <div className="space-y-3">
                  <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider px-1">Liabilities</h4>
                  {bs.liabilities.length === 0 ? (
                    <p className="text-xs text-slate-500 px-1">No outstanding liabilities.</p>
                  ) : (
                    bs.liabilities.map((sec, i) => (
                      <div key={i} className="rounded-xl bg-slate-800/40 border border-slate-800 p-3 space-y-2">
                        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{sec.category}</p>
                        <div className="space-y-1 font-mono text-xs">
                          {sec.lines.map((l) => (
                            <div key={l.account_id} className="flex items-center justify-between text-slate-300">
                              <span className="font-sans">{l.account_name} ({l.account_code})</span>
                              <span className="text-white">${Number(l.balance).toFixed(2)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))
                  )}

                  {/* Equity */}
                  <h4 className="text-xs font-bold text-purple-400 uppercase tracking-wider px-1 pt-2">Equity</h4>
                  {bs.equity.map((sec, i) => (
                    <div key={i} className="rounded-xl bg-slate-800/40 border border-slate-800 p-3 space-y-2">
                      <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{sec.category}</p>
                      <div className="space-y-1 font-mono text-xs">
                        {sec.lines.map((l) => (
                          <div key={l.account_id} className="flex items-center justify-between text-slate-300">
                            <span className="font-sans">{l.account_name} ({l.account_code})</span>
                            <span className="text-white">${Number(l.balance).toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* REPORT 3: PROFIT & LOSS */}
      {activeTab === "PL" && (
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h2 className="text-xl font-bold text-white">Profit & Loss (Income Statement)</h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Period: {startDate} &rarr; {endDate} &bull; Currency: USD
              </p>
            </div>

            {pl && (
              <div className="text-right">
                <span className="text-xs text-slate-400 block font-medium">Net Operating Income</span>
                <span
                  className={`text-xl font-extrabold font-mono ${
                    Number(pl.net_income) >= 0 ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  ${Number(pl.net_income).toFixed(2)}
                </span>
              </div>
            )}
          </div>

          {loading ? (
            <div className="text-center py-12 text-slate-500">Computing profit and loss...</div>
          ) : !pl ? (
            <div className="text-center py-12 text-slate-500">No revenue or expense data for this range.</div>
          ) : (
            <div className="space-y-6">
              {/* Revenue */}
              <div className="rounded-xl bg-slate-800/40 border border-slate-800 p-4 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-700/60">
                  <h3 className="text-sm font-bold text-blue-400 uppercase tracking-wider">Operating Revenues</h3>
                  <span className="font-mono font-bold text-white">${Number(pl.total_revenue).toFixed(2)}</span>
                </div>
                <div className="space-y-1.5 font-mono text-xs">
                  {pl.revenues.map((r) => (
                    <div key={r.account_id} className="flex items-center justify-between text-slate-300">
                      <span className="font-sans">{r.account_name} ({r.account_code})</span>
                      <span className="text-white">${Number(r.amount).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expenses */}
              <div className="rounded-xl bg-slate-800/40 border border-slate-800 p-4 space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-slate-700/60">
                  <h3 className="text-sm font-bold text-amber-400 uppercase tracking-wider">Operating Expenses</h3>
                  <span className="font-mono font-bold text-white">${Number(pl.total_expense).toFixed(2)}</span>
                </div>
                <div className="space-y-1.5 font-mono text-xs">
                  {pl.expenses.map((e) => (
                    <div key={e.account_id} className="flex items-center justify-between text-slate-300">
                      <span className="font-sans">{e.account_name} ({e.account_code})</span>
                      <span className="text-white">${Number(e.amount).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Net Income Summary Card */}
              <div className="p-5 rounded-2xl bg-gradient-to-r from-purple-900/30 to-emerald-900/30 border border-purple-500/30 flex items-center justify-between">
                <div>
                  <h4 className="text-base font-bold text-white">Bottom Line Net Income</h4>
                  <p className="text-xs text-slate-400">Total Revenue (${Number(pl.total_revenue).toFixed(2)}) minus Total Expenses (${Number(pl.total_expense).toFixed(2)})</p>
                </div>
                <span
                  className={`text-2xl font-black font-mono ${
                    Number(pl.net_income) >= 0 ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  ${Number(pl.net_income).toFixed(2)}
                </span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
