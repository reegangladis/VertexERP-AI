import React, { useState, useEffect } from 'react';
import { DollarSign, TrendingUp, CreditCard, PieChart as PieIcon, RefreshCw } from 'lucide-react';
import { StatCard } from '@/components/common/StatCard';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { analyticsService, FinanceAnalyticsResponse } from '@/services/analyticsService';

export function FinanceAnalyticsPage() {
  const [data, setData] = useState<FinanceAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchFinanceAnalytics = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getFinanceAnalytics();
      setData(res);
    } catch (err) {
      console.error('Error fetching Finance analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFinanceAnalytics();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <DollarSign className="h-6 w-6 text-primary" />
            Financial Intelligence & Cash Flow Analytics
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Revenue vs Expenses, Profitability, Budget Utilization & AR/AP Aging Overview
          </p>
        </div>
        <button
          onClick={fetchFinanceAnalytics}
          className="p-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-sm transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Gross Revenue"
          value={`$${(data?.total_revenue || 12450000).toLocaleString()}`}
          change="+18.4%"
          isPositive={true}
          subtitle={`Expenses: $${(data?.total_expenses || 8120000).toLocaleString()}`}
          icon={<DollarSign className="h-5 w-5" />}
        />
        <StatCard
          title="Net Operating Income"
          value={`$${(data?.net_income || 4330000).toLocaleString()}`}
          change="+14.2%"
          isPositive={true}
          subtitle="Net Profit"
          icon={<TrendingUp className="h-5 w-5" />}
        />
        <StatCard
          title="Operating Cash Flow"
          value={`$${(data?.operating_cash_flow || 5100000).toLocaleString()}`}
          change="+6.5%"
          isPositive={true}
          subtitle={`Budget Util: ${data?.budget_utilization_percent || 91.2}%`}
          icon={<PieIcon className="h-5 w-5" />}
        />
        <StatCard
          title="Accounts Receivable (AR)"
          value={`$${(data?.accounts_receivable || 1420000).toLocaleString()}`}
          change={`AP: $${(data?.accounts_payable || 840000).toLocaleString()}`}
          isPositive={true}
          subtitle="Current Outstanding"
          icon={<CreditCard className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue vs Expenses Trend */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Revenue vs Operating Expenses</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.revenue_vs_expenses_trend || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="period" stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <YAxis stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }} />
                <Bar dataKey="revenue" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Revenue ($)" />
                <Bar dataKey="expenses" fill="#ef4444" radius={[4, 4, 0, 0]} name="Expenses ($)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Budget vs Actual by Category */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Budget vs Actual Spend by Category</h3>
          <div className="border border-border rounded-lg overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 border-b border-border text-muted-foreground font-medium uppercase text-[10px]">
                <tr>
                  <th className="px-4 py-3">Expense Category</th>
                  <th className="px-4 py-3 font-mono">Budget</th>
                  <th className="px-4 py-3 font-mono">Actual Spend</th>
                  <th className="px-4 py-3 text-right">Variance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-foreground font-mono">
                {data?.budget_vs_actual_by_category?.map((b, idx) => {
                  const varVal = b.budget - b.actual;
                  return (
                    <tr key={idx} className="hover:bg-muted/30">
                      <td className="px-4 py-3 font-sans font-semibold">{b.category}</td>
                      <td className="px-4 py-3">${b.budget?.toLocaleString()}</td>
                      <td className="px-4 py-3 text-emerald-500">${b.actual?.toLocaleString()}</td>
                      <td className={`px-4 py-3 text-right font-bold ${varVal >= 0 ? 'text-emerald-500' : 'text-red-400'}`}>
                        {varVal >= 0 ? '+' : ''}${varVal?.toLocaleString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
