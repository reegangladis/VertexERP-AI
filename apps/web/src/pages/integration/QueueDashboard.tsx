import React from 'react';
import {
  Activity,
} from 'lucide-react';

export default function QueueDashboard() {
  const queues = [
    { name: 'inventory_sync_queue', depth: 42, pending: 35, processing: 7, completed: 18900, failed: 0, consumers: 4 },
    { name: 'email_notifications_queue', depth: 12, pending: 10, processing: 2, completed: 42000, failed: 0, consumers: 6 },
    { name: 'payroll_processing_queue', depth: 0, pending: 0, processing: 0, completed: 1250, failed: 0, consumers: 2 },
    { name: 'dlq_poison_messages', depth: 0, pending: 0, processing: 0, completed: 0, failed: 0, consumers: 1 },
  ];

  const recentMessages = [
    { id: 'msg_99a81b2c', queue: 'inventory_sync_queue', status: 'completed', attempts: '1/3', consumer: 'worker_node_01', time: '10:14:50' },
    { id: 'msg_88f72c3d', queue: 'email_notifications_queue', status: 'processing', attempts: '1/3', consumer: 'worker_node_03', time: '10:14:48' },
    { id: 'msg_77e63d4e', queue: 'inventory_sync_queue', status: 'pending', attempts: '0/3', consumer: '-', time: '10:14:42' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Message Queue Dashboard & Consumers</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Producer and Consumer metrics, message tracking, retry counters, and poison message DLQ.
          </p>
        </div>
      </div>

      {/* Queue Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {queues.map((q, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-slate-800 dark:text-slate-200 truncate">{q.name}</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono">
                {q.consumers} workers
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <div>
                <p className="text-xs text-slate-400">Queue Depth</p>
                <h3 className="text-2xl font-bold mt-0.5">{q.depth}</h3>
              </div>
              <div className="text-right text-xs font-mono">
                <p className="text-emerald-600">{q.completed.toLocaleString()} acked</p>
                <p className="text-slate-400">{q.pending} pending</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Live Message Activity Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Activity className="h-5 w-5 text-purple-500" /> Active Queue Message Activity
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Message ID</th>
                <th className="px-4 py-3">Queue Name</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Attempts</th>
                <th className="px-4 py-3">Assigned Consumer</th>
                <th className="px-4 py-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {recentMessages.map((m, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{m.id}</td>
                  <td className="px-4 py-3 font-mono text-xs font-bold text-slate-700 dark:text-slate-300">{m.queue}</td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded text-xs font-medium font-mono ${
                        m.status === 'completed'
                          ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                          : m.status === 'processing'
                          ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300'
                          : 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300'
                      }`}
                    >
                      {m.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono">{m.attempts}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-500">{m.consumer}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{m.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
