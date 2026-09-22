import React, { useEffect, useState } from "react";
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  Plus,
  Search,
  Filter,
  RefreshCw,
  ClipboardCheck,
  Factory,
  Package,
  FileText,
} from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { QualityInspection, ProductionOrder } from "../types";

export const QualityInspectionsPage: React.FC = () => {
  const [inspections, setInspections] = useState<QualityInspection[]>([]);
  const [productionOrders, setProductionOrders] = useState<ProductionOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [filterType, setFilterType] = useState<string>("ALL");
  const [filterResult, setFilterResult] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [notification, setNotification] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Form State
  const [formData, setFormData] = useState({
    production_order_id: "",
    work_order_id: "",
    product_id: "",
    inspection_type: "FINAL_ASSEMBLY" as "RECEIVING" | "IN_PROCESS" | "FINAL_ASSEMBLY",
    inspected_quantity: 10,
    passed_quantity: 10,
    failed_quantity: 0,
    result: "PASSED" as "PENDING" | "PASSED" | "FAILED" | "CONDITIONALLY_PASSED",
    defect_reason: "",
    notes: "",
  });

  const loadData = async () => {
    try {
      setLoading(true);
      const [inspRes, ordersRes] = await Promise.allSettled([
        manufacturingApi.getQualityInspections({ page: 1, page_size: 50 }),
        manufacturingApi.getProductionOrders({ page: 1, page_size: 50 }),
      ]);

      if (inspRes.status === "fulfilled") {
        setInspections(inspRes.value.items || []);
      }
      if (ordersRes.status === "fulfilled") {
        setProductionOrders(ordersRes.value.items || []);
      }
    } catch (err) {
      console.error("Failed to load quality inspections", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleOrderChange = (orderId: string) => {
    const selected = productionOrders.find((o) => o.id === orderId);
    setFormData((prev) => ({
      ...prev,
      production_order_id: orderId,
      product_id: selected?.product_id || prev.product_id,
      inspected_quantity: selected ? Number(selected.planned_quantity) : prev.inspected_quantity,
      passed_quantity: selected ? Number(selected.planned_quantity) : prev.passed_quantity,
      failed_quantity: 0,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.production_order_id || !formData.product_id) {
      setNotification({ type: "error", message: "Please select a production order and product." });
      return;
    }

    try {
      setSubmitting(true);
      await manufacturingApi.createQualityInspection({
        production_order_id: formData.production_order_id,
        work_order_id: formData.work_order_id || null,
        product_id: formData.product_id,
        inspection_type: formData.inspection_type,
        inspected_quantity: Number(formData.inspected_quantity),
        passed_quantity: Number(formData.passed_quantity),
        failed_quantity: Number(formData.failed_quantity),
        result: formData.result,
        defect_reason: formData.defect_reason || null,
        notes: formData.notes || null,
      });

      setNotification({ type: "success", message: "Quality inspection logged successfully!" });
      setShowModal(false);
      await loadData();
    } catch (err: any) {
      setNotification({
        type: "error",
        message: err.message || "Failed to record quality inspection.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Calculations for KPIs
  const totalCount = inspections.length;
  const passedCount = inspections.filter((i) => i.result === "PASSED").length;
  const failedCount = inspections.filter((i) => i.result === "FAILED").length;
  const conditionalCount = inspections.filter((i) => i.result === "CONDITIONALLY_PASSED").length;
  const passRate = totalCount > 0 ? ((passedCount / totalCount) * 100).toFixed(1) : "100.0";

  const filteredInspections = inspections.filter((i) => {
    const matchesType = filterType === "ALL" || i.inspection_type === filterType;
    const matchesResult = filterResult === "ALL" || i.result === filterResult;
    const matchesSearch =
      searchQuery === "" ||
      i.inspection_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      i.product_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (i.defect_reason && i.defect_reason.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesType && matchesResult && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 text-white p-6 rounded-2xl shadow-xl border border-emerald-900/40">
        <div>
          <div className="flex items-center gap-2 text-emerald-400 font-semibold text-xs mb-1 uppercase tracking-wider">
            <ShieldCheck className="w-4 h-4" /> Quality Control & Compliance
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Quality Inspections & Audits</h1>
          <p className="text-slate-400 text-xs mt-1 max-w-xl">
            Audit receiving raw materials, in-process sub-assemblies, and finished goods against tolerance specs with defect tracking and automated dispositioning.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-semibold text-xs text-white shadow-lg shadow-emerald-600/30 transition-all self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          Log Quality Inspection
        </button>
      </div>

      {/* Notification */}
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
              <AlertTriangle className="w-4 h-4 text-rose-400 shrink-0" />
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
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Total Inspections</span>
            <ClipboardCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-white mt-2">{totalCount}</div>
          <div className="text-[11px] text-slate-400 mt-1">Across all production stages</div>
        </div>

        <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Passed Inspections</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-300 mt-2">{passedCount}</div>
          <div className="text-[11px] text-emerald-400/80 mt-1">{passRate}% First-Pass Yield</div>
        </div>

        <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Failed Inspections</span>
            <XCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-300 mt-2">{failedCount}</div>
          <div className="text-[11px] text-rose-400/80 mt-1">Quarantined / Scrap routed</div>
        </div>

        <div className="bg-slate-900/60 backdrop-blur border border-slate-800 p-4 rounded-xl">
          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400 font-medium">Conditional Approvals</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-300 mt-2">{conditionalCount}</div>
          <div className="text-[11px] text-amber-400/80 mt-1">Deviation sign-off required</div>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-slate-900/60 backdrop-blur border border-slate-800 rounded-2xl p-5">
        {/* Controls Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div className="flex flex-wrap items-center gap-2">
            {/* Filter by Type */}
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value="ALL">All Inspection Types</option>
              <option value="RECEIVING">Receiving QC</option>
              <option value="IN_PROCESS">In-Process QC</option>
              <option value="FINAL_ASSEMBLY">Final Assembly QC</option>
            </select>

            {/* Filter by Result */}
            <select
              value={filterResult}
              onChange={(e) => setFilterResult(e.target.value)}
              className="bg-slate-800/80 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value="ALL">All Results</option>
              <option value="PASSED">Passed</option>
              <option value="FAILED">Failed</option>
              <option value="CONDITIONALLY_PASSED">Conditional</option>
              <option value="PENDING">Pending</option>
            </select>

            <button
              onClick={loadData}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/60"
              title="Refresh"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              placeholder="Search inspection or SKU..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-800/80 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500 w-full sm:w-60"
            />
          </div>
        </div>

        {/* Inspections Table */}
        <div className="overflow-x-auto mt-4">
          <table className="w-full text-left text-xs">
            <thead className="text-[11px] uppercase tracking-wider text-slate-400 bg-slate-800/50 border-y border-slate-800">
              <tr>
                <th className="py-3 px-4">Inspection #</th>
                <th className="py-3 px-4">Stage / Type</th>
                <th className="py-3 px-4">Product / SKU</th>
                <th className="py-3 px-3 text-right">Inspected</th>
                <th className="py-3 px-3 text-right text-emerald-400">Passed</th>
                <th className="py-3 px-3 text-right text-rose-400">Failed</th>
                <th className="py-3 px-4">Result</th>
                <th className="py-3 px-4">Defect Reason</th>
                <th className="py-3 px-4">Inspection Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={9} className="text-center py-16 text-slate-500">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-slate-400" />
                    Loading quality records...
                  </td>
                </tr>
              ) : filteredInspections.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-16 text-slate-500">
                    No quality inspection records found.
                  </td>
                </tr>
              ) : (
                filteredInspections.map((insp) => (
                  <tr key={insp.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4 font-semibold text-white">
                      {insp.inspection_number}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="inline-block px-2 py-0.5 rounded-md text-[10px] font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                        {insp.inspection_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-medium text-slate-300">
                      <div className="truncate max-w-[140px]" title={insp.product_id}>
                        {insp.product_id}
                      </div>
                    </td>
                    <td className="py-3.5 px-3 text-right font-medium text-slate-200">
                      {Number(insp.inspected_quantity).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-3 text-right font-bold text-emerald-400">
                      {Number(insp.passed_quantity).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-3 text-right font-bold text-rose-400">
                      {Number(insp.failed_quantity).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          insp.result === "PASSED"
                            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                            : insp.result === "FAILED"
                            ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                            : insp.result === "CONDITIONALLY_PASSED"
                            ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                            : "bg-slate-700 text-slate-300"
                        }`}
                      >
                        {insp.result === "PASSED" && <CheckCircle2 className="w-3 h-3" />}
                        {insp.result === "FAILED" && <XCircle className="w-3 h-3" />}
                        {insp.result === "CONDITIONALLY_PASSED" && <AlertTriangle className="w-3 h-3" />}
                        {insp.result}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px] max-w-[160px] truncate">
                      {insp.defect_reason || "—"}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                      {new Date(insp.inspection_date).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Log Inspection Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
            <div className="flex items-center justify-between p-5 border-b border-slate-800">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" /> Log Quality Inspection
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Production Order</label>
                <select
                  value={formData.production_order_id}
                  onChange={(e) => handleOrderChange(e.target.value)}
                  required
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  <option value="">Select Production Order...</option>
                  {productionOrders.map((o) => (
                    <option key={o.id} value={o.id}>
                      {o.order_number} (Product: {o.product_id})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Inspection Stage</label>
                  <select
                    value={formData.inspection_type}
                    onChange={(e: any) =>
                      setFormData((prev) => ({ ...prev, inspection_type: e.target.value }))
                    }
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="FINAL_ASSEMBLY">Final Assembly QC</option>
                    <option value="IN_PROCESS">In-Process QC</option>
                    <option value="RECEIVING">Receiving QC</option>
                  </select>
                </div>

                <div>
                  <label className="block text-slate-300 font-medium mb-1">Inspection Result</label>
                  <select
                    value={formData.result}
                    onChange={(e: any) => setFormData((prev) => ({ ...prev, result: e.target.value }))}
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  >
                    <option value="PASSED">Passed</option>
                    <option value="CONDITIONALLY_PASSED">Conditionally Passed</option>
                    <option value="FAILED">Failed</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-slate-300 font-medium mb-1">Inspected Qty</label>
                  <input
                    type="number"
                    value={formData.inspected_quantity}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, inspected_quantity: Number(e.target.value) }))
                    }
                    required
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-emerald-400 font-medium mb-1">Passed Qty</label>
                  <input
                    type="number"
                    value={formData.passed_quantity}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, passed_quantity: Number(e.target.value) }))
                    }
                    required
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-rose-400 font-medium mb-1">Failed Qty</label>
                  <input
                    type="number"
                    value={formData.failed_quantity}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, failed_quantity: Number(e.target.value) }))
                    }
                    required
                    className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Defect Reason (if any)</label>
                <input
                  type="text"
                  placeholder="e.g., Dimensional tolerance breach ±0.5mm"
                  value={formData.defect_reason}
                  onChange={(e) => setFormData((prev) => ({ ...prev, defect_reason: e.target.value }))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">Notes / Observations</label>
                <textarea
                  rows={2}
                  placeholder="Additional inspection notes..."
                  value={formData.notes}
                  onChange={(e) => setFormData((prev) => ({ ...prev, notes: e.target.value }))}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-emerald-500 resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 font-semibold text-white shadow-lg shadow-emerald-600/30 transition-all disabled:opacity-50"
                >
                  {submitting ? "Saving..." : "Record Inspection"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
