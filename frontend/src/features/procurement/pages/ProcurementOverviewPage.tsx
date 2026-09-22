import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ShoppingCart,
  Users,
  FileSpreadsheet,
  CheckCircle2,
  DollarSign,
  Plus,
  ArrowUpRight,
  Sparkles,
  TrendingUp,
  Clock,
  AlertCircle,
} from "lucide-react";
import { procurementApi } from "../api/procurementApi";
import { PurchaseOrder, PurchaseRequest, Supplier } from "../types";

export const ProcurementOverviewPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [totalSuppliers, setTotalSuppliers] = useState(0);
  const [totalPOs, setTotalPOs] = useState(0);
  const [totalPRs, setTotalPRs] = useState(0);
  const [totalSpend, setTotalSpend] = useState(0);
  const [recentPOs, setRecentPOs] = useState<PurchaseOrder[]>([]);
  const [pendingPRs, setPendingPRs] = useState<PurchaseRequest[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [supRes, poRes, prRes] = await Promise.allSettled([
          procurementApi.getSuppliers({ page: 1, page_size: 100 }),
          procurementApi.getPurchaseOrders({ page: 1, page_size: 50 }),
          procurementApi.getPurchaseRequests({ page: 1, page_size: 50 }),
        ]);

        if (supRes.status === "fulfilled") {
          setTotalSuppliers(supRes.value.total || supRes.value.items?.length || 0);
        }
        if (poRes.status === "fulfilled") {
          const pos = poRes.value.items || [];
          setTotalPOs(poRes.value.total || pos.length);
          const spend = pos.reduce((acc, p) => acc + (Number(p.total_amount) || 0), 0);
          setTotalSpend(spend);
          setRecentPOs(pos.slice(0, 5));
        }
        if (prRes.status === "fulfilled") {
          const prs = prRes.value.items || [];
          setTotalPRs(prRes.value.total || prs.length);
          setPendingPRs(prs.filter((p) => p.status === "SUBMITTED" || p.status === "DRAFT").slice(0, 5));
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const kpis = [
    {
      title: "Active Vendors & Suppliers",
      value: totalSuppliers,
      sub: "Approved supply partners",
      icon: <Users className="w-5 h-5 text-indigo-400" />,
      color: "from-indigo-500/10 to-blue-500/10 border-indigo-500/20 text-indigo-400",
    },
    {
      title: "Open Purchase Orders",
      value: totalPOs,
      sub: "Active procurement contracts",
      icon: <ShoppingCart className="w-5 h-5 text-emerald-400" />,
      color: "from-emerald-500/10 to-teal-500/10 border-emerald-500/20 text-emerald-400",
    },
    {
      title: "Requisitions (PR)",
      value: totalPRs,
      sub: "Departmental purchase requests",
      icon: <FileSpreadsheet className="w-5 h-5 text-amber-400" />,
      color: "from-amber-500/10 to-orange-500/10 border-amber-500/20 text-amber-400",
    },
    {
      title: "Total Committed Spend",
      value: `$${totalSpend.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: "Across all purchase orders",
      icon: <TrendingUp className="w-5 h-5 text-purple-400" />,
      color: "from-purple-500/10 to-pink-500/10 border-purple-500/20 text-purple-400",
    },
  ];

  const quickActions = [
    {
      title: "Suppliers & Vendors",
      desc: "Manage vendor contacts, payment terms & ratings",
      to: "/procurement/suppliers",
      icon: <Users className="w-5 h-5 text-indigo-400" />,
    },
    {
      title: "Purchase Requests (PR)",
      desc: "Create and review departmental requisitions",
      to: "/procurement/requests",
      icon: <FileSpreadsheet className="w-5 h-5 text-amber-400" />,
    },
    {
      title: "Purchase Orders (PO)",
      desc: "Issue orders, track fulfillment & receipts",
      to: "/procurement/orders",
      icon: <ShoppingCart className="w-5 h-5 text-emerald-400" />,
    },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Procurement & Vendor Management
            </h1>
            <span className="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              <Sparkles className="w-3 h-3" /> Procure-to-Pay Workflow
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Requisitions, multi-vendor purchase orders, tax & currency calculations, and fulfillment tracking.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/procurement/requests"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-colors shadow-sm"
          >
            <FileSpreadsheet className="w-4 h-4 text-amber-400" />
            New Purchase Request
          </Link>
          <Link
            to="/procurement/orders"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Purchase Order
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => (
          <div
            key={idx}
            className={`p-5 rounded-xl bg-gradient-to-br ${kpi.color} border bg-slate-900/60 backdrop-blur-sm relative overflow-hidden`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                {kpi.title}
              </span>
              <div className="p-2 rounded-lg bg-slate-800/80 border border-slate-700/50">
                {kpi.icon}
              </div>
            </div>
            <div className="mt-3">
              <div className="text-2xl font-bold text-slate-100 tracking-tight">
                {loading ? "..." : kpi.value}
              </div>
              <p className="text-xs text-slate-400 mt-1">{kpi.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Navigation Cards */}
      <div>
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-3">
          Procurement Operations
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {quickActions.map((action, idx) => (
            <Link
              key={idx}
              to={action.to}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 hover:bg-slate-800/50 transition-all group flex items-start gap-3.5"
            >
              <div className="p-2.5 rounded-lg bg-slate-800 border border-slate-700/60 group-hover:scale-105 transition-transform">
                {action.icon}
              </div>
              <div>
                <h3 className="text-sm font-semibold text-slate-200 group-hover:text-white transition-colors">
                  {action.title}
                </h3>
                <p className="text-xs text-slate-400 mt-1">{action.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent POs and Pending PRs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent POs */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ShoppingCart className="w-4 h-4 text-emerald-400" />
              <h2 className="text-sm font-semibold text-slate-200">Recent Purchase Orders</h2>
            </div>
            <Link
              to="/procurement/orders"
              className="text-xs text-indigo-400 hover:text-indigo-300"
            >
              View All &rarr;
            </Link>
          </div>

          {recentPOs.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">
              No purchase orders created yet.
            </div>
          ) : (
            <div className="divide-y divide-slate-800">
              {recentPOs.map((po) => (
                <div key={po.id} className="py-3 flex items-center justify-between">
                  <div>
                    <div className="text-xs font-bold font-mono text-emerald-400">
                      {po.order_number}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Ordered: {po.order_date} • {po.items?.length || 0} line items
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-slate-100 font-mono">
                      ${Number(po.total_amount || 0).toFixed(2)}
                    </div>
                    <span
                      className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                        po.status === "RECEIVED"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : po.status === "ISSUED"
                          ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {po.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Requisitions */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-amber-400" />
              <h2 className="text-sm font-semibold text-slate-200">Pending Requisitions (PR)</h2>
            </div>
            <Link
              to="/procurement/requests"
              className="text-xs text-amber-400 hover:text-amber-300"
            >
              View All &rarr;
            </Link>
          </div>

          {pendingPRs.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">
              No pending purchase requests.
            </div>
          ) : (
            <div className="divide-y divide-slate-800">
              {pendingPRs.map((pr) => (
                <div key={pr.id} className="py-3 flex items-center justify-between">
                  <div>
                    <div className="text-xs font-bold font-mono text-amber-400">
                      {pr.request_number}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Priority: <span className="font-semibold text-slate-300">{pr.priority}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <span
                      className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                        pr.status === "SUBMITTED"
                          ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {pr.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
