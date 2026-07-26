import React, { useState } from 'react';
import { Shield, Plus, Trash2, Play, CheckCircle2, XCircle, Save, ChevronDown, ChevronRight } from 'lucide-react';

type Operator = '==' | '!=' | '>' | '<' | '>=' | '<=' | 'in' | 'contains' | 'matches' | 'is_null' | 'is_not_null';
interface RuleCondition { id: string; field: string; operator: Operator; value: string; }
interface BusinessRule {
  id: string;
  name: string;
  rule_group: string;
  priority: number;
  is_active: boolean;
  conditions: RuleCondition[];
  actions: string[];
}

const MOCK_RULES: BusinessRule[] = [
  {
    id: 'r1', name: 'High-Value Invoice Alert', rule_group: 'finance', priority: 1, is_active: true,
    conditions: [{ id: 'c1', field: 'invoice.amount', operator: '>=', value: '50000' }],
    actions: ['send_email', 'create_task'],
  },
  {
    id: 'r2', name: 'Senior Employee Escalation', rule_group: 'hr', priority: 2, is_active: true,
    conditions: [
      { id: 'c2', field: 'employee.level', operator: '==', value: 'senior' },
      { id: 'c3', field: 'leave.days', operator: '>', value: '14' },
    ],
    actions: ['escalate_approval'],
  },
  {
    id: 'r3', name: 'Low Stock Reorder', rule_group: 'inventory', priority: 1, is_active: false,
    conditions: [{ id: 'c4', field: 'product.stock_qty', operator: '<=', value: '10' }],
    actions: ['create_purchase_order'],
  },
];

const OPERATORS: Operator[] = ['==', '!=', '>', '<', '>=', '<=', 'in', 'contains', 'matches', 'is_null', 'is_not_null'];
const ACTION_OPTIONS = [
  'send_email', 'send_notification', 'create_task', 'escalate_approval',
  'create_purchase_order', 'update_record', 'run_ai_copilot', 'execute_webhook',
];
const GROUPS = ['general', 'hr', 'finance', 'crm', 'inventory', 'manufacturing'];

export function RuleBuilder() {
  const [rules, setRules] = useState<BusinessRule[]>(MOCK_RULES);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [testData, setTestData] = useState('{\n  "invoice": {\n    "amount": 75000\n  }\n}');
  const [testResult, setTestResult] = useState<any>(null);
  const [activeGroup, setActiveGroup] = useState<string>('all');

  const selected = rules.find(r => r.id === selectedId);

  const addRule = () => {
    const newRule: BusinessRule = {
      id: `r${Date.now()}`,
      name: 'New Rule',
      rule_group: 'general',
      priority: rules.length + 1,
      is_active: true,
      conditions: [{ id: `c${Date.now()}`, field: '', operator: '==', value: '' }],
      actions: [],
    };
    setRules(prev => [...prev, newRule]);
    setSelectedId(newRule.id);
  };

  const runTest = () => {
    try {
      const ctx = JSON.parse(testData);
      if (!selected) return;
      let matched = true;
      for (const cond of selected.conditions) {
        const parts = cond.field.split('.');
        let val: any = ctx;
        for (const p of parts) val = val?.[p];
        const expected = isNaN(Number(cond.value)) ? cond.value : Number(cond.value);
        if (cond.operator === '>=' && !(val >= expected)) matched = false;
        if (cond.operator === '==' && !(val == expected)) matched = false;
        if (cond.operator === '<=' && !(val <= expected)) matched = false;
        if (cond.operator === '>' && !(val > expected)) matched = false;
        if (cond.operator === '<' && !(val < expected)) matched = false;
      }
      setTestResult({ matched, actions: matched ? selected.actions : [] });
    } catch {
      setTestResult({ error: 'Invalid JSON in test data' });
    }
  };

  const filtered = activeGroup === 'all' ? rules : rules.filter(r => r.rule_group === activeGroup);

  return (
    <div className="rb-root">
      <div className="rb-header">
        <div>
          <h1 className="wf-page-title"><Shield className="wf-title-icon" style={{ color: '#0ea5e9' }} /> Rule Builder</h1>
          <p className="wf-page-subtitle">Define enterprise business rules and expression logic</p>
        </div>
        <button className="wf-btn wf-btn-primary" onClick={addRule}><Plus className="h-4 w-4" /> New Rule</button>
      </div>

      {/* Group Filter */}
      <div className="rb-groups">
        {['all', ...GROUPS].map(g => (
          <button key={g} className={`rb-group-btn ${activeGroup === g ? 'active' : ''}`} onClick={() => setActiveGroup(g)}>
            {g}
          </button>
        ))}
      </div>

      <div className="rb-body">
        {/* Rule List */}
        <div className="rb-list">
          {filtered.map(rule => (
            <div
              key={rule.id}
              className={`rb-rule-card ${selectedId === rule.id ? 'rb-rule-selected' : ''}`}
              onClick={() => setSelectedId(rule.id)}
            >
              <div className="rb-rule-card-top">
                <div className="rb-rule-info">
                  <div className="rb-rule-name">{rule.name}</div>
                  <div className="rb-rule-meta">
                    <span className="wf-category-badge">{rule.rule_group}</span>
                    <span className="rb-priority">P{rule.priority}</span>
                  </div>
                </div>
                <div className={`rb-toggle ${rule.is_active ? 'rb-toggle-on' : ''}`}
                  onClick={e => { e.stopPropagation(); setRules(prev => prev.map(r => r.id === rule.id ? { ...r, is_active: !r.is_active } : r)); }}>
                  <div className="rb-toggle-thumb" />
                </div>
              </div>
              <div className="rb-rule-conditions">
                {rule.conditions.slice(0, 2).map(c => (
                  <div key={c.id} className="rb-condition-pill">
                    {c.field} <strong>{c.operator}</strong> {c.value || '…'}
                  </div>
                ))}
                {rule.conditions.length > 2 && <div className="rb-condition-pill rb-more">+{rule.conditions.length - 2} more</div>}
              </div>
            </div>
          ))}
          {filtered.length === 0 && <div className="rb-empty">No rules in this group</div>}
        </div>

        {/* Editor */}
        <div className="rb-editor">
          {selected ? (
            <>
              <div className="rb-editor-header">
                <input
                  className="rb-rule-name-input"
                  value={selected.name}
                  onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? { ...r, name: e.target.value } : r))}
                />
                <button className="wf-btn wf-btn-ghost">
                  <Save className="h-4 w-4" /> Save
                </button>
                <button className="wf-btn" style={{ background: 'rgba(239,68,68,0.12)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' }}
                  onClick={() => { setRules(prev => prev.filter(r => r.id !== selected.id)); setSelectedId(null); }}>
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {/* Group & Priority */}
              <div className="rb-field-row">
                <div className="rb-field-group">
                  <label className="rb-label">Rule Group</label>
                  <select className="rb-input" value={selected.rule_group} onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? { ...r, rule_group: e.target.value } : r))}>
                    {GROUPS.map(g => <option key={g}>{g}</option>)}
                  </select>
                </div>
                <div className="rb-field-group">
                  <label className="rb-label">Priority</label>
                  <input type="number" className="rb-input" value={selected.priority} min={1} max={100}
                    onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? { ...r, priority: +e.target.value } : r))} />
                </div>
              </div>

              {/* Conditions */}
              <div className="rb-section-label">Conditions <span className="rb-logic-badge">AND</span></div>
              <div className="rb-conditions-list">
                {selected.conditions.map((cond, idx) => (
                  <div key={cond.id} className="rb-condition-row">
                    {idx > 0 && <div className="rb-and-label">AND</div>}
                    <input className="rb-input rb-cond-field" placeholder="field.path" value={cond.field}
                      onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? {
                        ...r, conditions: r.conditions.map(c => c.id === cond.id ? { ...c, field: e.target.value } : c)
                      } : r))}
                    />
                    <select className="rb-input rb-cond-op" value={cond.operator}
                      onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? {
                        ...r, conditions: r.conditions.map(c => c.id === cond.id ? { ...c, operator: e.target.value as Operator } : c)
                      } : r))}>
                      {OPERATORS.map(op => <option key={op}>{op}</option>)}
                    </select>
                    <input className="rb-input rb-cond-val" placeholder="value" value={cond.value}
                      onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? {
                        ...r, conditions: r.conditions.map(c => c.id === cond.id ? { ...c, value: e.target.value } : c)
                      } : r))}
                    />
                    <button className="rb-cond-delete" onClick={() => setRules(prev => prev.map(r => r.id === selected.id ? {
                      ...r, conditions: r.conditions.filter(c => c.id !== cond.id)
                    } : r))}>
                      <XCircle className="h-4 w-4" />
                    </button>
                  </div>
                ))}
                <button className="rb-add-cond-btn" onClick={() => setRules(prev => prev.map(r => r.id === selected.id ? {
                  ...r, conditions: [...r.conditions, { id: `c${Date.now()}`, field: '', operator: '==', value: '' }]
                } : r))}>
                  <Plus className="h-3.5 w-3.5" /> Add Condition
                </button>
              </div>

              {/* Actions */}
              <div className="rb-section-label">Actions</div>
              <div className="rb-actions-grid">
                {ACTION_OPTIONS.map(action => (
                  <label key={action} className="rb-action-item">
                    <input type="checkbox"
                      checked={selected.actions.includes(action)}
                      onChange={e => setRules(prev => prev.map(r => r.id === selected.id ? {
                        ...r, actions: e.target.checked ? [...r.actions, action] : r.actions.filter(a => a !== action)
                      } : r))}
                    />
                    <span>{action.replace(/_/g, ' ')}</span>
                  </label>
                ))}
              </div>

              {/* Test Runner */}
              <div className="rb-section-label">Rule Test Runner</div>
              <div className="rb-tester">
                <textarea className="rb-test-input" value={testData} onChange={e => setTestData(e.target.value)} rows={5} />
                <button className="wf-btn wf-btn-primary" onClick={runTest}><Play className="h-4 w-4" /> Run Test</button>
                {testResult && (
                  <div className={`rb-test-result ${testResult.matched ? 'rb-test-pass' : testResult.error ? 'rb-test-error' : 'rb-test-fail'}`}>
                    {testResult.error ? (
                      <><XCircle className="h-4 w-4" /> {testResult.error}</>
                    ) : testResult.matched ? (
                      <><CheckCircle2 className="h-4 w-4" /> Rule matched! Actions: {testResult.actions.join(', ')}</>
                    ) : (
                      <><XCircle className="h-4 w-4" /> Rule did not match</>
                    )}
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="rb-no-selection">
              <Shield className="h-10 w-10" style={{ color: '#1e3a5f' }} />
              <p>Select a rule to edit or create a new one</p>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .rb-root { padding: 0; }
        .rb-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.25rem; flex-wrap: wrap; gap: 1rem; }
        .rb-groups { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
        .rb-group-btn { padding: 0.35rem 0.875rem; border-radius: 9999px; border: 1px solid var(--color-border, #334155); background: transparent; color: #94a3b8; font-size: 0.78rem; font-weight: 500; cursor: pointer; text-transform: capitalize; transition: all 0.15s; }
        .rb-group-btn.active { background: rgba(99,102,241,0.15); border-color: #6366f1; color: #818cf8; }
        .rb-body { display: grid; grid-template-columns: 320px 1fr; gap: 1rem; }
        .rb-list { display: flex; flex-direction: column; gap: 0.625rem; max-height: calc(100vh - 280px); overflow-y: auto; padding-right: 0.25rem; }
        .rb-rule-card { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.625rem; padding: 0.875rem; cursor: pointer; transition: all 0.15s; }
        .rb-rule-card:hover { border-color: #4f6c99; }
        .rb-rule-selected { border-color: #6366f1; box-shadow: 0 0 0 2px rgba(99,102,241,0.2); }
        .rb-rule-card-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; }
        .rb-rule-name { font-size: 0.875rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); }
        .rb-rule-meta { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.25rem; }
        .rb-priority { font-size: 0.7rem; background: rgba(245,158,11,0.15); color: #fbbf24; padding: 0.1rem 0.4rem; border-radius: 0.25rem; font-weight: 600; }
        .rb-toggle { width: 2.25rem; height: 1.25rem; border-radius: 9999px; background: #334155; position: relative; cursor: pointer; transition: background 0.2s; flex-shrink: 0; }
        .rb-toggle-on { background: #6366f1; }
        .rb-toggle-thumb { position: absolute; top: 2px; left: 2px; width: 0.875rem; height: 0.875rem; border-radius: 50%; background: #fff; transition: transform 0.2s; }
        .rb-toggle-on .rb-toggle-thumb { transform: translateX(1rem); }
        .rb-rule-conditions { display: flex; flex-wrap: wrap; gap: 0.25rem; }
        .rb-condition-pill { font-size: 0.7rem; background: rgba(14,165,233,0.1); border: 1px solid rgba(14,165,233,0.2); color: #38bdf8; padding: 0.15rem 0.5rem; border-radius: 0.25rem; }
        .rb-more { background: rgba(100,116,139,0.1); border-color: rgba(100,116,139,0.2); color: #64748b; }
        .rb-empty { color: #475569; font-size: 0.85rem; text-align: center; padding: 2rem; }
        .rb-editor { background: var(--color-surface, #1e293b); border: 1px solid var(--color-border, #334155); border-radius: 0.75rem; padding: 1.5rem; overflow-y: auto; max-height: calc(100vh - 280px); }
        .rb-editor-header { display: flex; gap: 0.625rem; align-items: center; margin-bottom: 1.25rem; }
        .rb-rule-name-input { flex: 1; background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.5rem; padding: 0.5rem 0.75rem; font-size: 0.95rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); }
        .rb-rule-name-input:focus { outline: none; border-color: #6366f1; }
        .rb-field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; }
        .rb-field-group { display: flex; flex-direction: column; gap: 0.25rem; }
        .rb-label { font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
        .rb-input { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.375rem; padding: 0.375rem 0.625rem; font-size: 0.8rem; color: var(--color-text-primary, #f1f5f9); }
        .rb-input:focus { outline: none; border-color: #6366f1; }
        .rb-section-label { font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.75rem; margin-top: 1.25rem; display: flex; align-items: center; gap: 0.5rem; }
        .rb-logic-badge { background: rgba(245,158,11,0.15); color: #fbbf24; padding: 0.1rem 0.4rem; border-radius: 0.25rem; font-size: 0.65rem; }
        .rb-conditions-list { display: flex; flex-direction: column; gap: 0.5rem; }
        .rb-condition-row { display: flex; gap: 0.5rem; align-items: center; }
        .rb-and-label { font-size: 0.65rem; font-weight: 700; color: #475569; text-transform: uppercase; min-width: 2rem; }
        .rb-cond-field { flex: 2; }
        .rb-cond-op { flex: 1.5; }
        .rb-cond-val { flex: 2; }
        .rb-cond-delete { background: transparent; border: none; color: #475569; cursor: pointer; padding: 0.25rem; transition: color 0.15s; flex-shrink: 0; }
        .rb-cond-delete:hover { color: #f87171; }
        .rb-add-cond-btn { display: flex; align-items: center; gap: 0.375rem; padding: 0.375rem 0.75rem; border: 1px dashed var(--color-border, #334155); border-radius: 0.375rem; color: #64748b; background: transparent; font-size: 0.78rem; cursor: pointer; transition: all 0.15s; margin-top: 0.25rem; }
        .rb-add-cond-btn:hover { border-color: #6366f1; color: #818cf8; }
        .rb-actions-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; }
        .rb-action-item { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8rem; color: #94a3b8; cursor: pointer; padding: 0.375rem; border-radius: 0.375rem; transition: background 0.15s; text-transform: capitalize; }
        .rb-action-item:hover { background: rgba(99,102,241,0.08); }
        .rb-tester { display: flex; flex-direction: column; gap: 0.75rem; }
        .rb-test-input { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.5rem; padding: 0.625rem; font-size: 0.8rem; color: #94a3b8; font-family: monospace; resize: vertical; }
        .rb-test-result { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 0.875rem; border-radius: 0.5rem; font-size: 0.8rem; font-weight: 500; }
        .rb-test-pass { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
        .rb-test-fail { background: rgba(239,68,68,0.1); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
        .rb-test-error { background: rgba(245,158,11,0.1); color: #fbbf24; border: 1px solid rgba(245,158,11,0.2); }
        .rb-no-selection { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 0.75rem; color: #475569; font-size: 0.875rem; }
        @media (max-width: 768px) { .rb-body { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  );
}
