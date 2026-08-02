import React from 'react';
import {
  BarChart2,
} from 'lucide-react';

export default function ApiAnalyticsPage() {
  const topEndpoints = [
    { path: '/v1/erp/sync', calls: '45,200', avgLatency: '22.4 ms', p95Latency: '45.1 ms', errors: '0.02%' },
    { path: '/v1/crm/contacts', calls: '32,100', avgLatency: '11.2 ms', p95Latency: '28.0 ms', errors: '0.00%' },
    { path: '/v2/analytics/reports', calls: '18,400', avgLatency: '48.0 ms', p95Latency: '95.2 ms', errors: '0.12%' },
    { path: '/v1/finance/invoices', calls: '12,900', avgLatency: '15.6 ms', p95Latency: '32.4 ms', errors: '0.01%' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">API & Integration Analytics</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time API Gateway traffic distribution, latency percentiles, error rates, and cache hit ratios.
          </p>
        </div>
      </div>

      {/* Analytics KPI Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total API Volume</p>
          <h3 className="text-2xl font-bold mt-1">108,600</h3>
          <p className="text-xs text-emerald-600 mt-1 font-medium">+14.2% vs last week</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Average Latency</p>
          <h3 className="text-2xl font-bold mt-1">16.4 ms</h3>
          <p className="text-xs text-slate-400 mt-1 font-mono">P95: 42.1 ms</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Cache Hit Ratio</p>
          <h3 className="text-2xl font-bold mt-1">34.0 %</h3>
          <p className="text-xs text-indigo-600 mt-1 font-medium">Saved 36,900 DB queries</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Success Rate</p>
          <h3 className="text-2xl font-bold mt-1 text-emerald-600">99.94 %</h3>
          <p className="text-xs text-slate-400 mt-1">70 rate-limit blocks</p>
        </div>
      </div>

      {/* Top Endpoints Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <BarChart2 className="h-5 w-5 text-indigo-500" /> Endpoint Traffic Breakdown
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Endpoint Path</th>
                <th className="px-4 py-3">Call Volume</th>
                <th className="px-4 py-3">Avg Latency</th>
                <th className="px-4 py-3">P95 Latency</th>
                <th className="px-4 py-3">Error Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {topEndpoints.map((ep, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono font-bold text-indigo-600 dark:text-indigo-400">{ep.path}</td>
                  <td className="px-4 py-3 font-medium">{ep.calls}</td>
                  <td className="px-4 py-3 text-xs font-mono">{ep.avgLatency}</td>
                  <td className="px-4 py-3 text-xs font-mono">{ep.p95Latency}</td>
                  <td className="px-4 py-3 text-xs font-mono text-emerald-600">{ep.errors}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
