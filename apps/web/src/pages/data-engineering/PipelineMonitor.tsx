import React, { useEffect, useState } from 'react';
import {
  GitPullRequest,
  Play,
  Clock,
  CheckCircle2,
  RotateCw,
  ArrowRight,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { dataEngineeringApi, ETLJob, ETLRun } from '@/services/dataEngineeringApi';

export function PipelineMonitor() {
  const [jobs, setJobs] = useState<ETLJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggeringId, setTriggeringId] = useState<string | null>(null);
  const [selectedRun, setSelectedRun] = useState<ETLRun | null>(null);
  const [logsModalOpen, setLogsModalOpen] = useState(false);

  const fetchJobs = async () => {
    setLoading(true);
    const data = await dataEngineeringApi.getETLJobs();
    setJobs(data);
    setLoading(false);
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleRunNow = async (jobId: string) => {
    setTriggeringId(jobId);
    const runResult = await dataEngineeringApi.triggerPipelineRun(jobId);
    setSelectedRun(runResult);
    setLogsModalOpen(true);
    setTriggeringId(null);
    fetchJobs();
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="ETL / ELT Pipeline Monitor"
        subtitle="Real-time status, scheduling architecture, incremental ingestion runs, retry mechanisms, and execution logs"
        actions={
          <Button variant="outline" size="sm" onClick={fetchJobs} disabled={loading}>
            <RotateCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Pipelines
          </Button>
        }
      />

      {/* Active Pipeline Jobs Table */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <div>
            <h3 className="text-lg font-semibold text-slate-900">Configured Data Pipeline Jobs</h3>
            <p className="text-xs text-slate-500">Scheduled and trigger-based data pipelines across all enterprise ERP domains</p>
          </div>
          <div className="flex gap-2">
            <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
              <GitPullRequest className="h-3 w-3 mr-1" />
              {jobs.length} Pipelines Configured
            </span>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-600">
            <thead className="bg-slate-50 text-slate-700 uppercase text-xs font-semibold">
              <tr>
                <th className="py-3 px-4">Pipeline Name</th>
                <th className="py-3 px-4">Source & Target</th>
                <th className="py-3 px-4">Frequency</th>
                <th className="py-3 px-4">Load Strategy</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {jobs.map((job) => (
                <tr key={job.id} className="hover:bg-slate-50">
                  <td className="py-3 px-4 font-medium text-slate-900">
                    <div>{job.name}</div>
                    <div className="text-xs text-slate-400 font-normal">{job.description}</div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1.5 text-xs">
                      <span className="font-semibold px-2 py-0.5 bg-slate-100 rounded text-slate-700">{job.source_type}</span>
                      <ArrowRight className="h-3 w-3 text-slate-400" />
                      <span className="font-semibold px-2 py-0.5 bg-indigo-50 rounded text-indigo-700">{job.target_type}</span>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-xs font-mono">
                    <span className="flex items-center gap-1 text-slate-600">
                      <Clock className="h-3 w-3" />
                      {job.frequency} ({job.schedule_cron || 'INTERVAL'})
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${job.is_incremental ? 'bg-emerald-50 text-emerald-700' : 'bg-purple-50 text-purple-700'}`}>
                      {job.is_incremental ? 'Incremental Load' : 'Full Refresh'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      {job.status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">
                    <Button
                      size="sm"
                      variant="primary"
                      onClick={() => handleRunNow(job.id)}
                      disabled={triggeringId === job.id}
                    >
                      <Play className="h-3.5 w-3.5 mr-1" />
                      {triggeringId === job.id ? 'Running...' : 'Run Pipeline'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Execution Logs Modal */}
      <Modal
        isOpen={logsModalOpen}
        onClose={() => setLogsModalOpen(false)}
        title="Pipeline Execution Run Audit Log"
      >
        {selectedRun && (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-2 bg-slate-50 p-3 rounded-lg text-xs">
              <div>
                <span className="text-slate-500">Run Number:</span>
                <p className="font-bold text-slate-900">#{selectedRun.run_number}</p>
              </div>
              <div>
                <span className="text-slate-500">Execution Status:</span>
                <p className="font-bold text-emerald-600 flex items-center">
                  <CheckCircle2 className="h-3.5 w-3.5 mr-1" />
                  {selectedRun.status}
                </p>
              </div>
              <div>
                <span className="text-slate-500">Duration:</span>
                <p className="font-bold text-slate-900">{selectedRun.duration_seconds}s</p>
              </div>
            </div>

            <div className="bg-slate-950 p-4 rounded-lg text-emerald-400 font-mono text-xs space-y-2 overflow-x-auto">
              <p className="text-slate-400">[SYSTEM] Pipeline run initialized at {selectedRun.start_time}</p>
              <p>[EXTRACT] Extracted {selectedRun.rows_extracted} records from source system.</p>
              <p>[TRANSFORM] Enforced schema checks & drop duplicates. {selectedRun.rows_transformed} rows validated clean.</p>
              <p>[LOAD] Successfully loaded {selectedRun.rows_loaded} rows into target warehouse table.</p>
              <p className="text-slate-400">[SUCCESS] Run completed cleanly in {selectedRun.duration_seconds} seconds.</p>
            </div>

            <div className="flex justify-end">
              <Button variant="outline" onClick={() => setLogsModalOpen(false)}>
                Close Execution Log
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
