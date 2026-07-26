import React from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  Lock,
  Key,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Eye,
  Activity,
} from 'lucide-react';

export default function SecurityDashboard() {
  const securityEvents = [
    { event: 'OWASP SQLi Attempt Blocked', ip: '198.51.100.42', action: 'BLOCKED', severity: 'HIGH', time: '10 mins ago' },
    { event: 'Reflected XSS Input Sanitized', ip: '203.0.113.15', action: 'SANITIZED', severity: 'MEDIUM', time: '25 mins ago' },
    { event: 'Account Lockout Triggered', actor: 'user_dev_01', action: 'LOCKED_15M', severity: 'HIGH', time: '40 mins ago' },
    { event: 'JWT Master Secret Rotated', actor: 'VaultAutoRotate', action: 'COMPLETED', severity: 'INFO', time: '2 hours ago' },
  ];

  const headersStatus = [
    { header: 'Content-Security-Policy (CSP)', status: 'Enforced', value: "default-src 'self'" },
    { header: 'Strict-Transport-Security (HSTS)', status: 'Enforced', value: 'max-age=31536000; includeSubDomains' },
    { header: 'X-Frame-Options', status: 'Enforced', value: 'DENY' },
    { header: 'X-Content-Type-Options', status: 'Enforced', value: 'nosniff' },
    { header: 'Referrer-Policy', status: 'Enforced', value: 'strict-origin-when-cross-origin' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Security Hardening & OWASP Guard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            HTTP Security Headers, OWASP Top 10 defenses, Account Lockouts, and Secret Key Rotation.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300">
            <ShieldCheck className="h-3.5 w-3.5 mr-1" /> OWASP Defenses Active
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">OWASP Blocks (24h)</p>
          <h3 className="text-2xl font-bold mt-1 text-emerald-600">142</h3>
          <p className="text-xs text-slate-400 mt-1">SQLi: 18 • XSS: 124</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Account Lockouts</p>
          <h3 className="text-2xl font-bold mt-1">1 active</h3>
          <p className="text-xs text-slate-400 mt-1">Max 5 attempts / 15m</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Secret Rotation Health</p>
          <h3 className="text-2xl font-bold mt-1 text-indigo-600">100 %</h3>
          <p className="text-xs text-slate-400 mt-1">All secrets &lt; 90 days</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Security Scorecard</p>
          <h3 className="text-2xl font-bold mt-1 text-emerald-600">A+ Grade</h3>
          <p className="text-xs text-emerald-600 mt-1 font-medium">Zero critical CVEs</p>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Headers Panel */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Lock className="h-5 w-5 text-indigo-500" /> Enforced Security Headers
          </h2>
          <div className="space-y-3">
            {headersStatus.map((h, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-700/40 rounded-lg border border-slate-100 dark:border-slate-700/60 flex items-center justify-between">
                <div>
                  <h4 className="font-semibold text-xs text-slate-800 dark:text-slate-200">{h.header}</h4>
                  <p className="text-[11px] font-mono text-slate-400 truncate max-w-xs">{h.value}</p>
                </div>
                <span className="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-medium">
                  {h.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Security Audit Feed */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <ShieldAlert className="h-5 w-5 text-amber-500" /> Real-time Security Event Audit Log
          </h2>
          <div className="space-y-3">
            {securityEvents.map((e, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-700/40 rounded-lg border border-slate-100 dark:border-slate-700/60">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-800 dark:text-slate-200">{e.event}</span>
                  <span className="text-slate-400 font-normal">{e.time}</span>
                </div>
                <div className="flex items-center justify-between text-xs mt-2 font-mono">
                  <span className="text-slate-500">{e.ip || e.actor}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] ${
                      e.severity === 'HIGH'
                        ? 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                        : 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300'
                    }`}
                  >
                    {e.action}
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
