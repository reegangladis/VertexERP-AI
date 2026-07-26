import React from 'react';
import {
  Globe,
  Activity,
  Server,
  Zap,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Cpu,
} from 'lucide-react';

export default function CloudOperations() {
  const regions = [
    { code: 'us-east-1', name: 'US East (N. Virginia)', provider: 'AWS', role: 'PRIMARY', latency: '12.4 ms', status: 'HEALTHY' },
    { code: 'eu-central-1', name: 'EU Central (Frankfurt)', provider: 'AWS', role: 'SECONDARY', latency: '28.1 ms', status: 'HEALTHY' },
    { code: 'ap-south-1', name: 'APAC (Mumbai)', provider: 'Azure', role: 'SECONDARY', latency: '42.0 ms', status: 'HEALTHY' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Multi-Region Cloud Topology & Operations</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Global Active-Active multi-cloud architecture, Geo-DNS latency tracking, and regional failover controls.
          </p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
          <RefreshCw className="h-4 w-4" /> Trigger Geo-DNS Failover Test
        </button>
      </div>

      {/* Region Map Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {regions.map((r, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">{r.code}</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-bold">
                {r.role}
              </span>
            </div>
            <h3 className="font-bold text-base">{r.name}</h3>
            <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
              <span>Provider: {r.provider}</span>
              <span className="text-emerald-600 font-bold">Latency: {r.latency}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
