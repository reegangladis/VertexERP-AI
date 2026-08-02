import React from 'react';
import {
  FileCheck,
  CheckCircle2,
  Download,
} from 'lucide-react';

export default function ComplianceCenter() {
  const frameworks = [
    { name: 'SOC 2 Type II', score: '98.5%', status: 'Compliant', passed: 42, failed: 1, lastAudit: '2026-07-20' },
    { name: 'ISO / IEC 27001', score: '96.0%', status: 'Compliant', passed: 114, failed: 4, lastAudit: '2026-07-15' },
    { name: 'GDPR (EU Data Protection)', score: '100.0%', status: 'Compliant', passed: 28, failed: 0, lastAudit: '2026-07-22' },
    { name: 'HIPAA Security Architecture', score: '99.0%', status: 'Compliant', passed: 36, failed: 1, lastAudit: '2026-07-18' },
  ];

  const controls = [
    { control: 'Data Encryption at Rest (AES-256-GCM)', framework: 'SOC 2 / ISO 27001', status: 'Passed' },
    { control: 'TLS 1.3 Transport Encryption', framework: 'SOC 2 / GDPR', status: 'Passed' },
    { control: 'Multi-Tenant Scoped RBAC Authorization', framework: 'All Frameworks', status: 'Passed' },
    { control: 'GDPR Right-to-be-Forgotten Data Anonymizer', framework: 'GDPR', status: 'Passed' },
    { control: 'Immutable Administrative Audit Logs', framework: 'SOC 2 / ISO 27001', status: 'Passed' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Enterprise Compliance Center</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            SOC 2 Type II, ISO 27001, GDPR, and HIPAA security compliance governance.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
            <Download className="h-4 w-4" /> Export SOC 2 Audit Report
          </button>
        </div>
      </div>

      {/* Framework Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {frameworks.map((f, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm">{f.name}</span>
              <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-medium">
                {f.status}
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <h3 className="text-2xl font-bold text-emerald-600">{f.score}</h3>
              <span className="text-xs text-slate-400">{f.passed} / {f.passed + f.failed} controls</span>
            </div>
            <p className="text-[11px] text-slate-400">Last audit: {f.lastAudit}</p>
          </div>
        ))}
      </div>

      {/* Control Status Table */}
      <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileCheck className="h-5 w-5 text-indigo-500" /> Automated Compliance Verification Matrix
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400 text-xs uppercase font-medium">
              <tr>
                <th className="px-4 py-3">Control Requirement</th>
                <th className="px-4 py-3">Target Frameworks</th>
                <th className="px-4 py-3">Verification Result</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {controls.map((c, i) => (
                <tr key={i} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/30">
                  <td className="px-4 py-3 font-medium">{c.control}</td>
                  <td className="px-4 py-3 text-xs font-mono text-slate-500">{c.framework}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-medium">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> {c.status}
                    </span>
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
