import React from 'react';
import {
  Play,
  HardDrive,
} from 'lucide-react';

export default function BackupCenter() {
  const backups = [
    { id: 'bak_001', name: 'daily_production_snapshot_full', type: 'FULL', status: 'COMPLETED', size: '4.85 GB', sha256: 'e3b0c442...', duration: '2m 22s', date: '2026-07-26 02:00' },
    { id: 'bak_002', name: 'hourly_incremental_log_04', type: 'INCREMENTAL', status: 'COMPLETED', size: '124 MB', sha256: '8f947761...', duration: '12s', date: '2026-07-26 10:00' },
    { id: 'bak_003', name: 'hourly_incremental_log_03', type: 'INCREMENTAL', status: 'COMPLETED', size: '98 MB', sha256: '77c24a1b...', duration: '10s', date: '2026-07-26 09:00' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Database Backup & Storage Snapshot Center</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Automated database backup schedules, SHA-256 integrity checksums, and encrypted storage.
          </p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
          <Play className="h-4 w-4" /> Trigger Immediate Snapshot
        </button>
      </div>

      {/* Snapshot Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Latest Snapshot</p>
          <h3 className="text-xl font-bold mt-1">daily_production_snapshot_full</h3>
          <p className="text-xs text-emerald-600 mt-1 font-medium">SHA-256 Checksum Verified</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total Backup Storage</p>
          <h3 className="text-2xl font-bold mt-1">142.8 GB</h3>
          <p className="text-xs text-slate-400 mt-1">Retention: 90 days</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Backup SLA Compliance</p>
          <h3 className="text-2xl font-bold mt-1 text-emerald-600">100 %</h3>
          <p className="text-xs text-slate-400 mt-1">Next backup in 4 hours</p>
        </div>
      </div>

      {/* Backups Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <HardDrive className="h-5 w-5 text-indigo-500" /> Historical Snapshot Inventory
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Snapshot Name</th>
                <th className="px-4 py-3">Backup Type</th>
                <th className="px-4 py-3">Size</th>
                <th className="px-4 py-3">SHA-256 Checksum</th>
                <th className="px-4 py-3">Duration</th>
                <th className="px-4 py-3">Completed Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {backups.map((b, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium">{b.name}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-700 font-mono font-bold">
                      {b.type}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-xs font-mono">{b.size}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-400">{b.sha256}</td>
                  <td className="px-4 py-3 text-xs font-mono">{b.duration}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{b.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
