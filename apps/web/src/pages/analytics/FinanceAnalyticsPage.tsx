import React, { useState, useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  PieChart as PieIcon,
  Activity,
  CreditCard,
  Building,
  RefreshCw,
} from 'lucide-react';
import { analyticsService, FinanceAnalyticsResponse } from '@/services/analyticsService';

export function FinanceAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<FinanceAnalyticsResponse | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getFinanceAnalytics();
      setData(res);
    } catch (err) {
      console.error('Failed to load Finance analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-emerald-600 dark:text-emerald-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Finance & Accounting Intelligence</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time income statement overview, budget variance, cash flow analysis, and Accounts Receivable/Payable aging analytics.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh Analytics
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Net Income</span>
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">
              <DollarSign className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">${data.net_income.toLocaleString()}</h3>
          <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium">Revenue ${data.total_revenue.toLocaleString()}</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Budget Utilization</span>
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400">
              <PieIcon className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.budget_utilization_percent}%</h3>
          <p className="mt-1 text-xs text-blue-600 dark:text-blue-400 font-medium">Under Budget Cap</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Accounts Receivable</span>
            <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600 dark:bg-indigo-950/50 dark:text-indigo-400">
              <CreditCard className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">${data.accounts_receivable.toLocaleString()}</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Outstanding Customer Invoices</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Accounts Payable</span>
            <div className="rounded-lg bg-violet-50 p-2 text-violet-600 dark:bg-violet-950/50 dark:text-violet-400">
              <Building className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">${data.accounts_payable.toLocaleString()}</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Supplier Vendor Bills</p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Budget vs Actual by Category */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">Budget vs Actual Spend</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Department expense performance against allocated fiscal budgets</p>

          <div className="space-y-4">
            {data.budget_vs_actual_by_category.map((b, idx) => {
              const utilPct = Math.round((b.actual / b.budget) * 100);
              return (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                    <span>{b.category}</span>
                    <span>${b.actual.toLocaleString()} / ${b.budget.toLocaleString()} ({utilPct}%)</span>
                  </div>
                  <div className="h-2.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                    <div
                      className={`h-full rounded-full ${utilPct > 95 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                      style={{ width: `${utilPct}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* AR / AP Aging Breakdown */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">AR & AP Aging Schedule</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Aging schedule summary for receivables and payables</p>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="border-b border-slate-200 font-semibold text-slate-600 dark:border-slate-800 dark:text-slate-400">
                <tr>
                  <th className="py-2">Age Bracket</th>
                  <th className="py-2 text-right">Accounts Receivable</th>
                  <th className="py-2 text-right">Accounts Payable</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {data.ar_ap_aging_summary.map((row, idx) => (
                  <tr key={idx}>
                    <td className="py-2.5 font-medium text-slate-800 dark:text-slate-200">{row.bracket}</td>
                    <td className="py-2.5 text-right font-semibold text-emerald-600 dark:text-emerald-400">${row.ar.toLocaleString()}</td>
                    <td className="py-2.5 text-right font-semibold text-rose-600 dark:text-rose-400">${row.ap.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
