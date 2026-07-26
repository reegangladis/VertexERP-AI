import React from 'react';
import {
  AlertOctagon,
  CheckCircle2,
  Clock,
  ShieldAlert,
  UserCheck,
  Plus,
} from 'lucide-react';

export default function IncidentCenter() {
  const incidents = [
    {
      num: 'INC-2026-0042',
      title: 'API Gateway Connection Spike in EU Region',
      sev: 'P2',
      status: 'RESOLVED',
      mttr: '14.5 mins',
      oncall: 'SRE_Duty_Engineer_01',
      date: '2026-07-26 14:20',
      rca: 'Transient Redis cluster connection pool exhaustion during peak traffic',
    },
    {
      num: 'INC-2026-0041',
      title: 'Database Failover Simulation Test',
      sev: 'P3',
      status: 'RESOLVED',
      mttr: '8.2 mins',
      oncall: 'AutoDrillEngine',
      date: '2026-07-20 09:00',
      rca: 'Scheduled monthly disaster recovery failover validation drill',
    },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Operational Incident Response Center</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            P1-P4 incident triage, MTTR SLA telemetry, on-call runbook execution, and RCA logging.
          </p>
        </div>
        <button className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
          <Plus className="h-4 w-4" /> Log Operational Incident
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Mean Time to Resolution (MTTR)</p>
          <h3 className="text-3xl font-extrabold mt-1 text-emerald-600">11.3 mins</h3>
          <p className="text-xs text-slate-400 mt-1">Target SLA: &lt; 30.0 mins</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Active Open Incidents</p>
          <h3 className="text-3xl font-extrabold mt-1 text-slate-900 dark:text-white">0 Open</h3>
          <p className="text-xs text-emerald-600 mt-1 font-medium">All systems normal</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">On-Call Duty SRE</p>
          <h3 className="text-xl font-bold mt-1 text-indigo-600">SRE_Duty_Engineer_01</h3>
          <p className="text-xs text-slate-400 mt-1">Primary Shift (24/7)</p>
        </div>
      </div>

      {/* Incident Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-indigo-500" /> Historical Incident Audit Log
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Incident #</th>
                <th className="px-4 py-3">Title</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">MTTR</th>
                <th className="px-4 py-3">Assigned SRE</th>
                <th className="px-4 py-3">Logged Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {incidents.map((inc, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono font-bold text-slate-600 dark:text-slate-300">{inc.num}</td>
                  <td className="px-4 py-3 font-medium">{inc.title}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 font-mono font-bold">
                      {inc.sev}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-medium">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> {inc.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-indigo-600 dark:text-indigo-400">{inc.mttr}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-500">{inc.oncall}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{inc.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
