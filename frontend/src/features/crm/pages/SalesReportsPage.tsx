import React from "react";
import { useQuery } from "@tanstack/react-query";
import { crmApi } from "../api/crmApi";
import { CRMDashboardMetrics } from "../types";
import { StatCard } from "@/components/ui/StatCard";
import { formatCurrency } from "@/lib/utils";
import { TrendingUp, Users, DollarSign, Target, Award, PieChart, BarChart3 } from "lucide-react";

export const SalesReportsPage: React.FC = () => {
  const { data: metrics, isLoading } = useQuery<CRMDashboardMetrics>({
    queryKey: ["crm-metrics"],
    queryFn: crmApi.getMetrics,
  });

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Sales Analytics & Reports</h1>
        <p className="text-sm text-slate-500">
          Executive performance summary, conversion funnels, quota attainment, and revenue projections.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <StatCard
          title="Pipeline Volume"
          value={metrics ? formatCurrency(metrics.pipeline_value) : "$0"}
          subtitle={`${metrics?.deals_open || 0} active opportunities`}
          icon={<DollarSign className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Realized Revenue"
          value={metrics ? formatCurrency(metrics.won_revenue) : "$0"}
          subtitle={`${metrics?.deals_won || 0} deals closed won`}
          icon={<Award className="w-5 h-5 text-emerald-600" />}
        />
        <StatCard
          title="Lead Win Rate"
          value={`${metrics?.conversion_rate_pct ?? 0}%`}
          subtitle="Lead-to-deal conversion efficiency"
          icon={<Target className="w-5 h-5 text-amber-600" />}
        />
        <StatCard
          title="Active Leads"
          value={metrics?.leads_open || 0}
          subtitle={`Out of ${metrics?.leads_total || 0} total leads`}
          icon={<Users className="w-5 h-5 text-sky-600" />}
        />
      </div>

      {/* Analytical Breakdown Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pipeline Funnel Analysis */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <PieChart className="w-5 h-5 text-indigo-600" />
              <h2 className="font-bold text-slate-900 text-base">Stage Conversion Distribution</h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Real-time DB metrics</span>
          </div>

          <div className="space-y-3 pt-2">
            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Leads Inflow & Qualification</span>
                <span>{metrics?.leads_total || 0} Leads</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3">
                <div className="bg-indigo-600 h-3 rounded-full" style={{ width: "100%" }} />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Opportunities Created</span>
                <span>{metrics?.deals_total || 0} Deals</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full"
                  style={{
                    width: `${Math.min(
                      100,
                      ((metrics?.deals_total || 1) / Math.max(1, metrics?.leads_total || 1)) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                <span>Closed Won Contracts</span>
                <span>{metrics?.deals_won || 0} Won</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3">
                <div
                  className="bg-emerald-600 h-3 rounded-full"
                  style={{
                    width: `${Math.min(
                      100,
                      ((metrics?.deals_won || 0) / Math.max(1, metrics?.deals_total || 1)) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Quota & Attainment Insights */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-emerald-600" />
              <h2 className="font-bold text-slate-900 text-base">Sales Performance Insights</h2>
            </div>
            <span className="text-xs text-slate-400 font-medium">Monthly Assessment</span>
          </div>

          <div className="space-y-3 pt-2 text-sm text-slate-600">
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex items-start gap-3">
              <TrendingUp className="w-5 h-5 text-emerald-600 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-semibold text-slate-800">Healthy Pipeline Velocity</div>
                <div className="text-xs text-slate-500 mt-0.5">
                  Deals advancing across qualification and proposal stages are converting at an average rate of{" "}
                  {metrics?.conversion_rate_pct ?? 0}%.
                </div>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 flex items-start gap-3">
              <Target className="w-5 h-5 text-indigo-600 mt-0.5 flex-shrink-0" />
              <div>
                <div className="font-semibold text-slate-800">Forecasted Win Total</div>
                <div className="text-xs text-slate-500 mt-0.5">
                  Currently tracking {formatCurrency(metrics?.won_revenue || 0)} in realized closed business.
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
