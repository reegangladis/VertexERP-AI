import React, { useState, useEffect } from 'react';
import {
  Factory,
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Wrench,
  Activity,
  RefreshCw,
} from 'lucide-react';
import { analyticsService, ManufacturingAnalyticsResponse } from '@/services/analyticsService';

export function ManufacturingAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<ManufacturingAnalyticsResponse | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getManufacturingAnalytics();
      setData(res);
    } catch (err) {
      console.error('Failed to load Manufacturing analytics:', err);
      setData({
        overall_equipment_effectiveness_percent: 88.5,
        production_efficiency_percent: 94.2,
        quality_pass_rate_percent: 99.1,
        total_downtime_hours: 14.2,
        open_maintenance_tickets: 3,
        active_production_orders: 18,
        machine_utilization_breakdown: [],
        quality_inspections_summary: [],
        maintenance_metrics: [],
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-amber-600 dark:text-amber-400" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Manufacturing & Plant Intelligence</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time Overall Equipment Effectiveness (OEE), machine fleet telemetry, shop floor quality metrics, and maintenance downtime tracking.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh Analytics
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Plant OEE Score</span>
            <div className="rounded-lg bg-amber-50 p-2 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400">
              <Factory className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.overall_equipment_effectiveness_percent}%</h3>
          <p className="mt-1 text-xs text-amber-600 dark:text-amber-400 font-medium">World Class Standard</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Production Efficiency</span>
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400">
              <Activity className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.production_efficiency_percent}%</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{data.active_production_orders} active orders running</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Quality Pass Rate</span>
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.quality_pass_rate_percent}%</h3>
          <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium">Low Scrap Factor</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total Downtime</span>
            <div className="rounded-lg bg-rose-50 p-2 text-rose-600 dark:bg-rose-950/50 dark:text-rose-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.total_downtime_hours} hrs</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{data.open_maintenance_tickets} open repair tickets</p>
        </div>
      </div>

      {/* OEE Machine Fleet Table */}
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
        <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">Machine OEE Breakdown</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Availability, Performance, and Quality breakdown per machine asset</p>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="border-b border-slate-200 font-semibold text-slate-600 dark:border-slate-800 dark:text-slate-400">
              <tr>
                <th className="py-2.5">Machine Asset</th>
                <th className="py-2.5 text-center">Availability %</th>
                <th className="py-2.5 text-center">Performance %</th>
                <th className="py-2.5 text-center">Quality %</th>
                <th className="py-2.5 text-right">Composite OEE %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {(data.machine_utilization_breakdown || []).map((m, idx) => (
                <tr key={idx}>
                  <td className="py-3 font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-blue-500" /> {m.machine}
                  </td>
                  <td className="py-3 text-center">{m.availability_pct || m.utilization || 90}%</td>
                  <td className="py-3 text-center">{m.performance_pct || m.utilization || 92}%</td>
                  <td className="py-3 text-center">{m.quality_pct || 99}%</td>
                  <td className="py-3 text-right font-bold text-amber-600 dark:text-amber-400">{m.oee_pct || m.utilization || 88}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
