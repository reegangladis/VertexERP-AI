import React, { useState } from 'react';
import {
  Webhook,
  Plus,
  Play,
  ShieldCheck,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Copy,
  ExternalLink,
} from 'lucide-react';

export default function WebhookCenter() {
  const webhooks = [
    { id: '1', name: 'Order Fulfillments Webhook', targetUrl: 'https://api.fulfillment-partner.com/v1/events', events: ['order.created', 'order.shipped'], secret: 'whsec_9a8b7c6d5e4f3a2b1c', status: 'Active', deliveries: 1420 },
    { id: '2', name: 'CRM Contact Sync Endpoint', targetUrl: 'https://hooks.salesforce-partner.io/vertexerp', events: ['crm.contact.updated'], secret: 'whsec_1a2b3c4d5e6f7a8b9c', status: 'Active', deliveries: 890 },
    { id: '3', name: 'Billing Charge Webhook', targetUrl: 'https://finance-service.internal/webhook/payments', events: ['payment.charged', 'payment.failed'], secret: 'whsec_7f8e9d0c1b2a3f4e5d', status: 'Active', deliveries: 310 },
  ];

  const deliveryLogs = [
    { id: 'evt_1', webhook: 'Order Fulfillments Webhook', event: 'order.created', status: 200, latency: '14.2ms', attempt: '1/5', time: '10:14:22' },
    { id: 'evt_2', webhook: 'CRM Contact Sync Endpoint', event: 'crm.contact.updated', status: 200, latency: '22.8ms', attempt: '1/5', time: '10:12:05' },
    { id: 'evt_3', webhook: 'Billing Charge Webhook', event: 'payment.charged', status: 200, latency: '18.1ms', attempt: '1/5', time: '10:05:40' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Webhook Security & Delivery Center</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            HMAC SHA-256 signatures, event subscriptions, exponential backoff retries, and delivery telemetry.
          </p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
          <Plus className="h-4 w-4" /> Register New Webhook
        </button>
      </div>

      {/* Webhook Endpoints Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {webhooks.map((w) => (
          <div key={w.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-bold text-base">{w.name}</h3>
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-50 text-emerald-700 dark:bg-emerald-950/50 dark:text-emerald-300 font-medium mt-1">
                  <CheckCircle2 className="h-3 w-3 mr-1" /> {w.status}
                </span>
              </div>
              <button className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg text-slate-500">
                <Play className="h-4 w-4 text-indigo-500" />
              </button>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-medium text-slate-400 uppercase">Target URL</span>
              <p className="text-xs font-mono text-slate-700 dark:text-slate-300 truncate bg-slate-50 dark:bg-slate-900 p-2 rounded border border-slate-100 dark:border-slate-700/60">
                {w.targetUrl}
              </p>
            </div>

            <div className="space-y-1">
              <span className="text-[11px] font-medium text-slate-400 uppercase">Subscribed Events</span>
              <div className="flex flex-wrap gap-1">
                {w.events.map((e, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-indigo-50 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 rounded text-[11px] font-mono">
                    {e}
                  </span>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
              <span className="font-mono">{w.deliveries} deliveries</span>
              <span className="flex items-center gap-1 text-slate-500 font-mono">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" /> HMAC SHA256
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Webhook Delivery Logs */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Webhook className="h-5 w-5 text-indigo-500" /> Live Webhook Delivery Telemetry
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Event ID</th>
                <th className="px-4 py-3">Webhook Endpoint</th>
                <th className="px-4 py-3">Event Type</th>
                <th className="px-4 py-3">HTTP Status</th>
                <th className="px-4 py-3">Latency</th>
                <th className="px-4 py-3">Attempt</th>
                <th className="px-4 py-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {deliveryLogs.map((l, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{l.id}</td>
                  <td className="px-4 py-3 font-medium">{l.webhook}</td>
                  <td className="px-4 py-3 font-mono text-xs text-indigo-600 dark:text-indigo-400">{l.event}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300 font-mono font-bold">
                      {l.status} OK
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono">{l.latency}</td>
                  <td className="px-4 py-3 text-xs font-mono">{l.attempt}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{l.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
