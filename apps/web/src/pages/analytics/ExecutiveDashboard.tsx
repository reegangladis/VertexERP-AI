import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  Users,
  Package,
  Factory,
  Building,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Filter,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { analyticsService, ExecutiveAnalyticsResponse } from '@/services/analyticsService';

export function ExecutiveDashboard() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<ExecutiveAnalyticsResponse | null>(null);
  const [dateRange, setDateRange] = useState('YTD');
  const [branchFilter, setBranchFilter] = useState('ALL');

  useEffect(() => {
    fetchData();
  }, [dateRange, branchFilter]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getExecutiveDashboard();
      setData(res);
    } catch (err) {
      console.error('Failed to load executive analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <RefreshCw className="h-8 w-8 animate-spin text-blue-600 dark:text-blue-400" />
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400">Loading Executive Analytics Platform...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header & Controls */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Executive CEO Dashboard</h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-950/60 dark:text-blue-300">
              <Sparkles className="h-3 w-3" /> Live Analytics
            </span>
          </div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time cross-enterprise performance overview across Revenue, HR, CRM, Inventory, and Manufacturing.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 dark:border-slate-800 dark:bg-slate-900">
            <Filter className="h-4 w-4 text-slate-400" />
            <select
              value={branchFilter}
              onChange={(e) => setBranchFilter(e.target.value)}
              className="bg-transparent text-xs font-medium text-slate-700 focus:outline-none dark:text-slate-300"
            >
              <option value="ALL">All Enterprise Branches</option>
              <option value="HQ">Headquarters (NYC)</option>
              <option value="WEST">West Coast Operation</option>
              <option value="EU">EMEA Regional Hub</option>
            </select>
          </div>

          <div className="flex items-center rounded-lg border border-slate-200 bg-white p-1 dark:border-slate-800 dark:bg-slate-900">
            {['MTD', 'QTD', 'YTD', 'ALL'].map((period) => (
              <button
                key={period}
                onClick={() => setDateRange(period)}
                className={`rounded-md px-3 py-1 text-xs font-medium transition-all ${
                  dateRange === period
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100'
                }`}
              >
                {period}
              </button>
            ))}
          </div>

          <button
            onClick={fetchData}
            className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <RefreshCw className="h-3.5 w-3.5" /> Refresh
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {/* Revenue */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total Revenue</span>
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">
              <DollarSign className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">${data.total_revenue.toLocaleString()}</h3>
            <div className="mt-2 flex items-center gap-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
              <ArrowUpRight className="h-4 w-4" />
              <span>+{data.revenue_growth_yoy_percent}% YoY Growth</span>
            </div>
          </div>
        </div>

        {/* Profit Margin */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Net Profit</span>
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400">
              <TrendingUp className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">${data.net_profit.toLocaleString()}</h3>
            <div className="mt-2 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>Profit Margin:</span>
              <span className="font-semibold text-blue-600 dark:text-blue-400">{data.profit_margin_percent}%</span>
            </div>
          </div>
        </div>

        {/* Operating Cash Flow */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Cash Flow</span>
            <div className="rounded-lg bg-violet-50 p-2 text-violet-600 dark:bg-violet-950/50 dark:text-violet-400">
              <Activity className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">${data.operating_cash_flow.toLocaleString()}</h3>
            <div className="mt-2 flex items-center gap-1 text-xs font-medium text-emerald-600 dark:text-emerald-400">
              <ArrowUpRight className="h-4 w-4" />
              <span>Healthy Liquidity Ratio</span>
            </div>
          </div>
        </div>

        {/* Overall OEE */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Overall OEE</span>
            <div className="rounded-lg bg-amber-50 p-2 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400">
              <Factory className="h-5 w-5" />
            </div>
          </div>
          <div className="mt-3">
            <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">{data.overall_oee_percent}%</h3>
            <div className="mt-2 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">
              <span>Plant Yield:</span>
              <span className="font-semibold text-amber-600 dark:text-amber-400">World Class</span>
            </div>
          </div>
        </div>
      </div>

      {/* Secondary Metrics Bar */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center gap-3">
            <Users className="h-5 w-5 text-indigo-500" />
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Total Workforce</p>
              <p className="text-lg font-bold text-slate-900 dark:text-slate-100">{data.total_employees} Employees</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center gap-3">
            <Building className="h-5 w-5 text-cyan-500" />
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Active Customers</p>
              <p className="text-lg font-bold text-slate-900 dark:text-slate-100">{data.total_customers} Clients</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center gap-3">
            <Package className="h-5 w-5 text-emerald-500" />
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Inventory Valuation</p>
              <p className="text-lg font-bold text-slate-900 dark:text-slate-100">${(data.total_inventory_value / 1000000).toFixed(2)}M</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center gap-3">
            <DollarSign className="h-5 w-5 text-rose-500" />
            <div>
              <p className="text-xs text-slate-500 dark:text-slate-400">Operating Expenses</p>
              <p className="text-lg font-bold text-slate-900 dark:text-slate-100">${(data.total_expenses / 1000).toFixed(0)}k</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Financial Trend Bar Chart */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900 lg:col-span-2">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4 dark:border-slate-800">
            <div>
              <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Revenue & Expense Trajectory</h3>
              <p className="text-xs text-slate-500 dark:text-slate-400">Monthly breakdown of gross revenue vs operating costs</p>
            </div>
            <div className="flex items-center gap-4 text-xs font-semibold">
              <span className="flex items-center gap-1.5 text-emerald-600 dark:text-emerald-400">
                <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span> Revenue
              </span>
              <span className="flex items-center gap-1.5 text-rose-600 dark:text-rose-400">
                <span className="h-2.5 w-2.5 rounded-full bg-rose-500"></span> Expenses
              </span>
            </div>
          </div>

          <div className="mt-6 space-y-4">
            {data.monthly_financial_trend.map((item, idx) => {
              const maxVal = 250000;
              const revWidth = `${(item.revenue / maxVal) * 100}%`;
              const expWidth = `${(item.expenses / maxVal) * 100}%`;

              return (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs font-medium text-slate-700 dark:text-slate-300">
                    <span>{item.month}</span>
                    <span className="text-slate-500">Net Profit: ${item.profit.toLocaleString()}</span>
                  </div>
                  <div className="relative h-6 w-full overflow-hidden rounded-md bg-slate-100 dark:bg-slate-800">
                    <div
                      style={{ width: revWidth }}
                      className="absolute left-0 top-0 h-full bg-gradient-to-r from-emerald-500 to-teal-400 transition-all duration-500"
                    ></div>
                    <div
                      style={{ width: expWidth }}
                      className="absolute left-0 top-0 h-full bg-rose-500/40 border-r-2 border-rose-500 transition-all duration-500"
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Departmental Growth Distribution */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100">Department Performance</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Cross-divisional operational efficiency & growth</p>

          <div className="space-y-4">
            {data.department_performance.map((dept, idx) => (
              <div key={idx} className="rounded-lg border border-slate-100 p-3.5 dark:border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{dept.department}</span>
                  <span className="inline-flex items-center text-xs font-bold text-emerald-600 dark:text-emerald-400">
                    +{dept.growth_pct}% <ArrowUpRight className="h-3 w-3" />
                  </span>
                </div>
                <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  {dept.revenue_share_pct ? (
                    <span>Revenue Share: {dept.revenue_share_pct}%</span>
                  ) : dept.efficiency_pct ? (
                    <span>Operational Efficiency: {dept.efficiency_pct}%</span>
                  ) : dept.turnover_rate ? (
                    <span>Inventory Turnover: {dept.turnover_rate}x</span>
                  ) : (
                    <span>Retention Rate: {dept.retention_pct}%</span>
                  )}
                </div>
                <div className="mt-2 h-1.5 w-full rounded-full bg-slate-100 dark:bg-slate-800">
                  <div
                    className="h-full rounded-full bg-blue-600"
                    style={{ width: `${dept.growth_pct * 4}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
