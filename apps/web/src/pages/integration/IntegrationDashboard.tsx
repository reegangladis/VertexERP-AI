import React from 'react';
import {
  Layers,
  Network,
  Webhook,
  Activity,
  ArrowUpRight,
  Zap,
  CheckCircle2,
} from 'lucide-react';

export default function IntegrationDashboard() {
  const stats = [
    { label: 'Active Connectors', value: '12', change: '+3 this month', icon: <Layers className="h-5 w-5 text-indigo-500" /> },
    { label: 'API Gateway RPS', value: '142 req/s', change: 'Peak: 350 req/s', icon: <Network className="h-5 w-5 text-blue-500" /> },
    { label: 'Registered Webhooks', value: '28', change: '99.98% delivery rate', icon: <Webhook className="h-5 w-5 text-emerald-500" /> },
    { label: 'Queue Messages', value: '1,420 / min', change: 'DLQ depth: 0', icon: <Activity className="h-5 w-5 text-purple-500" /> },
  ];

  const activeConnectors = [
    { name: 'SAP S/4HANA ERP', provider: 'SAP', status: 'Healthy', latency: '42ms', category: 'ERP' },
    { name: 'Salesforce CRM Sync', provider: 'Salesforce', status: 'Healthy', latency: '28ms', category: 'CRM' },
    { name: 'Stripe Global Payments', provider: 'Stripe', status: 'Healthy', latency: '18ms', category: 'Payment' },
    { name: 'AWS S3 Document Lake', provider: 'AWS', status: 'Healthy', latency: '12ms', category: 'Storage' },
    { name: 'SendGrid Email Engine', provider: 'SendGrid', status: 'Healthy', latency: '35ms', category: 'Email' },
    { name: 'OpenAI GPT-4o Copilot', provider: 'OpenAI', status: 'Healthy', latency: '85ms', category: 'AI' },
  ];

  const recentEvents = [
    { event: 'erp.order.created', source: 'SAP Connector', time: '2 mins ago', status: 'Dispatched' },
    { event: 'crm.lead.updated', source: 'Salesforce Connector', time: '5 mins ago', status: 'Dispatched' },
    { event: 'payment.charge.succeeded', source: 'Stripe Webhook', time: '12 mins ago', status: 'Delivered' },
    { event: 'storage.file.uploaded', source: 'S3 Storage Provider', time: '18 mins ago', status: 'Processed' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Enterprise Integration Platform</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time management for API Gateway, Connectors, Webhooks, Event Bus, and Queues.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">
            <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> All Systems Operational
          </span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((item, idx) => (
          <div key={idx} className="p-5 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{item.label}</p>
              <h3 className="text-2xl font-bold mt-1">{item.value}</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{item.change}</p>
            </div>
            <div className="p-3 bg-slate-100 dark:bg-slate-700 rounded-lg">{item.icon}</div>
          </div>
        ))}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Connector Table */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <Layers className="h-5 w-5 text-indigo-500" /> Active Enterprise Connectors
            </h2>
            <button className="text-xs text-indigo-600 dark:text-indigo-400 hover:underline flex items-center gap-1 font-medium">
              View Marketplace <ArrowUpRight className="h-3.5 w-3.5" />
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
                <tr>
                  <th className="px-4 py-3">Connector Name</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Latency</th>
                  <th className="px-4 py-3">Health Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {activeConnectors.map((c, i) => (
                  <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                    <td className="px-4 py-3 font-medium">
                      <div className="font-semibold text-slate-800 dark:text-slate-200">{c.name}</div>
                      <div className="text-xs text-slate-400">{c.provider}</div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono">
                        {c.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs font-mono">{c.latency}</td>
                    <td className="px-4 py-3">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">
                        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mr-1.5"></span>
                        {c.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Live Event Activity Feed */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Zap className="h-5 w-5 text-amber-500" /> Live Event Bus Stream
          </h2>
          <div className="space-y-4">
            {recentEvents.map((e, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-700/40 rounded-lg border border-slate-100 dark:border-slate-700/60">
                <div className="flex items-center justify-between text-xs font-mono text-indigo-600 dark:text-indigo-400 font-semibold">
                  <span>{e.event}</span>
                  <span className="text-slate-400 font-normal">{e.time}</span>
                </div>
                <div className="flex items-center justify-between text-xs mt-2">
                  <span className="text-slate-500 dark:text-slate-400">Src: {e.source}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-medium">
                    {e.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
