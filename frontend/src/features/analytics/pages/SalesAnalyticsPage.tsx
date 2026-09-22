import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ShoppingCart,
  TrendingUp,
  Award,
  Users,
  Briefcase,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  SlidersHorizontal,
  FileSpreadsheet,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import {
  DateFilterPeriod,
  DimensionalDistributionData,
  DomainExecutiveSummary,
  MetricCardData,
} from "../types";

export const SalesAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<DateFilterPeriod>("THIS_MONTH");
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DomainExecutiveSummary | null>(null);
  const [distribution, setDistribution] = useState<DimensionalDistributionData | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, distRes] = await Promise.allSettled([
        analyticsApi.getDomainSummary("SALES", { period }),
        analyticsApi.getSalesPipelineDistribution({ period }),
      ]);
      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (distRes.status === "fulfilled") setDistribution(distRes.value);
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
            <h1 className="text-2xl font-bold tracking-tight text-white">Sales & CRM Analytics</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <ShoppingCart className="w-3.5 h-3.5" />
              Pipeline Velocity
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Track deal conversion stages, win rates, bookings trajectory, and sales representative performance.
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
                    ? "bg-blue-600 text-white shadow-md shadow-blue-600/30"
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
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-blue-400" : ""}`} />
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

      {/* Pipeline Funnel Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white">Deal Funnel & Stage Breakdown</h2>
              <p className="text-xs text-slate-400 mt-0.5">Weighted opportunity value across pipeline stages</p>
            </div>
            <Link
              to="/analytics/reports"
              className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
            >
              Export Cohort Report <FileSpreadsheet className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-4">
            {distribution?.breakdowns && distribution.breakdowns.length > 0 ? (
              distribution.breakdowns.map((b, i) => {
                const totalAmt = Number(b.total_amount ?? 0);
                const pct = Number(b.percentage_share ?? b.percentage ?? 0);
                return (
                  <div key={b.dimension_key || String(i)} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                        <span className="font-semibold text-white">{b.dimension_label}</span>
                        <span className="text-slate-400">({b.count ?? 0} deals)</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-emerald-400">${totalAmt.toLocaleString()}</span>
                        <span className="text-slate-400 font-medium">{pct}%</span>
                      </div>
                    </div>
                    <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        style={{ width: `${Math.min(100, Math.max(0, pct || 15))}%` }}
                        className="h-full bg-gradient-to-r from-blue-500 to-indigo-400 rounded-full transition-all duration-500"
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="py-12 text-center text-slate-500 text-xs">No active pipeline opportunities.</div>
            )}
          </div>
        </div>

        {/* Conversion Quick Facts */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white mb-1">Sales Benchmarking</h2>
            <p className="text-xs text-slate-400 mb-6">Target conversion thresholds & performance goals.</p>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="text-xs text-slate-400">Target Win Rate</div>
                <div className="text-xl font-bold text-white mt-1">65.0%</div>
                <div className="text-[11px] text-emerald-400 mt-0.5">Top-quartile SaaS benchmark</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="text-xs text-slate-400">Average Sales Cycle</div>
                <div className="text-xl font-bold text-white mt-1">28.4 Days</div>
                <div className="text-[11px] text-blue-400 mt-0.5">Lead to Closed Won conversion</div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Forecast Confidence</span>
            <span className="font-semibold text-emerald-400">92.0% High</span>
          </div>
        </div>
      </div>
    </div>
  );
};
