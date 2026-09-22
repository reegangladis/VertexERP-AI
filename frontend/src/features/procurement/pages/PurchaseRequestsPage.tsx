import React, { useEffect, useState } from "react";
import {
  FileSpreadsheet,
  Plus,
  Send,
  CheckCircle2,
  XCircle,
  Clock,
  Sparkles,
  AlertCircle,
} from "lucide-react";
import { procurementApi } from "../api/procurementApi";
import { inventoryApi } from "@/features/inventory/api/inventoryApi";
import { Product } from "@/features/inventory/types";
import { PurchaseRequest } from "../types";

export const PurchaseRequestsPage: React.FC = () => {
  const [requests, setRequests] = useState<PurchaseRequest[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>("");

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    priority: "MEDIUM" as const,
    reason: "",
    target_date: "",
    product_id: "",
    quantity: 1,
    estimated_unit_cost: 10,
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [prRes, prodRes] = await Promise.allSettled([
        procurementApi.getPurchaseRequests({ status: statusFilter || undefined }),
        inventoryApi.getProducts(),
      ]);

      if (prRes.status === "fulfilled") setRequests(prRes.value.items || []);
      if (prodRes.status === "fulfilled") setProducts(prodRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter]);

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      if (!formData.product_id) {
        setError("Product selection is required.");
        setSubmitting(false);
        return;
      }

      await procurementApi.createPurchaseRequest({
        priority: formData.priority,
        reason: formData.reason,
        target_date: formData.target_date || undefined,
        items: [
          {
            product_id: formData.product_id,
            quantity: Number(formData.quantity) || 1,
            estimated_unit_cost: Number(formData.estimated_unit_cost) || 0,
          } as any,
        ],
      });

      setIsModalOpen(false);
      setFormData({
        priority: "MEDIUM",
        reason: "",
        target_date: "",
        product_id: "",
        quantity: 1,
        estimated_unit_cost: 10,
      });
      await loadData();
    } catch (err: any) {
      setError(err?.message || "Failed to create requisition");
    } finally {
      setSubmitting(false);
    }
  };

  const handleSubmit = async (id: string) => {
    try {
      await procurementApi.submitPurchaseRequest(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to submit purchase request");
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await procurementApi.approvePurchaseRequest(id);
      await loadData();
    } catch (err: any) {
      alert(err?.message || "Failed to approve purchase request");
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Purchase Requests & Requisitions (PR)
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
              {requests.length} Requisitions
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Departmental procurement requisitions, approval matrices, and demand consolidation.
          </p>
        </div>

        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-amber-600 hover:bg-amber-500 text-white shadow-sm shadow-amber-600/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Create Purchase Request
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
            <option value="SUBMITTED">SUBMITTED</option>
            <option value="APPROVED">APPROVED</option>
            <option value="ORDERED">ORDERED</option>
            <option value="REJECTED">REJECTED</option>
          </select>
        </div>
      </div>

      {/* Requisitions Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">PR Number</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Requested Lines</th>
                <th className="py-3 px-4">Justification</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Workflow</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={6} className="py-10 text-center text-slate-500">
                    Loading purchase requests...
                  </td>
                </tr>
              ) : requests.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    <FileSpreadsheet className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No purchase requisitions found.
                  </td>
                </tr>
              ) : (
                requests.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono font-bold text-amber-400">
                      {r.request_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          r.priority === "URGENT"
                            ? "bg-rose-500/10 text-rose-400 border-rose-500/20"
                            : r.priority === "HIGH"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : "bg-slate-800 text-slate-400 border-slate-700"
                        }`}
                      >
                        {r.priority}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      {r.items?.map((it, idx) => (
                        <div key={idx} className="text-[11px] font-mono text-slate-300">
                          {it.product_name || it.product_id.slice(0, 8)}: {it.quantity} units (~${Number(it.estimated_total_cost || 0).toFixed(2)})
                        </div>
                      ))}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 max-w-xs truncate">
                      {r.reason || "-"}
                    </td>
                    <td className="py-3.5 px-4 text-center">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${
                          r.status === "APPROVED" || r.status === "ORDERED"
                            ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                            : r.status === "SUBMITTED"
                            ? "bg-blue-500/10 text-blue-400 border-blue-500/20"
                            : r.status === "DRAFT"
                            ? "bg-amber-500/10 text-amber-400 border-amber-500/20"
                            : "bg-rose-500/10 text-rose-400 border-rose-500/20"
                        }`}
                      >
                        {r.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {r.status === "DRAFT" && (
                          <button
                            onClick={() => handleSubmit(r.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-amber-600 hover:bg-amber-500 text-white shadow-sm"
                          >
                            Submit
                          </button>
                        )}
                        {r.status === "SUBMITTED" && (
                          <button
                            onClick={() => handleApprove(r.id)}
                            className="px-2.5 py-1 text-xs font-semibold rounded bg-emerald-600 hover:bg-emerald-500 text-white shadow-sm"
                          >
                            Approve
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

      {/* Create PR Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <FileSpreadsheet className="w-5 h-5 text-amber-400" />
                New Purchase Requisition
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

            <form onSubmit={handleCreateRequest} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Priority Level
                  </label>
                  <select
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: e.target.value as any })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  >
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                    <option value="URGENT">Urgent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Target Fulfillment Date
                  </label>
                  <input
                    type="date"
                    value={formData.target_date}
                    onChange={(e) => setFormData({ ...formData, target_date: e.target.value })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="col-span-2">
                  <label className="block text-xs font-medium text-slate-300 mb-1">
                    Product Item *
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
                    value={formData.quantity}
                    onChange={(e) => setFormData({ ...formData, quantity: parseFloat(e.target.value) || 1 })}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Estimated Unit Cost ($)
                </label>
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={formData.estimated_unit_cost}
                  onChange={(e) => setFormData({ ...formData, estimated_unit_cost: parseFloat(e.target.value) || 0 })}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Business Justification
                </label>
                <textarea
                  rows={2}
                  placeholder="Explain requirement, project or customer need..."
                  value={formData.reason}
                  onChange={(e) => setFormData({ ...formData, reason: e.target.value })}
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
                  {submitting ? "Saving..." : "Create Requisition"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
