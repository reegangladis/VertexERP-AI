import React, { useState, useEffect } from 'react';
import {
  Users,
  Clock,
  Calendar,
  Award,
  BookOpen,
  TrendingUp,
  RefreshCw,
  UserCheck,
  Building2,
  PieChart as PieIcon,
} from 'lucide-react';
import { analyticsService, HRAnalyticsResponse } from '@/services/analyticsService';

export function HRAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<HRAnalyticsResponse | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getHRAnalytics();
      setData(res);
    } catch (err) {
      console.error('Failed to load HR analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-indigo-600 dark:text-indigo-400" />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">HR & Workforce Intelligence</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Comprehensive analytics on headcount growth, attendance efficiency, leave utilization, performance, and L&D training metrics.
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
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Total Workforce</span>
            <div className="rounded-lg bg-indigo-50 p-2 text-indigo-600 dark:bg-indigo-950/50 dark:text-indigo-400">
              <Users className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.total_employees}</h3>
          <p className="mt-1 text-xs text-indigo-600 dark:text-indigo-400 font-medium">+{data.headcount_growth_percent}% YoY Growth</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Attendance Rate</span>
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">
              <Clock className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.attendance_rate_percent}%</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{data.active_employees} active employees present</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Training Completion</span>
            <div className="rounded-lg bg-cyan-50 p-2 text-cyan-600 dark:bg-cyan-950/50 dark:text-cyan-400">
              <BookOpen className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.training_completion_rate}%</h3>
          <p className="mt-1 text-xs text-cyan-600 dark:text-cyan-400 font-medium">L&D Certification Target Met</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Top Performers</span>
            <div className="rounded-lg bg-amber-50 p-2 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400">
              <Award className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.top_performer_count}</h3>
          <p className="mt-1 text-xs text-amber-600 dark:text-amber-400 font-medium">Exceeds Expectations Rating</p>
        </div>
      </div>

      {/* Analytics Breakdown Row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Department Headcount Breakdown */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">Department Headcount Distribution</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Total workforce allocation across corporate departments</p>

          <div className="space-y-3">
            {data.department_headcount_breakdown.map((dept, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                  <span>{dept.department}</span>
                  <span>{dept.count} ({dept.percentage}%)</span>
                </div>
                <div className="h-2.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full"
                    style={{ width: `${dept.percentage}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Leave Category Distribution */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">Leave Utilization Breakdown</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Total days taken by category across organization</p>

          <div className="grid grid-cols-2 gap-4">
            {data.leave_category_distribution.map((cat, idx) => (
              <div key={idx} className="rounded-lg border border-slate-100 p-4 dark:border-slate-800">
                <div className="text-xs font-medium text-slate-500 dark:text-slate-400">{cat.category}</div>
                <div className="mt-2 text-xl font-bold text-slate-900 dark:text-slate-100">{cat.days} Days</div>
                <div className="mt-1 text-xs text-indigo-600 dark:text-indigo-400 font-semibold">Approved Absence</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
