import React, { useEffect, useState } from "react";
import {
  FileSpreadsheet,
  Download,
  Play,
  Search,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  Calendar,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import { AnalyticsReport, ReportExecutionResult } from "../types";

export const ReportsHubPage: React.FC = () => {
  const [reports, setReports] = useState<AnalyticsReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [executingCode, setExecutingCode] = useState<string | null>(null);
  const [executionResult, setExecutionResult] = useState<ReportExecutionResult | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const loadReports = async () => {
    setLoading(true);
    try {
      const res = await analyticsApi.listReports();
      setReports(res.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const handleRunReport = async (reportCode: string) => {
    setExecutingCode(reportCode);
    try {
      const result = await analyticsApi.executeReport(reportCode, {}, "JSON");
      setExecutionResult(result);
    } finally {
      setExecutingCode(null);
    }
  };

  const handleExportCsv = async (reportCode: string) => {
    try {
      const result = await analyticsApi.executeReport(reportCode, {}, "CSV");
      if (result.csv_content) {
        const blob = new Blob([result.csv_content], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `${reportCode}_${new Date().toISOString().slice(0, 10)}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    } catch (err) {
      console.error("CSV Export failed", err);
    }
  };

  const filteredReports = reports.filter(
    (r) =>
      r.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      r.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (r.description && r.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-6 rounded-2xl border border-slate-800 backdrop-blur-xl">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">Parameterized Reports Hub</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <FileSpreadsheet className="w-3.5 h-3.5" />
              Direct CSV Export
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Execute analytical reports across Finance, CRM, Inventory Aging, Manufacturing Yield, and Payroll with instant CSV downloads.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={loadReports}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 border border-slate-700 transition"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-emerald-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative w-full sm:w-80">
        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search report title or code..."
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-brand-500"
        />
      </div>

      {/* Reports Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredReports.map((rep) => (
          <div
            key={rep.id}
            className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between hover:border-slate-700 transition group"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                  {rep.category}
                </span>
                <span className="font-mono text-[11px] text-brand-400">{rep.code}</span>
              </div>
              <h3 className="text-base font-bold text-white group-hover:text-brand-300 transition-colors">
                {rep.title}
              </h3>
              <p className="text-xs text-slate-400 mt-1.5 line-clamp-2">{rep.description}</p>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
              <button
                onClick={() => handleRunReport(rep.code)}
                disabled={executingCode === rep.code}
                className="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold bg-brand-600 hover:bg-brand-500 text-white transition disabled:opacity-50"
              >
                {executingCode === rep.code ? (
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Play className="w-3.5 h-3.5" />
                )}
                Run Report
              </button>

              <button
                onClick={() => handleExportCsv(rep.code)}
                className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition"
                title="Download CSV"
              >
                <Download className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Execution Result Data Table */}
      {executionResult && (
        <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 mt-8 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white">
                  {executionResult.report_title || executionResult.title || "Report Result"}
                </h2>
                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-semibold">
                  {executionResult.result_summary?.row_count ?? executionResult.row_count ?? (executionResult.rows || []).length} Rows
                </span>
                <span className="text-slate-500 text-xs">
                  ({executionResult.execution_time_ms ?? executionResult.execution_duration_ms ?? 0} ms)
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Executed at {new Date(executionResult.created_at || executionResult.executed_at || Date.now()).toLocaleTimeString()}
              </p>
            </div>

            <button
              onClick={() => handleExportCsv(executionResult.report_code)}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 transition"
            >
              <Download className="w-3.5 h-3.5" /> Export CSV
            </button>
          </div>

          <div className="overflow-x-auto border border-slate-800 rounded-xl">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-800/80 text-slate-300 font-semibold uppercase text-[10px] border-b border-slate-800">
                <tr>
                  {(executionResult.headers || executionResult.columns || []).map((col) => (
                    <th key={col} className="px-5 py-3">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {(executionResult.rows || []).map((row, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    {(executionResult.headers || executionResult.columns || []).map((col) => (
                      <td key={col} className="px-5 py-3 text-slate-300 font-medium">
                        {row[col] !== undefined && row[col] !== null ? String(row[col]) : "—"}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
