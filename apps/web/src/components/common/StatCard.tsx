import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  change?: string;
  isPositive?: boolean;
  subtitle?: string;
  icon?: React.ReactNode;
  badgeText?: string;
}

export function StatCard({ title, value, change, isPositive = true, subtitle, icon, badgeText }: StatCardProps) {
  return (
    <div className="bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm hover:shadow-md transition-all duration-300 glass-card space-y-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title}</span>
        {icon && <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-700/50 text-indigo-600 dark:text-indigo-400">{icon}</div>}
      </div>

      <div className="flex items-baseline justify-between">
        <h3 className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{value}</h3>
        {change && (
          <span
            className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold font-mono ${
              isPositive
                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950/80 dark:text-emerald-300'
                : 'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300'
            }`}
          >
            {isPositive ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
            {change}
          </span>
        )}
      </div>

      {(subtitle || badgeText) && (
        <div className="pt-2 border-t border-slate-100 dark:border-slate-700/60 flex items-center justify-between text-xs text-slate-400">
          <span>{subtitle}</span>
          {badgeText && <span className="font-mono text-[10px] uppercase font-bold text-indigo-500">{badgeText}</span>}
        </div>
      )}
    </div>
  );
}
