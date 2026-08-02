import React from 'react';
import {
  Tag,
  GitCommit,
  RotateCcw,
  CheckCircle2,
  Layers,
  ShieldCheck,
} from 'lucide-react';

export default function ReleaseDashboard() {
  const releases = [
    {
      version: 'v1.0.0',
      name: 'VertexERP AI Global Enterprise Release',
      type: 'MAJOR',
      status: 'RELEASED',
      sha: 'a7f9b2c',
      date: '2026-07-26',
      author: 'ChiefSoftwareArchitect',
      notes: 'Full 20-phase enterprise platform release supporting global multi-cloud deployment, FinOps, and Zero Trust security.',
    },
    {
      version: 'v0.9.5-rc.2',
      name: 'Phase 19 Production Readiness Candidate',
      type: 'MINOR',
      status: 'ARCHIVED',
      sha: '08049a3',
      date: '2026-07-20',
      author: 'ReleaseEngineeringManager',
      notes: 'OWASP Top 10 hardening, CSP/HSTS headers, and PITR restore drill verification.',
    },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Release Engineering & SemVer Governance</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Semantic Versioning (v1.0.0), Release Candidate approvals, single-click Rollbacks, and Release Notes.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-indigo-600 text-white shadow-sm">
            <Tag className="h-4 w-4 mr-1.5" /> Active Version: v1.0.0
          </span>
        </div>
      </div>

      {/* Release Hero Card */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl p-6 text-white shadow-md space-y-3">
        <div className="flex items-center justify-between">
          <span className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-mono font-bold tracking-wide">
            GLOBAL RELEASE VERIFIED
          </span>
          <span className="text-xs opacity-80">Released 2026-07-26</span>
        </div>
        <h2 className="text-2xl font-extrabold">VertexERP AI v1.0.0 — Enterprise Production Release</h2>
        <p className="text-sm text-indigo-100 max-w-3xl">
          Complete Enterprise AI Operating System ready for global multi-region cloud deployment.
        </p>
        <div className="pt-2 flex items-center gap-4 text-xs">
          <span className="flex items-center gap-1 font-mono"><GitCommit className="h-3.5 w-3.5" /> Commit: a7f9b2c</span>
          <span className="flex items-center gap-1"><ShieldCheck className="h-3.5 w-3.5" /> Security Scan: PASSED</span>
          <span className="flex items-center gap-1"><CheckCircle2 className="h-3.5 w-3.5" /> 100% Tests Passed</span>
        </div>
      </div>

      {/* Release History Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Layers className="h-5 w-5 text-indigo-500" /> Historical Release Version Audit
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Version</th>
                <th className="px-4 py-3">Release Title</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Commit SHA</th>
                <th className="px-4 py-3">Release Date</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {releases.map((r, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-mono font-bold text-indigo-600 dark:text-indigo-400">{r.version}</td>
                  <td className="px-4 py-3 font-medium">{r.name}</td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 rounded text-xs bg-slate-100 dark:bg-slate-700 font-mono">
                      {r.type}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-medium">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> {r.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono text-xs text-slate-400">{r.sha}</td>
                  <td className="px-4 py-3 text-xs text-slate-400">{r.date}</td>
                  <td className="px-4 py-3">
                    <button className="px-2 py-1 text-xs bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 rounded flex items-center gap-1 transition">
                      <RotateCcw className="h-3 w-3 text-slate-500" /> Rollback
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
