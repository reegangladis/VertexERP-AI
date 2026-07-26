import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  TrendingUp,
  Package,
  Factory,
  Users,
  RefreshCw,
  TrendingDown,
  Activity,
  CheckCircle2,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { observabilityService } from '@/services/observabilityService';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Legend } from 'recharts';

export function BusinessDashboard() {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [financialTrend, setFinancialTrend] = useState<any[]>([]);
  const [warehouseData, setWarehouseData] = useState<any[]>([]);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const res = await observabilityService.getBusinessMetrics();
      setData(res);

      // Generate simulated visual trends
      setFinancialTrend([
        { month: 'Jan', revenue: 210000, expenses: 140000 },
        { month: 'Feb', revenue: 230000, expenses: 150000 },
        { month: 'Mar', revenue: 280000, expenses: 170000 },
        { month: 'Apr', revenue: 310000, expenses: 190000 },
        { month: 'May', revenue: 290000, expenses: 180000 },
        { month: 'Jun', revenue: 320000, expenses: 195000 },
      ]);

      setWarehouseData([
        { name: 'Central WH', capacity: 90, utilized: 78.5 },
        { name: 'East branch', capacity: 100, utilized: 64.2 },
        { name: 'West warehouse', capacity: 80, utilized: 72.0 },
        { name: 'North logistics', capacity: 120, utilized: 84.5 },
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Business Dashboard"
        subtitle="Observe corporate financial growth rates, sales volume, production OEE, and HR telemetry metrics."
        actions={
          <Button variant="outline" size="sm" onClick={loadMetrics} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </Button>
        }
      />

      {/* Summary KPI Cards */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 border-l-4 border-l-emerald-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Monthly Revenue</span>
                <h3 className="text-xl font-bold text-foreground">${data.revenue.current_month.toLocaleString()}</h3>
                <p className="text-xs text-emerald-600 flex items-center">
                  <TrendingUp className="h-3.5 w-3.5 mr-0.5" />
                  +{data.revenue.growth_rate_percent}% growth MoM
                </p>
              </div>
              <div className="p-2 rounded bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600">
                <DollarSign className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-blue-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Completed Orders Today</span>
                <h3 className="text-xl font-bold text-foreground">{data.orders.completed_today}</h3>
                <p className="text-xs text-blue-600 flex items-center">
                  <CheckCircle2 className="h-3.5 w-3.5 mr-0.5" />
                  {data.orders.fulfillment_rate_percent}% fulfillment rate
                </p>
              </div>
              <div className="p-2 rounded bg-blue-50 dark:bg-blue-950/20 text-blue-600">
                <Package className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-indigo-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Shop floor OEE</span>
                <h3 className="text-xl font-bold text-foreground">{data.production.oee_percent}%</h3>
                <p className="text-xs text-indigo-600 flex items-center">
                  <Activity className="h-3.5 w-3.5 mr-0.5 animate-pulse" />
                  {data.production.active_runs} active runs
                </p>
              </div>
              <div className="p-2 rounded bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600">
                <Factory className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-teal-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Headcount Attendance</span>
                <h3 className="text-xl font-bold text-foreground">{data.hr.active_headcount} Active</h3>
                <p className="text-xs text-teal-600 flex items-center">
                  <Users className="h-3.5 w-3.5 mr-0.5" />
                  {data.hr.attendance_rate_today}% rate today
                </p>
              </div>
              <div className="p-2 rounded bg-teal-50 dark:bg-teal-950/20 text-teal-600">
                <Users className="h-5 w-5" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Corporate Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Financial Area Chart */}
        <Card className="p-5 space-y-4">
          <div>
            <h4 className="text-xs font-bold text-foreground">Monthly Financial Growth Trends</h4>
            <p className="text-[10px] text-muted-foreground">Historical comparison of corporate revenues vs overhead expenditures.</p>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={financialTrend} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                <defs>
                  <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="expenseGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f43f5e" stopOpacity={0.1}/>
                    <stop offset="95%" stopColor="#f43f5e" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted-foreground/10" />
                <XAxis dataKey="month" className="text-[10px] fill-muted-foreground font-mono" />
                <YAxis className="text-[10px] fill-muted-foreground font-mono" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--color-border)', borderRadius: '8px' }} />
                <Legend className="text-[10px]" />
                <Area type="monotone" dataKey="revenue" name="Revenue ($)" stroke="#10b981" fillOpacity={1} fill="url(#revenueGrad)" strokeWidth={2} />
                <Area type="monotone" dataKey="expenses" name="Expenses ($)" stroke="#f43f5e" fillOpacity={1} fill="url(#expenseGrad)" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Warehouse Bar Chart */}
        <Card className="p-5 space-y-4">
          <div>
            <h4 className="text-xs font-bold text-foreground">Warehouse Inventory Storage Load</h4>
            <p className="text-[10px] text-muted-foreground">Capacity limit volumes vs current active utilization rates.</p>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={warehouseData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted-foreground/10" />
                <XAxis dataKey="name" className="text-[10px] fill-muted-foreground font-mono" />
                <YAxis className="text-[10px] fill-muted-foreground font-mono" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--color-border)', borderRadius: '8px' }} />
                <Legend className="text-[10px]" />
                <Bar dataKey="utilized" name="Active Utilization (%)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
export default BusinessDashboard;
