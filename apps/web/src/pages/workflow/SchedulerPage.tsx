import React, { useState } from 'react';
import { Calendar, Plus, Play, Pause, Trash2, Clock, CheckCircle2, XCircle, RefreshCw, AlertTriangle } from 'lucide-react';

interface ScheduledJob {
  id: string;
  name: string;
  workflow: string;
  schedule_type: 'cron' | 'recurring' | 'one_time' | 'delayed';
  cron_expression?: string;
  next_run_at?: string;
  last_run_at?: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  run_count: number;
}

const MOCK_JOBS: ScheduledJob[] = [
  { id: 'j1', name: 'Daily Finance Report', workflow: 'Finance Report Generator', schedule_type: 'cron', cron_expression: '0 8 * * *', next_run_at: '2026-07-27 08:00', last_run_at: '2026-07-26 08:00', status: 'active', run_count: 180 },
  { id: 'j2', name: 'Hourly Inventory Check', workflow: 'Inventory Reorder', schedule_type: 'cron', cron_expression: '0 * * * *', next_run_at: '2026-07-26 23:00', last_run_at: '2026-07-26 22:00', status: 'active', run_count: 4320 },
  { id: 'j3', name: 'Weekly Employee Sync', workflow: 'HRMS Data Sync', schedule_type: 'cron', cron_expression: '0 9 * * 1', next_run_at: '2026-08-02 09:00', last_run_at: '2026-07-26 09:00', status: 'active', run_count: 52 },
  { id: 'j4', name: 'Monthly Payroll Run', workflow: 'Payroll Processing', schedule_type: 'cron', cron_expression: '0 0 1 * *', next_run_at: '2026-08-01 00:00', last_run_at: '2026-07-01 00:00', status: 'paused', run_count: 12 },
  { id: 'j5', name: 'Q3 Budget Review', workflow: 'Budget Approval Flow', schedule_type: 'one_time', next_run_at: '2026-08-01 10:00', status: 'active', run_count: 0 },
];

const CRON_PRESETS = [
  { label: 'Every minute', expr: '* * * * *' },
  { label: 'Every 5 minutes', expr: '*/5 * * * *' },
  { label: 'Every hour', expr: '0 * * * *' },
  { label: 'Daily at 8am', expr: '0 8 * * *' },
  { label: 'Daily at midnight', expr: '0 0 * * *' },
  { label: 'Every Monday 9am', expr: '0 9 * * 1' },
  { label: '1st of month', expr: '0 0 1 * *' },
];

function statusStyle(status: string) {
  if (status === 'active') return { badge: 'wf-badge-success', dot: '#10b981' };
  if (status === 'paused') return { badge: 'wf-badge-warning', dot: '#f59e0b' };
  if (status === 'failed') return { badge: 'wf-badge-danger', dot: '#f87171' };
  return { badge: 'wf-badge-neutral', dot: '#64748b' };
}

export function SchedulerPage() {
  const [jobs, setJobs] = useState<ScheduledJob[]>(MOCK_JOBS);
  const [showCreate, setShowCreate] = useState(false);
  const [newJob, setNewJob] = useState({ name: '', workflow: '', schedule_type: 'cron' as const, cron_expression: '0 8 * * *', next_run_at: '' });
  const [nextRunPreview, setNextRunPreview] = useState<string | null>(null);

  const previewNextRun = (expr: string) => {
    // Simplified preview — in prod this calls API /scheduler/preview-next-run
    const now = new Date();
    now.setHours(now.getHours() + 1);
    setNextRunPreview(now.toLocaleString());
  };

  const toggleJobStatus = (id: string) => {
    setJobs(prev => prev.map(j => j.id === id ? {
      ...j, status: j.status === 'active' ? 'paused' : 'active'
    } : j));
  };

  const deleteJob = (id: string) => setJobs(prev => prev.filter(j => j.id !== id));

  const createJob = () => {
    const job: ScheduledJob = {
      id: `j${Date.now()}`,
      ...newJob,
      status: 'active',
      run_count: 0,
      next_run_at: newJob.next_run_at || '2026-07-27 08:00',
    };
    setJobs(prev => [job, ...prev]);
    setShowCreate(false);
  };

  return (
    <div className="sched-root">
      <div className="sched-header">
        <div>
          <h1 className="wf-page-title"><Calendar className="wf-title-icon" style={{ color: '#f59e0b' }} /> Job Scheduler</h1>
          <p className="wf-page-subtitle">Schedule, manage, and monitor recurring and one-time workflow jobs</p>
        </div>
        <button className="wf-btn wf-btn-primary" onClick={() => setShowCreate(s => !s)}>
          <Plus className="h-4 w-4" /> New Job
        </button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <div className="sched-create-panel">
          <div className="rb-section-label" style={{ marginTop: 0 }}>New Scheduled Job</div>
          <div className="sched-form-grid">
            <div className="rb-field-group">
              <label className="rb-label">Job Name</label>
              <input className="rb-input" placeholder="e.g. Daily Finance Report" value={newJob.name} onChange={e => setNewJob(p => ({ ...p, name: e.target.value }))} />
            </div>
            <div className="rb-field-group">
              <label className="rb-label">Workflow</label>
              <input className="rb-input" placeholder="Workflow name or ID" value={newJob.workflow} onChange={e => setNewJob(p => ({ ...p, workflow: e.target.value }))} />
            </div>
            <div className="rb-field-group">
              <label className="rb-label">Schedule Type</label>
              <select className="rb-input" value={newJob.schedule_type} onChange={e => setNewJob(p => ({ ...p, schedule_type: e.target.value as any }))}>
                <option value="cron">Cron</option>
                <option value="recurring">Recurring</option>
                <option value="one_time">One Time</option>
                <option value="delayed">Delayed</option>
              </select>
            </div>
            {newJob.schedule_type === 'cron' && (
              <div className="rb-field-group">
                <label className="rb-label">Cron Expression</label>
                <div className="sched-cron-row">
                  <input className="rb-input sched-cron-input" value={newJob.cron_expression}
                    onChange={e => { setNewJob(p => ({ ...p, cron_expression: e.target.value })); previewNextRun(e.target.value); }}
                  />
                  <button className="sched-preview-btn" onClick={() => previewNextRun(newJob.cron_expression)}>Preview</button>
                </div>
                {nextRunPreview && <div className="sched-next-preview">Next run: {nextRunPreview}</div>}
              </div>
            )}
            {newJob.schedule_type !== 'cron' && (
              <div className="rb-field-group">
                <label className="rb-label">Run At</label>
                <input type="datetime-local" className="rb-input" onChange={e => setNewJob(p => ({ ...p, next_run_at: e.target.value }))} />
              </div>
            )}
          </div>
          {/* Presets */}
          <div className="sched-presets">
            <span className="rb-label">Quick Presets:</span>
            {CRON_PRESETS.map(p => (
              <button key={p.expr} className="sched-preset-btn" onClick={() => setNewJob(prev => ({ ...prev, cron_expression: p.expr }))}>
                {p.label}
              </button>
            ))}
          </div>
          <div className="sched-form-actions">
            <button className="wf-btn wf-btn-primary" onClick={createJob}><CheckCircle2 className="h-4 w-4" /> Create Job</button>
            <button className="wf-btn wf-btn-ghost" onClick={() => setShowCreate(false)}>Cancel</button>
          </div>
        </div>
      )}

      {/* Job Table */}
      <div className="wf-section" style={{ marginBottom: 0 }}>
        <div className="wf-table-container">
          <table className="wf-table">
            <thead>
              <tr>
                <th>Job Name</th>
                <th>Workflow</th>
                <th>Schedule</th>
                <th>Next Run</th>
                <th>Last Run</th>
                <th>Status</th>
                <th>Runs</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {jobs.map(job => {
                const s = statusStyle(job.status);
                return (
                  <tr key={job.id}>
                    <td className="wf-table-name">
                      <div className="sched-status-dot" style={{ background: s.dot }} />
                      {job.name}
                    </td>
                    <td className="wf-muted">{job.workflow}</td>
                    <td>
                      <span className="wf-trigger-badge">{job.schedule_type}</span>
                      {job.cron_expression && <code className="sched-cron-badge">{job.cron_expression}</code>}
                    </td>
                    <td className="wf-muted">{job.next_run_at || '—'}</td>
                    <td className="wf-muted">{job.last_run_at || '—'}</td>
                    <td><span className={`wf-badge ${s.badge}`}>{job.status}</span></td>
                    <td><span className="sched-run-count">{job.run_count.toLocaleString()}</span></td>
                    <td>
                      <div className="wf-row-actions">
                        <button className="wf-icon-btn" title={job.status === 'active' ? 'Pause' : 'Resume'} onClick={() => toggleJobStatus(job.id)}>
                          {job.status === 'active' ? <Pause className="h-3.5 w-3.5" /> : <Play className="h-3.5 w-3.5" />}
                        </button>
                        <button className="wf-icon-btn wf-icon-btn-success" title="Trigger Now">
                          <RefreshCw className="h-3.5 w-3.5" />
                        </button>
                        <button className="wf-icon-btn" title="Delete" onClick={() => deleteJob(job.id)} style={{ color: '#f87171' }}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <style>{`
        .sched-root { padding: 0; }
        .sched-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
        .sched-create-panel { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; padding: 1.25rem; margin-bottom: 1.25rem; }
        .sched-form-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
        .sched-cron-row { display: flex; gap: 0.5rem; }
        .sched-cron-input { flex: 1; font-family: monospace; }
        .sched-preview-btn { padding: 0.375rem 0.75rem; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 0.375rem; color: #818cf8; font-size: 0.78rem; cursor: pointer; white-space: nowrap; }
        .sched-next-preview { font-size: 0.72rem; color: #10b981; margin-top: 0.3rem; }
        .sched-presets { display: flex; flex-wrap: wrap; gap: 0.375rem; align-items: center; margin-bottom: 1rem; }
        .sched-preset-btn { padding: 0.2rem 0.625rem; border-radius: 9999px; border: 1px solid var(--color-border, #334155); background: var(--color-bg, #0f172a); color: #94a3b8; font-size: 0.72rem; cursor: pointer; transition: all 0.15s; }
        .sched-preset-btn:hover { border-color: #6366f1; color: #818cf8; }
        .sched-form-actions { display: flex; gap: 0.625rem; }
        .sched-status-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; flex-shrink: 0; }
        .sched-cron-badge { font-size: 0.7rem; font-family: monospace; background: rgba(100,116,139,0.12); color: #64748b; padding: 0.1rem 0.375rem; border-radius: 0.25rem; margin-left: 0.375rem; }
        .sched-run-count { font-size: 0.8rem; color: #94a3b8; }
      `}</style>
    </div>
  );
}
