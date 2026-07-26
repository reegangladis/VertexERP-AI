import React, { useState } from 'react';
import {
  LayoutDashboard, Zap, CheckCircle2, XCircle, Clock, TrendingUp,
  Play, Pause, AlertTriangle, Activity, BarChart2, Calendar, Settings
} from 'lucide-react';

interface StatCardProps {
  label: string;
  value: string;
  sub?: string;
  icon: React.ReactNode;
  color: string;
  trend?: string;
}

function StatCard({ label, value, sub, icon, color, trend }: StatCardProps) {
  return (
    <div className="workflow-stat-card">
      <div className="workflow-stat-icon" style={{ background: color }}>{icon}</div>
      <div className="workflow-stat-body">
        <div className="workflow-stat-value">{value}</div>
        <div className="workflow-stat-label">{label}</div>
        {sub && <div className="workflow-stat-sub">{sub}</div>}
        {trend && <div className="workflow-stat-trend">{trend}</div>}
      </div>
    </div>
  );
}

const MOCK_WORKFLOWS = [
  { id: '1', name: 'Employee Onboarding', status: 'published', category: 'HR', lastRun: '2 min ago', executions: 48, successRate: 98 },
  { id: '2', name: 'Invoice Approval', status: 'published', category: 'Finance', lastRun: '15 min ago', executions: 212, successRate: 95 },
  { id: '3', name: 'Lead Scoring AI', status: 'published', category: 'CRM', lastRun: '1 hr ago', executions: 1024, successRate: 99 },
  { id: '4', name: 'Inventory Reorder', status: 'published', category: 'Inventory', lastRun: '3 hr ago', executions: 76, successRate: 100 },
  { id: '5', name: 'Quality Inspection', status: 'draft', category: 'Manufacturing', lastRun: 'Never', executions: 0, successRate: 0 },
];

const MOCK_EXECUTIONS = [
  { id: 'e1', workflow: 'Employee Onboarding', status: 'completed', duration: '1.2s', trigger: 'Manual', time: '2 min ago' },
  { id: 'e2', workflow: 'Invoice Approval', status: 'running', duration: '–', trigger: 'ERP Event', time: '5 min ago' },
  { id: 'e3', workflow: 'Lead Scoring AI', status: 'completed', duration: '0.8s', trigger: 'AI Event', time: '1 hr ago' },
  { id: 'e4', workflow: 'Invoice Approval', status: 'failed', duration: '3.1s', trigger: 'Scheduled', time: '2 hr ago' },
  { id: 'e5', workflow: 'Inventory Reorder', status: 'completed', duration: '0.5s', trigger: 'Database', time: '3 hr ago' },
];

function statusBadge(status: string) {
  const map: Record<string, string> = {
    completed: 'wf-badge-success',
    running: 'wf-badge-info',
    failed: 'wf-badge-danger',
    pending: 'wf-badge-warning',
    published: 'wf-badge-success',
    draft: 'wf-badge-neutral',
  };
  return `wf-badge ${map[status] || 'wf-badge-neutral'}`;
}

export function WorkflowDashboard() {
  const [activeTab, setActiveTab] = useState<'workflows' | 'executions'>('workflows');

  return (
    <div className="wf-dashboard">
      {/* Header */}
      <div className="wf-dashboard-header">
        <div>
          <h1 className="wf-page-title">
            <Zap className="wf-title-icon" />
            Workflow Automation
          </h1>
          <p className="wf-page-subtitle">Monitor, manage, and automate your enterprise workflows</p>
        </div>
        <a href="/workflows/designer" className="wf-btn wf-btn-primary">
          <Play className="h-4 w-4" /> New Workflow
        </a>
      </div>

      {/* Stats */}
      <div className="wf-stats-grid">
        <StatCard label="Total Workflows" value="42" sub="↑ 6 this month" icon={<Zap className="h-5 w-5" />} color="linear-gradient(135deg, #6366f1, #8b5cf6)" trend="+17%" />
        <StatCard label="Running Now" value="7" sub="Live executions" icon={<Activity className="h-5 w-5" />} color="linear-gradient(135deg, #0ea5e9, #38bdf8)" />
        <StatCard label="Completed Today" value="1,284" sub="Success rate 97.2%" icon={<CheckCircle2 className="h-5 w-5" />} color="linear-gradient(135deg, #10b981, #34d399)" trend="+5.3%" />
        <StatCard label="Failed Today" value="36" sub="Auto-retry: 28" icon={<XCircle className="h-5 w-5" />} color="linear-gradient(135deg, #ef4444, #f87171)" />
        <StatCard label="Pending Approvals" value="18" sub="3 overdue" icon={<Clock className="h-5 w-5" />} color="linear-gradient(135deg, #f59e0b, #fbbf24)" />
        <StatCard label="Scheduled Jobs" value="24" sub="Next: in 3 min" icon={<Calendar className="h-5 w-5" />} color="linear-gradient(135deg, #8b5cf6, #a78bfa)" />
      </div>

      {/* Tabs */}
      <div className="wf-section">
        <div className="wf-tabs">
          <button className={`wf-tab ${activeTab === 'workflows' ? 'active' : ''}`} onClick={() => setActiveTab('workflows')}>
            <LayoutDashboard className="h-4 w-4" /> Active Workflows
          </button>
          <button className={`wf-tab ${activeTab === 'executions' ? 'active' : ''}`} onClick={() => setActiveTab('executions')}>
            <Activity className="h-4 w-4" /> Recent Executions
          </button>
        </div>

        {activeTab === 'workflows' && (
          <div className="wf-table-container">
            <table className="wf-table">
              <thead>
                <tr>
                  <th>Workflow Name</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Last Run</th>
                  <th>Executions</th>
                  <th>Success Rate</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_WORKFLOWS.map(wf => (
                  <tr key={wf.id}>
                    <td className="wf-table-name">
                      <Zap className="wf-row-icon" />
                      {wf.name}
                    </td>
                    <td><span className="wf-category-badge">{wf.category}</span></td>
                    <td><span className={statusBadge(wf.status)}>{wf.status}</span></td>
                    <td className="wf-muted">{wf.lastRun}</td>
                    <td>{wf.executions.toLocaleString()}</td>
                    <td>
                      <div className="wf-progress-bar-wrap">
                        <div className="wf-progress-bar" style={{ width: `${wf.successRate}%`, background: wf.successRate >= 95 ? '#10b981' : '#f59e0b' }} />
                        <span>{wf.successRate}%</span>
                      </div>
                    </td>
                    <td>
                      <div className="wf-row-actions">
                        <a href={`/workflows/designer/${wf.id}`} className="wf-icon-btn" title="Edit">
                          <Settings className="h-3.5 w-3.5" />
                        </a>
                        <button className="wf-icon-btn wf-icon-btn-success" title="Execute">
                          <Play className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === 'executions' && (
          <div className="wf-table-container">
            <table className="wf-table">
              <thead>
                <tr>
                  <th>Workflow</th>
                  <th>Status</th>
                  <th>Duration</th>
                  <th>Trigger</th>
                  <th>Time</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_EXECUTIONS.map(ex => (
                  <tr key={ex.id}>
                    <td className="wf-table-name"><Activity className="wf-row-icon" />{ex.workflow}</td>
                    <td><span className={statusBadge(ex.status)}>{ex.status}</span></td>
                    <td>{ex.duration}</td>
                    <td><span className="wf-trigger-badge">{ex.trigger}</span></td>
                    <td className="wf-muted">{ex.time}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="wf-quick-actions">
        <h3 className="wf-section-title">Quick Actions</h3>
        <div className="wf-quick-actions-grid">
          {[
            { label: 'New Workflow', href: '/workflows/designer', icon: <Zap />, color: '#6366f1' },
            { label: 'Rule Builder', href: '/workflows/rules', icon: <Settings />, color: '#0ea5e9' },
            { label: 'Approval Center', href: '/workflows/approvals', icon: <CheckCircle2 />, color: '#10b981' },
            { label: 'Scheduler', href: '/workflows/scheduler', icon: <Calendar />, color: '#f59e0b' },
            { label: 'Execution Monitor', href: '/workflows/executions', icon: <Activity />, color: '#8b5cf6' },
            { label: 'Templates', href: '/workflows/templates', icon: <LayoutDashboard />, color: '#ec4899' },
          ].map(action => (
            <a key={action.label} href={action.href} className="wf-quick-action-card">
              <div className="wf-quick-action-icon" style={{ background: action.color }}>{action.icon}</div>
              <span>{action.label}</span>
            </a>
          ))}
        </div>
      </div>

      <style>{`
        .wf-dashboard { padding: 0; }
        .wf-dashboard-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 2rem; flex-wrap: wrap; gap: 1rem; }
        .wf-page-title { font-size: 1.75rem; font-weight: 700; display: flex; align-items: center; gap: 0.625rem; margin: 0 0 0.25rem; color: var(--color-text-primary, #f1f5f9); }
        .wf-title-icon { color: #818cf8; }
        .wf-page-subtitle { color: var(--color-text-secondary, #94a3b8); font-size: 0.9rem; margin: 0; }
        .wf-btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.25rem; border-radius: 0.5rem; font-size: 0.875rem; font-weight: 600; cursor: pointer; text-decoration: none; transition: all 0.2s; }
        .wf-btn-primary { background: linear-gradient(135deg, #6366f1, #8b5cf6); color: #fff; border: none; box-shadow: 0 4px 14px rgba(99,102,241,0.4); }
        .wf-btn-primary:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(99,102,241,0.5); }
        .wf-stats-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
        .workflow-stat-card { display: flex; align-items: center; gap: 1rem; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; padding: 1.25rem; transition: transform 0.2s, box-shadow 0.2s; }
        .workflow-stat-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.25); }
        .workflow-stat-icon { width: 2.75rem; height: 2.75rem; border-radius: 0.625rem; display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
        .workflow-stat-value { font-size: 1.5rem; font-weight: 700; color: var(--color-text-primary, #f1f5f9); line-height: 1; }
        .workflow-stat-label { font-size: 0.78rem; color: var(--color-text-secondary, #94a3b8); margin-top: 0.2rem; }
        .workflow-stat-sub { font-size: 0.72rem; color: #64748b; margin-top: 0.15rem; }
        .workflow-stat-trend { font-size: 0.75rem; color: #10b981; font-weight: 600; margin-top: 0.2rem; }
        .wf-section { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; overflow: hidden; margin-bottom: 2rem; }
        .wf-tabs { display: flex; border-bottom: 1px solid var(--color-border, #334155); padding: 0 1rem; }
        .wf-tab { display: flex; align-items: center; gap: 0.4rem; padding: 0.875rem 1rem; font-size: 0.875rem; font-weight: 500; color: #64748b; border-bottom: 2px solid transparent; background: none; border-top: none; border-left: none; border-right: none; cursor: pointer; transition: all 0.2s; }
        .wf-tab.active { color: #818cf8; border-bottom-color: #818cf8; }
        .wf-tab:hover { color: var(--color-text-primary, #f1f5f9); }
        .wf-table-container { overflow-x: auto; }
        .wf-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
        .wf-table th { text-align: left; padding: 0.875rem 1.25rem; font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--color-border, #334155); }
        .wf-table td { padding: 0.875rem 1.25rem; border-bottom: 1px solid var(--color-border, #1e293b); color: var(--color-text-primary, #f1f5f9); }
        .wf-table tr:last-child td { border-bottom: none; }
        .wf-table tr:hover td { background: rgba(99,102,241,0.04); }
        .wf-table-name { display: flex; align-items: center; gap: 0.5rem; font-weight: 500; }
        .wf-row-icon { width: 1rem; height: 1rem; color: #818cf8; }
        .wf-muted { color: #64748b !important; font-size: 0.8rem !important; }
        .wf-badge { display: inline-flex; align-items: center; padding: 0.2rem 0.6rem; border-radius: 9999px; font-size: 0.72rem; font-weight: 600; text-transform: capitalize; }
        .wf-badge-success { background: rgba(16,185,129,0.15); color: #34d399; }
        .wf-badge-info { background: rgba(14,165,233,0.15); color: #38bdf8; }
        .wf-badge-danger { background: rgba(239,68,68,0.15); color: #f87171; }
        .wf-badge-warning { background: rgba(245,158,11,0.15); color: #fbbf24; }
        .wf-badge-neutral { background: rgba(100,116,139,0.15); color: #94a3b8; }
        .wf-category-badge { display: inline-flex; padding: 0.2rem 0.6rem; border-radius: 0.25rem; font-size: 0.72rem; font-weight: 500; background: rgba(99,102,241,0.15); color: #818cf8; }
        .wf-trigger-badge { display: inline-flex; padding: 0.2rem 0.6rem; border-radius: 0.25rem; font-size: 0.72rem; background: rgba(14,165,233,0.12); color: #38bdf8; }
        .wf-progress-bar-wrap { display: flex; align-items: center; gap: 0.5rem; }
        .wf-progress-bar-wrap > div { height: 0.375rem; border-radius: 9999px; transition: width 0.4s; }
        .wf-progress-bar-wrap > span { font-size: 0.8rem; color: #94a3b8; min-width: 3rem; }
        .wf-row-actions { display: flex; gap: 0.375rem; }
        .wf-icon-btn { display: flex; align-items: center; justify-content: center; width: 1.75rem; height: 1.75rem; border-radius: 0.375rem; background: rgba(100,116,139,0.15); color: #94a3b8; border: none; cursor: pointer; transition: all 0.15s; }
        .wf-icon-btn:hover { background: rgba(99,102,241,0.2); color: #818cf8; }
        .wf-icon-btn-success:hover { background: rgba(16,185,129,0.2); color: #34d399; }
        .wf-section-title { font-size: 1rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); margin: 0 0 1rem; }
        .wf-quick-actions { margin-bottom: 2rem; }
        .wf-quick-actions-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 0.75rem; }
        .wf-quick-action-card { display: flex; flex-direction: column; align-items: center; gap: 0.625rem; padding: 1.25rem 0.75rem; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; text-decoration: none; color: var(--color-text-secondary, #94a3b8); font-size: 0.8rem; font-weight: 500; transition: all 0.2s; }
        .wf-quick-action-card:hover { transform: translateY(-2px); border-color: #6366f1; color: var(--color-text-primary, #f1f5f9); box-shadow: 0 4px 14px rgba(99,102,241,0.2); }
        .wf-quick-action-icon { width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; display: flex; align-items: center; justify-content: center; color: #fff; }
        .wf-quick-action-icon svg { width: 1.25rem; height: 1.25rem; }
      `}</style>
    </div>
  );
}
