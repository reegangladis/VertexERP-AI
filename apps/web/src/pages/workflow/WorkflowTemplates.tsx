import React, { useState } from 'react';
import { LayoutDashboard, Zap, Users, DollarSign, Package, Factory, Brain, Search, Play, ChevronRight, Star } from 'lucide-react';

interface Template {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: React.ReactNode;
  color: string;
  tags: string[];
  nodes: number;
  is_popular: boolean;
}

const TEMPLATES: Template[] = [
  { id: 't1', name: 'Employee Onboarding', description: 'Automate new hire onboarding with multi-level approval, document verification, and AI welcome summary.', category: 'HR', icon: <Users />, color: '#6366f1', tags: ['Approval', 'AI', 'Multi-level'], nodes: 8, is_popular: true },
  { id: 't2', name: 'Payroll Processing', description: 'Scheduled monthly payroll run with exception handling, manager approval, and payslip generation.', category: 'HR', icon: <Users />, color: '#8b5cf6', tags: ['Scheduled', 'Approval'], nodes: 6, is_popular: false },
  { id: 't3', name: 'Invoice Approval Workflow', description: 'Multi-level invoice approval with amount-based routing, finance director and CFO sign-off.', category: 'Finance', icon: <DollarSign />, color: '#10b981', tags: ['Finance', 'Multi-level', 'Rules'], nodes: 7, is_popular: true },
  { id: 't4', name: 'Expense Claim Process', description: 'Employee expense submission with receipt upload, policy validation, and manager approval.', category: 'Finance', icon: <DollarSign />, color: '#34d399', tags: ['Approval', 'File Upload'], nodes: 5, is_popular: false },
  { id: 't5', name: 'CRM Lead Qualification', description: 'AI-powered lead scoring with rule engine qualification and sales team assignment.', category: 'CRM', icon: <Brain />, color: '#ec4899', tags: ['AI', 'Rules', 'CRM'], nodes: 5, is_popular: true },
  { id: 't6', name: 'Customer Support Escalation', description: 'Auto-escalate unresolved support tickets to senior staff using SLA-based triggers.', category: 'CRM', icon: <Users />, color: '#f59e0b', tags: ['Escalation', 'SLA'], nodes: 4, is_popular: false },
  { id: 't7', name: 'Inventory Reorder', description: 'Database trigger-based automatic purchase order creation when stock drops below threshold.', category: 'Inventory', icon: <Package />, color: '#0ea5e9', tags: ['Database Trigger', 'Rules'], nodes: 4, is_popular: false },
  { id: 't8', name: 'Production Order Approval', description: 'Manufacturing production order creation with BOM validation and plant manager approval.', category: 'Manufacturing', icon: <Factory />, color: '#64748b', tags: ['Approval', 'Manufacturing'], nodes: 6, is_popular: false },
  { id: 't9', name: 'AI RAG Document Processing', description: 'Automatically extract and index documents to RAG knowledge base with embedding generation.', category: 'AI', icon: <Brain />, color: '#6366f1', tags: ['AI', 'RAG', 'File Upload'], nodes: 5, is_popular: true },
  { id: 't10', name: 'ML Model Prediction Pipeline', description: 'Scheduled ML inference pipeline with anomaly detection and alert notification.', category: 'AI', icon: <Brain />, color: '#818cf8', tags: ['AI', 'ML', 'Scheduled'], nodes: 6, is_popular: false },
  { id: 't11', name: 'Budget Approval Cycle', description: 'Multi-level budget approval workflow with department head, finance director, and CEO sign-off.', category: 'Finance', icon: <DollarSign />, color: '#f59e0b', tags: ['Finance', 'Multi-level', '3-level'], nodes: 9, is_popular: false },
  { id: 't12', name: 'Compliance Audit Trail', description: 'Automated audit data collection with evidence gathering, review, and report generation.', category: 'Compliance', icon: <Zap />, color: '#ef4444', tags: ['Audit', 'Compliance', 'Scheduled'], nodes: 7, is_popular: false },
];

const CATEGORIES = ['All', 'HR', 'Finance', 'CRM', 'Inventory', 'Manufacturing', 'AI', 'Compliance'];

export function WorkflowTemplates() {
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');
  const [deployingId, setDeployingId] = useState<string | null>(null);
  const [deployed, setDeployed] = useState<Set<string>>(new Set());

  const filtered = TEMPLATES.filter(t => {
    const catMatch = activeCategory === 'All' || t.category === activeCategory;
    const searchMatch = !search || t.name.toLowerCase().includes(search.toLowerCase()) || t.description.toLowerCase().includes(search.toLowerCase());
    return catMatch && searchMatch;
  });

  const handleDeploy = (id: string) => {
    setDeployingId(id);
    setTimeout(() => {
      setDeployingId(null);
      setDeployed(prev => new Set(prev).add(id));
    }, 1200);
  };

  return (
    <div className="tmpl-root">
      <div className="tmpl-header">
        <div>
          <h1 className="wf-page-title"><LayoutDashboard className="wf-title-icon" style={{ color: '#ec4899' }} /> Workflow Templates</h1>
          <p className="wf-page-subtitle">Pre-built enterprise automation templates — deploy and customize in seconds</p>
        </div>
        <div className="tmpl-count-badge">{TEMPLATES.length} Templates</div>
      </div>

      {/* Search & Category Filter */}
      <div className="tmpl-controls">
        <div className="em-search-wrap" style={{ width: '280px' }}>
          <Search className="em-search-icon" />
          <input className="em-search" placeholder="Search templates…" value={search} onChange={e => setSearch(e.target.value)} />
        </div>
        <div className="tmpl-categories">
          {CATEGORIES.map(cat => (
            <button key={cat} className={`rb-group-btn ${activeCategory === cat ? 'active' : ''}`} onClick={() => setActiveCategory(cat)}>{cat}</button>
          ))}
        </div>
      </div>

      {/* Popular Section */}
      {activeCategory === 'All' && !search && (
        <div className="tmpl-section">
          <div className="rb-section-label" style={{ marginTop: 0 }}><Star className="h-3.5 w-3.5" style={{ color: '#f59e0b' }} /> Popular Templates</div>
          <div className="tmpl-grid">
            {TEMPLATES.filter(t => t.is_popular).map(t => (
              <TemplateCard key={t.id} template={t} deploying={deployingId === t.id} deployed={deployed.has(t.id)} onDeploy={() => handleDeploy(t.id)} />
            ))}
          </div>
        </div>
      )}

      {/* All / Filtered */}
      <div className="tmpl-section">
        {(activeCategory !== 'All' || search) && <div className="rb-section-label" style={{ marginTop: 0 }}>{filtered.length} result{filtered.length !== 1 ? 's' : ''}</div>}
        {activeCategory === 'All' && !search && <div className="rb-section-label"><LayoutDashboard className="h-3.5 w-3.5" /> All Templates</div>}
        <div className="tmpl-grid">
          {filtered.map(t => (
            <TemplateCard key={t.id} template={t} deploying={deployingId === t.id} deployed={deployed.has(t.id)} onDeploy={() => handleDeploy(t.id)} />
          ))}
        </div>
        {filtered.length === 0 && (
          <div className="tmpl-empty">
            <LayoutDashboard className="h-10 w-10" style={{ color: '#1e3a5f' }} />
            <p>No templates match your search</p>
          </div>
        )}
      </div>

      <style>{`
        .tmpl-root { padding: 0; }
        .tmpl-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem; }
        .tmpl-count-badge { padding: 0.375rem 0.875rem; background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3); border-radius: 9999px; font-size: 0.8rem; color: #818cf8; font-weight: 600; }
        .tmpl-controls { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
        .tmpl-categories { display: flex; flex-wrap: wrap; gap: 0.375rem; }
        .tmpl-section { margin-bottom: 2rem; }
        .tmpl-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
        .tmpl-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 3rem; gap: 0.75rem; color: #475569; font-size: 0.875rem; }
      `}</style>
    </div>
  );
}

function TemplateCard({ template, deploying, deployed, onDeploy }: {
  template: Template;
  deploying: boolean;
  deployed: boolean;
  onDeploy: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  return (
    <div className="tmpl-card">
      <div className="tmpl-card-header">
        <div className="tmpl-card-icon" style={{ background: template.color }}>{template.icon}</div>
        <div className="tmpl-card-info">
          <div className="tmpl-card-name">{template.name}</div>
          <div className="tmpl-card-category">{template.category}</div>
        </div>
        {template.is_popular && <Star className="h-4 w-4" style={{ color: '#f59e0b', flexShrink: 0 }} />}
      </div>
      <div className="tmpl-card-desc">{template.description}</div>
      <div className="tmpl-card-tags">
        {template.tags.map(tag => <span key={tag} className="wf-trigger-badge">{tag}</span>)}
        <span className="tmpl-node-count">{template.nodes} nodes</span>
      </div>
      <div className="tmpl-card-actions">
        <button className="tmpl-preview-btn" onClick={() => setExpanded(e => !e)}>
          Preview <ChevronRight className={`h-3.5 w-3.5 tmpl-chevron ${expanded ? 'tmpl-chevron-open' : ''}`} />
        </button>
        <button
          className={`wf-btn ${deployed ? 'tmpl-deployed-btn' : 'wf-btn-primary'}`}
          style={deployed ? {} : { fontSize: '0.8rem', padding: '0.4rem 0.875rem' }}
          onClick={onDeploy}
          disabled={deploying || deployed}
        >
          {deploying ? <><div className="em-spin"><RefreshCw className="h-3.5 w-3.5" /></div> Deploying…</> :
           deployed ? <><CheckCircle2Icon className="h-3.5 w-3.5" /> Deployed</> :
           <><Play className="h-3.5 w-3.5" /> Deploy</>}
        </button>
      </div>
      {expanded && (
        <div className="tmpl-preview">
          <div className="tmpl-preview-nodes">
            {['Trigger', 'Condition', 'Approval', 'Action', 'AI Node'].slice(0, template.nodes > 5 ? 5 : template.nodes).map((n, i) => (
              <div key={i} className="tmpl-preview-node">
                <Zap className="h-3 w-3" style={{ color: template.color }} />
                <span>{n}</span>
                {i < 4 && <ChevronRight className="h-3 w-3" style={{ color: '#334155' }} />}
              </div>
            ))}
            {template.nodes > 5 && <span className="tmpl-preview-more">+{template.nodes - 5} more</span>}
          </div>
        </div>
      )}
      <style>{`
        .tmpl-card { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; transition: all 0.2s; }
        .tmpl-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.25); border-color: #4f6c99; }
        .tmpl-card-header { display: flex; align-items: center; gap: 0.75rem; }
        .tmpl-card-icon { width: 2.5rem; height: 2.5rem; border-radius: 0.5rem; display: flex; align-items: center; justify-content: center; color: #fff; flex-shrink: 0; }
        .tmpl-card-icon svg { width: 1.25rem; height: 1.25rem; }
        .tmpl-card-name { font-size: 0.9rem; font-weight: 700; color: var(--color-text-primary, #f1f5f9); }
        .tmpl-card-category { font-size: 0.72rem; color: #64748b; }
        .tmpl-card-desc { font-size: 0.8rem; color: #94a3b8; line-height: 1.5; }
        .tmpl-card-tags { display: flex; flex-wrap: wrap; gap: 0.3rem; align-items: center; }
        .tmpl-node-count { font-size: 0.7rem; color: #475569; }
        .tmpl-card-actions { display: flex; gap: 0.625rem; align-items: center; }
        .tmpl-preview-btn { display: flex; align-items: center; gap: 0.25rem; background: transparent; border: 1px solid var(--color-border, #334155); border-radius: 0.375rem; color: #64748b; font-size: 0.78rem; padding: 0.35rem 0.625rem; cursor: pointer; transition: all 0.15s; flex: 1; }
        .tmpl-preview-btn:hover { border-color: #6366f1; color: #818cf8; }
        .tmpl-chevron { transition: transform 0.2s; }
        .tmpl-chevron-open { transform: rotate(90deg); }
        .tmpl-deployed-btn { background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.3); color: #34d399; font-size: 0.8rem; padding: 0.4rem 0.875rem; }
        .tmpl-preview { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.5rem; padding: 0.875rem; }
        .tmpl-preview-nodes { display: flex; flex-wrap: wrap; gap: 0.25rem; align-items: center; }
        .tmpl-preview-node { display: flex; align-items: center; gap: 0.25rem; font-size: 0.72rem; color: #94a3b8; }
        .tmpl-preview-more { font-size: 0.7rem; color: #64748b; }
      `}</style>
    </div>
  );
}

function RefreshCw({ className }: { className: string }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 1 0 .49-3.36"/></svg>;
}
function CheckCircle2Icon({ className }: { className: string }) {
  return <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>;
}
