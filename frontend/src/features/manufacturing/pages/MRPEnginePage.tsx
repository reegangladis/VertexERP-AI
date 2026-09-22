import React, { useEffect, useState } from "react";
import {
  Cpu,
  Play,
  CheckCircle2,
  AlertCircle,
  Clock,
  ArrowRight,
  Package,
  ShoppingCart,
  Factory,
  Layers,
  Search,
  Filter,
  RefreshCw,
  FileCheck,
  ChevronRight,
  Calendar,
  Sparkles,
} from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { MRPRun, MRPPlannedOrder } from "../types";

export const MRPEnginePage: React.FC = () => {
  const [runs, setRuns] = useState<MRPRun[]>([]);
  const [selectedRun, setSelectedRun] = useState<MRPRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [horizonDays, setHorizonDays] = useState(30);
  const [activeTab, setActiveTab] = useState<"ALL" | "MANUFACTURE" | "PURCHASE">("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [convertingId, setConvertingId] = useState<string | null>(null);
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  const fetchRuns = async (selectLatest = false) => {
    try {
      setLoading(true);
      const res = await manufacturingApi.getMRPRuns({ page: 1, page_size: 20 });
      const items = res.items || [];
      setRuns(items);
      if (items.length > 0) {
        if (selectLatest || !selectedRun) {
          const detailed = await manufacturingApi.getMRPRunById(items[0].id);
          setSelectedRun(detailed);
        } else {
          // Refresh current selected run
          const detailed = await manufacturingApi.getMRPRunById(selectedRun.id);
          setSelectedRun(detailed);
        }
      }
    } catch (err) {
      console.error("Failed to load MRP runs", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRuns(true);
  }, []);

  const handleExecuteMRP = async () => {
    try {
      setExecuting(true);
      setNotification(null);
      const result = await manufacturingApi.executeMRPRun(horizonDays);
      setNotification({
        type: "success",
        message: `MRP Run ${result.run_number} completed! Generated ${result.total_items_planned} planned orders (${result.total_production_orders_generated} Production, ${result.total_purchase_requests_generated} Purchase).`,
      });
      await fetchRuns(true);
    } catch (err: any) {
      setNotification({
        type: "error",
        message: err.message || "Failed to execute MRP run.",
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleSelectRun = async (run: MRPRun) => {
    try {
      setLoading(true);
      const detailed = await manufacturingApi.getMRPRunById(run.id);
      setSelectedRun(detailed);
    } catch (err) {
      console.error("Failed to load detailed MRP run", err);
    } finally {
      setLoading(false);
    }
  };

  const handleConvertPlannedOrder = async (orderId: string) => {
    try {
      setConvertingId(orderId);
      const res = await manufacturingApi.convertPlannedOrder(orderId);
      setNotification({
        type: "success",
        message: `Successfully converted to ${res.converted_type} #${res.number || res.document_id.slice(0, 8)}`,
      });
      if (selectedRun) {
        const refreshed = await manufacturingApi.getMRPRunById(selectedRun.id);
        setSelectedRun(refreshed);
      }
    } catch (err: any) {
      setNotification({
        type: "error",
        message: err.message || "Failed to convert planned order.",
      });
    } finally {
      setConvertingId(null);
    }
  };

  const filteredPlannedOrders = (selectedRun?.planned_orders || []).filter((item: MRPPlannedOrder) => {
    const matchesTab = activeTab === "ALL" || item.order_type === activeTab;
    const matchesSearch =
      searchQuery === "" ||
      item.product_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.order_type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.status.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesTab && matchesSearch;
  });

  const totalPlannedProduction = (selectedRun?.planned_orders || []).filter(
    (p) => p.order_type === "MANUFACTURE"
  ).length;
  const totalPlannedPurchase = (selectedRun?.planned_orders || []).filter(
    (p) => p.order_type === "PURCHASE"
  ).length;
  const totalConverted = (selectedRun?.planned_orders || []).filter((p) => p.status === "CONVERTED").length;

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white p-6 rounded-2xl shadow-xl border border-indigo-900/50">
        <div>
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs mb-1 uppercase tracking-wider">
            <Sparkles className="w-4 h-4" /> Multi-Level Gross-to-Net Engine
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Material Requirements Planning (MRP)</h1>
          <p className="text-slate-400 text-xs mt-1 max-w-xl">
            Calculates gross requirements from open sales orders, checks on-hand stock and lead times, exploding multi-level BOMs into planned production orders and purchase requests.
          </p>
        </div>

        {/* MRP Trigger Controls */}
        <div className="flex flex-wrap items-center gap-3 bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 shadow-inner">
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Calendar className="w-4 h-4 text-indigo-400" />
            <span>Horizon:</span>
            <select
              value={horizonDays}
              onChange={(e) => setHorizonDays(Number(e.target.value))}
              className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value={15}>15 Days</option>
              <option value={30}>30 Days</option>
              <option value={60}>60 Days</option>
              <option value={90}>90 Days</option>
            </select>
          </div>

          <button
            onClick={handleExecuteMRP}
            disabled={executing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-xs text-white shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {executing ? (
              <>
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                Calculating MRP...
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-current" />
                Run MRP Calculation
              </>
            )}
          </button>
        </div>
      </div>

      {/* Notification Banner */}
      {notification && (
        <div
          className={`flex items-center justify-between p-4 rounded-xl text-xs font-medium border ${
            notification.type === "success"
              ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/50"
              : "bg-rose-950/40 text-rose-300 border-rose-800/50"
          }`}
        >
          <div className="flex items-center gap-2">
            {notification.type === "success" ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
            ) : (
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            )}
            <span>{notification.message}</span>
          </div>
          <button
            onClick={() => setNotification(null)}
            className="text-slate-400 hover:text-white ml-4 font-bold"
          >
            ✕
          </button>
        </div>
      )}

      {/* KPI Stats */}
      {selectedRun && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">Selected MRP Run</span>
              <Cpu className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-xl font-bold text-white mt-2">{selectedRun.run_number}</div>
            <div className="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
              <Clock className="w-3 h-3" />
              {new Date(selectedRun.run_date).toLocaleString()}
            </div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">Planned Production</span>
              <Factory className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-xl font-bold text-amber-300 mt-2">{totalPlannedProduction} Orders</div>
            <div className="text-[11px] text-slate-400 mt-1">Multi-level assembly components</div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">Planned Procurement</span>
              <ShoppingCart className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-xl font-bold text-emerald-300 mt-2">{totalPlannedPurchase} Requests</div>
            <div className="text-[11px] text-slate-400 mt-1">Raw materials gross shortages</div>
          </div>

          <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-400 font-medium">Conversion Rate</span>
              <FileCheck className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="text-xl font-bold text-cyan-300 mt-2">
              {totalConverted} / {selectedRun.planned_orders?.length || 0}
            </div>
            <div className="text-[11px] text-slate-400 mt-1">Converted to PO / PR docs</div>
          </div>
        </div>
      )}

      {/* Main Content Layout: Run Selector + Requirements Table */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar: Runs History */}
        <div className="lg:col-span-1 bg-slate-900/60 backdrop-blur border border-slate-800 rounded-2xl p-4 flex flex-col h-[650px]">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800">
            <h2 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-indigo-400" /> MRP History
            </h2>
            <button
              onClick={() => fetchRuns(false)}
              className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
              title="Refresh History"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 mt-3 pr-1">
            {runs.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-xs">No MRP runs recorded yet.</div>
            ) : (
              runs.map((r) => {
                const isSelected = selectedRun?.id === r.id;
                return (
                  <button
                    key={r.id}
                    onClick={() => handleSelectRun(r)}
                    className={`w-full text-left p-3 rounded-xl border transition-all ${
                      isSelected
                        ? "bg-indigo-600/20 border-indigo-500/50 shadow-sm"
                        : "bg-slate-800/40 border-slate-800/80 hover:bg-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-xs text-white">{r.run_number}</span>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-semibold ${
                          r.status === "COMPLETED"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                            : r.status === "RUNNING"
                            ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                        }`}
                      >
                        {r.status}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-[11px] text-slate-400 mt-1.5">
                      <span>{r.planning_horizon_days}d horizon</span>
                      <span>•</span>
                      <span>{r.total_items_planned} planned</span>
                    </div>
                    <div className="text-[10px] text-slate-500 mt-1">
                      {new Date(r.run_date).toLocaleString()}
                    </div>
                  </button>
                );
              })
            )}
          </div>
        </div>

        {/* Right Section: Gross-to-Net Planned Orders */}
        <div className="lg:col-span-3 bg-slate-900/60 backdrop-blur border border-slate-800 rounded-2xl p-5 flex flex-col min-h-[650px]">
          {selectedRun ? (
            <>
              {/* Table Controls */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-bold text-white">Gross-to-Net Requirements</span>
                  <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-0.5 rounded-full font-medium">
                    {filteredPlannedOrders.length} items
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {/* Filter Tabs */}
                  <div className="flex rounded-lg bg-slate-800/80 p-1 border border-slate-700/60 text-xs">
                    {(["ALL", "MANUFACTURE", "PURCHASE"] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`px-3 py-1 rounded-md font-medium transition-all ${
                          activeTab === tab
                            ? "bg-indigo-600 text-white shadow-sm"
                            : "text-slate-400 hover:text-white"
                        }`}
                      >
                        {tab === "ALL" ? "All" : tab === "MANUFACTURE" ? "Production" : "Purchase"}
                      </button>
                    ))}
                  </div>

                  {/* Search Bar */}
                  <div className="relative">
                    <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
                    <input
                      type="text"
                      placeholder="Search SKU..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="bg-slate-800/80 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                    />
                  </div>
                </div>
              </div>

              {/* Requirements Table */}
              <div className="flex-1 overflow-x-auto mt-4">
                <table className="w-full text-left text-xs">
                  <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-800/50 border-y border-slate-800">
                    <tr>
                      <th className="py-3 px-4">Type</th>
                      <th className="py-3 px-4">Product / SKU</th>
                      <th className="py-3 px-3 text-right">Gross Req</th>
                      <th className="py-3 px-3 text-right">On Hand</th>
                      <th className="py-3 px-3 text-right">Net Req</th>
                      <th className="py-3 px-3 text-right font-bold text-indigo-300">Plan Qty</th>
                      <th className="py-3 px-4">Due Date</th>
                      <th className="py-3 px-4">Status</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {filteredPlannedOrders.length === 0 ? (
                      <tr>
                        <td colSpan={9} className="text-center py-16 text-slate-500">
                          No planned requirements match your filters.
                        </td>
                      </tr>
                    ) : (
                      filteredPlannedOrders.map((item) => {
                        const isMfg = item.order_type === "MANUFACTURE";
                        const isConverted = item.status === "CONVERTED";
                        return (
                          <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                            <td className="py-3 px-4">
                              <span
                                className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold ${
                                  isMfg
                                    ? "bg-indigo-500/15 text-indigo-400 border border-indigo-500/30"
                                    : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                }`}
                              >
                                {isMfg ? <Factory className="w-3 h-3" /> : <ShoppingCart className="w-3 h-3" />}
                                {item.order_type}
                              </span>
                            </td>
                            <td className="py-3 px-4 font-semibold text-slate-200">
                              <div className="truncate max-w-[140px]" title={item.product_id}>
                                {item.product_id}
                              </div>
                            </td>
                            <td className="py-3 px-3 text-right font-medium text-slate-300">
                              {Number(item.gross_requirement).toLocaleString()}
                            </td>
                            <td className="py-3 px-3 text-right font-medium text-slate-400">
                              {Number(item.on_hand_stock).toLocaleString()}
                            </td>
                            <td className="py-3 px-3 text-right font-medium text-amber-400">
                              {Number(item.net_requirement).toLocaleString()}
                            </td>
                            <td className="py-3 px-3 text-right font-bold text-indigo-300">
                              {Number(item.planned_quantity).toLocaleString()}
                            </td>
                            <td className="py-3 px-4 text-slate-400">
                              {new Date(item.required_date).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`inline-block px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                                  isConverted
                                    ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                    : "bg-slate-700/50 text-slate-300 border border-slate-600/40"
                                }`}
                              >
                                {item.status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right">
                              {isConverted ? (
                                <span className="text-[11px] text-emerald-400 font-medium">Converted</span>
                              ) : (
                                <button
                                  onClick={() => handleConvertPlannedOrder(item.id)}
                                  disabled={convertingId === item.id}
                                  className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-semibold text-white shadow transition-all disabled:opacity-50 ${
                                    isMfg
                                      ? "bg-indigo-600 hover:bg-indigo-500 shadow-indigo-600/20"
                                      : "bg-emerald-600 hover:bg-emerald-500 shadow-emerald-600/20"
                                  }`}
                                >
                                  {convertingId === item.id ? (
                                    <RefreshCw className="w-3 h-3 animate-spin" />
                                  ) : (
                                    <ArrowRight className="w-3 h-3" />
                                  )}
                                  {isMfg ? "Create Prod Order" : "Create PR"}
                                </button>
                              )}
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-slate-400">
              <Cpu className="w-12 h-12 text-slate-600 mb-3" />
              <h3 className="text-base font-semibold text-white">No MRP Run Selected</h3>
              <p className="text-xs text-slate-500 max-w-sm mt-1">
                Execute a new calculation or select a historical run from the left panel to inspect gross-to-net exploded requirements.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
