import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  DollarSign,
  Users,
  Package,
  Factory,
  Activity,
  Sparkles,
  RefreshCw,
  Zap,
  ShieldCheck,
  Globe,
  ArrowUpRight,
} from 'lucide-react';
import { StatCard } from '@/components/common/StatCard';
import { DataTable } from '@/components/common/DataTable';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts';

export function ExecutiveDashboard() {
  const [loading, setLoading] = useState(false);
  const [dateRange, setDateRange] = useState('YTD');

  const revenueData = [
    { month: 'Jan', revenue: 1200000, profit: 340000 },
    { month: 'Feb', revenue: 1450000, profit: 410000 },
    { month: 'Mar', revenue: 1300000, profit: 380000 },
    { month: 'Apr', revenue: 1680000, profit: 520000 },
    { month: 'May', revenue: 1950000, profit: 610000 },
    { month: 'Jun', revenue: 2100000, profit: 680000 },
    { month: 'Jul', revenue: 2450000, profit: 820000 },
  ];

  const departmentPerformance = [
    { dept: 'Sales & CRM', score: 96, growth: '+14%' },
    { dept: 'HR & Talent', score: 92, growth: '+8%' },
    { dept: 'Inventory', score: 94, growth: '+11%' },
    { dept: 'Finance', score: 98, growth: '+18%' },
    { dept: 'Manufacturing', score: 90, growth: '+6%' },
  ];

  const topProjects = [
    { id: 'PRJ-101', name: 'Global ERP Cloud Migration', department: 'IT Operations', value: '$1,200,000', status: 'IN_PROGRESS', score: '98%' },
    { id: 'PRJ-102', name: 'AI Demand Forecast Rollout', department: 'Data Science', value: '$450,000', status: 'COMPLETED', score: '100%' },
    { id: 'PRJ-103', name: 'Automated Supply Chain Hub', department: 'Logistics', value: '$820,000', status: 'IN_PROGRESS', score: '94%' },
    { id: 'PRJ-104', name: 'FinOps Cost Reduction Engine', department: 'Finance', value: '$340,000', status: 'COMPLETED', score: '99%' },
  ];

  const projectColumns = [
    { header: 'Project ID', accessorKey: (row: any) => <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">{row.id}</span> },
    { header: 'Project Name', accessorKey: (row: any) => <span className="font-semibold text-slate-800 dark:text-slate-200">{row.name}</span> },
    { header: 'Department', accessorKey: 'department' as const },
    { header: 'Contract Value', accessorKey: (row: any) => <span className="font-mono font-bold text-emerald-600">{row.value}</span> },
    {
      header: 'Status',
      accessorKey: (row: any) => (
        <span
          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
            row.status === 'COMPLETED'
              ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300'
              : 'bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300'
          }`}
        >
          {row.status}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Executive CEO Cockpit</h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-950 dark:text-indigo-300 px-3 py-1 text-xs font-bold font-mono">
              <Sparkles className="h-3.5 w-3.5" /> Vertex AI Telemetry
            </span>
          </div>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">
            Real-time multi-cloud financial telemetry, workforce analytics, and autonomous AI recommendations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="text-xs bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-3 py-2 rounded-xl font-semibold focus:outline-none"
          >
            <option value="MTD">Month to Date (MTD)</option>
            <option value="QTD">Quarter to Date (QTD)</option>
            <option value="YTD">Year to Date (YTD)</option>
          </select>
          <button className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-sm transition">
            <RefreshCw className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Gross Revenue"
          value="$14,250,800"
          change="+18.4%"
          isPositive={true}
          subtitle="VS previous period"
          icon={<DollarSign className="h-5 w-5" />}
          badgeText="Target Exceeded"
        />
        <StatCard
          title="Active Enterprise Users"
          value="12,450"
          change="+12.1%"
          isPositive={true}
          subtitle="Across 3 global regions"
          icon={<Users className="h-5 w-5" />}
          badgeText="99.99% Uptime"
        />
        <StatCard
          title="Inventory Stock Valuation"
          value="$8,420,000"
          change="+4.2%"
          isPositive={true}
          subtitle="Turnover ratio: 6.4x"
          icon={<Package className="h-5 w-5" />}
          badgeText="Optimized"
        />
        <StatCard
          title="Net Profit Margin"
          value="28.4 %"
          change="+2.8%"
          isPositive={true}
          subtitle="EBITDA Margin 34.1%"
          icon={<Activity className="h-5 w-5" />}
          badgeText="High Efficiency"
        />
      </div>

      {/* Main Charts & AI Insights Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue & Profit Growth Chart (2 cols) */}
        <div className="lg:col-span-2 bg-white dark:bg-slate-800/90 rounded-2xl border border-slate-200/80 dark:border-slate-800 p-5 shadow-sm glass-card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-indigo-500" /> Revenue & Profit Trajectory (2026 YTD)
            </h2>
            <span className="text-xs text-slate-400 font-mono">USD Millions</span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={revenueData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorProfit" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.1} />
                <XAxis dataKey="month" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    borderColor: '#334155',
                    borderRadius: '12px',
                    color: '#f8fafc',
                  }}
                />
                <Area type="monotone" dataKey="revenue" stroke="#6366f1" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" name="Gross Revenue" />
                <Area type="monotone" dataKey="profit" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorProfit)" name="Net Profit" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* AI Executive Insights Card (1 col) */}
        <div className="bg-gradient-to-br from-indigo-900 via-slate-900 to-purple-950 text-white rounded-2xl p-5 shadow-xl border border-indigo-500/30 flex flex-col justify-between space-y-4 relative overflow-hidden">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-mono font-bold tracking-wide border border-indigo-500/30 flex items-center gap-1">
                <Sparkles className="h-3.5 w-3.5" /> Vertex AI Copilot
              </span>
              <span className="text-[11px] opacity-70">Updated 2m ago</span>
            </div>

            <h3 className="text-xl font-extrabold leading-snug">Autonomous Enterprise Insights</h3>

            <div className="space-y-3 text-xs opacity-90">
              <div className="p-3 bg-white/10 rounded-xl backdrop-blur-sm border border-white/10 space-y-1">
                <p className="font-bold text-amber-300">💡 FinOps Optimization Alert</p>
                <p className="text-[11px]">Convert 8 EKS worker nodes to AWS Savings Plans to save **$3,200/mo**.</p>
              </div>

              <div className="p-3 bg-white/10 rounded-xl backdrop-blur-sm border border-white/10 space-y-1">
                <p className="font-bold text-emerald-300">📈 Sales Conversion Surge</p>
                <p className="text-[11px]">CRM win rate increased **+14%** following Phase 14 AI Copilot integration.</p>
              </div>
            </div>
          </div>

          <button className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-lg transition flex items-center justify-center gap-2">
            <span>Explore AI Copilot Recommendations</span>
            <ArrowUpRight className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Enterprise Data Table */}
      <DataTable
        title="High-Priority Enterprise Strategic Initiatives"
        data={topProjects}
        columns={projectColumns}
        searchPlaceholder="Filter strategic projects..."
      />
    </div>
  );
}
export default ExecutiveDashboard;
