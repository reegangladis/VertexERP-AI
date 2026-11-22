import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Boxes,
  Warehouse as WarehouseIcon,
  Layers,
  ArrowDownToLine,
  ArrowLeftRight,
  SlidersHorizontal,
  Plus,
  TrendingUp,
  AlertTriangle,
  History,
  CheckCircle2,
  Clock,
  Sparkles,
  Search,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { StockBalance, StockMovement } from "../types";

export const InventoryOverviewPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [totalProducts, setTotalProducts] = useState(0);
  const [totalWarehouses, setTotalWarehouses] = useState(0);
  const [totalValuation, setTotalValuation] = useState(0);
  const [totalOnHandUnits, setTotalOnHandUnits] = useState(0);
  const [recentMovements, setRecentMovements] = useState<StockMovement[]>([]);
  const [lowStockBalances, setLowStockBalances] = useState<StockBalance[]>([]);

  useEffect(() => {
    async function loadData() {
      try {
        const [productsRes, warehousesRes, balancesRes, movementsRes] = await Promise.allSettled([
          inventoryApi.getProducts({ page: 1, page_size: 1 }),
          inventoryApi.getWarehouses({ page: 1, page_size: 50 }),
          inventoryApi.getStockBalances({ page: 1, page_size: 100 }),
          inventoryApi.getStockMovements({ page: 1, page_size: 8 }),
        ]);

        if (productsRes.status === "fulfilled") {
          setTotalProducts(productsRes.value.total);
        }
        if (warehousesRes.status === "fulfilled") {
          setTotalWarehouses(warehousesRes.value.total);
        }
        if (balancesRes.status === "fulfilled") {
          const items = balancesRes.value.items || [];
          const valuation = items.reduce((acc, item) => acc + (Number(item.total_value) || 0), 0);
          const onHand = items.reduce((acc, item) => acc + (Number(item.quantity_on_hand) || 0), 0);
          setTotalValuation(valuation);
          setTotalOnHandUnits(onHand);
          setLowStockBalances(items.filter((b) => Number(b.quantity_available) <= 10).slice(0, 5));
        }
        if (movementsRes.status === "fulfilled") {
          setRecentMovements(movementsRes.value.items || []);
        }
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const kpis = [
    {
      title: "Total SKUs & Products",
      value: totalProducts,
      sub: "Active catalog items",
      icon: <Boxes className="w-5 h-5 text-blue-400" />,
      color: "from-blue-500/10 to-indigo-500/10 border-blue-500/20 text-blue-400",
    },
    {
      title: "Warehouses & Hubs",
      value: totalWarehouses,
      sub: "Active storage facilities",
      icon: <WarehouseIcon className="w-5 h-5 text-emerald-400" />,
      color: "from-emerald-500/10 to-teal-500/10 border-emerald-500/20 text-emerald-400",
    },
    {
      title: "Stock Valuation",
      value: `$${totalValuation.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      sub: "Moving average asset value",
      icon: <TrendingUp className="w-5 h-5 text-amber-400" />,
      color: "from-amber-500/10 to-orange-500/10 border-amber-500/20 text-amber-400",
    },
    {
      title: "On-Hand Physical Units",
      value: totalOnHandUnits.toLocaleString(),
      sub: "Across all locations & bins",
      icon: <Layers className="w-5 h-5 text-purple-400" />,
      color: "from-purple-500/10 to-pink-500/10 border-purple-500/20 text-purple-400",
    },
  ];

  const quickActions = [
    {
      title: "Products & SKUs",
      desc: "Manage master catalog, barcodes & pricing",
      to: "/inventory/products",
      icon: <Boxes className="w-5 h-5 text-blue-400" />,
    },
    {
      title: "Warehouses & Bins",
      desc: "Configure multi-level storage hierarchy",
      to: "/inventory/warehouses",
      icon: <WarehouseIcon className="w-5 h-5 text-emerald-400" />,
    },
    {
      title: "Stock Balances",
      desc: "Real-time on-hand, reserved & available quantities",
      to: "/inventory/balances",
      icon: <Layers className="w-5 h-5 text-purple-400" />,
    },
    {
      title: "Goods Receipts (GRN)",
      desc: "Receive shipments against Purchase Orders",
      to: "/inventory/receipts",
      icon: <ArrowDownToLine className="w-5 h-5 text-teal-400" />,
    },
    {
      title: "Inter-Warehouse Transfers",
      desc: "Dispatch & receive inter-branch transfers",
      to: "/inventory/transfers",
      icon: <ArrowLeftRight className="w-5 h-5 text-amber-400" />,
    },
    {
      title: "Stock Adjustments",
      desc: "Physical count reconciliation & approvals",
      to: "/inventory/adjustments",
      icon: <SlidersHorizontal className="w-5 h-5 text-rose-400" />,
    },
  ];

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Inventory Management & Stock Ledger
            </h1>
            <span className="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Sparkles className="w-3 h-3" /> Double-Entry Ledger
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time multi-warehouse inventory, immutable movements ledger, and stock valuation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/inventory/receipts"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700/60 transition-colors shadow-sm"
          >
            <ArrowDownToLine className="w-4 h-4 text-teal-400" />
            Receive Stock
          </Link>
          <Link
            to="/inventory/products"
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-blue-600 hover:bg-blue-500 text-white shadow-sm shadow-blue-600/30 transition-colors"
          >
            <Plus className="w-4 h-4" />
            New Product
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
          Inventory Modules & Operations
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
                <p className="text-xs text-slate-400 mt-1 line-clamp-2">{action.desc}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Movements & Low Stock Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ledger Activity Stream */}
        <div className="lg:col-span-2 rounded-xl bg-slate-900/60 border border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-blue-400" />
              <h2 className="text-sm font-semibold text-slate-200">
                Recent Stock Ledger Movements
              </h2>
            </div>
            <Link
              to="/inventory/ledger"
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              View Full Ledger &rarr;
            </Link>
          </div>

          {recentMovements.length === 0 ? (
            <div className="text-center py-10 text-xs text-slate-500">
              No stock movements recorded yet. Create receipts, transfers or adjustments to populate ledger.
            </div>
          ) : (
            <div className="divide-y divide-slate-800/80">
              {recentMovements.map((m) => (
                <div key={m.id} className="py-3 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded uppercase ${
                        m.movement_type === "RECEIPT" || m.movement_type === "TRANSFER_IN" || m.movement_type === "ADJUSTMENT_IN"
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                          : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                      }`}
                    >
                      {m.movement_type}
                    </span>
                    <div>
                      <div className="text-xs font-medium text-slate-200">
                        {m.product_name || m.product_id}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Ref: {m.reference_type} {m.reference_id ? `(#${m.reference_id.slice(0, 8)})` : ""}
                      </div>
                    </div>
                  </div>

                  <div className="text-right">
                    <div
                      className={`text-xs font-semibold ${
                        Number(m.quantity) >= 0 ? "text-emerald-400" : "text-rose-400"
                      }`}
                    >
                      {Number(m.quantity) >= 0 ? `+${m.quantity}` : m.quantity} units
                    </div>
                    <div className="text-[10px] text-slate-400">
                      ${Number(m.total_cost || 0).toFixed(2)} value
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Low Stock Watchlist */}
        <div className="rounded-xl bg-slate-900/60 border border-slate-800 p-5">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h2 className="text-sm font-semibold text-slate-200">Low Stock Alerts</h2>
            </div>
            <Link
              to="/inventory/balances"
              className="text-xs text-amber-400 hover:text-amber-300 transition-colors"
            >
              All Balances &rarr;
            </Link>
          </div>

          {lowStockBalances.length === 0 ? (
            <div className="text-center py-10 text-xs text-emerald-400/80 flex flex-col items-center gap-2">
              <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              <span>All stock balances are within healthy thresholds.</span>
            </div>
          ) : (
            <div className="space-y-3">
              {lowStockBalances.map((b) => (
                <div
                  key={b.id}
                  className="p-3 rounded-lg bg-slate-800/40 border border-amber-500/20 flex items-center justify-between"
                >
                  <div>
                    <div className="text-xs font-medium text-slate-200">
                      {b.product_name || b.product_id}
                    </div>
                    <div className="text-[10px] text-slate-400">
                      Warehouse: {b.warehouse_name || b.warehouse_id.slice(0, 8)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-amber-400">
                      {b.quantity_available} avail
                    </div>
                    <div className="text-[10px] text-slate-500">
                      {b.quantity_on_hand} on-hand
                    </div>
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
