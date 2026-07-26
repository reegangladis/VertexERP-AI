import React, { useState } from 'react';
import { CheckCircle2, XCircle, Clock, Users, AlertTriangle, ChevronRight, MessageSquare, UserCheck, UserX, Send, ArrowRight } from 'lucide-react';

type ApprovalStatus = 'pending' | 'approved' | 'rejected' | 'delegated' | 'escalated';

interface ApprovalLevel { level: number; approver: string; status: ApprovalStatus; timestamp?: string; comments?: string; }
interface ApprovalItem {
  id: string;
  title: string;
  description: string;
  requester: string;
  department: string;
  amount?: number;
  dueDate: string;
  levels: ApprovalLevel[];
  currentLevel: number;
  maxLevels: number;
  status: ApprovalStatus;
  createdAt: string;
}

const MOCK_APPROVALS: ApprovalItem[] = [
  {
    id: 'a1', title: 'Capital Equipment Purchase', description: 'CNC Machine for Manufacturing Plant B',
    requester: 'Ahmad Raza', department: 'Manufacturing', amount: 125000,
    dueDate: '2026-07-28', createdAt: '2026-07-26 09:00', status: 'pending', currentLevel: 2, maxLevels: 3,
    levels: [
      { level: 1, approver: 'Sara Ahmed', status: 'approved', timestamp: '2026-07-26 10:20', comments: 'Looks good.' },
      { level: 2, approver: 'David Chen', status: 'pending' },
      { level: 3, approver: 'CEO', status: 'pending' },
    ],
  },
  {
    id: 'a2', title: 'Hiring: Senior ML Engineer', description: 'New headcount for AI team Q3',
    requester: 'Priya Singh', department: 'AI Platform', dueDate: '2026-07-30', createdAt: '2026-07-25 14:00', status: 'pending', currentLevel: 1, maxLevels: 2,
    levels: [
      { level: 1, approver: 'James Wilson', status: 'pending' },
      { level: 2, approver: 'CHRO', status: 'pending' },
    ],
  },
  {
    id: 'a3', title: 'Marketing Budget Q3 2026', description: 'Digital & trade-show budget increase',
    requester: 'Elena Kowalski', department: 'Marketing', amount: 75000,
    dueDate: '2026-07-27', createdAt: '2026-07-24 16:00', status: 'approved', currentLevel: 2, maxLevels: 2,
    levels: [
      { level: 1, approver: 'Finance Director', status: 'approved', timestamp: '2026-07-25', comments: 'Approved within budget.' },
      { level: 2, approver: 'CFO', status: 'approved', timestamp: '2026-07-26', comments: 'Go ahead.' },
    ],
  },
  {
    id: 'a4', title: 'Remote Work Policy Extension', description: 'Extend remote work arrangement for EU team',
    requester: 'Marco Rossi', department: 'HR', dueDate: '2026-07-29', createdAt: '2026-07-25 11:00', status: 'escalated', currentLevel: 2, maxLevels: 2,
    levels: [
      { level: 1, approver: 'HR Manager', status: 'escalated', comments: 'Escalated due to policy conflict.' },
      { level: 2, approver: 'CHRO', status: 'pending' },
    ],
  },
];

function statusIcon(s: ApprovalStatus) {
  if (s === 'approved') return <CheckCircle2 className="h-4 w-4" style={{ color: '#34d399' }} />;
  if (s === 'rejected') return <XCircle className="h-4 w-4" style={{ color: '#f87171' }} />;
  if (s === 'pending') return <Clock className="h-4 w-4" style={{ color: '#fbbf24' }} />;
  if (s === 'delegated') return <UserCheck className="h-4 w-4" style={{ color: '#38bdf8' }} />;
  if (s === 'escalated') return <AlertTriangle className="h-4 w-4" style={{ color: '#f97316' }} />;
  return null;
}

export function ApprovalCenter() {
  const [approvals, setApprovals] = useState<ApprovalItem[]>(MOCK_APPROVALS);
  const [selectedId, setSelectedId] = useState<string | null>('a1');
  const [comment, setComment] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const selected = approvals.find(a => a.id === selectedId);
  const filtered = filterStatus === 'all' ? approvals : approvals.filter(a => a.status === filterStatus);

  const handleAction = (action: 'approved' | 'rejected' | 'delegated' | 'escalated') => {
    setApprovals(prev => prev.map(a => a.id === selectedId ? { ...a, status: action } : a));
    setComment('');
  };

  return (
    <div className="ac-root">
      <div className="ac-header">
        <div>
          <h1 className="wf-page-title"><CheckCircle2 className="wf-title-icon" style={{ color: '#10b981' }} /> Approval Center</h1>
          <p className="wf-page-subtitle">Review, approve, delegate, and track multi-level approval workflows</p>
        </div>
        <div className="ac-header-stats">
          <div className="ac-stat"><Clock className="h-4 w-4 text-amber-400" /> <strong>{approvals.filter(a => a.status === 'pending').length}</strong> Pending</div>
          <div className="ac-stat"><AlertTriangle className="h-4 w-4 text-orange-400" /> <strong>{approvals.filter(a => a.status === 'escalated').length}</strong> Escalated</div>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="ac-filters">
        {(['all', 'pending', 'approved', 'rejected', 'escalated', 'delegated'] as string[]).map(s => (
          <button key={s} className={`ac-filter-btn ${filterStatus === s ? 'active' : ''}`} onClick={() => setFilterStatus(s)}>
            {s}
          </button>
        ))}
      </div>

      <div className="ac-body">
        {/* Left: Approval List */}
        <div className="ac-list">
          {filtered.map(a => (
            <div key={a.id} className={`ac-card ${selectedId === a.id ? 'ac-card-selected' : ''} ${a.status === 'escalated' ? 'ac-card-urgent' : ''}`}
              onClick={() => setSelectedId(a.id)}>
              <div className="ac-card-top">
                <div className="ac-card-info">
                  <div className="ac-card-title">{a.title}</div>
                  <div className="ac-card-meta">
                    <span className="wf-category-badge">{a.department}</span>
                    {a.amount && <span className="ac-amount">${a.amount.toLocaleString()}</span>}
                  </div>
                </div>
                {statusIcon(a.status)}
              </div>
              <div className="ac-card-bottom">
                <span className="ac-requester"><Users className="h-3 w-3" />{a.requester}</span>
                <span className="ac-due">Due: {a.dueDate}</span>
              </div>
              <div className="ac-level-dots">
                {a.levels.map(l => (
                  <div key={l.level} className={`ac-level-dot ${l.status === 'approved' ? 'ac-dot-approved' : l.status === 'pending' && l.level === a.currentLevel ? 'ac-dot-current' : ''}`} title={l.approver} />
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Right: Detail Panel */}
        {selected ? (
          <div className="ac-detail">
            <div className="ac-detail-title">{selected.title}</div>
            <div className="ac-detail-desc">{selected.description}</div>

            <div className="ac-detail-grid">
              <div><div className="rb-label">Requester</div><div className="ac-detail-val">{selected.requester}</div></div>
              <div><div className="rb-label">Department</div><div className="ac-detail-val">{selected.department}</div></div>
              {selected.amount && <div><div className="rb-label">Amount</div><div className="ac-detail-val ac-amount-large">${selected.amount.toLocaleString()}</div></div>}
              <div><div className="rb-label">Due Date</div><div className="ac-detail-val">{selected.dueDate}</div></div>
            </div>

            {/* Approval Chain */}
            <div className="ac-chain-section">
              <div className="rb-section-label">Approval Chain</div>
              <div className="ac-chain">
                {selected.levels.map((level, idx) => (
                  <React.Fragment key={level.level}>
                    <div className={`ac-chain-step ${level.level === selected.currentLevel && selected.status === 'pending' ? 'ac-chain-step-active' : ''}`}>
                      <div className="ac-chain-level">Level {level.level}</div>
                      <div className="ac-chain-top">
                        {statusIcon(level.status)}
                        <div>
                          <div className="ac-chain-approver">{level.approver}</div>
                          {level.timestamp && <div className="ac-chain-time">{level.timestamp}</div>}
                          {level.comments && <div className="ac-chain-comment">"{level.comments}"</div>}
                        </div>
                      </div>
                    </div>
                    {idx < selected.levels.length - 1 && (
                      <ArrowRight className="ac-chain-arrow" />
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Comment */}
            <div className="ac-comment-box">
              <div className="rb-section-label">Comment</div>
              <textarea
                className="rb-test-input"
                rows={3}
                placeholder="Add a comment or justification..."
                value={comment}
                onChange={e => setComment(e.target.value)}
              />
            </div>

            {/* Action Buttons */}
            {selected.status === 'pending' && (
              <div className="ac-actions">
                <button className="ac-action-btn ac-approve" onClick={() => handleAction('approved')}>
                  <CheckCircle2 className="h-4 w-4" /> Approve
                </button>
                <button className="ac-action-btn ac-reject" onClick={() => handleAction('rejected')}>
                  <XCircle className="h-4 w-4" /> Reject
                </button>
                <button className="ac-action-btn ac-delegate" onClick={() => handleAction('delegated')}>
                  <UserCheck className="h-4 w-4" /> Delegate
                </button>
                <button className="ac-action-btn ac-escalate" onClick={() => handleAction('escalated')}>
                  <AlertTriangle className="h-4 w-4" /> Escalate
                </button>
              </div>
            )}

            {selected.status !== 'pending' && (
              <div className={`rb-test-result ${selected.status === 'approved' ? 'rb-test-pass' : selected.status === 'rejected' ? 'rb-test-fail' : 'rb-test-error'}`}>
                {statusIcon(selected.status)} Request {selected.status}
              </div>
            )}
          </div>
        ) : (
          <div className="ac-no-selection">
            <CheckCircle2 className="h-12 w-12" style={{ color: '#1e3a5f' }} />
            <p>Select an approval request to review</p>
          </div>
        )}
      </div>

      <style>{`
        .ac-root { padding: 0; }
        .ac-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem; }
        .ac-header-stats { display: flex; gap: 1.25rem; }
        .ac-stat { display: flex; align-items: center; gap: 0.375rem; font-size: 0.875rem; color: #94a3b8; }
        .ac-stat strong { color: var(--color-text-primary, #f1f5f9); }
        .ac-filters { display: flex; gap: 0.5rem; margin-bottom: 1.25rem; flex-wrap: wrap; }
        .ac-filter-btn { padding: 0.35rem 0.875rem; border-radius: 9999px; border: 1px solid var(--color-border, #334155); background: transparent; color: #94a3b8; font-size: 0.78rem; cursor: pointer; text-transform: capitalize; transition: all 0.15s; }
        .ac-filter-btn.active { background: rgba(16,185,129,0.15); border-color: #10b981; color: #34d399; }
        .ac-body { display: grid; grid-template-columns: 320px 1fr; gap: 1rem; }
        .ac-list { display: flex; flex-direction: column; gap: 0.625rem; max-height: calc(100vh - 310px); overflow-y: auto; }
        .ac-card { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.625rem; padding: 0.875rem; cursor: pointer; transition: all 0.15s; }
        .ac-card:hover { border-color: #4f6c99; }
        .ac-card-selected { border-color: #10b981; box-shadow: 0 0 0 2px rgba(16,185,129,0.2); }
        .ac-card-urgent { border-left: 3px solid #f97316; }
        .ac-card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; gap: 0.5rem; }
        .ac-card-title { font-size: 0.875rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); margin-bottom: 0.25rem; }
        .ac-card-meta { display: flex; align-items: center; gap: 0.5rem; }
        .ac-amount { font-size: 0.75rem; color: #10b981; font-weight: 600; }
        .ac-amount-large { font-size: 1.1rem; font-weight: 700; color: #10b981; }
        .ac-card-bottom { display: flex; justify-content: space-between; align-items: center; margin: 0.5rem 0 0.375rem; font-size: 0.75rem; }
        .ac-requester { display: flex; align-items: center; gap: 0.25rem; color: #94a3b8; }
        .ac-due { color: #f59e0b; }
        .ac-level-dots { display: flex; gap: 0.25rem; margin-top: 0.375rem; }
        .ac-level-dot { width: 0.5rem; height: 0.5rem; border-radius: 50%; background: #334155; }
        .ac-dot-approved { background: #10b981; }
        .ac-dot-current { background: #f59e0b; box-shadow: 0 0 0 2px rgba(245,158,11,0.3); }
        .ac-detail { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; padding: 1.5rem; overflow-y: auto; max-height: calc(100vh - 310px); display: flex; flex-direction: column; gap: 1.25rem; }
        .ac-detail-title { font-size: 1.1rem; font-weight: 700; color: var(--color-text-primary, #f1f5f9); }
        .ac-detail-desc { font-size: 0.875rem; color: #94a3b8; }
        .ac-detail-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 1rem; padding: 1rem; background: var(--color-bg, #0f172a); border-radius: 0.5rem; }
        .ac-detail-val { font-size: 0.875rem; color: var(--color-text-primary, #f1f5f9); font-weight: 500; margin-top: 0.25rem; }
        .ac-chain-section { }
        .ac-chain { display: flex; align-items: flex-start; flex-wrap: wrap; gap: 0.25rem; }
        .ac-chain-step { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.5rem; padding: 0.75rem; min-width: 160px; }
        .ac-chain-step-active { border-color: #f59e0b; box-shadow: 0 0 0 2px rgba(245,158,11,0.2); }
        .ac-chain-level { font-size: 0.65rem; font-weight: 700; color: #475569; text-transform: uppercase; margin-bottom: 0.375rem; }
        .ac-chain-top { display: flex; align-items: flex-start; gap: 0.5rem; }
        .ac-chain-approver { font-size: 0.8rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); }
        .ac-chain-time { font-size: 0.7rem; color: #475569; }
        .ac-chain-comment { font-size: 0.72rem; color: #64748b; font-style: italic; margin-top: 0.2rem; }
        .ac-chain-arrow { width: 1.25rem; height: 1.25rem; color: #334155; margin-top: 1.25rem; flex-shrink: 0; }
        .ac-comment-box { }
        .ac-actions { display: flex; gap: 0.625rem; flex-wrap: wrap; }
        .ac-action-btn { display: flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 600; cursor: pointer; border: 1px solid; transition: all 0.15s; }
        .ac-approve { background: rgba(16,185,129,0.12); color: #34d399; border-color: rgba(16,185,129,0.3); }
        .ac-approve:hover { background: rgba(16,185,129,0.22); }
        .ac-reject { background: rgba(239,68,68,0.1); color: #f87171; border-color: rgba(239,68,68,0.3); }
        .ac-reject:hover { background: rgba(239,68,68,0.2); }
        .ac-delegate { background: rgba(14,165,233,0.1); color: #38bdf8; border-color: rgba(14,165,233,0.3); }
        .ac-escalate { background: rgba(249,115,22,0.1); color: #fb923c; border-color: rgba(249,115,22,0.3); }
        .ac-no-selection { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; gap: 0.75rem; color: #475569; font-size: 0.875rem; background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; }
        @media (max-width: 768px) { .ac-body { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  );
}
