import React from 'react';
import {
  Network,
  Key,
  Plus,
  Lock,
} from 'lucide-react';

export default function ApiGatewayPage() {
  const routes = [
    { path: '/v1/erp/sync', target: 'SAP ERP Connector', version: 'v1', rateLimit: '50 RPS', cache: 'Disabled', auth: 'API Key / OAuth2' },
    { path: '/v1/crm/contacts', target: 'Salesforce CRM Connector', version: 'v1', rateLimit: '100 RPS', cache: '60s TTL', auth: 'API Key / OAuth2' },
    { path: '/v2/analytics/reports', target: 'BI Analytics Engine', version: 'v2', rateLimit: '20 RPS', cache: '300s TTL', auth: 'JWT Scope Guard' },
    { path: '/v1/finance/invoices', target: 'Finance Service Core', version: 'v1', rateLimit: '80 RPS', cache: 'Disabled', auth: 'API Key' },
    { path: '/v1/ai/copilot/chat', target: 'AI Copilot Platform', version: 'v1', rateLimit: '15 RPS', cache: 'Disabled', auth: 'JWT Bearer' },
  ];

  const apiKeys = [
    { name: 'Production Backend Gateway Key', prefix: 'vx_live_8f3a...', scopes: 'read, write, admin', created: '2026-07-01', rps: 100 },
    { name: 'Staging Integration Key', prefix: 'vx_test_2b9c...', scopes: 'read, connectors:execute', created: '2026-07-15', rps: 50 },
    { name: 'Mobile App Client Key', prefix: 'vx_live_9d1e...', scopes: 'read', created: '2026-07-20', rps: 30 },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">API Gateway & Routing Policy</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            API versioning, Token Bucket rate limiting, response caching, and key authentication.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
            <Plus className="h-4 w-4" /> Add Gateway Route Policy
          </button>
        </div>
      </div>

      {/* Gateway Policies Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Network className="h-5 w-5 text-indigo-500" /> Active Route Policies & Versioning
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">URI Route Path</th>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Target Backend Service</th>
                <th className="px-4 py-3">Rate Limit</th>
                <th className="px-4 py-3">Cache TTL</th>
                <th className="px-4 py-3">Auth Scheme</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {routes.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono text-indigo-600 dark:text-indigo-400 font-semibold">{r.path}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-700 font-mono font-bold">
                      {r.version}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-700 dark:text-slate-200">{r.target}</td>
                  <td className="px-4 py-3 text-xs font-mono">{r.rateLimit}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-500">{r.cache}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 font-medium">
                      <Lock className="h-3 w-3 mr-1" /> {r.auth}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* API Keys Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Key className="h-5 w-5 text-amber-500" /> Active API Keys & Scopes
          </h2>
          <button className="px-3 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-medium transition flex items-center gap-1">
            <Plus className="h-3.5 w-3.5" /> Generate New Key
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Key Name</th>
                <th className="px-4 py-3">Prefix</th>
                <th className="px-4 py-3">Granted Scopes</th>
                <th className="px-4 py-3">RPS Limit</th>
                <th className="px-4 py-3">Created Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {apiKeys.map((k, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium">{k.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{k.prefix}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 rounded text-xs font-mono">
                      {k.scopes}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono">{k.rps} req/s</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{k.created}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
