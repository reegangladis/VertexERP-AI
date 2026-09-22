import React, { useEffect, useState } from "react";
import {
  SlidersHorizontal,
  Plus,
  Send,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Warehouse as WarehouseIcon,
  Sparkles,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { Product, StockAdjustment, Warehouse } from "../types";

export const StockAdjustmentsPage: React.FC = () => {
  const [adjustments, setAdjustments] = useState<StockAdjustment[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    warehouse_id: "",
    reason: "PHYSICAL_COUNT",
    product_id: "",
    counted_quantity: 0,
    notes: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [adjRes, whRes, prodRes] = await Promise.allSettled([
        inventoryApi.getAdjustments({ status: statusFilter || undefined }),
        inventoryApi.getWarehouses(),
        inventoryApi.getProducts(),
      ]);

      if (adjRes.status === "fulfilled") setAdjustments(adjRes.value.items || []);
      if (whRes.status === "fulfilled") setWarehouses(whRes.value.items || []);
      if (prodRes.status === "fulfilled") setProducts(prodRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleCreateAdjustment = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!formData.warehouse_id || !formData.product_id) {
        setError("Warehouse and product are required.");
        setSubmitting(false);
        return;
      }

      await inventoryApi.createAdjustment({
        warehouse_id: formData.warehouse_id,
        reason: formData.reason,
        notes: formData.notes,
        items: [
          {
            product_id: formData.product_id,
            counted_quantity: Number(formData.counted_quantity) || 0,
            reason: formData.reason,
          } as any,
        ],
      });

      setIsModalOpen(false);
      setFormData({
        warehouse_id: "",
        reason: "PHYSICAL_COUNT",
        product_id: "",
        counted_quantity: 0,
        notes: "",
      });
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Failed to create adjustment");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async (id: string) => {
    try {
      await inventoryApi.submitAdjustment(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to submit adjustment");
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await inventoryApi.approveAdjustment(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to approve adjustment");
    }
  };

  const handlePost = async (id: string) => {
    try {
      await inventoryApi.postAdjustment(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to post adjustment to ledger");
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Stock Adjustments & Variance Reconciliation
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">
              {adjustments.length} Adjustments
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Physical stock count reconciliation with strict dual-control approval workflows.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-500 text-white shadow-sm shadow-rose-600/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Stock Adjustment
        </button>
      </div>

      {/* Filters */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-medium">Filter by Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">DRAFT</option>
            <option value="SUBMITTED">SUBMITTED</option>
            <option value="APPROVED">APPROVED</option>
            <option value="POSTED">POSTED</option>
            <option value="REJECTED">REJECTED</option>
          </select>
        </div>
      </div>

      {/* Adjustments Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Adjustment #</th>
                <th className="py-3 px-4">Warehouse</th>
                <th className="py-3 px-4">Reason</th>
                <th className="py-3 px-4">Variance Items</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Workflow Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-500">
                    Loading stock adjustments...
                  </td>
                </tr>
              ) : adjustments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    <SlidersHorizontal className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No stock adjustments recorded.
                  </td>
                </tr>
              ) : (
                adjustments.map((a) => (
                  <tr key={a.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-rose-400">
                      {a.adjustment_number}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {warehouses.find((w) => w.id === a.warehouse_id)?.name || a.warehouse_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 px-4 text-slate-200">{a.reason}</td>
                    <td className="py-3.5 px-4">
                      {a.items?.map((it, idx) => (
                        <div key={idx} className="text-[11px] font-mono">
                          Sys: {it.system_quantity} &rarr; Count: {it.counted_quantity} (
                          <span
                            className={
                              Number(it.variance_quantity) >= 0 ? "text-emerald-400" : "text-rose-400"
                            }
                          >
                            {Number(it.variance_quantity) > 0 ? `+${it.variance_quantity}` : it.variance_quantity}
                          </span>
                          )
                        </div>
                      ))}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          a.status === "POSTED"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : a.status === "APPROVED"
                            ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                            : a.status === "SUBMITTED"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : a.status === "DRAFT"
                            ? "bg-slate-800 text-slate-300 border-slate-700"
                            : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        }`}
                      >
                        {a.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {a.status === "DRAFT" && (
                          <button
                            onClick={() => handleSubmit(a.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-amber-600 hover:bg-amber-500 text-white"
                          >
                            Submit
                          </button>
                        )}
                        {a.status === "SUBMITTED" && (
                          <button
                            onClick={() => handleApprove(a.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 hover:bg-blue-500 text-white"
                          >
                            Approve
                          </button>
                        )}
                        {a.status === "APPROVED" && (
                          <button
                            onClick={() => handlePost(a.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm"
                          >
                            Post to Ledger
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Adjustment Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <SlidersHorizontal className="w-5 h-5 text-rose-400" />
                Record Stock Count Adjustment
              </h2>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-200">
                ✕
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleCreateAdjustment} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Warehouse *
                </label>
                <select
                  required
                  value={formData.warehouse_id}
                  onChange={(e) => setFormData({ ...formData, warehouse_id: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                >
                  <option value="">Select Warehouse Facility...</option>
                  {warehouses.map((w) => (
                    <option key={w.id} value={w.id}>
                      {w.name} ({w.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Product *
                  </label>
                  <select
                    required
                    value={formData.product_id}
                    onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                  >
                    <option value="">Select Product...</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.sku})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Physical Count *
                  </label>
                  <input
                    type="number"
                    min="0"
                    required
                    value={formData.counted_quantity}
                    onChange={(e) => setFormData({ ...formData, counted_quantity: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Reason</label>
                <select
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-rose-500"
                >
                  <option value="PHYSICAL_COUNT">Annual / Cycle Physical Count</option>
                  <option value="DAMAGED_GOODS">Damaged Goods Write-off</option>
                  <option value="EXPIRY">Expired Items Write-off</option>
                  <option value="FOUND_STOCK">Found Inventory Reconciliation</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 text-xs font-medium rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-500 text-white shadow-sm shadow-rose-600/30 disabled:opacity-50"
                >
                  {submitting ? "Saving..." : "Create Adjustment Draft"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
