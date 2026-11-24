import React from "react";
import { cn } from "@/lib/utils";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export interface StatCardProps {
  title: string;
  value: string | number;
  change?: string | number;
  changeType?: "increase" | "decrease" | "neutral";
  icon?: React.ReactNode;
  description?: string;
  subtitle?: string;
  className?: string;
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  change,
  changeType = "neutral",
  icon,
  description,
  subtitle,
  className,
  onClick,
}) => {
  const descText = description || subtitle;
  return (
    <div
      onClick={onClick}
      className={cn(
        "p-5 rounded-xl border border-slate-800/80 bg-slate-900/60 backdrop-blur-sm transition-all duration-200",
        onClick && "cursor-pointer hover:border-slate-700 hover:bg-slate-800/50 hover:shadow-lg",
        className
      )}
    >
      <div className="flex items-center justify-between gap-2">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        {icon && (
          <div className="p-2 rounded-lg bg-slate-800/80 text-brand-400 shrink-0 border border-slate-700/50">
            {icon}
          </div>
        )}
      </div>

      <div className="mt-3 flex items-baseline gap-2">
        <div className="text-2xl font-bold tracking-tight text-slate-100">{value}</div>
        {change !== undefined && (
          <span
            className={cn(
              "inline-flex items-center gap-0.5 text-xs font-semibold px-1.5 py-0.5 rounded",
              changeType === "increase" && "text-emerald-400 bg-emerald-500/10",
              changeType === "decrease" && "text-rose-400 bg-rose-500/10",
              changeType === "neutral" && "text-slate-400 bg-slate-800"
            )}
          >
            {changeType === "increase" && <TrendingUp className="w-3 h-3" />}
            {changeType === "decrease" && <TrendingDown className="w-3 h-3" />}
            {changeType === "neutral" && <Minus className="w-3 h-3" />}
            {change}
          </span>
        )}
      </div>

      {(description || subtitle) && (
        <p className="mt-1.5 text-xs text-slate-400 leading-relaxed">{description || subtitle}</p>
      )}
    </div>
  );
};
