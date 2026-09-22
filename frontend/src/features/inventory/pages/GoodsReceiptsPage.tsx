import React, { useEffect, useState } from "react";
import {
  ArrowDownToLine,
  Plus,
  CheckCircle2,
  XCircle,
  FileText,
  Warehouse as WarehouseIcon,
  Sparkles,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { GoodsReceipt, Product, Warehouse } from "../types";

export const GoodsReceiptsPage: React.FC = () => {
  const [receipts, setReceipts] = useState<GoodsReceipt[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    warehouse_id: "",
    vendor_delivery_note: "",
    product_id: "",
    quantity_received: 1,
    unit_cost: 10,
    notes: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [recRes, whRes, prodRes] = await Promise.allSettled([
        inventoryApi.getGoodsReceipts({ status: statusFilter || undefined }),
        inventoryApi.getWarehouses(),
        inventoryApi.getProducts(),
      ]);

      if (recRes.status === "fulfilled") setReceipts(recRes.value.items || []);
      if (whRes.status === "fulfilled") setWarehouses(whRes.value.items || []);
      if (prodRes.status === "fulfilled") setProducts(prodRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleCreateReceipt = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!formData.warehouse_id || !formData.product_id) {
        setError("Warehouse and product are required.");
        setSubmitting(false);
        return;
      }

      await inventoryApi.createGoodsReceipt({
        warehouse_id: formData.warehouse_id,
        vendor_delivery_note: formData.vendor_delivery_note,
        notes: formData.notes,
        items: [
          {
            product_id: formData.product_id,
            quantity_received: Number(formData.quantity_received) || 1,
            unit_cost: Number(formData.unit_cost) || 0,
            quantity_rejected: 0,
          } as any,
        ],
      });

      setIsModalOpen(false);
      setFormData({
        warehouse_id: "",
        vendor_delivery_note: "",
        product_id: "",
        quantity_received: 1,
        unit_cost: 10,
        notes: "",
      });
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Failed to create goods receipt");
    } finally {
      setSubmitting(false);
    }
  };

  const handlePost = async (id: string) => {
    try {
      await inventoryApi.postGoodsReceipt(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to post goods receipt to ledger");
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Goods Receipt Notes (GRN)
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-teal-500/10 text-teal-400 border border-teal-500/20">
              {receipts.length} GRNs
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Receive incoming vendor shipments, inspect items, and update valuation & stock ledgers.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-teal-600 hover:bg-teal-500 text-white shadow-sm shadow-teal-600/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Goods Receipt
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-medium">Filter by Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">DRAFT</option>
            <option value="POSTED">POSTED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>
      </div>

      {/* Receipts Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">GRN #</th>
                <th className="py-3 px-4">Warehouse</th>
                <th className="py-3 px-4">Delivery Note #</th>
                <th className="py-3 px-4">Receipt Date</th>
                <th className="py-3 px-4">Received Items</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-slate-500">
                    Loading goods receipts...
                  </td>
                </tr>
              ) : receipts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    <ArrowDownToLine className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No goods receipts recorded.
                  </td>
                </tr>
              ) : (
                receipts.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-teal-400">
                      {r.grn_number}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {warehouses.find((w) => w.id === r.warehouse_id)?.name || r.warehouse_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {r.vendor_delivery_note || "-"}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300">{r.received_date}</td>
                    <td className="py-3.5 px-4">
                      {r.items?.map((it, idx) => (
                        <div key={idx} className="text-[11px] font-mono">
                          {it.product_name || it.product_id.slice(0, 8)}: +{it.quantity_received} units @ ${Number(it.unit_cost || 0).toFixed(2)}
                        </div>
                      ))}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          r.status === "POSTED"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : r.status === "DRAFT"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {r.status === "DRAFT" && (
                        <button
                          onClick={() => handlePost(r.id)}
                          className="px-2.5 py-1 text-xs font-semibold rounded bg-teal-600 hover:bg-teal-500 text-white shadow-sm"
                        >
                          Post to Ledger
                        </button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Goods Receipt Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <ArrowDownToLine className="w-5 h-5 text-teal-400" />
                Record Goods Receipt (GRN)
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

            <form onSubmit={handleCreateReceipt} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Warehouse *
                  </label>
                  <select
                    required
                    value={formData.warehouse_id}
                    onChange={(e) => setFormData({ ...formData, warehouse_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                  >
                    <option value="">Select Warehouse...</option>
                    {warehouses.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.name} ({w.code})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Vendor Delivery Note #
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. DN-2026-99"
                    value={formData.vendor_delivery_note}
                    onChange={(e) => setFormData({ ...formData, vendor_delivery_note: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Product *
                  </label>
                  <select
                    required
                    value={formData.product_id}
                    onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
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
                    Qty Received *
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.quantity_received}
                    onChange={(e) => setFormData({ ...formData, quantity_received: parseFloat(e.target.value) || 1 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Unit Cost ($) *
                  </label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    value={formData.unit_cost}
                    onChange={(e) => setFormData({ ...formData, unit_cost: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Receiving Notes</label>
                <textarea
                  rows={2}
                  placeholder="Optional inspection remarks..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-teal-500"
                />
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
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-teal-600 hover:bg-teal-500 text-white shadow-sm shadow-teal-600/30 disabled:opacity-50"
                >
                  {submitting ? "Creating..." : "Save GRN Draft"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
