import React from 'react';
import { FolderOpen, Sparkles, Plus } from 'lucide-react';
import { Button } from './Button';

interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  actionLabel?: string;
  onAction?: () => void;
  aiPrompt?: string;
}

export function EmptyState({
  title = 'No records found',
  description = 'There are no active records in this view yet. Create your first record or ask Vertex AI to generate sample telemetry data.',
  icon = <FolderOpen className="h-8 w-8 text-indigo-500" />,
  actionLabel,
  onAction,
  aiPrompt = 'Generate sample records with AI Copilot',
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-10 border border-slate-200/80 dark:border-slate-800 rounded-2xl bg-white/60 dark:bg-slate-800/40 text-center min-h-[340px] glass-card space-y-4 max-w-xl mx-auto my-6">
      <div className="flex items-center justify-center h-16 w-16 rounded-2xl bg-indigo-50 dark:bg-indigo-950/60 border border-indigo-100 dark:border-indigo-900 shadow-inner">
        {icon}
      </div>

      <div className="space-y-1">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">{title}</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto leading-relaxed">{description}</p>
      </div>

      {aiPrompt && (
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-[11px] font-mono text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
          <Sparkles className="h-3 w-3 text-purple-500" />
          <span>{aiPrompt}</span>
        </div>
      )}

      {actionLabel && onAction && (
        <Button
          variant="primary"
          onClick={onAction}
          className="mt-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-md transition font-bold text-xs py-2.5 px-5"
          leftIcon={<Plus className="h-4 w-4" />}
        >
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
export default EmptyState;
