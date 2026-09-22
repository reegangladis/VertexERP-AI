import React, { useEffect, useState } from "react";
import {
  ArrowLeftRight,
  Plus,
  Send,
  CheckCircle2,
  XCircle,
  Truck,
  Warehouse as WarehouseIcon,
  AlertCircle,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { Product, StockTransfer, Warehouse } from "../types";

export const StockTransfersPage: React.FC = () => {
  const [transfers, setTransfers] = useState<StockTransfer[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    source_warehouse_id: "",
    destination_warehouse_id: "",
    product_id: "",
    requested_quantity: 1,
    notes: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [transRes, whRes, prodRes] = await Promise.allSettled([
        inventoryApi.getTransfers({ status: statusFilter || undefined }),
        inventoryApi.getWarehouses(),
        inventoryApi.getProducts(),
      ]);

      if (transRes.status === "fulfilled") setTransfers(transRes.value.items || []);
      if (whRes.status === "fulfilled") setWarehouses(whRes.value.items || []);
      if (prodRes.status === "fulfilled") setProducts(prodRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleCreateTransfer = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!formData.source_warehouse_id || !formData.destination_warehouse_id || !formData.product_id) {
        setError("Source warehouse, destination warehouse, and product are required.");
        setSubmitting(false);
        return;
      }
      if (formData.source_warehouse_id === formData.destination_warehouse_id) {
        setError("Source and destination warehouses cannot be the same.");
        setSubmitting(false);
        return;
      }

      await inventoryApi.createTransfer({
        source_warehouse_id: formData.source_warehouse_id,
        destination_warehouse_id: formData.destination_warehouse_id,
        notes: formData.notes,
        items: [
          {
            product_id: formData.product_id,
            requested_quantity: Number(formData.requested_quantity) || 1,
          } as any,
        ],
      });

      setIsModalOpen(false);
      setFormData({
        source_warehouse_id: "",
        destination_warehouse_id: "",
        product_id: "",
        requested_quantity: 1,
        notes: "",
      });
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Failed to create transfer");
    } finally {
      setSubmitting(false);
    }
  };

  const handleDispatch = async (id: string) => {
    try {
      await inventoryApi.dispatchTransfer(id, { tracking_number: `TRK-${Date.now().toString().slice(-6)}` });
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to dispatch transfer");
    }
  };

  const handleReceive = async (transfer: StockTransfer) => {
    try {
      const itemsToReceive = transfer.items.map((it) => ({
        item_id: it.id,
        received_quantity: it.shipped_quantity || it.requested_quantity,
      }));
      await inventoryApi.receiveTransfer(transfer.id, itemsToReceive);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to receive transfer");
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Inter-Warehouse Stock Transfers
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {transfers.length} Transfers
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Dispatch, track in-transit items, and receive inter-warehouse movements with double-entry ledgering.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-amber-600 hover:bg-amber-500 text-white shadow-sm shadow-amber-600/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Transfer Request
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-medium">Filter by Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">DRAFT</option>
            <option value="IN_TRANSIT">IN_TRANSIT</option>
            <option value="COMPLETED">COMPLETED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>
      </div>

      {/* Transfers Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Transfer #</th>
                <th className="py-3 px-4">Source Hub</th>
                <th className="py-3 px-4">Destination Hub</th>
                <th className="py-3 px-4">Items</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4">Tracking #</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={7} className="py-10 text-center text-slate-500">
                    Loading stock transfers...
                  </td>
                </tr>
              ) : transfers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-12 text-center text-slate-500">
                    <ArrowLeftRight className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No stock transfers recorded yet.
                  </td>
                </tr>
              ) : (
                transfers.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-amber-400">
                      {t.transfer_number}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {warehouses.find((w) => w.id === t.source_warehouse_id)?.name || t.source_warehouse_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {warehouses.find((w) => w.id === t.destination_warehouse_id)?.name || t.destination_warehouse_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 px-4">
                      {t.items?.length || 0} product lines
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          t.status === "COMPLETED"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : t.status === "IN_TRANSIT"
                            ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                            : t.status === "DRAFT"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : "bg-slate-800 text-slate-400 border-slate-700"
                        }`}
                      >
                        {t.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {t.tracking_number || "-"}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      {t.status === "DRAFT" && (
                        <button
                          onClick={() => handleDispatch(t.id)}
                          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 hover:bg-blue-500 text-white ml-auto"
                        >
                          <Send className="w-3 h-3" /> Dispatch
                        </button>
                      )}
                      {t.status === "IN_TRANSIT" && (
                        <button
                          onClick={() => handleReceive(t)}
                          className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-semibold rounded bg-emerald-600 hover:bg-emerald-500 text-white ml-auto"
                        >
                          <CheckCircle2 className="w-3 h-3" /> Receive
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

      {/* Create Transfer Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <ArrowLeftRight className="w-5 h-5 text-amber-400" />
                Initiate Stock Transfer
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

            <form onSubmit={handleCreateTransfer} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Source Warehouse *
                  </label>
                  <select
                    required
                    value={formData.source_warehouse_id}
                    onChange={(e) => setFormData({ ...formData, source_warehouse_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="">Select Origin...</option>
                    {warehouses.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.name} ({w.code})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Destination Warehouse *
                  </label>
                  <select
                    required
                    value={formData.destination_warehouse_id}
                    onChange={(e) => setFormData({ ...formData, destination_warehouse_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="">Select Target...</option>
                    {warehouses.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.name} ({w.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Product SKU *
                  </label>
                  <select
                    required
                    value={formData.product_id}
                    onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="">Select Product SKU...</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.name} ({p.sku})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Quantity *
                  </label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.requested_quantity}
                    onChange={(e) => setFormData({ ...formData, requested_quantity: parseInt(e.target.value) || 1 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Transfer Notes</label>
                <textarea
                  rows={2}
                  placeholder="Optional routing or dispatch instructions..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
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
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-amber-600 hover:bg-amber-500 text-white shadow-sm shadow-amber-600/30 disabled:opacity-50"
                >
                  {submitting ? "Initiating..." : "Initiate Transfer"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
