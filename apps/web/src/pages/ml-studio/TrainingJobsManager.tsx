import React, { useState } from 'react';
import {
  Cpu,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Terminal,
  Plus,
  Server,
  Layers,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';

export function TrainingJobsManager() {
  const [selectedJobId, setSelectedJobId] = useState<string>('JOB-TRAIN-8941');

  const jobs = [
    {
      id: 'JOB-TRAIN-8941',
      name: 'XGBoost Attrition Model Retraining',
      framework: 'XGBOOST',
      dataset: 'DS-HR-ATTRITION',
      status: 'RUNNING',
      progress: 68,
      duration: '02m 45s',
      started_at: '2026-07-26 16:30:10',
    },
    {
      id: 'JOB-TRAIN-8940',
      name: 'Random Forest Customer Churn Baseline',
      framework: 'SCIKIT_LEARN',
      dataset: 'DS-CRM-CHURN',
      status: 'COMPLETED',
      progress: 100,
      duration: '01m 12s',
      started_at: '2026-07-26 15:10:00',
    },
    {
      id: 'JOB-TRAIN-8939',
      name: 'CatBoost Fraud Detector Trial #4',
      framework: 'CATBOOST',
      dataset: 'DS-FIN-FRAUD',
      status: 'FAILED',
      progress: 42,
      duration: '00m 35s',
      error: 'MemoryLimitExceeded: Worker memory threshold exceeded (> 8GB)',
      started_at: '2026-07-26 14:00:00',
    },
  ];

  const logs = [
    '[16:30:10 INFO] Initializing training worker environment on PyTorch-CPU Node-04',
    '[16:30:12 INFO] Loading dataset DS-HR-ATTRITION v1.0 (1,470 records)',
    '[16:30:15 INFO] Preprocessing features using StandardScaler and OneHotEncoder',
    '[16:30:18 INFO] Executing 5-Fold Stratified Cross Validation',
    '[16:30:25 INFO] Fold 1/5 Complete — Train Acc: 0.952, Val Acc: 0.918',
    '[16:30:35 INFO] Fold 2/5 Complete — Train Acc: 0.948, Val Acc: 0.924',
    '[16:30:45 INFO] Fold 3/5 Complete — Train Acc: 0.955, Val Acc: 0.931',
    '[16:30:55 INFO] [RUNNING Epoch 68/100] Log Loss: 0.1852 ...',
  ];

  const selectedJob = jobs.find((j) => j.id === selectedJobId) || jobs[0];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Training Jobs Manager & Worker Queue"
        subtitle="Monitor training job execution, status transitions, stdout log streams, and retry failed worker runs"
        actions={
          <Button variant="primary" icon={<Plus className="w-4 h-4" />}>
            Configure Training Job
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Training Jobs List */}
        <Card className="p-5 space-y-4 lg:col-span-1">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-indigo-500" /> Training Queue
          </h3>

          <div className="space-y-3">
            {jobs.map((job) => (
              <div
                key={job.id}
                onClick={() => setSelectedJobId(job.id)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedJobId === job.id
                    ? 'border-indigo-500 bg-indigo-50/40 dark:bg-indigo-950/40'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">{job.id}</span>
                  <span
                    className={`text-[10px] uppercase font-extrabold px-2 py-0.5 rounded ${
                      job.status === 'RUNNING'
                        ? 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300 animate-pulse'
                        : job.status === 'COMPLETED'
                        ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
                        : 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-300'
                    }`}
                  >
                    {job.status}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white line-clamp-1">{job.name}</h4>
                <div className="mt-2 text-xs text-slate-500 flex justify-between items-center">
                  <span>Framework: {job.framework}</span>
                  <span>{job.duration}</span>
                </div>
                {job.status === 'RUNNING' && (
                  <div className="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full mt-3 overflow-hidden">
                    <div className="bg-indigo-500 h-full transition-all" style={{ width: `${job.progress}%` }} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>

        {/* Right Column: Selected Job Details & Live Logs */}
        <div className="lg:col-span-2 space-y-5">
          <Card className="p-6 space-y-5">
            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
              <div>
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-sm font-bold text-indigo-600 dark:text-indigo-400">{selectedJob.id}</span>
                  <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                    {selectedJob.framework}
                  </span>
                </div>
                <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">{selectedJob.name}</h2>
              </div>
              {selectedJob.status === 'FAILED' && (
                <Button variant="secondary" icon={<RotateCcw className="w-4 h-4" />}>
                  Retry Training Job
                </Button>
              )}
            </div>

            {/* Error banner if failed */}
            {selectedJob.error && (
              <div className="p-4 bg-rose-50 dark:bg-rose-950/50 border border-rose-200 dark:border-rose-800 rounded-lg flex items-center space-x-3 text-rose-800 dark:text-rose-300 text-xs">
                <AlertTriangle className="w-5 h-5 text-rose-500 flex-shrink-0" />
                <span>{selectedJob.error}</span>
              </div>
            )}

            {/* Job Metadata Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 text-xs">
              <div>
                <span className="text-slate-400 uppercase text-[10px]">Dataset Target</span>
                <p className="font-semibold text-slate-900 dark:text-white mt-0.5">{selectedJob.dataset}</p>
              </div>
              <div>
                <span className="text-slate-400 uppercase text-[10px]">Started At</span>
                <p className="font-semibold text-slate-900 dark:text-white mt-0.5">{selectedJob.started_at}</p>
              </div>
              <div>
                <span className="text-slate-400 uppercase text-[10px]">Elapsed Time</span>
                <p className="font-semibold text-slate-900 dark:text-white mt-0.5">{selectedJob.duration}</p>
              </div>
              <div>
                <span className="text-slate-400 uppercase text-[10px]">Worker Node</span>
                <p className="font-semibold text-slate-900 dark:text-white mt-0.5">k8s-worker-ml-04</p>
              </div>
            </div>

            {/* Training Logs Console */}
            <div className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-500" /> Training Stdout Telemetry Stream
              </h4>
              <div className="p-4 bg-black text-emerald-400 font-mono text-xs rounded-lg space-y-1 max-h-72 overflow-y-auto">
                {logs.map((log, idx) => (
                  <div key={idx}>&gt; {log}</div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
