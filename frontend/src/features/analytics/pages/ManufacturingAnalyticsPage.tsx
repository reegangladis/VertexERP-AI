import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Factory,
  ShieldCheck,
  TrendingUp,
  Cpu,
  Layers,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  FileSpreadsheet,
  AlertOctagon,
  CheckCircle2,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import {
  DateFilterPeriod,
  DomainExecutiveSummary,
  TimeSeriesData,
} from "../types";

export const ManufacturingAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<DateFilterPeriod>("THIS_MONTH");
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DomainExecutiveSummary | null>(null);
  const [fpyTrend, setFpyTrend] = useState<TimeSeriesData | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, fpyRes] = await Promise.allSettled([
        analyticsApi.getDomainSummary("MANUFACTURING", { period }),
        analyticsApi.getManufacturingFpyTrend({ period }),
      ]);
      if (sumRes.status === "fulfilled") setSummary(sumRes.value);
      if (fpyRes.status === "fulfilled") setFpyTrend(fpyRes.value);
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
            <h1 className="text-2xl font-bold tracking-tight text-white">Manufacturing & MRP Analytics</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
              <Factory className="w-3.5 h-3.5" />
              Shop Floor Yield & Quality
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Production order completion velocity, First-Pass Yield (FPY), quality control failure rates, and scrap loss metrics.
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
                    ? "bg-purple-600 text-white shadow-md shadow-purple-600/30"
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
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-purple-400" : ""}`} />
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

      {/* Yield & Scrap Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white">First-Pass Yield (FPY) Trajectory</h2>
              <p className="text-xs text-slate-400 mt-0.5">Quality inspection pass rate without rework requirement</p>
            </div>
            <Link
              to="/analytics/reports"
              className="text-xs text-purple-400 hover:text-purple-300 flex items-center gap-1 font-medium"
            >
              Export QC Log <FileSpreadsheet className="w-3.5 h-3.5" />
            </Link>
          </div>

          {fpyTrend?.series && fpyTrend.series.length > 0 ? (
            <div className="space-y-6">
              <div className="h-56 flex items-end gap-4 pt-6 border-b border-slate-800 pb-2">
                {fpyTrend.series.map((pt, i) => {
                  const fpyVal = Number(pt.primary_value ?? pt.value ?? 0);
                  const barHeight = Math.min(100, Math.max(10, fpyVal));
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-2 h-full justify-end group">
                      <div className="w-full flex items-end justify-center h-full">
                        <div
                          style={{ height: `${barHeight}%` }}
                          className="w-3/4 bg-gradient-to-t from-purple-600 to-indigo-400 rounded-t transition-all duration-300 group-hover:brightness-125"
                          title={`Yield: ${fpyVal}%`}
                        />
                      </div>
                      <span className="text-[11px] font-medium text-slate-400 truncate">{pt.label}</span>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-sm bg-purple-500" />
                  <span>QC Passed Percentage (%)</span>
                </div>
                <span className="text-slate-500 font-medium">Target: &gt;= 95.0% FPY</span>
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 text-xs">
              No quality inspection series recorded.
            </div>
          )}
        </div>

        {/* Quality SLA & Scrap Summary */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white mb-1">Production Quality Standards</h2>
            <p className="text-xs text-slate-400 mb-6">Target yield thresholds and defect management protocols.</p>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="text-xs text-slate-400">Standard Yield Threshold</div>
                <div className="text-xl font-bold text-white mt-1">98.0%</div>
                <div className="text-[11px] text-emerald-400 mt-0.5">Compliant with ISO 9001 quality controls</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="text-xs text-slate-400">Scrap Ledger Audited</div>
                <div className="text-xl font-bold text-white mt-1">100% Auditable</div>
                <div className="text-[11px] text-purple-400 mt-0.5">Linked directly to inventory GL adjustments</div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>MRP Engine Status</span>
            <span className="font-semibold text-emerald-400">Synchronized</span>
          </div>
        </div>
      </div>
    </div>
  );
};
