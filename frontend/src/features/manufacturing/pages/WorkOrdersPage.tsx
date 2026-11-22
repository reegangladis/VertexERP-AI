import React, { useEffect, useState } from "react";
import { Wrench, Play, Pause, CheckCircle2, Clock, Search, User, DollarSign, Filter } from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { WorkOrder, WorkOrderStatus } from "../types";

export const WorkOrdersPage: React.FC = () => {
  const [workOrders, setWorkOrders] = useState<WorkOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("ALL");

  useEffect(() => {
    loadWorkOrders();
  }, []);

  async function loadWorkOrders() {
    setLoading(true);
    try {
      // Fetch recent production orders and aggregate work orders
      const res = await manufacturingApi.getProductionOrders({ page: 1, page_size: 50 });
      const allWos: WorkOrder[] = [];
      (res.items || []).forEach((po) => {
        if (po.work_orders) {
          allWos.push(...po.work_orders);
        }
      });
      setWorkOrders(allWos);
    } catch (err) {
      console.error("Failed to load work orders", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusChange(woId: string, newStatus: string, actualHours?: number) {
    try {
      await manufacturingApi.updateWorkOrderStatus(woId, newStatus, actualHours);
      loadWorkOrders();
    } catch (err) {
      console.error("Failed to update work order status", err);
      alert("Failed to update status.");
    }
  }

  const filtered = workOrders.filter((wo) => {
    const matchesSearch = wo.operation_name.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = filterStatus === "ALL" || wo.status === filterStatus;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <Wrench className="w-7 h-7 text-blue-400" /> Shop-Floor Work Orders
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Dispatch, track, and complete discrete work station operations with real-time labor accumulation.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search operations by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex flex-wrap gap-1.5">
          {["ALL", "PENDING", "IN_PROGRESS", "PAUSED", "COMPLETED"].map((st) => (
            <button
              key={st}
              onClick={() => setFilterStatus(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                filterStatus === st
                  ? "bg-blue-600 text-white shadow"
                  : "bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-800"
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Work Orders List */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.length === 0 ? (
          <div className="col-span-full py-16 text-center text-slate-500 bg-slate-900/40 rounded-2xl border border-slate-800">
            No work orders found. Confirm a Production Order to generate shop-floor operations.
          </div>
        ) : (
          filtered.map((wo) => (
            <div
              key={wo.id}
              className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 space-y-4 hover:border-slate-700 transition-all flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="w-6 h-6 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold text-xs flex items-center justify-center">
                      {wo.sequence}
                    </span>
                    <h3 className="font-semibold text-slate-100 text-sm">{wo.operation_name}</h3>
                  </div>
                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                      wo.status === "COMPLETED"
                        ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        : wo.status === "IN_PROGRESS"
                        ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                        : wo.status === "PAUSED"
                        ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                        : "bg-slate-800 text-slate-400 border border-slate-700"
                    }`}
                  >
                    {wo.status}
                  </span>
                </div>

                <div className="mt-3 space-y-1.5 text-xs text-slate-400">
                  <p className="font-mono text-[11px] truncate">Center: {wo.work_center_id}</p>
                  <div className="flex items-center justify-between text-[11px] pt-2 border-t border-slate-800">
                    <span>Planned: {Number(wo.planned_duration_hours).toFixed(1)}h</span>
                    <span>Actual: <strong className="text-slate-200">{Number(wo.actual_duration_hours).toFixed(1)}h</strong></span>
                    <span>Rate: ${Number(wo.hourly_rate).toFixed(2)}/h</span>
                  </div>
                </div>
              </div>

              {/* Total Labor Cost & Controls */}
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between">
                <div className="text-xs">
                  <span className="text-slate-500 block">Labor Cost</span>
                  <span className="font-bold text-slate-200">${Number(wo.total_labor_cost).toFixed(2)}</span>
                </div>

                <div className="flex items-center gap-1.5">
                  {wo.status === "PENDING" && (
                    <button
                      onClick={() => handleStatusChange(wo.id, "IN_PROGRESS")}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow"
                    >
                      <Play className="w-3 h-3" /> Start
                    </button>
                  )}
                  {wo.status === "IN_PROGRESS" && (
                    <>
                      <button
                        onClick={() => handleStatusChange(wo.id, "PAUSED")}
                        className="p-1.5 rounded-lg bg-amber-600/20 text-amber-400 hover:bg-amber-600/30 text-xs font-semibold"
                        title="Pause Operation"
                      >
                        <Pause className="w-3.5 h-3.5" />
                      </button>
                      <button
                        onClick={() => {
                          const hrs = prompt("Enter total actual duration in hours:", String(wo.planned_duration_hours));
                          if (hrs) handleStatusChange(wo.id, "COMPLETED", parseFloat(hrs));
                        }}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow"
                      >
                        <CheckCircle2 className="w-3 h-3" /> Complete
                      </button>
                    </>
                  )}
                  {wo.status === "PAUSED" && (
                    <button
                      onClick={() => handleStatusChange(wo.id, "IN_PROGRESS")}
                      className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow"
                    >
                      <Play className="w-3 h-3" /> Resume
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
