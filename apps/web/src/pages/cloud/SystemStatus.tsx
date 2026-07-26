import React from 'react';
import {
  CheckCircle2,
  Activity,
  Server,
  Database,
  Lock,
  Globe,
  Award,
} from 'lucide-react';

export default function SystemStatus() {
  const services = [
    { name: 'Core REST API Gateway', status: 'Operational', uptime: '99.99%' },
    { name: 'Multi-Tenant PostgreSQL Cluster', status: 'Operational', uptime: '99.99%' },
    { name: 'Redis Distributed Cache', status: 'Operational', uptime: '100.00%' },
    { name: 'Event Bus & Webhook Engine', status: 'Operational', uptime: '99.98%' },
    { name: 'ML Studio & Inference Pipeline', status: 'Operational', uptime: '99.95%' },
    { name: 'AI Copilot & Vector RAG Store', status: 'Operational', uptime: '99.99%' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Global System Operational Status</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time public system status, SLA uptime tracking, and service availability dashboard.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-emerald-600 text-white shadow-sm">
            <CheckCircle2 className="h-4 w-4 mr-1.5" /> ALL SYSTEMS OPERATIONAL — 99.99% Uptime
          </span>
        </div>
      </div>

      {/* Services Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {services.map((s, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm">{s.name}</span>
              <span className="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-bold">
                {s.status}
              </span>
            </div>
            <div className="flex items-baseline justify-between pt-2 border-t border-slate-100 dark:border-slate-700">
              <span className="text-xs text-slate-400">90-Day Uptime SLA</span>
              <span className="text-lg font-mono font-extrabold text-emerald-600">{s.uptime}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
