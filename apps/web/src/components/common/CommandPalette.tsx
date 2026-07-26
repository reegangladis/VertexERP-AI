import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Search,
  Command,
  LayoutDashboard,
  Brain,
  Workflow,
  Network,
  ShieldCheck,
  Server,
  DollarSign,
  Activity,
  Zap,
  ArrowRight,
  X,
} from 'lucide-react';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommandPalette({ isOpen, onClose }: CommandPaletteProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const navigate = useNavigate();

  const commands = [
    { label: 'Executive Dashboard', path: '/analytics/executive', icon: <LayoutDashboard className="h-4 w-4 text-indigo-500" />, category: 'Dashboards' },
    { label: 'ML Studio & AutoML', path: '/ml-studio/dashboard', icon: <Brain className="h-4 w-4 text-purple-500" />, category: 'AI & ML' },
    { label: 'Enterprise RAG Engine', path: '/rag', icon: <Search className="h-4 w-4 text-emerald-500" />, category: 'AI & ML' },
    { label: 'Workflow Designer', path: '/workflows/designer', icon: <Workflow className="h-4 w-4 text-amber-500" />, category: 'Automation' },
    { label: 'API Gateway', path: '/integrations/gateway', icon: <Network className="h-4 w-4 text-cyan-500" />, category: 'Integrations' },
    { label: 'Security Hardening', path: '/production/security', icon: <ShieldCheck className="h-4 w-4 text-rose-500" />, category: 'Production' },
    { label: 'Cloud Deployment', path: '/cloud/deployments', icon: <Server className="h-4 w-4 text-blue-500" />, category: 'Production' },
    { label: 'FinOps Cost Center', path: '/cloud/finops', icon: <DollarSign className="h-4 w-4 text-emerald-500" />, category: 'Operations' },
    { label: 'System Readiness', path: '/production/readiness', icon: <Activity className="h-4 w-4 text-indigo-500" />, category: 'Operations' },
    { label: 'Global System Status', path: '/cloud/status', icon: <Zap className="h-4 w-4 text-amber-500" />, category: 'Operations' },
  ];

  const filteredCommands = commands.filter((cmd) =>
    cmd.label.toLowerCase().includes(query.toLowerCase()) ||
    cmd.category.toLowerCase().includes(query.toLowerCase())
  );

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        if (isOpen) onClose();
        else setQuery('');
      } else if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-slate-900/60 backdrop-blur-sm p-4 animate-in fade-in duration-200">
      <div className="w-full max-w-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl shadow-2xl overflow-hidden glass-panel">
        {/* Search Bar */}
        <div className="flex items-center px-4 py-3.5 border-b border-slate-200 dark:border-slate-800">
          <Search className="h-5 w-5 text-indigo-500 mr-3" />
          <input
            type="text"
            placeholder="Type a command or search modules (Cmd + K)..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
            className="w-full bg-transparent text-sm text-slate-900 dark:text-slate-100 placeholder-slate-400 focus:outline-none font-medium"
          />
          <button onClick={onClose} className="p-1 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-md text-slate-400">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Results List */}
        <div className="max-h-96 overflow-y-auto p-2 space-y-1">
          {filteredCommands.length === 0 ? (
            <div className="p-8 text-center text-sm text-slate-400">
              No matching commands or modules found.
            </div>
          ) : (
            filteredCommands.map((cmd, idx) => (
              <button
                key={idx}
                onClick={() => {
                  navigate(cmd.path);
                  onClose();
                }}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-left text-sm transition ${
                  idx === selectedIndex
                    ? 'bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-300 font-semibold'
                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800">{cmd.icon}</div>
                  <span>{cmd.label}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-slate-400">
                    {cmd.category}
                  </span>
                  <ArrowRight className="h-3.5 w-3.5 text-slate-400 opacity-0 group-hover:opacity-100" />
                </div>
              </button>
            ))
          )}
        </div>

        {/* Footer info */}
        <div className="px-4 py-2 bg-slate-50 dark:bg-slate-900/80 border-t border-slate-200 dark:border-slate-800 text-[11px] text-slate-400 flex items-center justify-between">
          <span>Navigate with <kbd className="px-1.5 py-0.5 bg-slate-200 dark:bg-slate-800 rounded font-mono">↑</kbd> <kbd className="px-1.5 py-0.5 bg-slate-200 dark:bg-slate-800 rounded font-mono">↓</kbd></span>
          <span>Select with <kbd className="px-1.5 py-0.5 bg-slate-200 dark:bg-slate-800 rounded font-mono">Enter</kbd></span>
        </div>
      </div>
    </div>
  );
}
