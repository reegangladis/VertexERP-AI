import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  ShoppingCart,
  Plus,
  Send,
  CheckCircle2,
  XCircle,
  ArrowDownToLine,
  FileText,
  DollarSign,
  AlertCircle,
  Truck,
} from "lucide-react";
import { procurementApi } from "../api/procurementApi";
import { inventoryApi } from "@/features/inventory/api/inventoryApi";
import { Product, Warehouse } from "@/features/inventory/types";
import { PurchaseOrder, Supplier } from "../types";

export const PurchaseOrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    supplier_id: "",
    warehouse_id: "",
    product_id: "",
    quantity_ordered: 1,
    unit_price: 10,
    tax_rate: 0.1,
    notes: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [poRes, supRes, whRes, prodRes] = await Promise.allSettled([
        procurementApi.getPurchaseOrders({ status: statusFilter || undefined }),
        procurementApi.getSuppliers(),
        inventoryApi.getWarehouses(),
        inventoryApi.getProducts(),
      ]);

      if (poRes.status === "fulfilled") setOrders(poRes.value.items || []);
      if (supRes.status === "fulfilled") setSuppliers(supRes.value.items || []);
      if (whRes.status === "fulfilled") setWarehouses(whRes.value.items || []);
      if (prodRes.status === "fulfilled") setProducts(prodRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!formData.supplier_id || !formData.warehouse_id || !formData.product_id) {
        setError("Supplier, Delivery Warehouse, and Product are required.");
        setSubmitting(false);
        return;
      }

      await procurementApi.createPurchaseOrder({
        supplier_id: formData.supplier_id,
        warehouse_id: formData.warehouse_id,
        notes: formData.notes,
        items: [
          {
            product_id: formData.product_id,
            quantity_ordered: Number(formData.quantity_ordered) || 1,
            unit_price: Number(formData.unit_price) || 0,
            tax_rate: Number(formData.tax_rate) || 0,
          } as any,
        ],
      });

      setIsModalOpen(false);
      setFormData({
        supplier_id: "",
        warehouse_id: "",
        product_id: "",
        quantity_ordered: 1,
        unit_price: 10,
        tax_rate: 0.1,
        notes: "",
      });
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Failed to create purchase order");
    } finally {
      setSubmitting(false);
    }
  };

  const handleIssue = async (id: string) => {
    try {
      await procurementApi.issuePurchaseOrder(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to issue purchase order");
    }
  };

  const handleConfirm = async (id: string) => {
    try {
      await procurementApi.confirmPurchaseOrder(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to confirm purchase order");
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Purchase Orders (PO)
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
              {orders.length} Purchase Orders
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Vendor procurement contracts, item pricing, tax calculation, and goods receipt coordination.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Purchase Order
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xs text-slate-400 font-medium">Filter by Status:</span>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            <option value="">All Statuses</option>
            <option value="DRAFT">DRAFT</option>
            <option value="ISSUED">ISSUED</option>
            <option value="CONFIRMED">CONFIRMED</option>
            <option value="PARTIALLY_RECEIVED">PARTIALLY_RECEIVED</option>
            <option value="RECEIVED">RECEIVED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>
      </div>

      {/* Orders Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">PO Number</th>
                <th className="py-3 px-4">Vendor</th>
                <th className="py-3 px-4">Destination Warehouse</th>
                <th className="py-3 px-4 text-right">Subtotal</th>
                <th className="py-3 px-4 text-right">Tax</th>
                <th className="py-3 px-4 text-right">Total Amount</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    Loading purchase orders...
                  </td>
                </tr>
              ) : orders.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    <ShoppingCart className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No purchase orders recorded yet.
                  </td>
                </tr>
              ) : (
                orders.map((po) => (
                  <tr key={po.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-indigo-400">
                      {po.order_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-100">
                        {suppliers.find((s) => s.id === po.supplier_id)?.name || po.supplier_id.slice(0, 8)}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {warehouses.find((w) => w.id === po.warehouse_id)?.name || po.warehouse_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      ${Number(po.subtotal_amount || 0).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-400">
                      ${Number(po.tax_amount || 0).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-100">
                      ${Number(po.total_amount || 0).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          po.status === "RECEIVED"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : po.status === "CONFIRMED"
                            ? "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
                            : po.status === "ISSUED"
                            ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                            : po.status === "DRAFT"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        }`}
                      >
                        {po.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {po.status === "DRAFT" && (
                          <button
                            onClick={() => handleIssue(po.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-blue-600 hover:bg-blue-500 text-white shadow-sm"
                          >
                            Issue to Vendor
                          </button>
                        )}
                        {po.status === "ISSUED" && (
                          <button
                            onClick={() => handleConfirm(po.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm"
                          >
                            Confirm PO
                          </button>
                        )}
                        {(po.status === "ISSUED" || po.status === "CONFIRMED" || po.status === "PARTIALLY_RECEIVED") && (
                          <Link
                            to="/inventory/receipts"
                            className="flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded bg-teal-600 hover:bg-teal-500 text-white shadow-sm"
                          >
                            <ArrowDownToLine className="w-3 h-3" /> Receive
                          </Link>
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

      {/* Create Purchase Order Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <ShoppingCart className="w-5 h-5 text-indigo-400" />
                Create Purchase Order
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

            <form onSubmit={handleCreateOrder} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Vendor / Supplier *
                  </label>
                  <select
                    required
                    value={formData.supplier_id}
                    onChange={(e) => setFormData({ ...formData, supplier_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Select Vendor...</option>
                    {suppliers.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.name} ({s.code})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Delivery Warehouse *
                  </label>
                  <select
                    required
                    value={formData.warehouse_id}
                    onChange={(e) => setFormData({ ...formData, warehouse_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  >
                    <option value="">Select Warehouse...</option>
                    {warehouses.map((w) => (
                      <option key={w.id} value={w.id}>
                        {w.name} ({w.code})
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-3">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Product Item *
                  </label>
                  <select
                    required
                    value={formData.product_id}
                    onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
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
                  <label className="block text-xs font-medium text-slate-300 mb-1">Qty *</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={formData.quantity_ordered}
                    onChange={(e) => setFormData({ ...formData, quantity_ordered: parseFloat(e.target.value) || 1 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">Price ($) *</label>
                  <input
                    type="number"
                    min="0"
                    step="0.01"
                    required
                    value={formData.unit_price}
                    onChange={(e) => setFormData({ ...formData, unit_price: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Notes</label>
                <textarea
                  rows={2}
                  placeholder="Optional delivery terms or contract references..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
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
                  className="px-4 py-2 text-xs font-semibold rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white shadow-sm shadow-indigo-600/30 disabled:opacity-50"
                >
                  {submitting ? "Creating..." : "Create PO"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
