import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { aiApi } from "../api/aiApi";
import { StatCard } from "@/components/ui/StatCard";
import { DataTable } from "@/components/ui/DataTable";
import { formatCurrency } from "@/lib/utils";
import { TrendingUp, DollarSign, Target, BarChart2, CheckCircle2 } from "lucide-react";

export const SalesForecastingPage: React.FC = () => {
  const [scenario, setScenario] = useState<"PROJECTED" | "OPTIMISTIC" | "CONSERVATIVE">("PROJECTED");

  const { data: forecast, isLoading } = useQuery({
    queryKey: ["ai-sales-forecast"],
    queryFn: aiApi.getSalesForecast,
  });

  const columns = [
    {
      header: "Forecast Horizon",
      accessorKey: "month",
      cell: (row: any) => (
        <span className="font-semibold text-slate-800">{row.month}</span>
      ),
    },
    {
      header: "Baseline Run-Rate",
      accessorKey: "baseline_revenue",
      cell: (row: any) => (
        <span className="text-slate-600 font-medium">
          {formatCurrency(row.baseline_revenue)}
        </span>
      ),
    },
    {
      header: "Target Projection (ML)",
      accessorKey: "pipeline_projected",
      cell: (row: any) => (
        <span className="font-bold text-indigo-600">
          {formatCurrency(row.pipeline_projected)}
        </span>
      ),
    },
    {
      header: "Optimistic (+20%)",
      accessorKey: "optimistic_scenario",
      cell: (row: any) => (
        <span className="text-emerald-600 font-medium">
          {formatCurrency(row.optimistic_scenario)}
        </span>
      ),
    },
    {
      header: "Conservative (-15%)",
      accessorKey: "conservative_scenario",
      cell: (row: any) => (
        <span className="text-amber-600 font-medium">
          {formatCurrency(row.conservative_scenario)}
        </span>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2.5">
          <TrendingUp className="w-7 h-7 text-indigo-600" />
          <span>Predictive Sales & Revenue Forecasting</span>
        </h1>
        <p className="text-sm text-slate-500">
          6-month forward-looking financial trajectory synthesized from live CRM deal pipelines and probability distributions.
        </p>
      </div>

      {/* KPI Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <StatCard
          title="6-Month Projected Revenue"
          value={forecast ? formatCurrency(forecast.total_projected_6m) : "$0"}
          subtitle="Model-adjusted total bookings"
          icon={<DollarSign className="w-5 h-5 text-indigo-600" />}
        />
        <StatCard
          title="Weighted CRM Pipeline"
          value={forecast ? formatCurrency(forecast.weighted_pipeline) : "$0"}
          subtitle="Probability-weighted open opportunities"
          icon={<Target className="w-5 h-5 text-emerald-600" />}
        />
        <StatCard
          title="Statistical Confidence"
          value={`${forecast?.confidence_interval_pct ?? 90}%`}
          subtitle="95% confidence interval fit"
          icon={<BarChart2 className="w-5 h-5 text-purple-600" />}
        />
      </div>

      {/* Forecast Projections Table Card */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-6 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-3">
          <div>
            <h2 className="font-bold text-slate-900 text-base">Monthly Forward Projections</h2>
            <p className="text-xs text-slate-500">Multi-scenario forecast breakdown with confidence bands.</p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 font-medium">Scenario:</span>
            <div className="flex rounded-xl border border-slate-200 p-0.5 bg-slate-50">
              <button
                onClick={() => setScenario("PROJECTED")}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  scenario === "PROJECTED" ? "bg-white text-indigo-600 shadow-sm" : "text-slate-600"
                }`}
              >
                Projected
              </button>
              <button
                onClick={() => setScenario("OPTIMISTIC")}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  scenario === "OPTIMISTIC" ? "bg-white text-emerald-600 shadow-sm" : "text-slate-600"
                }`}
              >
                Optimistic
              </button>
              <button
                onClick={() => setScenario("CONSERVATIVE")}
                className={`px-3 py-1 rounded-lg text-xs font-semibold transition ${
                  scenario === "CONSERVATIVE" ? "bg-white text-amber-600 shadow-sm" : "text-slate-600"
                }`}
              >
                Conservative
              </button>
            </div>
          </div>
        </div>

        <DataTable
          columns={columns}
          data={forecast?.monthly_projections || []}
          isLoading={isLoading}
          emptyMessage="No forecast projections available."
        />
      </div>
    </div>
  );
};
