import React from 'react';
import {
  RotateCcw,
  CheckCircle2,
  Play,
} from 'lucide-react';

export default function RecoveryCenter() {
  const drMetrics = [
    { label: 'Recovery Point Objective (RPO)', target: '< 15 mins', achieved: '4.2 mins', status: 'Optimal' },
    { label: 'Recovery Time Objective (RTO)', target: '< 60 mins', achieved: '12.4 mins', status: 'Optimal' },
    { label: 'Last DR Simulation Drill', target: 'Monthly', achieved: 'Passed (2026-07-20)', status: 'Optimal' },
  ];

  const restoreHistory = [
    { id: 'rst_901', backup: 'daily_production_snapshot_full', env: 'disaster_recovery_standby', rpo: '4.2m', rto: '12.4m', status: 'VERIFIED', operator: 'admin_dr_op' },
    { id: 'rst_892', backup: 'daily_production_snapshot_full', env: 'staging', rpo: '5.0m', rto: '14.1m', status: 'VERIFIED', operator: 'automated_ci' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Disaster Recovery & PITR Restoration</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Recovery Point Objective (RPO), Recovery Time Objective (RTO), and Point-In-Time Restoration verification.
          </p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
          <Play className="h-4 w-4" /> Simulate DR Failover Drill
        </button>
      </div>

      {/* RPO / RTO SLA Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {drMetrics.map((m, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-2">
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>{m.label}</span>
              <span className="font-mono text-emerald-600 font-bold">{m.status}</span>
            </div>
            <div className="flex items-baseline justify-between">
              <h3 className="text-2xl font-bold text-emerald-600">{m.achieved}</h3>
              <span className="text-xs font-mono text-slate-400">SLA: {m.target}</span>
            </div>
          </div>
        ))}
      </div>

      {/* DR Drill Log Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <RotateCcw className="h-5 w-5 text-indigo-500" /> Historical Restoration & Failover Drills
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Restore Job ID</th>
                <th className="px-4 py-3">Target Environment</th>
                <th className="px-4 py-3">Achieved RPO</th>
                <th className="px-4 py-3">Achieved RTO</th>
                <th className="px-4 py-3">Verification Status</th>
                <th className="px-4 py-3">Executed By</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {restoreHistory.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono text-xs text-slate-500">{r.id}</td>
                  <td className="px-4 py-3 font-medium">{r.env}</td>
                  <td className="px-4 py-3 text-xs font-mono">{r.rpo}</td>
                  <td className="px-4 py-3 text-xs font-mono">{r.rto}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-medium">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> {r.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-500">{r.operator}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
