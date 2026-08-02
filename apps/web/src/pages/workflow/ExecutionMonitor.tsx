import React, { useState } from 'react';
import { Activity, CheckCircle2, XCircle, RefreshCw, X, Search, AlertCircle, Zap } from 'lucide-react';

type ExecStatus = 'completed' | 'running' | 'failed' | 'cancelled' | 'pending';
type StepStatus = 'completed' | 'running' | 'failed' | 'skipped' | 'pending';

interface ExecStep { step_key: string; step_name: string; step_type: string; status: StepStatus; duration_ms?: number; retry_count: number; input?: any; output?: any; error?: string; }
interface Execution { id: string; workflow: string; status: ExecStatus; trigger_type: string; started_at: string; duration_ms?: number; steps: ExecStep[]; error?: string; }

const MOCK_EXECUTIONS: Execution[] = [
  {
    id: 'ex1', workflow: 'Employee Onboarding', status: 'completed', trigger_type: 'Manual', started_at: '2026-07-26 22:00:01', duration_ms: 1242,
    steps: [
      { step_key: 'trigger', step_name: 'Manual Trigger', step_type: 'trigger', status: 'completed', duration_ms: 5, retry_count: 0 },
      { step_key: 'condition', step_name: 'Check Level', step_type: 'condition', status: 'completed', duration_ms: 12, retry_count: 0, output: { branch: 'senior' } },
      { step_key: 'approval', step_name: 'Manager Approval', step_type: 'approval', status: 'completed', duration_ms: 850, retry_count: 0 },
      { step_key: 'ai_copilot', step_name: 'AI Welcome Summary', step_type: 'ai_copilot', status: 'completed', duration_ms: 375, retry_count: 0 },
    ],
  },
  {
    id: 'ex2', workflow: 'Invoice Approval', status: 'running', trigger_type: 'ERP Event', started_at: '2026-07-26 21:55:00', duration_ms: undefined,
    steps: [
      { step_key: 'trigger', step_name: 'ERP Trigger', step_type: 'trigger', status: 'completed', duration_ms: 3, retry_count: 0 },
      { step_key: 'rule_check', step_name: 'High-Value Rule', step_type: 'condition', status: 'completed', duration_ms: 8, retry_count: 0 },
      { step_key: 'approval_l1', step_name: 'Finance Approval', step_type: 'approval', status: 'running', retry_count: 0 },
      { step_key: 'notify', step_name: 'Send Notification', step_type: 'action', status: 'pending', retry_count: 0 },
    ],
  },
  {
    id: 'ex3', workflow: 'Lead Scoring', status: 'failed', trigger_type: 'AI Event', started_at: '2026-07-26 21:00:00', duration_ms: 4500, error: 'ML model timeout after 4500ms',
    steps: [
      { step_key: 'trigger', step_name: 'AI Event Trigger', step_type: 'trigger', status: 'completed', duration_ms: 4, retry_count: 0 },
      { step_key: 'ml_predict', step_name: 'ML Prediction', step_type: 'ml_prediction', status: 'failed', duration_ms: 4496, retry_count: 2, error: 'Timeout' },
      { step_key: 'action', step_name: 'Update CRM', step_type: 'action', status: 'skipped', retry_count: 0 },
    ],
  },
];

function stepIcon(status: StepStatus) {
  if (status === 'completed') return <CheckCircle2 className="h-4 w-4" style={{ color: '#34d399' }} />;
  if (status === 'running') return <div className="em-spin"><RefreshCw className="h-4 w-4" style={{ color: '#38bdf8' }} /></div>;
  if (status === 'failed') return <XCircle className="h-4 w-4" style={{ color: '#f87171' }} />;
  if (status === 'skipped') return <div className="h-4 w-4 rounded-full bg-slate-700 flex items-center justify-center"><span style={{ fontSize: 8, color: '#64748b' }}>–</span></div>;
  return <div className="h-4 w-4 rounded-full" style={{ background: '#334155', border: '2px solid #475569' }} />;
}

function execStatusBadge(s: ExecStatus) {
  if (s === 'completed') return 'wf-badge-success';
  if (s === 'running') return 'wf-badge-info';
  if (s === 'failed') return 'wf-badge-danger';
  if (s === 'cancelled') return 'wf-badge-neutral';
  return 'wf-badge-warning';
}

export function ExecutionMonitor() {
  const [executions] = useState<Execution[]>(MOCK_EXECUTIONS);
  const [selectedId, setSelectedId] = useState<string | null>('ex1');
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [selectedStep, setSelectedStep] = useState<ExecStep | null>(null);

  const selected = executions.find(e => e.id === selectedId);
  const filtered = executions.filter(e => {
    const matchSearch = !search || e.workflow.toLowerCase().includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || e.status === statusFilter;
    return matchSearch && matchStatus;
  });

  return (
    <div className="em-root">
      <div className="em-header">
        <div>
          <h1 className="wf-page-title"><Activity className="wf-title-icon" style={{ color: '#8b5cf6' }} /> Execution Monitor</h1>
          <p className="wf-page-subtitle">Real-time workflow execution tracking, step inspection, and log viewer</p>
        </div>
        <div className="em-header-stats">
          <div className="ac-stat"><RefreshCw className="h-4 w-4" style={{ color: '#38bdf8', animation: 'spin 2s linear infinite' }} /><strong>{executions.filter(e => e.status === 'running').length}</strong> Running</div>
          <div className="ac-stat"><CheckCircle2 className="h-4 w-4" style={{ color: '#34d399' }} /><strong>{executions.filter(e => e.status === 'completed').length}</strong> Completed</div>
          <div className="ac-stat"><XCircle className="h-4 w-4" style={{ color: '#f87171' }} /><strong>{executions.filter(e => e.status === 'failed').length}</strong> Failed</div>
        </div>
      </div>

      <div className="em-body">
        {/* List */}
        <div className="em-list-col">
          <div className="em-search-row">
            <div className="em-search-wrap">
              <Search className="em-search-icon" />
              <input className="em-search" placeholder="Search workflows…" value={search} onChange={e => setSearch(e.target.value)} />
            </div>
          </div>
          <div className="ac-filters" style={{ marginBottom: '0.75rem' }}>
            {['all', 'running', 'completed', 'failed', 'cancelled'].map(s => (
              <button key={s} className={`ac-filter-btn ${statusFilter === s ? 'active' : ''}`} onClick={() => setStatusFilter(s)}>{s}</button>
            ))}
          </div>
          <div className="em-exec-list">
            {filtered.map(ex => (
              <div key={ex.id} className={`em-exec-card ${selectedId === ex.id ? 'em-exec-selected' : ''}`} onClick={() => { setSelectedId(ex.id); setSelectedStep(null); }}>
                <div className="em-exec-top">
                  <Zap className="h-3.5 w-3.5" style={{ color: '#818cf8', flexShrink: 0 }} />
                  <span className="em-exec-name">{ex.workflow}</span>
                  <span className={`wf-badge ${execStatusBadge(ex.status)}`}>{ex.status}</span>
                </div>
                <div className="em-exec-meta">
                  <span className="wf-trigger-badge">{ex.trigger_type}</span>
                  <span className="wf-muted" style={{ fontSize: '0.72rem' }}>{ex.started_at}</span>
                  {ex.duration_ms && <span className="em-duration">{(ex.duration_ms / 1000).toFixed(2)}s</span>}
                </div>
                <div className="em-step-bar">
                  {ex.steps.map(s => (
                    <div key={s.step_key} className={`em-step-seg em-seg-${s.status}`} title={s.step_name} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Detail */}
        {selected ? (
          <div className="em-detail-col">
            {/* Execution Header */}
            <div className="em-detail-header">
              <div>
                <div className="em-detail-title">{selected.workflow}</div>
                <div className="em-detail-meta">
                  <span className={`wf-badge ${execStatusBadge(selected.status)}`}>{selected.status}</span>
                  <span className="wf-trigger-badge">{selected.trigger_type}</span>
                  <span className="wf-muted" style={{ fontSize: '0.78rem' }}>Started: {selected.started_at}</span>
                  {selected.duration_ms && <span className="wf-muted" style={{ fontSize: '0.78rem' }}>Duration: {(selected.duration_ms / 1000).toFixed(2)}s</span>}
                </div>
              </div>
              {selected.status === 'running' && (
                <button className="wf-btn" style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', color: '#f87171', fontSize: '0.8rem', padding: '0.375rem 0.75rem' }}>
                  <X className="h-3.5 w-3.5" /> Cancel
                </button>
              )}
              {selected.status === 'failed' && (
                <button className="wf-btn wf-btn-primary" style={{ fontSize: '0.8rem', padding: '0.375rem 0.75rem' }}>
                  <RefreshCw className="h-3.5 w-3.5" /> Retry
                </button>
              )}
            </div>

            {selected.error && (
              <div className="em-error-bar">
                <AlertCircle className="h-4 w-4" /> {selected.error}
              </div>
            )}

            {/* Step Timeline */}
            <div className="em-timeline-section">
              <div className="rb-section-label" style={{ marginTop: 0 }}>Step Timeline</div>
              <div className="em-timeline">
                {selected.steps.map((step, idx) => (
                  <div key={step.step_key} className={`em-timeline-item ${selectedStep?.step_key === step.step_key ? 'em-timeline-selected' : ''}`}
                    onClick={() => setSelectedStep(selectedStep?.step_key === step.step_key ? null : step)}>
                    <div className="em-timeline-icon">{stepIcon(step.status)}</div>
                    {idx < selected.steps.length - 1 && <div className="em-timeline-connector" />}
                    <div className="em-timeline-body">
                      <div className="em-timeline-name">{step.step_name}</div>
                      <div className="em-timeline-meta">
                        <span className="wf-trigger-badge">{step.step_type.replace('_', ' ')}</span>
                        {step.duration_ms && <span style={{ fontSize: '0.72rem', color: '#64748b' }}>{step.duration_ms}ms</span>}
                        {step.retry_count > 0 && <span style={{ fontSize: '0.72rem', color: '#f59e0b' }}>↺{step.retry_count}</span>}
                      </div>
                      {step.error && <div className="em-step-error">{step.error}</div>}
                      {selectedStep?.step_key === step.step_key && (
                        <div className="em-step-detail">
                          {step.output && (
                            <div>
                              <div className="rb-label" style={{ marginBottom: '0.25rem' }}>Output</div>
                              <pre className="em-json-view">{JSON.stringify(step.output, null, 2)}</pre>
                            </div>
                          )}
                          {step.input && (
                            <div>
                              <div className="rb-label" style={{ marginBottom: '0.25rem' }}>Input</div>
                              <pre className="em-json-view">{JSON.stringify(step.input, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Log Viewer */}
            <div className="em-log-section">
              <div className="rb-section-label">Execution Log</div>
              <div className="em-log-viewer">
                {selected.steps.map(s => (
                  <div key={s.step_key} className={`em-log-line em-log-${s.status === 'failed' ? 'error' : 'info'}`}>
                    <span className="em-log-level">{s.status === 'failed' ? 'ERROR' : 'INFO '}</span>
                    <span className="em-log-step">[{s.step_key}]</span>
                    <span>{s.step_name} → {s.status}{s.duration_ms ? ` (${s.duration_ms}ms)` : ''}{s.error ? ` — ${s.error}` : ''}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="ac-no-selection"><Activity className="h-12 w-12" style={{ color: '#1e3a5f' }} /><p>Select an execution to inspect</p></div>
        )}
      </div>

      <style>{`
        .em-root { padding: 0; }
        .em-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem; }
        .em-header-stats { display: flex; gap: 1.25rem; flex-wrap: wrap; }
        .em-body { display: grid; grid-template-columns: 320px 1fr; gap: 1rem; }
        .em-list-col { display: flex; flex-direction: column; gap: 0; }
        .em-search-row { margin-bottom: 0.75rem; }
        .em-search-wrap { position: relative; }
        .em-search-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 0.875rem; height: 0.875rem; color: #64748b; }
        .em-search { width: 100%; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.5rem; padding: 0.5rem 0.75rem 0.5rem 2.25rem; font-size: 0.8rem; color: var(--color-text-primary, #f1f5f9); }
        .em-search:focus { outline: none; border-color: #6366f1; }
        .em-exec-list { display: flex; flex-direction: column; gap: 0.5rem; max-height: calc(100vh - 350px); overflow-y: auto; }
        .em-exec-card { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.625rem; padding: 0.875rem; cursor: pointer; transition: all 0.15s; }
        .em-exec-card:hover { border-color: #4f6c99; }
        .em-exec-selected { border-color: #8b5cf6; box-shadow: 0 0 0 2px rgba(139,92,246,0.2); }
        .em-exec-top { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.375rem; }
        .em-exec-name { font-size: 0.84rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); flex: 1; }
        .em-exec-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
        .em-duration { font-size: 0.72rem; color: #10b981; }
        .em-step-bar { display: flex; gap: 2px; height: 4px; border-radius: 2px; overflow: hidden; }
        .em-step-seg { flex: 1; border-radius: 2px; }
        .em-seg-completed { background: #10b981; }
        .em-seg-running { background: #38bdf8; animation: pulse 1.5s ease-in-out infinite; }
        .em-seg-failed { background: #f87171; }
        .em-seg-skipped { background: #334155; }
        .em-seg-pending { background: #1e293b; border: 1px solid #334155; }
        .em-detail-col { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; padding: 1.5rem; overflow-y: auto; max-height: calc(100vh - 310px); display: flex; flex-direction: column; gap: 1.25rem; }
        .em-detail-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
        .em-detail-title { font-size: 1.05rem; font-weight: 700; color: var(--color-text-primary, #f1f5f9); margin-bottom: 0.375rem; }
        .em-detail-meta { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
        .em-error-bar { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 0.875rem; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); border-radius: 0.5rem; font-size: 0.8rem; color: #f87171; }
        .em-timeline { position: relative; display: flex; flex-direction: column; gap: 0; }
        .em-timeline-item { display: flex; gap: 0.875rem; align-items: flex-start; position: relative; cursor: pointer; padding: 0.5rem 0.375rem; border-radius: 0.5rem; transition: background 0.15s; }
        .em-timeline-item:hover { background: rgba(99,102,241,0.06); }
        .em-timeline-selected { background: rgba(99,102,241,0.1) !important; }
        .em-timeline-icon { width: 1.5rem; flex-shrink: 0; display: flex; align-items: center; justify-content: center; margin-top: 0.125rem; position: relative; z-index: 1; }
        .em-timeline-connector { position: absolute; left: 0.75rem; top: 2rem; bottom: 0; width: 1px; background: #1e293b; z-index: 0; }
        .em-timeline-body { flex: 1; padding-bottom: 0.5rem; }
        .em-timeline-name { font-size: 0.85rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); margin-bottom: 0.25rem; }
        .em-timeline-meta { display: flex; align-items: center; gap: 0.5rem; }
        .em-step-error { font-size: 0.75rem; color: #f87171; margin-top: 0.25rem; }
        .em-step-detail { margin-top: 0.625rem; display: flex; flex-direction: column; gap: 0.5rem; }
        .em-json-view { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.375rem; padding: 0.625rem; font-size: 0.75rem; color: #94a3b8; font-family: monospace; overflow-x: auto; }
        .em-log-section { }
        .em-log-viewer { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.5rem; padding: 0.75rem; font-family: monospace; font-size: 0.75rem; display: flex; flex-direction: column; gap: 0.25rem; max-height: 200px; overflow-y: auto; }
        .em-log-line { display: flex; gap: 0.75rem; }
        .em-log-info { color: #64748b; }
        .em-log-error { color: #f87171; }
        .em-log-level { font-weight: 700; min-width: 3.5rem; }
        .em-log-step { color: #818cf8; min-width: 5rem; }
        .em-spin { animation: spin 1.5s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
        @media (max-width: 768px) { .em-body { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  );
}
