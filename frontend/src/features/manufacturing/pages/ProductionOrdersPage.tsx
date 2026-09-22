import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ClipboardList,
  Plus,
  Search,
  CheckCircle2,
  Play,
  Check,
  Ban,
  Clock,
  ArrowRight,
  Filter,
  X,
  Package,
} from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { ProductionOrder, ProductionOrderStatus, ProductionOrderPriority } from "../types";

export const ProductionOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<ProductionOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [priorityFilter, setPriorityFilter] = useState<string>("ALL");

  // Create Order Modal
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [productId, setProductId] = useState("");
  const [bomId, setBomId] = useState("");
  const [bomVersionId, setBomVersionId] = useState("");
  const [routingId, setRoutingId] = useState("");
  const [plannedQty, setPlannedQty] = useState("10.0000");
  const [targetWhId, setTargetWhId] = useState("");
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [dueDate, setDueDate] = useState(
    new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0]
  );
  const [priority, setPriority] = useState<ProductionOrderPriority>("MEDIUM");

  useEffect(() => {
    loadOrders();
  }, [statusFilter, priorityFilter]);

  async function loadOrders() {
    setLoading(true);
    try {
      const params: any = { page: 1, page_size: 50 };
      if (statusFilter !== "ALL") params.status = statusFilter;
      if (priorityFilter !== "ALL") params.priority = priorityFilter;
      const res = await manufacturingApi.getProductionOrders(params);
      setOrders(res.items || []);
    } catch (err) {
      console.error("Failed to load production orders", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleConfirmOrder(id: string) {
    try {
      await manufacturingApi.confirmProductionOrder(id);
      loadOrders();
    } catch (err) {
      console.error("Failed to confirm order", err);
      alert("Failed to confirm order.");
    }
  }

  async function handleCompleteOrder(id: string) {
    try {
      await manufacturingApi.completeProductionOrder(id);
      loadOrders();
    } catch (err) {
      console.error("Failed to complete order", err);
      alert("Failed to complete order.");
    }
  }

  async function handleCancelOrder(id: string) {
    if (!window.confirm("Are you sure you want to cancel this manufacturing order?")) return;
    try {
      await manufacturingApi.cancelProductionOrder(id);
      loadOrders();
    } catch (err) {
      console.error("Failed to cancel order", err);
      alert("Failed to cancel order.");
    }
  }

  async function handleCreateOrder(e: React.FormEvent) {
    e.preventDefault();
    try {
      await manufacturingApi.createProductionOrder({
        product_id: productId,
        bom_id: bomId,
        bom_version_id: bomVersionId,
        routing_id: routingId || undefined,
        planned_quantity: plannedQty,
        target_warehouse_id: targetWhId,
        planned_start_date: startDate,
        planned_due_date: dueDate,
        priority,
      });
      setIsModalOpen(false);
      setProductId("");
      setBomId("");
      setBomVersionId("");
      loadOrders();
    } catch (err) {
      console.error("Failed to create production order", err);
      alert("Failed to create order. Ensure valid Product, BOM, and Warehouse UUIDs.");
    }
  }

  const filtered = orders.filter((o) =>
    o.order_number.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <ClipboardList className="w-7 h-7 text-indigo-400" /> Production Orders (MO)
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Manufacturing work dispatching, raw material allocation, shop-floor status, and finished goods receipting.
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-medium text-sm text-white transition-all shadow-lg shadow-indigo-600/30 self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Create Production Order
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            placeholder="Search by order number (e.g. MO-2026-0001)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700 rounded-xl pl-9 pr-4 py-2 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-1.5 bg-slate-800/60 border border-slate-700 rounded-xl p-1 text-xs">
            {["ALL", "PLANNED", "CONFIRMED", "IN_PROGRESS", "COMPLETED"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-lg font-medium transition-all ${
                  statusFilter === st
                    ? "bg-indigo-600 text-white shadow"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none"
          >
            <option value="ALL">All Priorities</option>
            <option value="LOW">LOW</option>
            <option value="MEDIUM">MEDIUM</option>
            <option value="HIGH">HIGH</option>
            <option value="URGENT">URGENT</option>
          </select>
        </div>
      </div>

      {/* Orders Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-800/80 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
              <tr>
                <th className="px-5 py-4">Order #</th>
                <th className="px-5 py-4">Planned Qty</th>
                <th className="px-5 py-4">Progress</th>
                <th className="px-5 py-4">Unit Cost</th>
                <th className="px-5 py-4">Total Cost</th>
                <th className="px-5 py-4">Priority</th>
                <th className="px-5 py-4">Status</th>
                <th className="px-5 py-4">Due Date</th>
                <th className="px-5 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-12 text-slate-500 text-sm">
                    No production orders found matching criteria.
                  </td>
                </tr>
              ) : (
                filtered.map((mo) => {
                  const planned = Number(mo.planned_quantity) || 1;
                  const produced = Number(mo.produced_quantity) || 0;
                  const pct = Math.min(100, Math.round((produced / planned) * 100));

                  return (
                    <tr key={mo.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-4">
                        <div className="font-semibold text-slate-100">{mo.order_number}</div>
                        <span className="text-[11px] text-slate-500 font-mono">Product: {mo.product_id.substring(0, 8)}...</span>
                      </td>
                      <td className="px-5 py-4 font-semibold text-slate-200">{Number(mo.planned_quantity).toFixed(2)}</td>
                      <td className="px-5 py-4">
                        <div className="w-32">
                          <div className="flex justify-between text-xs text-slate-400 mb-1">
                            <span>{produced.toFixed(0)} / {planned.toFixed(0)}</span>
                            <span className="font-bold text-slate-200">{pct}%</span>
                          </div>
                          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                            <div
                              className="bg-indigo-500 h-full rounded-full transition-all"
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      </td>
                      <td className="px-5 py-4 font-mono text-xs text-slate-300">${Number(mo.unit_cost).toFixed(2)}</td>
                      <td className="px-5 py-4 font-mono text-xs font-semibold text-slate-100">${Number(mo.total_cost).toFixed(2)}</td>
                      <td className="px-5 py-4">
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
                      <td className="px-5 py-4">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${
                            mo.status === "COMPLETED"
                              ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                              : mo.status === "IN_PROGRESS"
                              ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                              : mo.status === "CONFIRMED"
                              ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                              : "bg-slate-800 text-slate-400 border border-slate-700"
                          }`}
                        >
                          {mo.status}
                        </span>
                      </td>
                      <td className="px-5 py-4 text-xs text-slate-400">{mo.planned_due_date}</td>
                      <td className="px-5 py-4 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {mo.status === "PLANNED" && (
                            <button
                              onClick={() => handleConfirmOrder(mo.id)}
                              className="p-1.5 rounded-lg bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30 text-xs font-medium flex items-center gap-1"
                              title="Confirm Order & Generate Work Orders"
                            >
                              <Check className="w-3.5 h-3.5" /> Confirm
                            </button>
                          )}
                          {mo.status === "IN_PROGRESS" && (
                            <button
                              onClick={() => handleCompleteOrder(mo.id)}
                              className="p-1.5 rounded-lg bg-emerald-600/20 text-emerald-400 hover:bg-emerald-600/30 text-xs font-medium flex items-center gap-1"
                              title="Mark Complete"
                            >
                              <CheckCircle2 className="w-3.5 h-3.5" /> Complete
                            </button>
                          )}
                          {mo.status !== "COMPLETED" && mo.status !== "CANCELLED" && (
                            <button
                              onClick={() => handleCancelOrder(mo.id)}
                              className="p-1.5 rounded-lg bg-rose-600/10 text-rose-400 hover:bg-rose-600/20 text-xs"
                              title="Cancel Order"
                            >
                              <Ban className="w-3.5 h-3.5" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Order Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-100">Create Production Order</h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleCreateOrder} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Product UUID *</label>
                <input
                  type="text"
                  required
                  placeholder="Finished Good Product ID"
                  value={productId}
                  onChange={(e) => setProductId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">BOM UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Bill of Materials ID"
                    value={bomId}
                    onChange={(e) => setBomId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">BOM Version UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="BOM Version ID"
                    value={bomVersionId}
                    onChange={(e) => setBomVersionId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Routing UUID (Optional)</label>
                  <input
                    type="text"
                    placeholder="Routing ID"
                    value={routingId}
                    onChange={(e) => setRoutingId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Target Warehouse UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Finished Goods Warehouse"
                    value={targetWhId}
                    onChange={(e) => setTargetWhId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Planned Qty *</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={plannedQty}
                    onChange={(e) => setPlannedQty(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Due Date</label>
                  <input
                    type="date"
                    value={dueDate}
                    onChange={(e) => setDueDate(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="URGENT">URGENT</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-sm text-white font-semibold shadow-lg shadow-indigo-600/30"
                >
                  Schedule Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
