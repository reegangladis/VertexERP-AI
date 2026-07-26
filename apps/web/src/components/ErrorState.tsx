import React from 'react';
import { AlertTriangle, RefreshCw, Terminal, ArrowLeft } from 'lucide-react';
import { Button } from './Button';
import { useNavigate } from 'react-router-dom';

interface ErrorStateProps {
  title?: string;
  description?: string;
  error?: Error | string;
  onRetry?: () => void;
}

export function ErrorState({
  title = 'System Telemetry Error',
  description = 'An unexpected execution error occurred while rendering this module.',
  error,
  onRetry,
}: ErrorStateProps) {
  const navigate = useNavigate();
  const errorMessage = error instanceof Error ? error.message : error;

  return (
    <div className="flex flex-col items-center justify-center p-8 border border-rose-200 dark:border-rose-900/60 rounded-2xl bg-rose-50/40 dark:bg-rose-950/20 text-center min-h-[340px] glass-card space-y-4 max-w-xl mx-auto my-6">
      <div className="flex items-center justify-center h-14 w-14 rounded-2xl bg-rose-100 dark:bg-rose-950/80 text-rose-600 dark:text-rose-400 shadow-inner">
        <AlertTriangle className="h-7 w-7" />
      </div>

      <div className="space-y-1">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">{title}</h3>
        <p className="text-xs text-slate-500 dark:text-slate-400 max-w-md mx-auto leading-relaxed">{description}</p>
      </div>

      {errorMessage && (
        <div className="w-full bg-slate-950 text-rose-300 font-mono text-[11px] p-3 rounded-xl border border-rose-900/40 text-left overflow-x-auto">
          <div className="flex items-center justify-between text-slate-500 text-[10px] pb-1 border-b border-slate-800 mb-1">
            <span className="flex items-center gap-1"><Terminal className="h-3 w-3" /> Execution Traceback</span>
            <span>REQ-ERR-500</span>
          </div>
          <code>{errorMessage}</code>
        </div>
      )}

      <div className="flex items-center gap-3 pt-2">
        {onRetry && (
          <Button
            variant="primary"
            onClick={onRetry}
            className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-md text-xs font-bold px-4 py-2"
            leftIcon={<RefreshCw className="h-3.5 w-3.5" />}
          >
            Retry Diagnostics
          </Button>
        )}
        <Button
          variant="outline"
          onClick={() => navigate('/analytics/executive')}
          className="rounded-xl text-xs font-semibold px-4 py-2"
          leftIcon={<ArrowLeft className="h-3.5 w-3.5" />}
        >
          Return to Cockpit
        </Button>
      </div>
    </div>
  );
}
export default ErrorState;
