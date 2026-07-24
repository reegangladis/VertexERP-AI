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
    info: 'bg-blue-500/10 border-blue-500/30 text-blue-500',
    success: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-500',
    warning: 'bg-amber-500/10 border-amber-500/30 text-amber-500',
    danger: 'bg-destructive/10 border-destructive/30 text-destructive',
  };

  const icons = {
    info: <Info className="h-4 w-4" />,
    success: <CheckCircle2 className="h-4 w-4" />,
    warning: <AlertCircle className="h-4 w-4" />,
    danger: <XCircle className="h-4 w-4" />,
  };

  return (
    <div
      className={`relative w-full rounded-lg border p-4 flex gap-3 text-sm ${styles[variant]} ${className}`}
      role="alert"
      {...props}
    >
      <div className="shrink-0 pt-0.5">{icons[variant]}</div>
      <div className="flex flex-col gap-1 w-full text-foreground">
        {title && <h5 className="font-semibold leading-none tracking-tight">{title}</h5>}
        <div className="text-xs leading-relaxed text-muted-foreground">{children}</div>
      </div>
    </div>
  );
}
export default Alert;
