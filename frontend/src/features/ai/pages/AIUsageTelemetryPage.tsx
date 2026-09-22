/**
 * AI Usage & Telemetry Dashboard Page
 * VertexERP AI V2
 */

import React, { useEffect, useState } from "react";
import {
  Activity,
  Cpu,
  Coins,
  Layers,
  Wrench,
  Shield,
  Clock,
  AlertCircle,
  BarChart3,
  RefreshCw,
} from "lucide-react";
import { aiApi } from "../api/aiApi";
import { AIUsageSummary, ERPToolInfo } from "../types";

export const AIUsageTelemetryPage: React.FC = () => {
  const [summary, setSummary] = useState<AIUsageSummary | null>(null);
  const [tools, setTools] = useState<ERPToolInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [usageData, toolData] = await Promise.all([
        aiApi.getUsageSummary(),
        aiApi.getAvailableTools(),
      ]);
      setSummary(usageData);
      setTools(toolData.tools);
    } catch (err) {
      console.error("Failed to load AI usage telemetry:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6 bg-slate-950 text-slate-100 min-h-screen">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100 flex items-center space-x-2">
            <Activity className="w-5 h-5 text-indigo-400" />
            <span>AI Platform Telemetry & Observability</span>
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Real-time token consumption, LLM pricing metrics, and registered ERP domain tools.
          </p>
        </div>
        <button
          onClick={loadData}
          disabled={isLoading}
          className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 border border-slate-700 transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Invocations */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total AI Invocations</span>
            <Cpu className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {summary?.total_calls.toLocaleString() || "0"}
          </div>
          <div className="text-[11px] text-slate-500">Across all provider adapters</div>
        </div>

        {/* Total Tokens */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Tokens Consumed</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">
            {summary?.total_tokens.toLocaleString() || "0"}
          </div>
          <div className="text-[11px] text-slate-500">Prompt + Completion Tokens</div>
        </div>

        {/* Total Cost USD */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Estimated Cost</span>
            <Coins className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">
            ${summary?.total_cost_usd.toFixed(4) || "0.0000"}
          </div>
          <div className="text-[11px] text-slate-500">Calculated via live pricing table</div>
        </div>

        {/* Registered Tools */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Active ERP Tools</span>
            <Wrench className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold text-slate-100">{tools.length}</div>
          <div className="text-[11px] text-slate-500">Inventory, Finance, CRM, HR</div>
        </div>
      </div>

      {/* Provider & Model Breakdown Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 text-indigo-400" />
          <span>Provider & Model Telemetry Breakdown</span>
        </h2>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-2.5 px-3">Provider</th>
                <th className="py-2.5 px-3">Model</th>
                <th className="py-2.5 px-3 text-right">Invocations</th>
                <th className="py-2.5 px-3 text-right">Prompt Tokens</th>
                <th className="py-2.5 px-3 text-right">Completion Tokens</th>
                <th className="py-2.5 px-3 text-right">Total Tokens</th>
                <th className="py-2.5 px-3 text-right">Avg Latency</th>
                <th className="py-2.5 px-3 text-right">Total Cost (USD)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {summary?.by_provider && summary.by_provider.length > 0 ? (
                summary.by_provider.map((item, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition">
                    <td className="py-2.5 px-3 font-medium text-slate-200 uppercase">
                      {item.provider}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-[11px] text-indigo-300">
                      {item.model}
                    </td>
                    <td className="py-2.5 px-3 text-right">{item.total_calls}</td>
                    <td className="py-2.5 px-3 text-right text-slate-400">
                      {item.total_prompt_tokens.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-400">
                      {item.total_completion_tokens.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right font-medium text-slate-200">
                      {item.total_tokens.toLocaleString()}
                    </td>
                    <td className="py-2.5 px-3 text-right text-slate-400">
                      {item.avg_latency_ms} ms
                    </td>
                    <td className="py-2.5 px-3 text-right font-medium text-emerald-400">
                      ${item.total_cost_usd.toFixed(6)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={8} className="text-center py-6 text-slate-500">
                    No telemetry records available for this period.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Registered ERP Domain Tools */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-semibold text-slate-200 flex items-center space-x-2">
          <Wrench className="w-4 h-4 text-purple-400" />
          <span>Registered ERP Domain Tools (Zero-Trust Guarded)</span>
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {tools.map((t, idx) => (
            <div
              key={idx}
              className="p-3.5 rounded-lg border border-slate-800 bg-slate-950/50 space-y-2"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-semibold text-indigo-300">
                  {t.name}
                </span>
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                    t.is_mutation
                      ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                      : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  }`}
                >
                  {t.is_mutation ? "Mutation (Requires Confirmation)" : "Read Query"}
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-normal">{t.description}</p>
              <div className="text-[10px] text-slate-500 font-mono">
                ACTION: {t.action_type}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
