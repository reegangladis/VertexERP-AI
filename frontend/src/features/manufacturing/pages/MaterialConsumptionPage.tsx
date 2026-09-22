import React, { useEffect, useState } from "react";
import {
  Package,
  Plus,
  Search,
  ArrowDownLeft,
  ArrowUpRight,
  Trash2,
  CheckCircle2,
  AlertTriangle,
  X,
  Layers,
  DollarSign,
} from "lucide-react";
import { manufacturingApi } from "../api/manufacturingApi";
import { MaterialConsumption, ProductionOutput, ProductionScrap, ProductionOrder } from "../types";

export const MaterialConsumptionPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<"CONSUMPTIONS" | "OUTPUTS" | "SCRAPS">("CONSUMPTIONS");
  const [consumptions, setConsumptions] = useState<MaterialConsumption[]>([]);
  const [outputs, setOutputs] = useState<ProductionOutput[]>([]);
  const [scraps, setScraps] = useState<ProductionScrap[]>([]);
  const [loading, setLoading] = useState(true);

  // Consumption Modal
  const [isConsumeModalOpen, setIsConsumeModalOpen] = useState(false);
  const [cOrderId, setCOrderId] = useState("");
  const [cProductId, setCProductId] = useState("");
  const [cWarehouseId, setCWarehouseId] = useState("");
  const [cQty, setCQty] = useState("10.0000");
  const [cBatch, setCBatch] = useState("");

  // Output Modal
  const [isOutputModalOpen, setIsOutputModalOpen] = useState(false);
  const [oOrderId, setOOrderId] = useState("");
  const [oWarehouseId, setOWarehouseId] = useState("");
  const [oQty, setOQty] = useState("1.0000");
  const [oBatch, setOBatch] = useState("");
  const [oSerial, setOSerial] = useState("");

  // Scrap Modal
  const [isScrapModalOpen, setIsScrapModalOpen] = useState(false);
  const [sOrderId, setSOrderId] = useState("");
  const [sProductId, setSProductId] = useState("");
  const [sWarehouseId, setSWarehouseId] = useState("");
  const [sQty, setSQty] = useState("1.0000");
  const [sReason, setSReason] = useState("DEFECTIVE_RAW_MATERIAL");

  useEffect(() => {
    loadLedgerData();
  }, []);

  async function loadLedgerData() {
    setLoading(true);
    try {
      const res = await manufacturingApi.getProductionOrders({ page: 1, page_size: 50 });
      const allCons: MaterialConsumption[] = [];
      const allOuts: ProductionOutput[] = [];
      const allScraps: ProductionScrap[] = [];

      (res.items || []).forEach((po) => {
        if (po.consumptions) allCons.push(...po.consumptions);
        if (po.outputs) allOuts.push(...po.outputs);
        if (po.scraps) allScraps.push(...po.scraps);
      });

      setConsumptions(allCons);
      setOutputs(allOuts);
      setScraps(allScraps);
    } catch (err) {
      console.error("Failed to load manufacturing ledger data", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleConsume(e: React.FormEvent) {
    e.preventDefault();
    try {
      await manufacturingApi.recordMaterialConsumption(cOrderId, {
        product_id: cProductId,
        warehouse_id: cWarehouseId,
        consumed_quantity: cQty,
        batch_number: cBatch || undefined,
      });
      setIsConsumeModalOpen(false);
      loadLedgerData();
    } catch (err) {
      console.error("Failed to record consumption", err);
      alert("Failed to record consumption. Verify sufficient stock on hand.");
    }
  }

  async function handleOutput(e: React.FormEvent) {
    e.preventDefault();
    try {
      await manufacturingApi.recordProductionOutput(oOrderId, {
        target_warehouse_id: oWarehouseId || undefined,
        produced_quantity: oQty,
        batch_number: oBatch || undefined,
        serial_number: oSerial || undefined,
      });
      setIsOutputModalOpen(false);
      loadLedgerData();
    } catch (err) {
      console.error("Failed to record production output", err);
      alert("Failed to record output.");
    }
  }

  async function handleScrap(e: React.FormEvent) {
    e.preventDefault();
    try {
      await manufacturingApi.recordProductionScrap(sOrderId, {
        product_id: sProductId,
        warehouse_id: sWarehouseId || undefined,
        scrap_quantity: sQty,
        scrap_reason: sReason,
      });
      setIsScrapModalOpen(false);
      loadLedgerData();
    } catch (err) {
      console.error("Failed to record scrap", err);
      alert("Failed to record scrap.");
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-100 flex items-center gap-2.5">
            <Package className="w-7 h-7 text-emerald-400" /> Production Inventory Ledger
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Auditable stock movements for raw material issuance (MFG_CONSUMPTION), finished goods receipt (MFG_OUTPUT), and scrap losses (MFG_SCRAP).
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => setIsConsumeModalOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 font-medium text-xs text-white shadow-md shadow-blue-600/30 transition-all"
          >
            <ArrowDownLeft className="w-3.5 h-3.5" /> Issue Materials
          </button>
          <button
            onClick={() => setIsOutputModalOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 font-medium text-xs text-white shadow-md shadow-emerald-600/30 transition-all"
          >
            <ArrowUpRight className="w-3.5 h-3.5" /> Record Output
          </button>
          <button
            onClick={() => setIsScrapModalOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-rose-600/80 hover:bg-rose-600 font-medium text-xs text-white shadow-md shadow-rose-600/30 transition-all"
          >
            <Trash2 className="w-3.5 h-3.5" /> Log Scrap
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-3">
        {[
          { key: "CONSUMPTIONS", label: `Material Consumptions (${consumptions.length})`, color: "text-blue-400" },
          { key: "OUTPUTS", label: `Finished Goods Outputs (${outputs.length})`, color: "text-emerald-400" },
          { key: "SCRAPS", label: `Production Scrap (${scraps.length})`, color: "text-rose-400" },
        ].map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key as any)}
            className={`px-4 py-2 rounded-xl text-xs font-semibold transition-all ${
              activeTab === tab.key
                ? "bg-slate-800 text-slate-100 border border-slate-700 shadow"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tables based on active tab */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          {activeTab === "CONSUMPTIONS" && (
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/80 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Product ID</th>
                  <th className="px-5 py-3.5">Consumed Qty</th>
                  <th className="px-5 py-3.5">Unit Cost</th>
                  <th className="px-5 py-3.5">Total Cost</th>
                  <th className="px-5 py-3.5">Batch #</th>
                  <th className="px-5 py-3.5">Stock Movement ID</th>
                  <th className="px-5 py-3.5">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {consumptions.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-slate-500 text-xs">
                      No material consumption transactions recorded yet.
                    </td>
                  </tr>
                ) : (
                  consumptions.map((c) => (
                    <tr key={c.id} className="hover:bg-slate-800/30">
                      <td className="px-5 py-3.5 font-mono text-xs text-slate-200">{c.product_id}</td>
                      <td className="px-5 py-3.5 font-bold text-blue-400">-{Number(c.consumed_quantity).toFixed(4)}</td>
                      <td className="px-5 py-3.5 font-mono text-xs">${Number(c.unit_cost).toFixed(2)}</td>
                      <td className="px-5 py-3.5 font-mono text-xs font-semibold text-slate-100">${Number(c.total_cost).toFixed(2)}</td>
                      <td className="px-5 py-3.5 text-xs text-slate-400">{c.batch_number || "—"}</td>
                      <td className="px-5 py-3.5 font-mono text-[11px] text-slate-500">{c.stock_movement_id || "—"}</td>
                      <td className="px-5 py-3.5 text-xs text-slate-400">{c.consumed_at.split("T")[0]}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}

          {activeTab === "OUTPUTS" && (
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/80 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Product ID</th>
                  <th className="px-5 py-3.5">Produced Qty</th>
                  <th className="px-5 py-3.5">Unit Mfg Cost</th>
                  <th className="px-5 py-3.5">Total Mfg Cost</th>
                  <th className="px-5 py-3.5">Batch / Serial</th>
                  <th className="px-5 py-3.5">Stock Movement ID</th>
                  <th className="px-5 py-3.5">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {outputs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-slate-500 text-xs">
                      No finished goods outputs recorded yet.
                    </td>
                  </tr>
                ) : (
                  outputs.map((o) => (
                    <tr key={o.id} className="hover:bg-slate-800/30">
                      <td className="px-5 py-3.5 font-mono text-xs text-slate-200">{o.product_id}</td>
                      <td className="px-5 py-3.5 font-bold text-emerald-400">+{Number(o.produced_quantity).toFixed(4)}</td>
                      <td className="px-5 py-3.5 font-mono text-xs text-emerald-300">${Number(o.unit_manufacturing_cost).toFixed(2)}</td>
                      <td className="px-5 py-3.5 font-mono text-xs font-semibold text-slate-100">${Number(o.total_manufacturing_cost).toFixed(2)}</td>
                      <td className="px-5 py-3.5 text-xs text-slate-400">{o.batch_number || o.serial_number || "—"}</td>
                      <td className="px-5 py-3.5 font-mono text-[11px] text-slate-500">{o.stock_movement_id || "—"}</td>
                      <td className="px-5 py-3.5 text-xs text-slate-400">{o.output_date.split("T")[0]}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}

          {activeTab === "SCRAPS" && (
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/80 text-xs uppercase font-semibold text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="px-5 py-3.5">Product ID</th>
                  <th className="px-5 py-3.5">Scrap Qty</th>
                  <th className="px-5 py-3.5">Reason</th>
                  <th className="px-5 py-3.5">Unit Cost</th>
                  <th className="px-5 py-3.5">Total Scrap Loss</th>
                  <th className="px-5 py-3.5">Stock Movement ID</th>
                  <th className="px-5 py-3.5">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800">
                {scraps.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="text-center py-12 text-slate-500 text-xs">
                      No production scrap records logged.
                    </td>
                  </tr>
                ) : (
                  scraps.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-800/30">
                      <td className="px-5 py-3.5 font-mono text-xs text-slate-200">{s.product_id}</td>
                      <td className="px-5 py-3.5 font-bold text-rose-400">-{Number(s.scrap_quantity).toFixed(4)}</td>
                      <td className="px-5 py-3.5 text-xs font-medium text-slate-300">{s.scrap_reason}</td>
                      <td className="px-5 py-3.5 font-mono text-xs">${Number(s.unit_cost).toFixed(2)}</td>
                      <td className="px-5 py-3.5 font-mono text-xs font-semibold text-rose-400">${Number(s.total_scrap_cost).toFixed(2)}</td>
                      <td className="px-5 py-3.5 font-mono text-[11px] text-slate-500">{s.stock_movement_id || "—"}</td>
                      <td className="px-5 py-3.5 text-xs text-slate-400">{s.recorded_at.split("T")[0]}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {/* Consume Modal */}
      {isConsumeModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <ArrowDownLeft className="w-5 h-5 text-blue-400" /> Issue Raw Material
              </h2>
              <button onClick={() => setIsConsumeModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleConsume} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Production Order UUID *</label>
                <input
                  type="text"
                  required
                  placeholder="Order ID"
                  value={cOrderId}
                  onChange={(e) => setCOrderId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Raw Product UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Product ID"
                    value={cProductId}
                    onChange={(e) => setCProductId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Warehouse UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Raw WH ID"
                    value={cWarehouseId}
                    onChange={(e) => setCWarehouseId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Quantity to Deduct *</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={cQty}
                    onChange={(e) => setCQty(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Batch Number</label>
                  <input
                    type="text"
                    placeholder="e.g. BATCH-2026"
                    value={cBatch}
                    onChange={(e) => setCBatch(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsConsumeModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-sm text-white font-semibold shadow-lg shadow-blue-600/30"
                >
                  Deduct from Inventory
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Output Modal */}
      {isOutputModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <ArrowUpRight className="w-5 h-5 text-emerald-400" /> Receipt Finished Goods Output
              </h2>
              <button onClick={() => setIsOutputModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleOutput} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Production Order UUID *</label>
                <input
                  type="text"
                  required
                  placeholder="Order ID"
                  value={oOrderId}
                  onChange={(e) => setOOrderId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Produced Quantity *</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={oQty}
                    onChange={(e) => setOQty(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Target Warehouse UUID</label>
                  <input
                    type="text"
                    placeholder="Defaults to MO target WH"
                    value={oWarehouseId}
                    onChange={(e) => setOWarehouseId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Batch Number</label>
                  <input
                    type="text"
                    placeholder="Batch #"
                    value={oBatch}
                    onChange={(e) => setOBatch(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Serial Number</label>
                  <input
                    type="text"
                    placeholder="Serial #"
                    value={oSerial}
                    onChange={(e) => setOSerial(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsOutputModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-sm text-white font-semibold shadow-lg shadow-emerald-600/30"
                >
                  Receipt into Inventory
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Scrap Modal */}
      {isScrapModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
                <Trash2 className="w-5 h-5 text-rose-400" /> Log Production Waste / Scrap
              </h2>
              <button onClick={() => setIsScrapModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleScrap} className="space-y-3">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Production Order UUID *</label>
                <input
                  type="text"
                  required
                  placeholder="Order ID"
                  value={sOrderId}
                  onChange={(e) => setSOrderId(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100 focus:outline-none focus:border-rose-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Product UUID *</label>
                  <input
                    type="text"
                    required
                    placeholder="Scrapped Product ID"
                    value={sProductId}
                    onChange={(e) => setSProductId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Warehouse UUID (Optional)</label>
                  <input
                    type="text"
                    placeholder="Warehouse to deduct from"
                    value={sWarehouseId}
                    onChange={(e) => setSWarehouseId(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Scrap Quantity *</label>
                  <input
                    type="number"
                    step="0.0001"
                    required
                    value={sQty}
                    onChange={(e) => setSQty(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-400 mb-1">Scrap Reason</label>
                  <select
                    value={sReason}
                    onChange={(e) => setSReason(e.target.value)}
                    className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-100"
                  >
                    <option value="DEFECTIVE_RAW_MATERIAL">DEFECTIVE_RAW_MATERIAL</option>
                    <option value="MACHINE_MALFUNCTION">MACHINE_MALFUNCTION</option>
                    <option value="OPERATOR_ERROR">OPERATOR_ERROR</option>
                    <option value="EXPIRED_BATCH">EXPIRED_BATCH</option>
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsScrapModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-sm text-slate-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-sm text-white font-semibold shadow-lg shadow-rose-600/30"
                >
                  Record Scrap Loss
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
