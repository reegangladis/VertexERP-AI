import React from 'react';
import {
  Play,
  Server,
} from 'lucide-react';

export default function DeploymentDashboard() {
  const environments = [
    { name: 'Production (US-East)', version: 'v1.0.0', strategy: 'CANARY', canarySplit: '100%', status: 'HEALTHY', provider: 'AWS EKS' },
    { name: 'Production (EU-Central)', version: 'v1.0.0', strategy: 'CANARY', canarySplit: '100%', status: 'HEALTHY', provider: 'AWS EKS' },
    { name: 'Production (APAC-Mumbai)', version: 'v1.0.0', strategy: 'BLUE_GREEN', canarySplit: '100%', status: 'HEALTHY', provider: 'Azure AKS' },
    { name: 'Staging Environment', version: 'v1.0.1-rc.1', strategy: 'ROLLING', canarySplit: '100%', status: 'HEALTHY', provider: 'GCP GKE' },
  ];

  return (
    <div className="p-6 space-y-6 bg-slate-50 dark:bg-slate-900 min-h-screen text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Multi-Region Deployment Dashboard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Canary traffic splits, Blue-Green deployments, and Kubernetes cluster environment status.
          </p>
        </div>
        <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium shadow-sm transition flex items-center gap-1.5">
          <Play className="h-4 w-4" /> Trigger New Deployment
        </button>
      </div>

      {/* Environments Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {environments.map((env, idx) => (
          <div key={idx} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Server className="h-5 w-5 text-indigo-500" />
                <h3 className="font-bold text-base">{env.name}</h3>
              </div>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-mono bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 font-bold">
                {env.status}
              </span>
            </div>

            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="p-2 bg-slate-50 dark:bg-slate-700/40 rounded">
                <span className="text-slate-400 block">Version</span>
                <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">{env.version}</span>
              </div>
              <div className="p-2 bg-slate-50 dark:bg-slate-700/40 rounded">
                <span className="text-slate-400 block">Strategy</span>
                <span className="font-mono font-bold">{env.strategy}</span>
              </div>
              <div className="p-2 bg-slate-50 dark:bg-slate-700/40 rounded">
                <span className="text-slate-400 block">Cloud Provider</span>
                <span className="font-mono text-slate-700 dark:text-slate-300">{env.provider}</span>
              </div>
            </div>

            {/* Traffic Split Slider */}
            <div className="space-y-1.5 pt-2 border-t border-slate-100 dark:border-slate-700">
              <div className="flex justify-between text-xs text-slate-500">
                <span>Canary Traffic Allocation</span>
                <span className="font-mono font-bold text-indigo-600">{env.canarySplit}</span>
              </div>
              <div className="w-full bg-slate-200 dark:bg-slate-700 h-2 rounded-full overflow-hidden">
                <div className="bg-indigo-600 h-full rounded-full" style={{ width: env.canarySplit }}></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
