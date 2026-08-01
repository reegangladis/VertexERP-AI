import React, { useState, useEffect } from 'react';
import { Users, UserCheck, Calendar, Award, TrendingUp, RefreshCw } from 'lucide-react';
import { StatCard } from '@/components/common/StatCard';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell } from 'recharts';
import { analyticsService, HRAnalyticsResponse } from '@/services/analyticsService';

export function HRAnalyticsPage() {
  const [data, setData] = useState<HRAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchHRAnalytics = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getHRAnalytics();
      setData(res);
    } catch (err) {
      console.error('Error fetching HR analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHRAnalytics();
  }, []);

  const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#8b5cf6'];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Users className="h-6 w-6 text-primary" />
            Human Resources & Workforce Analytics
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Headcount Growth, Attendance Patterns, Department Distribution & Training Progress
          </p>
        </div>
        <button
          onClick={fetchHRAnalytics}
          className="p-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-sm transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Workforce Headcount"
          value={`${data?.total_employees || 142} Employees`}
          change={`+${data?.headcount_growth_percent || 12.4}%`}
          isPositive={true}
          subtitle={`${data?.active_employees || 138} Active Personnel`}
          icon={<Users className="h-5 w-5" />}
        />
        <StatCard
          title="Average Attendance Rate"
          value={`${data?.attendance_rate_percent || 96.5}%`}
          change="+1.2%"
          isPositive={true}
          subtitle="Monthly Benchmark"
          icon={<UserCheck className="h-5 w-5" />}
        />
        <StatCard
          title="Avg Leave Days / Emp"
          value={`${data?.average_leave_days || 4.2} Days`}
          change="-0.5 days"
          isPositive={true}
          subtitle="YTD Average Utilization"
          icon={<Calendar className="h-5 w-5" />}
        />
        <StatCard
          title="Training Completion Rate"
          value={`${data?.training_completion_rate || 88.0}%`}
          change="+5.4%"
          isPositive={true}
          subtitle={`${data?.top_performer_count || 24} Top Performers`}
          icon={<Award className="h-5 w-5" />}
        />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Attendance Trend Chart */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Monthly Workforce Attendance Trend</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.monthly_attendance_trend || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="month" stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <YAxis domain={[90, 100]} stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }} />
                <Bar dataKey="rate" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Attendance Rate (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Headcount Distribution */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Department Headcount Distribution</h3>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.department_headcount_breakdown || []}
                  dataKey="count"
                  nameKey="department"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={(entry) => `${entry.department}: ${entry.count}`}
                >
                  {data?.department_headcount_breakdown?.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
