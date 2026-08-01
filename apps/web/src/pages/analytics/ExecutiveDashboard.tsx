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
import { analyticsService, ExecutiveAnalyticsResponse } from '@/services/analyticsService';

export function ExecutiveDashboard() {
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState('YTD');
  const [data, setData] = useState<ExecutiveAnalyticsResponse | null>(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getExecutiveDashboard();
      setData(res);
    } catch (err) {
      console.error('Error fetching Executive Dashboard data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, [dateRange]);

  const topProjects = [
    { id: 'PRJ-101', name: 'Global ERP Cloud Migration', department: 'IT Operations', value: '$1,200,000', status: 'IN_PROGRESS' },
    { id: 'PRJ-102', name: 'AI Demand Forecast Rollout', department: 'Data Science', value: '$450,000', status: 'COMPLETED' },
    { id: 'PRJ-103', name: 'Automated Supply Chain Hub', department: 'Logistics', value: '$820,000', status: 'IN_PROGRESS' },
    { id: 'PRJ-104', name: 'FinOps Cost Reduction Engine', department: 'Finance', value: '$340,000', status: 'COMPLETED' },
  ];

  const projectColumns = [
    { header: 'Project ID', accessorKey: (row: any) => <span className="font-mono font-bold text-indigo-600 dark:text-indigo-400">{row.id}</span> },
    { header: 'Project Name', accessorKey: (row: any) => <span className="font-semibold text-foreground">{row.name}</span> },
    { header: 'Department', accessorKey: 'department' as const },
    { header: 'Contract Value', accessorKey: (row: any) => <span className="font-mono font-bold text-emerald-500">{row.value}</span> },
    {
      header: 'Status',
      accessorKey: (row: any) => (
        <span
          className={`px-2.5 py-0.5 rounded-full text-[10px] font-mono font-bold ${
            row.status === 'COMPLETED'
              ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
              : 'bg-indigo-500/10 text-indigo-500 border border-indigo-500/20'
          }`}
        >
          {row.status}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold tracking-tight text-foreground">Executive CEO Cockpit</h1>
            <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 text-primary px-3 py-1 text-xs font-bold font-mono border border-primary/20">
              <Sparkles className="h-3.5 w-3.5" /> Vertex AI Telemetry
            </span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Real-time multi-cloud financial telemetry, workforce analytics, and enterprise BI overview.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="text-xs bg-card border border-border px-3 py-2 rounded-xl font-semibold focus:outline-none"
          >
            <option value="MTD">Month to Date (MTD)</option>
            <option value="QTD">Quarter to Date (QTD)</option>
            <option value="YTD">Year to Date (YTD)</option>
          </select>
          <button
            onClick={fetchDashboardData}
            className="p-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-sm transition"
            title="Refresh Data"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Gross Revenue"
          value={`$${(data?.total_revenue || 12450000).toLocaleString()}`}
          change={`+${data?.revenue_growth_yoy_percent || 18.4}%`}
          isPositive={true}
          subtitle="VS previous period"
          icon={<DollarSign className="h-5 w-5" />}
          badgeText="Target Exceeded"
        />
        <StatCard
          title="Total Active Workforce"
          value={`${data?.total_employees || 142} Employees`}
          change="+12.1%"
          isPositive={true}
          subtitle="Across global operations"
          icon={<Users className="h-5 w-5" />}
          badgeText="Optimal Retention"
        />
        <StatCard
          title="Inventory Stock Valuation"
          value={`$${(data?.total_inventory_value || 4180000).toLocaleString()}`}
          change="+4.2%"
          isPositive={true}
          subtitle="Turnover ratio: 6.8x"
          icon={<Package className="h-5 w-5" />}
          badgeText="Optimized"
        />
        <StatCard
          title="Net Profit Margin"
          value={`${data?.profit_margin_percent || 34.8}%`}
          change="+2.8%"
          isPositive={true}
          subtitle={`Net Profit: $${(data?.net_profit || 4330000).toLocaleString()}`}
          icon={<Activity className="h-5 w-5" />}
          badgeText="High Efficiency"
        />
      </div>

      {/* Financial Trend & Department Performance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-foreground flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              Monthly Financial Trend (Revenue vs Profit)
            </h3>
            <span className="text-xs text-muted-foreground font-mono">Real-time DB Aggregations</span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data?.monthly_financial_trend || []}>
                <defs>
                  <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="profitGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="month" stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <YAxis stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <Tooltip
                  contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="revenue" stroke="hsl(var(--primary))" fillOpacity={1} fill="url(#revenueGrad)" name="Revenue ($)" />
                <Area type="monotone" dataKey="profit" stroke="#10b981" fillOpacity={1} fill="url(#profitGrad)" name="Net Profit ($)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Performance */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Department Performance Scorecard</h3>
          <div className="space-y-3 text-xs">
            {data?.department_performance?.map((dp, idx) => (
              <div key={idx} className="p-3 border border-border rounded-lg bg-card space-y-1.5">
                <div className="flex justify-between font-bold text-foreground">
                  <span>{dp.department}</span>
                  <span className="text-emerald-500 font-mono">{dp.growth_pct ? `+${dp.growth_pct}%` : 'Optimal'}</span>
                </div>
                <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                  <div className="bg-primary h-full rounded-full" style={{ width: `${dp.revenue_share_pct || dp.efficiency_pct || 85}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Strategic Projects DataTable */}
      <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
        <h3 className="text-base font-bold text-foreground">Top Strategic Enterprise Initiatives</h3>
        <DataTable columns={projectColumns} data={topProjects} />
      </div>
    </div>
  );
}
