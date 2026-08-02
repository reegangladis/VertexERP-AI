import React from 'react';
import {
  Zap,
  RotateCcw,
  Plus,
} from 'lucide-react';

export default function EventMonitor() {
  const topics = [
    { name: 'erp.order.created', consumers: 3, retention: '168 hrs', activeEvents: 4500 },
    { name: 'crm.lead.updated', consumers: 2, retention: '168 hrs', activeEvents: 2800 },
    { name: 'payment.charge.failed', consumers: 4, retention: '336 hrs', activeEvents: 120 },
    { name: 'system.audit.log', consumers: 1, retention: '720 hrs', activeEvents: 18900 },
  ];

  const liveEvents = [
    { id: 'evt_98f12a3b', topic: 'erp.order.created', status: 'Published', partition: 'part_0', time: '10:15:02', replayed: false },
    { id: 'evt_44b91d2c', topic: 'crm.lead.updated', status: 'Published', partition: 'part_1', time: '10:14:45', replayed: false },
    { id: 'rpl_11e89f0a', topic: 'payment.charge.failed', status: 'Replayed', partition: 'part_0', time: '10:10:00', replayed: true },
    { id: 'evt_77c24a1b', topic: 'system.audit.log', status: 'Published', partition: 'part_2', time: '10:08:12', replayed: false },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Event Bus Monitor & Replay Engine</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Publish/Subscribe topic streams, Dead Letter Queue (DLQ), and historical event replay.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
            <Plus className="h-4 w-4" /> Create Event Topic
          </button>
        </div>
      </div>

      {/* Topics Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {topics.map((t, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 shadow-sm space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400 truncate">{t.name}</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 font-mono">
                {t.retention}
              </span>
            </div>
            <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>{t.consumers} active consumers</span>
              <span className="font-semibold text-slate-800 dark:text-slate-200">{t.activeEvents.toLocaleString()} evts</span>
            </div>
          </div>
        ))}
      </div>

      {/* Live Event Stream */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Zap className="h-5 w-5 text-amber-500" /> Live Published Events & Replay Logs
          </h2>
          <button className="px-3 py-1.5 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-xs font-medium transition flex items-center gap-1">
            <RotateCcw className="h-3.5 w-3.5" /> Trigger Event Replay
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Event ID</th>
                <th className="px-4 py-3">Topic Name</th>
                <th className="px-4 py-3">Partition Key</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Replayed</th>
                <th className="px-4 py-3">Published Time</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {liveEvents.map((e, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{e.id}</td>
                  <td className="px-4 py-3 font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">{e.topic}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-400">{e.partition}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-indigo-50 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300 font-medium">
                      {e.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono">
                    {e.replayed ? (
                      <span className="text-amber-600 font-bold">Yes (Offset Replay)</span>
                    ) : (
                      <span className="text-slate-400">No</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-400">{e.time}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
