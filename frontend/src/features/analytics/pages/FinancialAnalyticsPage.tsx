import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  DollarSign,
  TrendingUp,
  Receipt,
  CreditCard,
  Scale,
  Building2,
  FileSpreadsheet,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Sparkles,
  PieChart,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import { DateFilterPeriod, DomainExecutiveSummary, MetricCardData, TimeSeriesData } from "../types";

export const FinancialAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<DateFilterPeriod>("THIS_MONTH");
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DomainExecutiveSummary | null>(null);
  const [trend, setTrend] = useState<TimeSeriesData | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, trendRes] = await Promise.allSettled([
        analyticsApi.getDomainSummary("FINANCE", { period }),
        analyticsApi.getFinancialTrend({ period }),
      ]);
      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (trendRes.status === "fulfilled") setTrend(trendRes.value);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [period]);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">Financial & Profitability Analytics</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <DollarSign className="w-3.5 h-3.5" />
              General Ledger Telemetry
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Realtime revenue recognition, operating margins, DSO liquidity metrics, and cash runway.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center bg-slate-800/80 rounded-xl p-1 border border-slate-700/60">
            {(["THIS_WEEK", "THIS_MONTH", "THIS_QUARTER", "THIS_YEAR"] as DateFilterPeriod[]).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  period === p
                    ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/30"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {p.replace("_", " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase())}
              </button>
            ))}
          </div>

          <button
            onClick={loadData}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-emerald-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {summary?.kpis.map((kpi, i) => (
          <div
            key={kpi.code || kpi.kpi_code || String(i)}
            className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition group"
          >
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span className="font-medium truncate">{kpi.name}</span>
              <span
                className={`w-2 h-2 rounded-full ${
                  kpi.status === "ON_TRACK"
                    ? "bg-emerald-400"
                    : kpi.status === "WARNING"
                    ? "bg-amber-400"
                    : "bg-rose-500"
                }`}
              />
            </div>
            <div className="text-2xl font-bold text-white tracking-tight">
              {kpi.formatted_value || (kpi.current_value !== undefined && kpi.current_value !== null ? Number(kpi.current_value).toLocaleString() : "0")}
            </div>
            <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-800/60 text-xs">
              <span className="text-slate-500">{kpi.period_label}</span>
              {kpi.delta_percentage !== undefined && kpi.delta_percentage !== null && (
                <span
                  className={`font-semibold flex items-center ${
                    kpi.delta_percentage >= 0 ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  {kpi.delta_percentage >= 0 ? (
                    <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />
                  ) : (
                    <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                  )}
                  {kpi.delta_percentage}%
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Monthly Financial Trend */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-semibold text-white">Multi-Period Revenue vs Expense Trajectory</h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Comparative view of billed invoices vs approved vendor payables
            </p>
          </div>
          <Link
            to="/analytics/reports"
            className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium"
          >
            Run P&L Statement <FileSpreadsheet className="w-3.5 h-3.5" />
          </Link>
        </div>

        {trend?.series && trend.series.length > 0 ? (
          <div className="space-y-6">
            <div className="h-64 flex items-end gap-4 pt-6 border-b border-slate-800 pb-2">
              {trend.series.map((pt, i) => {
                const revVal = Number(pt.primary_value ?? pt.value ?? 0);
                const expVal = Number(pt.secondary_value ?? 0);
                const maxVal = Math.max(
                  ...trend.series.map((s) => Math.max(Number(s.primary_value ?? s.value ?? 0), Number(s.secondary_value ?? 0))),
                  10000
                );
                const revHeight = Math.min(100, Math.max(8, (revVal / maxVal) * 100));
                const expHeight = Math.min(100, Math.max(6, (expVal / maxVal) * 100));
                return (
                  <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                    <div className="w-full flex items-end justify-center gap-2 h-full">
                      <div
                        style={{ height: `${revHeight}%` }}
                        className="w-1/2 bg-gradient-to-t from-emerald-600 to-teal-400 rounded-t transition-all duration-300 group-hover:brightness-125"
                        title={`Revenue: $${revVal.toLocaleString()}`}
                      />
                      <div
                        style={{ height: `${expHeight}%` }}
                        className="w-1/2 bg-gradient-to-t from-rose-600 to-amber-500 rounded-t transition-all duration-300 group-hover:brightness-125"
                        title={`Expenses: $${expVal.toLocaleString()}`}
                      />
                    </div>
                    <span className="text-[11px] font-medium text-slate-400 truncate">{pt.label}</span>
                  </div>
                );
              })}
            </div>

            <div className="flex items-center justify-between text-xs text-slate-400">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-sm bg-emerald-500" />
                  <span>Gross Invoiced Revenue</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-sm bg-rose-500" />
                  <span>Operating Expenses</span>
                </div>
              </div>
              <span className="text-slate-500">Interval: {trend.interval}</span>
            </div>
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-slate-500 text-xs">
            No financial series recorded for this range.
          </div>
        )}
      </div>
    </div>
  );
};
