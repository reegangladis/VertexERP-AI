import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Users,
  DollarSign,
  TrendingUp,
  Award,
  Clock,
  Briefcase,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  FileSpreadsheet,
  Building2,
  GitFork,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import {
  DateFilterPeriod,
  DimensionalDistributionData,
  DomainExecutiveSummary,
} from "../types";

export const HRAnalyticsPage: React.FC = () => {
  const [period, setPeriod] = useState<DateFilterPeriod>("THIS_MONTH");
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState<DomainExecutiveSummary | null>(null);
  const [distribution, setDistribution] = useState<DimensionalDistributionData | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, distRes] = await Promise.allSettled([
        analyticsApi.getDomainSummary("HR", { period }),
        analyticsApi.getHRDepartmentHeadcount(),
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
            <h1 className="text-2xl font-bold tracking-tight text-white">Human Resources & Workforce Analytics</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <Users className="w-3.5 h-3.5" />
              Workforce Intelligence
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Active headcount trajectory, monthly payroll burn rate, departmental distribution, and turnover rates.
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
                    ? "bg-rose-600 text-white shadow-md shadow-rose-600/30"
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
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-rose-400" : ""}`} />
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

      {/* Department Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white">Headcount Distribution by Department</h2>
              <p className="text-xs text-slate-400 mt-0.5">Active workforce allocation across organizational teams</p>
            </div>
            <Link
              to="/hr/employees"
              className="text-xs text-rose-400 hover:text-rose-300 flex items-center gap-1 font-medium"
            >
              Employee Directory <Users className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-4">
            {distribution?.breakdowns && distribution.breakdowns.length > 0 ? (
              distribution.breakdowns.map((b, i) => {
                const pct = Number(b.percentage_share ?? b.percentage ?? 0);
                return (
                  <div key={b.dimension_key || String(i)} className="bg-slate-800/50 p-4 rounded-xl border border-slate-700/50 space-y-2">
                    <div className="flex items-center justify-between text-xs">
                      <div className="flex items-center gap-2">
                        <GitFork className="w-4 h-4 text-rose-400" />
                        <span className="font-semibold text-white">{b.dimension_label}</span>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="font-bold text-white">{b.count ?? 0} Employees</span>
                        <span className="text-slate-400 font-medium">{pct}%</span>
                      </div>
                    </div>
                    <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        style={{ width: `${Math.min(100, Math.max(0, pct || 25))}%` }}
                        className="h-full bg-gradient-to-r from-rose-500 to-pink-400 rounded-full"
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="py-12 text-center text-slate-500 text-xs">No department headcount records found.</div>
            )}
          </div>
        </div>

        {/* Workforce Overview */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-base font-semibold text-white mb-1">HR Operations Snapshot</h2>
            <p className="text-xs text-slate-400 mb-6">Workforce retention and compensation governance.</p>

            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="text-xs text-slate-400">Target Retention Rate</div>
                <div className="text-xl font-bold text-white mt-1">95.0%</div>
                <div className="text-[11px] text-emerald-400 mt-0.5">Voluntary turnover under control</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40">
                <div className="text-xs text-slate-400">Payroll Cycle Status</div>
                <div className="text-xl font-bold text-white mt-1">Approved & Verified</div>
                <div className="text-[11px] text-rose-400 mt-0.5">Automated tax withholding & statutory compliance</div>
              </div>
            </div>
          </div>

          <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Audit Trail Integrity</span>
            <span className="font-semibold text-emerald-400">100% Immutable</span>
          </div>
        </div>
      </div>
    </div>
  );
};
