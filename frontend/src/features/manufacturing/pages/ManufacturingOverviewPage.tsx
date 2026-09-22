import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Factory,
  Cpu,
  Layers,
  GitMerge,
  ClipboardList,
  CheckCircle2,
  AlertTriangle,
  Play,
  ArrowRight,
  TrendingUp,
  Package,
  Wrench,
  Clock,
  Plus,
} from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { ProductionOrder, WorkOrder, QualityInspection } from "../types";

export const ManufacturingOverviewPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [totalOrders, setTotalOrders] = useState(0);
  const [inProgressOrders, setInProgressOrders] = useState(0);
  const [completedOrders, setCompletedOrders] = useState(0);
  const [recentOrders, setRecentOrders] = useState<ProductionOrder[]>([]);
  const [recentInspections, setRecentInspections] = useState<QualityInspection[]>([]);
  const [totalWorkCenters, setTotalWorkCenters] = useState(0);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [ordersRes, wcRes, qcRes] = await Promise.allSettled([
          manufacturingApi.getProductionOrders({ page: 1, page_size: 10 }),
          manufacturingApi.getWorkCenters({ page: 1, page_size: 50 }),
          manufacturingApi.getQualityInspections({ page: 1, page_size: 5 }),
        ]);

        if (ordersRes.status === "fulfilled") {
          const orders = ordersRes.value.items || [];
          setRecentOrders(orders);
          setTotalOrders(ordersRes.value.total || orders.length);
          setInProgressOrders(orders.filter((o) => o.status === "IN_PROGRESS").length);
          setCompletedOrders(orders.filter((o) => o.status === "COMPLETED").length);
        }

        if (wcRes.status === "fulfilled") {
          setTotalWorkCenters(wcRes.value.total || (wcRes.value.items || []).length);
        }

        if (qcRes.status === "fulfilled") {
          setRecentInspections(qcRes.value.items || []);
        }
      } catch (err) {
        console.error("Failed to load manufacturing dashboard data", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-xl border border-indigo-900/50">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm mb-1 uppercase tracking-wider">
            <Factory className="w-4 h-4" /> Production Operations & MRP Engine
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Manufacturing Control Hub</h1>
          <p className="text-slate-400 text-sm mt-1 max-w-xl">
            Real-time material requirements planning, auditable inventory consumption ledger, shop-floor execution, and quality control.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link
            to="/manufacturing/mrp"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-medium text-sm transition-all shadow-lg shadow-indigo-600/30"
          >
            <Cpu className="w-4 h-4" /> Run MRP Engine
          </Link>
          <Link
            to="/manufacturing/production-orders"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 font-medium text-sm transition-all"
          >
            <Plus className="w-4 h-4" /> New Production Order
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-indigo-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Orders</span>
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-400">
              <ClipboardList className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-100">{inProgressOrders}</span>
            <span className="text-xs text-blue-400 font-medium">In Progress</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">{totalOrders} Total Orders Scheduled</p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-emerald-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Completed Output</span>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-100">{completedOrders}</span>
            <span className="text-xs text-emerald-400 font-medium">Orders Finished</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Receipted into Finished Goods Ledger</p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-amber-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Work Centers</span>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400">
              <Factory className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-100">{totalWorkCenters}</span>
            <span className="text-xs text-amber-400 font-medium">Operational</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Machining, Assembly, Testing Stations</p>
        </div>

        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-5 hover:border-purple-500/40 transition-all shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Quality Assurance</span>
            <div className="p-2.5 rounded-xl bg-purple-500/10 text-purple-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-100">
              {recentInspections.filter((q) => q.result === "PASSED").length} / {recentInspections.length || 1}
            </span>
            <span className="text-xs text-purple-400 font-medium">Inspections Passed</span>
          </div>
          <p className="text-xs text-slate-500 mt-1">Zero-Defect Quality Target</p>
        </div>
      </div>

      {/* Domain Navigation Hub */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {[
          { label: "Bills of Materials", path: "/manufacturing/boms", icon: Layers, color: "text-indigo-400" },
          { label: "Routings & Ops", path: "/manufacturing/routings", icon: GitMerge, color: "text-cyan-400" },
          { label: "Work Centers", path: "/manufacturing/work-centers", icon: Factory, color: "text-amber-400" },
          { label: "Work Orders", path: "/manufacturing/work-orders", icon: Wrench, color: "text-blue-400" },
          { label: "Material Ledger", path: "/manufacturing/consumptions", icon: Package, color: "text-emerald-400" },
          { label: "Quality Checks", path: "/manufacturing/quality", icon: CheckCircle2, color: "text-purple-400" },
        ].map((item, idx) => {
          const Icon = item.icon;
          return (
            <Link
              key={idx}
              to={item.path}
              className="bg-slate-900/50 hover:bg-slate-800/80 border border-slate-800 rounded-xl p-3.5 flex flex-col items-center justify-center gap-2 text-center transition-all group hover:border-slate-700"
            >
              <Icon className={`w-5 h-5 ${item.color} group-hover:scale-110 transition-transform`} />
              <span className="text-xs font-medium text-slate-300 group-hover:text-white">{item.label}</span>
            </Link>
          );
        })}
      </div>

      {/* Main Grid Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Production Orders */}
        <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-lg font-semibold text-slate-100">Live Production Orders</h2>
              <p className="text-xs text-slate-400">Recent manufacturing orders on the shop floor</p>
            </div>
            <Link
              to="/manufacturing/production-orders"
              className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
            >
              View All <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="text-xs uppercase bg-slate-800/60 text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-4 py-3 rounded-l-lg">Order #</th>
                  <th className="px-4 py-3">Planned Qty</th>
                  <th className="px-4 py-3">Produced</th>
                  <th className="px-4 py-3">Priority</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3 rounded-r-lg">Due Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {recentOrders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-slate-500 text-xs">
                      No production orders found. Create one to begin assembly.
                    </td>
                  </tr>
                ) : (
                  recentOrders.slice(0, 5).map((mo) => (
                    <tr key={mo.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-4 py-3 font-semibold text-slate-100">{mo.order_number}</td>
                      <td className="px-4 py-3">{Number(mo.planned_quantity).toFixed(2)}</td>
                      <td className="px-4 py-3 text-emerald-400 font-medium">
                        {Number(mo.produced_quantity).toFixed(2)}
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded text-[11px] font-semibold ${
                            mo.priority === "URGENT"
                              ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                              : mo.priority === "HIGH"
                              ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                              : "bg-slate-800 text-slate-400"
                          }`}
                        >
                          {mo.priority}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${
                            mo.status === "COMPLETED"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : mo.status === "IN_PROGRESS"
                              ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                              : mo.status === "CONFIRMED"
                              ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                              : "bg-slate-800 text-slate-400 border border-slate-700"
                          }`}
                        >
                          <span
                            className={`w-1.5 h-1.5 rounded-full ${
                              mo.status === "COMPLETED"
                                ? "bg-emerald-400"
                                : mo.status === "IN_PROGRESS"
                                ? "bg-blue-400 animate-pulse"
                                : "bg-slate-400"
                            }`}
                          />
                          {mo.status}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-xs text-slate-400">{mo.planned_due_date}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Quality Inspections Feed */}
        <div className="bg-slate-900/60 border border-slate-800/80 rounded-2xl p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-100 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-purple-400" /> Quality Inspections
              </h2>
              <Link to="/manufacturing/quality" className="text-xs text-indigo-400 hover:text-indigo-300">
                View QC
              </Link>
            </div>
            <p className="text-xs text-slate-400 mb-4">Latest quality control audits & batch releases</p>

            <div className="space-y-3">
              {recentInspections.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">No inspections logged yet.</p>
              ) : (
                recentInspections.slice(0, 4).map((qc) => (
                  <div key={qc.id} className="p-3 rounded-xl bg-slate-800/50 border border-slate-800 text-xs flex items-center justify-between">
                    <div>
                      <span className="font-semibold text-slate-200">{qc.inspection_number}</span>
                      <p className="text-slate-400 text-[11px] mt-0.5">
                        {qc.inspection_type} • Passed: {Number(qc.passed_quantity).toFixed(0)} / Failed: {Number(qc.failed_quantity).toFixed(0)}
                      </p>
                    </div>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        qc.result === "PASSED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : qc.result === "CONDITIONALLY_PASSED"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                      }`}
                    >
                      {qc.result}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
            <span>Material Ledger Protection: <strong className="text-emerald-400">Enforced</strong></span>
            <Link to="/manufacturing/consumptions" className="text-indigo-400 hover:underline">
              Ledger Logs
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
