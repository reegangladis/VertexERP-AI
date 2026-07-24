import React from 'react';
import { useNotification, ToastNotification } from '@/hooks/useNotification';
import { CheckCircle2, AlertCircle, Info, XCircle, X } from 'lucide-react';
import { Button } from './Button';

export function ToastContainer() {
  const { notifications, removeNotification } = useNotification();

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 w-full max-w-sm pointer-events-none">
      {notifications.map((toast) => (
        <Toast
          key={toast.id}
          toast={toast}
          onClose={() => removeNotification(toast.id)}
        />
      ))}
    </div>
  );
}

interface ToastProps {
  toast: ToastNotification;
  onClose: () => void;
}

function Toast({ toast, onClose }: ToastProps) {
  const styles = {
    info: 'bg-card border-blue-500/30 text-blue-500',
    success: 'bg-card border-emerald-500/30 text-emerald-500',
    warning: 'bg-card border-amber-500/30 text-amber-500',
    error: 'bg-card border-destructive/30 text-destructive',
  };

  const icons = {
    info: <Info className="h-4 w-4 shrink-0" />,
    success: <CheckCircle2 className="h-4 w-4 shrink-0" />,
    warning: <AlertCircle className="h-4 w-4 shrink-0" />,
    error: <XCircle className="h-4 w-4 shrink-0" />,
  };

  return (
    <div
      className={`pointer-events-auto flex items-center justify-between gap-3 w-full rounded-lg border p-4 shadow-lg bg-card animate-in slide-in-from-bottom-5 duration-200 ${
        styles[toast.type]
      }`}
      role="alert"
    >
      <div className="flex items-center gap-3">
        {icons[toast.type]}
        <p className="text-sm font-medium text-foreground">{toast.message}</p>
      </div>
      <Button
        variant="ghost"
        size="sm"
        onClick={onClose}
        className="p-1 h-auto w-auto rounded hover:bg-muted text-muted-foreground"
      >
        <X className="h-3.5 w-3.5" />
      </Button>
    </div>
  );
}
export default ToastContainer;
