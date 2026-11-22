import React, { useEffect, useState } from "react";
import {
  Award,
  Layers,
  Plus,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Sparkles,
  SlidersHorizontal,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import { KPICategory, KPIDefinition } from "../types";

export const KPICatalogPage: React.FC = () => {
  const [kpis, setKpis] = useState<KPIDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");

  const loadKPIs = async () => {
    setLoading(true);
    try {
      const category = selectedCategory === "ALL" ? undefined : selectedCategory;
      const res = await analyticsApi.getKPIDefinitions(category);
      setKpis(res.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKPIs();
  }, [selectedCategory]);

  const filteredKpis = kpis.filter(
    (k) =>
      k.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      k.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (k.description && k.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">Enterprise KPI Catalog</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-400 border border-brand-500/20">
              <Award className="w-3.5 h-3.5" />
              Metrics Dictionary
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Standardized business metric formulas, performance targets, alert thresholds, and domain assignments.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadKPIs}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-brand-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search metric code or name..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
          />
        </div>

        <div className="flex items-center gap-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 overflow-x-auto w-full sm:w-auto">
          {["ALL", "FINANCE", "SALES", "INVENTORY", "MANUFACTURING", "HR"].map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                selectedCategory === cat
                  ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                  : "text-slate-400 hover:text-slate-200"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* KPI Table */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/60 text-slate-400 uppercase tracking-wider text-[10px] font-semibold border-b border-slate-800">
              <tr>
                <th className="px-6 py-4">Metric Code & Name</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Unit</th>
                <th className="px-6 py-4">Target SLA</th>
                <th className="px-6 py-4">Warning Threshold</th>
                <th className="px-6 py-4">Critical Threshold</th>
                <th className="px-6 py-4">Calculation</th>
                <th className="px-6 py-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredKpis.length > 0 ? (
                filteredKpis.map((kpi) => (
                  <tr key={kpi.id} className="hover:bg-slate-800/40 transition">
                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">{kpi.name}</div>
                      <div className="text-[11px] font-mono text-brand-400 mt-0.5">{kpi.code}</div>
                      {kpi.description && (
                        <div className="text-[11px] text-slate-400 mt-1 line-clamp-1 max-w-sm">
                          {kpi.description}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {kpi.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-300">{kpi.unit}</td>
                    <td className="px-6 py-4 font-semibold text-emerald-400">
                      {kpi.target_value !== null && kpi.target_value !== undefined
                        ? Number(kpi.target_value).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-6 py-4 font-semibold text-amber-400">
                      {kpi.warning_threshold !== null && kpi.warning_threshold !== undefined
                        ? Number(kpi.warning_threshold).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-6 py-4 font-semibold text-rose-400">
                      {kpi.critical_threshold !== null && kpi.critical_threshold !== undefined
                        ? Number(kpi.critical_threshold).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-6 py-4 font-mono text-[11px] text-slate-400">{kpi.calculation_method}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-400">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Active
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-500">
                    {loading ? "Loading KPI catalog definitions..." : "No KPI definitions matching your criteria."}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
