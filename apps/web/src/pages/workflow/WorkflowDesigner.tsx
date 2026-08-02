import React, { useState } from 'react';
import {
  Zap, Trash2, Settings, Save, Upload, Play, GitBranch,
  CheckCircle2, X, MousePointer,
  Brain, Search, BarChart2, Globe
} from 'lucide-react';

type NodeType = 'trigger' | 'action' | 'condition' | 'approval' | 'ai_copilot' | 'rag_search' | 'ml_prediction' | 'external_api';

interface WFNode {
  id: string;
  type: NodeType;
  label: string;
  x: number;
  y: number;
  config?: Record<string, any>;
}

const NODE_PALETTE: { type: NodeType; label: string; icon: React.ReactNode; color: string; bg: string }[] = [
  { type: 'trigger', label: 'Trigger', icon: <Zap />, color: '#f59e0b', bg: 'rgba(245,158,11,0.15)' },
  { type: 'action', label: 'Action', icon: <Play />, color: '#10b981', bg: 'rgba(16,185,129,0.15)' },
  { type: 'condition', label: 'Condition', icon: <GitBranch />, color: '#0ea5e9', bg: 'rgba(14,165,233,0.15)' },
  { type: 'approval', label: 'Approval', icon: <CheckCircle2 />, color: '#8b5cf6', bg: 'rgba(139,92,246,0.15)' },
  { type: 'ai_copilot', label: 'AI Copilot', icon: <Brain />, color: '#ec4899', bg: 'rgba(236,72,153,0.15)' },
  { type: 'rag_search', label: 'RAG Search', icon: <Search />, color: '#06b6d4', bg: 'rgba(6,182,212,0.15)' },
  { type: 'ml_prediction', label: 'ML Predict', icon: <BarChart2 />, color: '#6366f1', bg: 'rgba(99,102,241,0.15)' },
  { type: 'external_api', label: 'External API', icon: <Globe />, color: '#64748b', bg: 'rgba(100,116,139,0.15)' },
];

const NODE_COLORS: Record<NodeType, { border: string; bg: string; icon: string }> = {
  trigger:      { border: '#f59e0b', bg: 'rgba(245,158,11,0.12)',  icon: '#fbbf24' },
  action:       { border: '#10b981', bg: 'rgba(16,185,129,0.12)',  icon: '#34d399' },
  condition:    { border: '#0ea5e9', bg: 'rgba(14,165,233,0.12)',  icon: '#38bdf8' },
  approval:     { border: '#8b5cf6', bg: 'rgba(139,92,246,0.12)', icon: '#a78bfa' },
  ai_copilot:   { border: '#ec4899', bg: 'rgba(236,72,153,0.12)', icon: '#f472b6' },
  rag_search:   { border: '#06b6d4', bg: 'rgba(6,182,212,0.12)',  icon: '#22d3ee' },
  ml_prediction:{ border: '#6366f1', bg: 'rgba(99,102,241,0.12)', icon: '#818cf8' },
  external_api: { border: '#64748b', bg: 'rgba(100,116,139,0.1)', icon: '#94a3b8' },
};

const INITIAL_NODES: WFNode[] = [
  { id: 'n1', type: 'trigger',   label: 'Manual Trigger',       x: 60,  y: 180 },
  { id: 'n2', type: 'condition', label: 'Check Employee Level',  x: 260, y: 80  },
  { id: 'n3', type: 'approval',  label: 'Manager Approval',     x: 460, y: 80  },
  { id: 'n4', type: 'action',    label: 'Send Email',            x: 460, y: 280 },
  { id: 'n5', type: 'ai_copilot',label: 'AI Summary',           x: 660, y: 180 },
];

const INITIAL_EDGES = [
  { id: 'e1', source: 'n1', target: 'n2' },
  { id: 'e2', source: 'n2', target: 'n3', label: 'Senior' },
  { id: 'e3', source: 'n2', target: 'n4', label: 'Junior' },
  { id: 'e4', source: 'n3', target: 'n5' },
  { id: 'e5', source: 'n4', target: 'n5' },
];

function NodePaletteItem({ item, onDrop }: { item: typeof NODE_PALETTE[0], onDrop: (type: NodeType) => void }) {
  return (
    <button className="wfd-palette-item" onClick={() => onDrop(item.type)} style={{ borderColor: item.color }}>
      <span className="wfd-palette-icon" style={{ background: item.bg, color: item.color }}>{item.icon}</span>
      <span className="wfd-palette-label">{item.label}</span>
    </button>
  );
}

function CanvasNode({ node, selected, onClick, onDelete }: {
  node: WFNode; selected: boolean; onClick: () => void; onDelete: () => void;
}) {
  const colors = NODE_COLORS[node.type];
  const palette = NODE_PALETTE.find(p => p.type === node.type);
  return (
    <div
      className={`wfd-node ${selected ? 'wfd-node-selected' : ''}`}
      style={{
        left: node.x, top: node.y,
        borderColor: selected ? '#818cf8' : colors.border,
        background: colors.bg,
      }}
      onClick={onClick}
    >
      <div className="wfd-node-header">
        <span className="wfd-node-type-badge" style={{ color: colors.icon }}>
          {palette?.icon}
        </span>
        <span className="wfd-node-label">{node.label}</span>
        <button className="wfd-node-delete" onClick={e => { e.stopPropagation(); onDelete(); }}>
          <X className="h-3 w-3" />
        </button>
      </div>
      <div className="wfd-node-type-label">{node.type.replace('_', ' ')}</div>
      <div className="wfd-node-connector-out" title="Drag to connect" />
    </div>
  );
}

export function WorkflowDesigner() {
  const [nodes, setNodes] = useState<WFNode[]>(INITIAL_NODES);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState('Employee Onboarding Workflow');
  const [status, setStatus] = useState<'draft' | 'published'>('draft');
  const [saved, setSaved] = useState(false);

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  const addNode = (type: NodeType) => {
    const palette = NODE_PALETTE.find(p => p.type === type)!;
    const newNode: WFNode = {
      id: `n${Date.now()}`,
      type,
      label: `New ${palette.label}`,
      x: 80 + Math.random() * 200,
      y: 80 + Math.random() * 200,
    };
    setNodes(prev => [...prev, newNode]);
    setSelectedNodeId(newNode.id);
  };

  const deleteNode = (id: string) => {
    setNodes(prev => prev.filter(n => n.id !== id));
    if (selectedNodeId === id) setSelectedNodeId(null);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const handlePublish = () => {
    setStatus('published');
    handleSave();
  };

  return (
    <div className="wfd-root">
      {/* Toolbar */}
      <div className="wfd-toolbar">
        <div className="wfd-toolbar-left">
          <Zap className="wfd-brand-icon" />
          <input
            className="wfd-name-input"
            value={workflowName}
            onChange={e => setWorkflowName(e.target.value)}
          />
          <span className={`wf-badge ${status === 'published' ? 'wf-badge-success' : 'wf-badge-neutral'}`}>
            {status}
          </span>
        </div>
        <div className="wfd-toolbar-right">
          <button className="wf-btn wf-btn-ghost" onClick={handleSave}>
            <Save className="h-4 w-4" /> {saved ? 'Saved!' : 'Save Draft'}
          </button>
          <button className="wf-btn wf-btn-primary" onClick={handlePublish}>
            <Upload className="h-4 w-4" /> Publish
          </button>
        </div>
      </div>

      <div className="wfd-body">
        {/* Palette */}
        <div className="wfd-palette">
          <div className="wfd-palette-title">
            <MousePointer className="h-3.5 w-3.5" /> Node Palette
          </div>
          {NODE_PALETTE.map(item => (
            <NodePaletteItem key={item.type} item={item} onDrop={addNode} />
          ))}
          <div className="wfd-palette-hint">Click to add node to canvas</div>
        </div>

        {/* Canvas */}
        <div className="wfd-canvas" onClick={() => setSelectedNodeId(null)}>
          <div className="wfd-canvas-grid" />
          {/* SVG Edges */}
          <svg className="wfd-edges-svg">
            {INITIAL_EDGES.map(edge => {
              const src = nodes.find(n => n.id === edge.source);
              const tgt = nodes.find(n => n.id === edge.target);
              if (!src || !tgt) return null;
              const sx = src.x + 160, sy = src.y + 30;
              const tx = tgt.x, ty = tgt.y + 30;
              const mx = (sx + tx) / 2;
              return (
                <g key={edge.id}>
                  <path
                    d={`M${sx},${sy} C${mx},${sy} ${mx},${ty} ${tx},${ty}`}
                    fill="none" stroke="#334155" strokeWidth="1.5" strokeDasharray="4 2"
                  />
                  {edge.label && (
                    <text x={mx} y={(sy + ty) / 2 - 6} textAnchor="middle"
                      fontSize="10" fill="#64748b">{edge.label}</text>
                  )}
                </g>
              );
            })}
          </svg>
          {/* Nodes */}
          {nodes.map(node => (
            <CanvasNode
              key={node.id}
              node={node}
              selected={selectedNodeId === node.id}
              onClick={(e?: any) => { if (e) e.stopPropagation(); setSelectedNodeId(node.id); }}
              onDelete={() => deleteNode(node.id)}
            />
          ))}
          <div className="wfd-canvas-hint">
            <MousePointer className="h-4 w-4" />
            Click palette items to add nodes · Click nodes to edit
          </div>
        </div>

        {/* Properties Panel */}
        <div className="wfd-props-panel">
          <div className="wfd-props-title">
            <Settings className="h-3.5 w-3.5" />
            {selectedNode ? 'Node Properties' : 'Properties'}
          </div>
          {selectedNode ? (
            <div className="wfd-props-content">
              <div className="wfd-props-group">
                <label className="wfd-props-label">Label</label>
                <input
                  className="wfd-props-input"
                  value={selectedNode.label}
                  onChange={e => setNodes(prev => prev.map(n =>
                    n.id === selectedNode.id ? { ...n, label: e.target.value } : n
                  ))}
                />
              </div>
              <div className="wfd-props-group">
                <label className="wfd-props-label">Type</label>
                <div className="wfd-props-type-badge" style={{ borderColor: NODE_COLORS[selectedNode.type].border }}>
                  {selectedNode.type.replace('_', ' ')}
                </div>
              </div>
              {selectedNode.type === 'trigger' && (
                <div className="wfd-props-group">
                  <label className="wfd-props-label">Trigger Type</label>
                  <select className="wfd-props-input">
                    <option>manual</option>
                    <option>rest_api</option>
                    <option>database</option>
                    <option>scheduled</option>
                    <option>webhook</option>
                    <option>erp_event</option>
                    <option>ai_event</option>
                  </select>
                </div>
              )}
              {selectedNode.type === 'condition' && (
                <>
                  <div className="wfd-props-group">
                    <label className="wfd-props-label">Field</label>
                    <input className="wfd-props-input" placeholder="e.g. employee.level" />
                  </div>
                  <div className="wfd-props-group">
                    <label className="wfd-props-label">Operator</label>
                    <select className="wfd-props-input">
                      <option>==</option><option>!=</option>
                      <option>&gt;</option><option>&lt;</option>
                      <option>contains</option><option>in</option>
                    </select>
                  </div>
                  <div className="wfd-props-group">
                    <label className="wfd-props-label">Value</label>
                    <input className="wfd-props-input" placeholder="e.g. senior" />
                  </div>
                </>
              )}
              {selectedNode.type === 'action' && (
                <div className="wfd-props-group">
                  <label className="wfd-props-label">Action Type</label>
                  <select className="wfd-props-input">
                    <option>send_email</option>
                    <option>send_notification</option>
                    <option>create_task</option>
                    <option>update_record</option>
                    <option>generate_report</option>
                  </select>
                </div>
              )}
              {(selectedNode.type === 'ai_copilot' || selectedNode.type === 'rag_search') && (
                <div className="wfd-props-group">
                  <label className="wfd-props-label">Prompt / Query</label>
                  <textarea className="wfd-props-input wfd-props-textarea" placeholder="Enter your prompt or query..." />
                </div>
              )}
              <div className="wfd-props-group">
                <label className="wfd-props-label">Max Retries</label>
                <input className="wfd-props-input" type="number" defaultValue={0} min={0} max={5} />
              </div>
              <div className="wfd-props-group">
                <label className="wfd-props-label">Timeout (s)</label>
                <input className="wfd-props-input" type="number" defaultValue={30} />
              </div>
              <button className="wfd-props-delete-btn" onClick={() => deleteNode(selectedNode.id)}>
                <Trash2 className="h-3.5 w-3.5" /> Remove Node
              </button>
            </div>
          ) : (
            <div className="wfd-props-empty">
              <MousePointer className="h-8 w-8 wfd-props-empty-icon" />
              <p>Select a node to edit its properties</p>
            </div>
          )}
        </div>
      </div>

      <style>{`
        .wfd-root { display: flex; flex-direction: column; height: calc(100vh - 120px); background: var(--color-bg, #0f172a); border-radius: 0.75rem; overflow: hidden; border: 1px solid var(--color-border, #334155); }
        .wfd-toolbar { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1.25rem; background: var(--color-surface, #1e293b); border-bottom: 1px solid var(--color-border, #334155); gap: 1rem; }
        .wfd-toolbar-left { display: flex; align-items: center; gap: 0.75rem; flex: 1; min-width: 0; }
        .wfd-toolbar-right { display: flex; align-items: center; gap: 0.625rem; }
        .wfd-brand-icon { width: 1.25rem; height: 1.25rem; color: #818cf8; flex-shrink: 0; }
        .wfd-name-input { background: transparent; border: 1px solid transparent; border-radius: 0.375rem; padding: 0.25rem 0.5rem; font-size: 0.9rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); min-width: 0; flex: 1; max-width: 320px; }
        .wfd-name-input:focus { outline: none; border-color: #6366f1; background: rgba(99,102,241,0.08); }
        .wfd-body { display: flex; flex: 1; overflow: hidden; }
        .wfd-palette { width: 170px; flex-shrink: 0; background: var(--color-surface, #1e293b); border-right: 1px solid var(--color-border, #334155); padding: 1rem 0.75rem; overflow-y: auto; display: flex; flex-direction: column; gap: 0.375rem; }
        .wfd-palette-title { display: flex; align-items: center; gap: 0.375rem; font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem; }
        .wfd-palette-item { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.625rem; background: var(--color-bg, #0f172a); border: 1px solid; border-radius: 0.5rem; cursor: pointer; transition: all 0.15s; width: 100%; text-align: left; }
        .wfd-palette-item:hover { transform: translateX(2px); opacity: 0.9; }
        .wfd-palette-icon { width: 1.75rem; height: 1.75rem; border-radius: 0.375rem; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .wfd-palette-icon svg { width: 0.875rem; height: 0.875rem; }
        .wfd-palette-label { font-size: 0.78rem; font-weight: 500; color: var(--color-text-primary, #f1f5f9); }
        .wfd-palette-hint { font-size: 0.65rem; color: #475569; text-align: center; margin-top: 0.5rem; line-height: 1.4; }
        .wfd-canvas { flex: 1; position: relative; overflow: auto; background: #090e1a; }
        .wfd-canvas-grid { position: absolute; inset: 0; background-image: radial-gradient(circle, #1e293b 1px, transparent 1px); background-size: 24px 24px; pointer-events: none; }
        .wfd-edges-svg { position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; }
        .wfd-node { position: absolute; width: 160px; background: var(--color-surface, #1e293b); border: 1.5px solid; border-radius: 0.625rem; padding: 0.625rem 0.75rem; cursor: pointer; transition: box-shadow 0.2s, transform 0.15s; user-select: none; }
        .wfd-node:hover { transform: translateY(-1px); box-shadow: 0 6px 20px rgba(0,0,0,0.4); }
        .wfd-node-selected { box-shadow: 0 0 0 2px #818cf8, 0 8px 24px rgba(99,102,241,0.3); transform: translateY(-1px); }
        .wfd-node-header { display: flex; align-items: center; gap: 0.375rem; margin-bottom: 0.25rem; }
        .wfd-node-type-badge svg { width: 0.875rem; height: 0.875rem; }
        .wfd-node-label { font-size: 0.78rem; font-weight: 600; color: var(--color-text-primary, #f1f5f9); flex: 1; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .wfd-node-delete { width: 1.25rem; height: 1.25rem; display: flex; align-items: center; justify-content: center; border-radius: 0.25rem; border: none; background: transparent; color: #64748b; cursor: pointer; opacity: 0; transition: opacity 0.15s; flex-shrink: 0; }
        .wfd-node:hover .wfd-node-delete { opacity: 1; }
        .wfd-node-delete:hover { background: rgba(239,68,68,0.15); color: #f87171; }
        .wfd-node-type-label { font-size: 0.65rem; text-transform: capitalize; color: #64748b; }
        .wfd-node-connector-out { position: absolute; right: -7px; top: 50%; transform: translateY(-50%); width: 12px; height: 12px; border-radius: 50%; background: #334155; border: 2px solid #475569; cursor: crosshair; transition: border-color 0.15s; }
        .wfd-node-connector-out:hover { border-color: #818cf8; background: #6366f1; }
        .wfd-canvas-hint { position: absolute; bottom: 1rem; left: 50%; transform: translateX(-50%); display: flex; align-items: center; gap: 0.375rem; font-size: 0.75rem; color: #334155; pointer-events: none; white-space: nowrap; }
        .wfd-props-panel { width: 220px; flex-shrink: 0; background: var(--color-surface, #1e293b); border-left: 1px solid var(--color-border, #334155); display: flex; flex-direction: column; overflow-y: auto; }
        .wfd-props-title { display: flex; align-items: center; gap: 0.375rem; font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; padding: 0.875rem 1rem; border-bottom: 1px solid var(--color-border, #334155); }
        .wfd-props-content { padding: 1rem; display: flex; flex-direction: column; gap: 0.875rem; }
        .wfd-props-group { display: flex; flex-direction: column; gap: 0.25rem; }
        .wfd-props-label { font-size: 0.7rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.04em; }
        .wfd-props-input { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); border-radius: 0.375rem; padding: 0.375rem 0.5rem; font-size: 0.8rem; color: var(--color-text-primary, #f1f5f9); width: 100%; transition: border-color 0.15s; }
        .wfd-props-input:focus { outline: none; border-color: #6366f1; }
        .wfd-props-textarea { min-height: 5rem; resize: vertical; }
        .wfd-props-type-badge { display: inline-flex; padding: 0.25rem 0.625rem; border-radius: 0.375rem; font-size: 0.75rem; font-weight: 500; border: 1px solid; color: var(--color-text-secondary, #94a3b8); text-transform: capitalize; }
        .wfd-props-delete-btn { display: flex; align-items: center; justify-content: center; gap: 0.375rem; width: 100%; padding: 0.5rem; border-radius: 0.375rem; border: 1px solid rgba(239,68,68,0.3); background: rgba(239,68,68,0.08); color: #f87171; font-size: 0.78rem; cursor: pointer; transition: all 0.15s; margin-top: 0.5rem; }
        .wfd-props-delete-btn:hover { background: rgba(239,68,68,0.15); }
        .wfd-props-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; flex: 1; gap: 0.5rem; padding: 2rem 1rem; color: #475569; font-size: 0.8rem; text-align: center; }
        .wfd-props-empty-icon { color: #334155; }
        .wf-btn-ghost { background: var(--color-bg, #0f172a); border: 1px solid var(--color-border, #334155); color: var(--color-text-secondary, #94a3b8); }
        .wf-btn-ghost:hover { border-color: #6366f1; color: #818cf8; }
      `}</style>
    </div>
  );
}
