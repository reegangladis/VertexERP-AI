import React from "react";
import { cn } from "@/lib/utils";
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from "lucide-react";

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "info" | "warning" | "error" | "success";
  title?: string;
  message?: string;
  onClose?: () => void;
}

export const Alert: React.FC<AlertProps> = ({
  className,
  variant = "info",
  title,
  message,
  children,
  onClose,
  ...props
}) => {
  const icons = {
    info: <Info className="w-4 h-4 text-blue-400 shrink-0 mt-0.5" />,
    warning: <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />,
    error: <AlertCircle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />,
    success: <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />,
  };

  const variants = {
    info: "bg-blue-950/40 border-blue-800/60 text-blue-200",
    warning: "bg-amber-950/40 border-amber-800/60 text-amber-200",
    error: "bg-red-950/40 border-red-800/60 text-red-200",
    success: "bg-emerald-950/40 border-emerald-800/60 text-emerald-200",
  };

  return (
    <div
      role="alert"
      className={cn("flex items-start justify-between gap-3 p-4 rounded-xl border text-sm", variants[variant], className)}
      {...props}
    >
      <div className="flex gap-3">
        {icons[variant]}
        <div className="space-y-1">
          {title && <h5 className="font-semibold">{title}</h5>}
          <div className="text-xs leading-relaxed opacity-90">{children || message}</div>
        </div>
      </div>
      {onClose && (
        <button
          type="button"
          onClick={onClose}
          className="p-1 rounded hover:bg-white/10 text-slate-400 hover:text-slate-200 transition-colors shrink-0"
          aria-label="Dismiss alert"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      )}
    </div>
  );
};

