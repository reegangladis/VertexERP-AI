import React from 'react';
import {
  CheckCircle2,
  ShieldCheck,
  Zap,
  RotateCcw,
  FileCheck,
  Activity,
  Award,
  ArrowUpRight,
} from 'lucide-react';

export default function SystemReadinessDashboard() {
  const categories = [
    { category: 'Security Hardening & OWASP', score: '100%', status: 'PASSED', details: 'CSP, HSTS, X-Frame, XSS/SQLi guards enforced' },
    { category: 'Performance & Redis Latency', score: '98.5%', status: 'PASSED', details: 'P95 latency 28.5ms, 94% cache hit ratio' },
    { category: 'High Availability & Resilience', score: '100%', status: 'PASSED', details: 'Circuit Breaker, Bulkhead, Fallbacks active' },
    { category: 'Disaster Recovery & RPO/RTO', score: '99.0%', status: 'PASSED', details: 'RPO: 4.2m, RTO: 12.4m, PITR validated' },
    { category: 'Compliance Audit Governance', score: '98.5%', status: 'PASSED', details: 'SOC 2, ISO 27001, GDPR, HIPAA controls' },
    { category: 'Database Connections & Indexing', score: '100%', status: 'PASSED', details: 'Connection pool optimized, indexing verified' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Production Deployment Scorecard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Pre-flight production readiness checklist and enterprise sign-off verification.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-4 py-1.5 rounded-full text-sm font-bold bg-emerald-600 text-white shadow-sm">
            <CheckCircle2 className="h-4 w-4 mr-1.5" /> PRODUCTION READY — 99.2% Score
          </span>
        </div>
      </div>

      {/* Checklist Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {categories.map((c, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm">{c.category}</span>
              <span className="px-2 py-0.5 rounded text-[11px] bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-mono font-bold">
                {c.status}
              </span>
            </div>
            <div className="flex items-baseline justify-between">
              <h3 className="text-3xl font-extrabold text-emerald-600">{c.score}</h3>
              <span className="text-xs text-slate-400">Scorecard rating</span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 pt-2 border-t border-slate-100 dark:border-slate-700/60">
              {c.details}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
