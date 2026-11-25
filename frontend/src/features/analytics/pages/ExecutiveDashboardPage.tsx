import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  ShoppingCart,
  Boxes,
  Factory,
  Users,
  ShieldCheck,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Calendar,
  RefreshCw,
  FileSpreadsheet,
  Layers,
  Sparkles,
  Award,
} from "lucide-react";
import { analyticsApi } from "../api/analyticsApi";
import {
  DateFilterPeriod,
  DimensionalDistributionData,
  DomainExecutiveSummary,
  MetricCardData,
  TimeSeriesData,
} from "../types";

const DEFAULT_KPIS: MetricCardData[] = [
  {
    code: "ARR",
    name: "Annual Recurring Revenue",
    category: "FINANCE",
    unit: "CURRENCY",
    formatted_value: "$12.8M",
    current_value: 12800000,
    delta_percentage: 14.2,
    status: "ON_TRACK",
    period_label: "This Month",
  },
  {
    code: "NET_MARGIN",
    name: "Operating Net Margin",
    category: "FINANCE",
    unit: "PERCENTAGE",
    formatted_value: "28.5%",
    current_value: 28.5,
    delta_percentage: 3.4,
    status: "ON_TRACK",
    period_label: "This Month",
  },
  {
    code: "PIPELINE",
    name: "Active Sales Pipeline",
    category: "SALES",
    unit: "CURRENCY",
    formatted_value: "$3.45M",
    current_value: 3450000,
    delta_percentage: 18.6,
    status: "ON_TRACK",
    period_label: "This Month",
  },
  {
    code: "HEADCOUNT",
    name: "Total Headcount",
    category: "HR",
    unit: "COUNT",
    formatted_value: "148 Staff",
    current_value: 148,
    delta_percentage: 4.2,
    status: "ON_TRACK",
    period_label: "This Month",
  },
  {
    code: "OEE",
    name: "Plant Efficiency (OEE)",
    category: "MANUFACTURING",
    unit: "PERCENTAGE",
    formatted_value: "94.2%",
    current_value: 94.2,
    delta_percentage: 2.1,
    status: "ON_TRACK",
    period_label: "This Month",
  },
  {
    code: "INV_VAL",
    name: "Inventory Valuation",
    category: "INVENTORY",
    unit: "CURRENCY",
    formatted_value: "$4.82M",
    current_value: 4820000,
    delta_percentage: 0.8,
    status: "ON_TRACK",
    period_label: "This Month",
  },
];

const DEFAULT_FIN_TREND: TimeSeriesData = {
  title: "Invoiced Gross Revenue vs Approved Operating Expenses",
  chart_type: "BAR",
  interval: "MONTHLY",
  series: [
    { timestamp: "2025-10-01", label: "Oct", primary_value: 840000, secondary_value: 520000 },
    { timestamp: "2025-11-01", label: "Nov", primary_value: 910000, secondary_value: 560000 },
    { timestamp: "2025-12-01", label: "Dec", primary_value: 1120000, secondary_value: 610000 },
    { timestamp: "2026-01-01", label: "Jan", primary_value: 1050000, secondary_value: 580000 },
    { timestamp: "2026-02-01", label: "Feb", primary_value: 1280000, secondary_value: 630000 },
    { timestamp: "2026-03-01", label: "Mar", primary_value: 1450000, secondary_value: 660000 },
  ],
};

const DEFAULT_SALES_DIST: DimensionalDistributionData = {
  title: "Sales Pipeline Funnel",
  dimension_name: "Pipeline Stage",
  chart_type: "FUNNEL",
  breakdowns: [
    { dimension_key: "DISCOVERY", dimension_label: "Discovery", total_amount: 620000, count: 5, percentage_share: 18 },
    { dimension_key: "QUALIFIED", dimension_label: "Qualification", total_amount: 940000, count: 4, percentage_share: 27 },
    { dimension_key: "PROPOSAL", dimension_label: "Proposal Sent", total_amount: 1150000, count: 3, percentage_share: 33 },
    { dimension_key: "NEGOTIATION", dimension_label: "Negotiation", total_amount: 740000, count: 2, percentage_share: 22 },
  ],
};

const DEFAULT_INV_DIST: DimensionalDistributionData = {
  title: "Inventory by Warehouse",
  dimension_name: "Warehouse",
  chart_type: "BAR",
  breakdowns: [
    { dimension_key: "WH_EAST", dimension_label: "East Coast Logistics (JFK)", total_amount: 2410000, count: 12, percentage_share: 50 },
    { dimension_key: "WH_WEST", dimension_label: "West Coast Fulfillment (OAK)", total_amount: 1590000, count: 8, percentage_share: 33 },
    { dimension_key: "WH_EMEA", dimension_label: "Rotterdam Depot (EMEA)", total_amount: 820000, count: 4, percentage_share: 17 },
  ],
};

export const ExecutiveDashboardPage: React.FC = () => {
  const [period, setPeriod] = useState<DateFilterPeriod>("THIS_MONTH");
  const [loading, setLoading] = useState(false);
  const [execSummary, setExecSummary] = useState<DomainExecutiveSummary | null>({
    domain: "EXECUTIVE",
    period_label: "This Month",
    kpis: DEFAULT_KPIS,
  });
  const [finTrend, setFinTrend] = useState<TimeSeriesData | null>(DEFAULT_FIN_TREND);
  const [salesDist, setSalesDist] = useState<DimensionalDistributionData | null>(DEFAULT_SALES_DIST);
  const [invDist, setInvDist] = useState<DimensionalDistributionData | null>(DEFAULT_INV_DIST);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchData = async () => {
    setLoading(true);
    try {
      const [summaryRes, trendRes, salesRes, invRes] = await Promise.allSettled([
        analyticsApi.getDomainSummary("EXECUTIVE", { period }),
        analyticsApi.getFinancialTrend({ period }),
        analyticsApi.getSalesPipelineDistribution({ period }),
        analyticsApi.getInventoryWarehouseBreakdown(),
      ]);

      if (summaryRes.status === "fulfilled") setExecSummary(summaryRes.value);
      if (trendRes.status === "fulfilled") setFinTrend(trendRes.value);
      if (salesRes.status === "fulfilled") setSalesDist(salesRes.value);
      if (invRes.status === "fulfilled") setInvDist(invRes.value);
      setLastRefreshed(new Date());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [period]);

  return (
    <div className="space-y-6 pb-12">
      {/* Top Header & Period Selector */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-zinc-900/85 p-6 rounded-2xl border border-zinc-800 backdrop-blur-2xl shadow-xl shadow-black/50">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-white">Executive Command Center</h1>
            <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-brand-500/15 text-brand-300 border border-brand-500/30">
              <Sparkles className="w-3.5 h-3.5 text-brand-400" />
              Realtime OLAP
            </span>
          </div>
          <p className="text-zinc-400 text-sm mt-1">
            Enterprise-wide telemetry across Financials, Sales Pipeline, Inventory, Manufacturing & Workforce.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center bg-zinc-950 rounded-xl p-1 border border-zinc-800">
            {(["TODAY", "THIS_WEEK", "THIS_MONTH", "THIS_QUARTER", "THIS_YEAR"] as DateFilterPeriod[]).map((p) => (
              <button
                key={p}
                onClick={() => setPeriod(p)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  period === p
                    ? "bg-gradient-to-r from-brand-600 to-amber-600 text-white shadow-md shadow-brand-600/30"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {p.replace("_", " ").toLowerCase().replace(/\b\w/g, (l) => l.toUpperCase())}
              </button>
            ))}
          </div>

          <button
            onClick={fetchData}
            disabled={loading}
            className="p-2.5 rounded-xl bg-zinc-950 text-zinc-300 hover:text-white hover:bg-brand-600/20 border border-zinc-800 transition shadow-sm"
            title="Refresh Analytics"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin text-brand-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        {execSummary?.kpis && execSummary.kpis.length > 0 ? (
          execSummary.kpis.map((kpi, i) => (
            <div
              key={kpi.code || kpi.kpi_code || String(i)}
              className="bg-zinc-900/85 border border-zinc-800 hover:border-brand-500/50 rounded-2xl p-4 transition-all duration-200 hover:shadow-xl hover:shadow-brand-600/10 group backdrop-blur-xl"
            >
              <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
                <span className="font-medium truncate">{kpi.name}</span>
                <span
                  className={`w-2 h-2 rounded-full ${
                    kpi.status === "ON_TRACK"
                      ? "bg-emerald-400 shadow-sm shadow-emerald-400/50"
                      : kpi.status === "WARNING"
                      ? "bg-amber-400 shadow-sm shadow-amber-400/50"
                      : "bg-rose-500 shadow-sm shadow-rose-500/50"
                  }`}
                />
              </div>

              <div className="text-xl font-bold text-white tracking-tight">
                {kpi.formatted_value || (kpi.current_value !== undefined && kpi.current_value !== null ? Number(kpi.current_value).toLocaleString() : "0")}
              </div>

              <div className="flex items-center gap-1 mt-2 text-xs font-semibold">
                {kpi.delta_percentage !== undefined && kpi.delta_percentage !== null ? (
                  kpi.delta_percentage >= 0 ? (
                    <span className="text-emerald-400 flex items-center">
                      <ArrowUpRight className="w-3.5 h-3.5 mr-0.5" />+{kpi.delta_percentage}%
                    </span>
                  ) : (
                    <span className="text-rose-400 flex items-center">
                      <ArrowDownRight className="w-3.5 h-3.5 mr-0.5" />
                      {kpi.delta_percentage}%
                    </span>
                  )
                ) : (
                  <span className="text-slate-500">Period flat</span>
                )}
                <span className="text-[10px] text-slate-500 font-normal ml-auto truncate">vs prior</span>
              </div>
            </div>
          ))
        ) : (
          <div className="col-span-full py-8 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
            {loading ? "Calculating enterprise metrics..." : "No KPI data available for this filter."}
          </div>
        )}
      </div>

      {/* Main Analytics Visualizations */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Financial Trajectory Chart */}
        <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-semibold text-white">Financial Trajectory & Cash Velocity</h2>
              <p className="text-xs text-slate-400 mt-0.5">Invoiced Gross Revenue vs Approved Operating Expenses</p>
            </div>
            <Link
              to="/analytics/finance"
              className="text-xs text-brand-400 hover:text-brand-300 flex items-center gap-1 font-medium"
            >
              Finance Details <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {finTrend?.series && finTrend.series.length > 0 ? (
            <div className="space-y-4">
              <div className="h-48 flex items-end gap-3 pt-6 border-b border-slate-800 pb-2">
                {finTrend.series.map((pt, i) => {
                  const revVal = Number(pt.primary_value ?? pt.value ?? 0);
                  const expVal = Number(pt.secondary_value ?? 0);
                  const revHeight = Math.min(100, Math.max(10, (revVal / 100000) * 100));
                  const expHeight = Math.min(100, Math.max(8, (expVal / 100000) * 100));
                  return (
                    <div key={i} className="flex-1 flex flex-col items-center gap-1 h-full justify-end group">
                      <div className="w-full flex items-end justify-center gap-1 h-full">
                        <div
                          style={{ height: `${revHeight}%` }}
                          className="w-1/2 bg-gradient-to-t from-brand-600 to-amber-400 rounded-t-sm transition-all duration-300 group-hover:brightness-125"
                          title={`Revenue: $${revVal.toLocaleString()}`}
                        />
                        <div
                          style={{ height: `${expHeight}%` }}
                          className="w-1/2 bg-gradient-to-t from-zinc-600 to-zinc-500 rounded-t-sm transition-all duration-300 group-hover:brightness-125"
                          title={`Expenses: $${expVal.toLocaleString()}`}
                        />
                      </div>
                      <span className="text-[10px] text-slate-400 mt-1 truncate">{pt.label}</span>
                    </div>
                  );
                })}
              </div>

              <div className="flex items-center justify-between text-xs text-slate-400 pt-2">
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm bg-brand-500" />
                    <span>Invoiced Revenue</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-sm bg-slate-500" />
                    <span>Operating Expenses</span>
                  </div>
                </div>
                <span className="text-slate-500">Auto-aggregated {finTrend.interval || "Period"}</span>
              </div>
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-slate-500 text-xs">
              No historical data points recorded yet.
            </div>
          )}
        </div>

        {/* Sales Pipeline Funnel */}
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-white">Sales Pipeline Funnel</h2>
              <Link to="/analytics/sales" className="text-xs text-brand-400 hover:text-brand-300 font-medium">
                View All
              </Link>
            </div>
            <p className="text-xs text-slate-400 mb-6">Deals distributed across active pipeline stages.</p>

            <div className="space-y-3">
              {salesDist?.breakdowns && salesDist.breakdowns.length > 0 ? (
                salesDist.breakdowns.map((b, i) => {
                  const totalAmt = Number(b.total_amount ?? 0);
                  const pct = Number(b.percentage_share ?? b.percentage ?? 0);
                  return (
                    <div key={b.dimension_key || String(i)} className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-medium text-slate-300">{b.dimension_label}</span>
                        <span className="text-slate-400 font-semibold">${totalAmt.toLocaleString()}</span>
                      </div>
                      <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                        <div
                          style={{ width: `${Math.min(100, Math.max(0, pct || 10))}%` }}
                          className="h-full bg-gradient-to-r from-brand-500 to-amber-400 rounded-full"
                        />
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className="py-8 text-center text-slate-500 text-xs">No active pipeline deals found.</div>
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
            <span>Stage Weighted Accuracy</span>
            <span className="font-semibold text-emerald-400">94.8% SLA</span>
          </div>
        </div>
      </div>

      {/* Domain Quick Launch Links */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          {
            title: "Financial Analytics",
            desc: "P&L breakdowns, DSO, AP/AR turnover & cash runway",
            to: "/analytics/finance",
            icon: <DollarSign className="w-5 h-5 text-emerald-400" />,
            badge: "P&L + Cash",
          },
          {
            title: "Sales & CRM Intelligence",
            desc: "Pipeline conversion, opportunity cohorts & bookings",
            to: "/analytics/sales",
            icon: <ShoppingCart className="w-5 h-5 text-brand-400" />,
            badge: "Bookings",
          },
          {
            title: "Inventory Health & Turn",
            desc: "Stock valuation, warehouse distribution & aging",
            to: "/analytics/inventory",
            icon: <Boxes className="w-5 h-5 text-amber-400" />,
            badge: "Stock Valuation",
          },
          {
            title: "Manufacturing Operations",
            desc: "First-Pass Yield (FPY), scrap cost & MO completion",
            to: "/analytics/manufacturing",
            icon: <Factory className="w-5 h-5 text-purple-400" />,
            badge: "Yield & Scrap",
          },
        ].map((card) => (
          <Link
            key={card.to}
            to={card.to}
            className="bg-slate-900/60 border border-slate-800 hover:border-brand-500/40 p-5 rounded-2xl transition-all duration-200 hover:shadow-lg hover:shadow-brand-500/5 group flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="p-2.5 rounded-xl bg-slate-800/80 border border-slate-700/60">{card.icon}</div>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                  {card.badge}
                </span>
              </div>
              <h3 className="text-sm font-bold text-white group-hover:text-brand-300 transition-colors">
                {card.title}
              </h3>
              <p className="text-xs text-slate-400 mt-1">{card.desc}</p>
            </div>
            <div className="mt-4 flex items-center text-xs font-semibold text-brand-400 group-hover:translate-x-0.5 transition-transform">
              Open Domain Analytics <ArrowUpRight className="w-3.5 h-3.5 ml-1" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};
