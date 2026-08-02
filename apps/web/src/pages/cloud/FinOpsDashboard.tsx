import React from 'react';
import {
  DollarSign,
  PieChart,
  Lightbulb,
} from 'lucide-react';

export default function FinOpsDashboard() {
  const serviceSpend = [
    { service: 'Kubernetes (EKS Worker Nodes)', cost: '$14,200.00', percent: '36.9%' },
    { service: 'PostgreSQL RDS Database', cost: '$11,500.00', percent: '29.9%' },
    { service: 'Redis ElastiCache Cluster', cost: '$3,800.00', percent: '9.8%' },
    { service: 'S3 Object Storage & Backups', cost: '$2,450.00', percent: '6.4%' },
    { service: 'Data Egress & Traffic Routing', cost: '$4,500.00', percent: '11.7%' },
    { service: 'Security WAF & KMS Encryption', cost: '$2,000.00', percent: '5.3%' },
  ];

  const recommendations = [
    { title: 'Purchase AWS Savings Plans / Reserved Instances for EKS', savings: 'Save $3,200 / mo', effort: 'Low' },
    { title: 'Right-size Staging PostgreSQL Instance (db.r6g.xlarge -> large)', savings: 'Save $850 / mo', effort: 'Low' },
    { title: 'Enable S3 Lifecycle Storage Compression Rules', savings: 'Save $420 / mo', effort: 'Medium' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">FinOps Cloud Cost & Budget Optimization</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Multi-cloud resource cost monitoring, budget utilization thresholds, and AI right-sizing recommendations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
            <DollarSign className="h-3.5 w-3.5 mr-1" /> Budget: 76.9% Utilized ($38.4k / $50k)
          </span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Monthly Cloud Spend</p>
          <h3 className="text-3xl font-extrabold mt-1 text-slate-900 dark:text-white">$38,450.00</h3>
          <p className="text-xs text-emerald-600 mt-1">Within monthly $50,000 budget</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Identified Cost Savings</p>
          <h3 className="text-3xl font-extrabold mt-1 text-emerald-600">$4,470.00 / mo</h3>
          <p className="text-xs text-slate-400 mt-1">3 Optimization Opportunities</p>
        </div>
        <div className="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <p className="text-xs text-slate-500 dark:text-slate-400">Budget Health Status</p>
          <h3 className="text-3xl font-extrabold mt-1 text-indigo-600">NORMAL</h3>
          <p className="text-xs text-slate-400 mt-1">Alert Threshold: 85.0%</p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cost Breakdown */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <PieChart className="h-5 w-5 text-indigo-500" /> Cloud Service Cost Breakdown
          </h2>
          <div className="space-y-3">
            {serviceSpend.map((s, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs p-2.5 bg-slate-50 dark:bg-slate-700/40 rounded">
                <span className="font-medium">{s.service}</span>
                <div className="flex items-center gap-3 font-mono">
                  <span className="text-slate-400">{s.percent}</span>
                  <span className="font-bold text-slate-800 dark:text-slate-200">{s.cost}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recommendations */}
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Lightbulb className="h-5 w-5 text-amber-500" /> AI Optimization Recommendations
          </h2>
          <div className="space-y-3">
            {recommendations.map((r, idx) => (
              <div key={idx} className="p-3 bg-slate-50 dark:bg-slate-700/40 rounded-lg border border-slate-100 dark:border-slate-700">
                <h4 className="font-semibold text-xs text-slate-800 dark:text-slate-200">{r.title}</h4>
                <div className="flex items-center justify-between text-xs mt-2 font-mono">
                  <span className="text-emerald-600 font-bold">{r.savings}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300">
                    Effort: {r.effort}
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
