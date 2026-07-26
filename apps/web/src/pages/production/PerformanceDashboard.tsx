import React from 'react';
import {
  Activity,
  Zap,
  TrendingUp,
  Clock,
  Database,
  Layers,
  BarChart2,
  CheckCircle2,
} from 'lucide-react';

export default function PerformanceDashboard() {
  const benchmarks = [
    { metric: 'API Average Response Time', value: '14.2 ms', target: '< 50 ms', status: 'Optimal' },
    { metric: 'P95 Response Latency', value: '28.5 ms', target: '< 100 ms', status: 'Optimal' },
    { metric: 'P99 Response Latency', value: '48.1 ms', target: '< 200 ms', status: 'Optimal' },
    { metric: 'Peak Throughput (RPS)', value: '1,450 req/s', target: '> 1,000 req/s', status: 'Optimal' },
    { metric: 'Redis Cache Hit Ratio', value: '94.2 %', target: '> 85.0 %', status: 'Optimal' },
    { metric: 'DB Connection Pool Util', value: '18 / 50 active', target: '< 80%', status: 'Optimal' },
  ];

  const slowQueries = [
    { query: 'SELECT * FROM inventory_transactions WHERE timestamp > ...', avgTime: '42.1 ms', calls: 140, indexUsed: 'idx_trans_timestamp' },
    { query: 'SELECT count(*) FROM audit_logs WHERE organization_id = ...', avgTime: '38.5 ms', calls: 320, indexUsed: 'idx_audit_org_id' },
    { query: 'SELECT * FROM ml_experiments WHERE status = ...', avgTime: '25.0 ms', calls: 85, indexUsed: 'idx_ml_exp_status' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Performance & Reliability Optimization</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Latency percentiles, DB query profiling, Redis caching efficiency, and Circuit Breaker telemetry.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">
            <Zap className="h-3.5 w-3.5 mr-1" /> Latency Targets Met
          </span>
        </div>
      </div>

      {/* Benchmark Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {benchmarks.map((b, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>{b.metric}</span>
              <span className="font-mono text-emerald-600 font-bold">{b.status}</span>
            </div>
            <div className="flex items-baseline justify-between">
              <h3 className="text-2xl font-bold">{b.value}</h3>
              <span className="text-xs font-mono text-slate-400">Target: {b.target}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Query Profiling Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Database className="h-5 w-5 text-indigo-500" /> Database Query Profiler & Index Optimizer
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">SQL Query Snippet</th>
                <th className="px-4 py-3">Avg Execution</th>
                <th className="px-4 py-3">Call Count</th>
                <th className="px-4 py-3">Active Index</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {slowQueries.map((q, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono text-xs text-slate-700 dark:text-slate-300 truncate max-w-md">{q.query}</td>
                  <td className="px-4 py-3 font-mono text-xs text-indigo-600 dark:text-indigo-400">{q.avgTime}</td>
                  <td className="px-4 py-3 text-xs font-mono">{q.calls}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono">
                      {q.indexUsed}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
