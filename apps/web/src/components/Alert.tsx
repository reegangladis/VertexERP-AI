import React from 'react';
import { AlertCircle, CheckCircle2, Info, XCircle } from 'lucide-react';

export type AlertVariant = 'info' | 'success' | 'warning' | 'danger';

interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: AlertVariant;
  title?: string;
}

export function Alert({
  variant = 'info',
  title,
  children,
  className = '',
  ...props
}: AlertProps) {
  const styles = {
    info: 'bg-blue-50 dark:bg-blue-950/40 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-300',
    success: 'bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300',
    warning: 'bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-300',
    danger: 'bg-rose-50 dark:bg-rose-950/40 border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300',
  };

  const icons = {
    info: <Info className="h-4 w-4 text-blue-500" />,
    success: <CheckCircle2 className="h-4 w-4 text-emerald-500" />,
    warning: <AlertCircle className="h-4 w-4 text-amber-500" />,
    danger: <XCircle className="h-4 w-4 text-rose-500" />,
  };

  return (
    <div
      className={`relative w-full rounded-xl border p-3.5 flex gap-3 text-xs shadow-sm glass-panel ${styles[variant]} ${className}`}
      role="alert"
      {...props}
    >
      <div className="shrink-0 pt-0.5">{icons[variant]}</div>
      <div className="flex flex-col gap-0.5 w-full">
        {title && <h5 className="font-bold leading-tight">{title}</h5>}
        <div className="text-xs opacity-90 leading-relaxed">{children}</div>
      </div>
    </div>
  );
}
export default Alert;
