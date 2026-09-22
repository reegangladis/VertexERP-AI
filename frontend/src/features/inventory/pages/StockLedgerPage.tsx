import React, { useEffect, useState } from "react";
import {
  History,
  Search,
  Filter,
  Warehouse as WarehouseIcon,
  Sparkles,
  ArrowUpRight,
  ArrowDownLeft,
  RefreshCw,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { StockMovement, Warehouse } from "../types";

export const StockLedgerPage: React.FC = () => {
  const [movements, setMovements] = useState<StockMovement[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [selectedWh, setSelectedWh] = useState<string>("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [movRes, whRes] = await Promise.allSettled([
        inventoryApi.getStockMovements({ warehouse_id: selectedWh || undefined, page: 1, page_size: 100 }),
        inventoryApi.getWarehouses(),
      ]);

      if (movRes.status === "fulfilled") setMovements(movRes.value.items || []);
      if (whRes.status === "fulfilled") setWarehouses(whRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedWh]);

  const filteredMovements = movements.filter((m) => {
    if (!search) return true;
    const matchSearch =
      (m.product_name || "").toLowerCase().includes(search.toLowerCase()) ||
      m.product_id.toLowerCase().includes(search.toLowerCase()) ||
      (m.reference_type || "").toLowerCase().includes(search.toLowerCase()) ||
      (m.reference_id || "").toLowerCase().includes(search.toLowerCase());
    return matchSearch;
  });

  const getMovementBadge = (type: string) => {
    switch (type) {
      case "RECEIPT":
      case "TRANSFER_IN":
      case "ADJUSTMENT_IN":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
      case "ISSUE":
      case "TRANSFER_OUT":
      case "ADJUSTMENT_OUT":
      case "SCRAP":
        return "bg-rose-500/10 text-rose-400 border-rose-500/20";
      default:
        return "bg-slate-800 text-slate-300 border-slate-700";
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Immutable Stock Movement Ledger
            </h1>
            <span className="flex items-center gap-1 text-[11px] font-medium px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Sparkles className="w-3 h-3" /> Append-Only Audit Trail
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Complete transaction history of every physical and logical inventory movement.
          </p>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-blue-400" />
          Refresh Ledger
        </button>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by product, reference type or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700/60 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <WarehouseIcon className="w-4 h-4 text-slate-400" />
          <select
            value={selectedWh}
            onChange={(e) => setSelectedWh(e.target.value)}
            className="bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="">All Warehouses</option>
            {warehouses.map((w) => (
              <option key={w.id} value={w.id}>
                {w.name} ({w.code})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Ledger Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Date / Time</th>
                <th className="py-3 px-4">Movement Type</th>
                <th className="py-3 px-4">Product</th>
                <th className="py-3 px-4">Warehouse</th>
                <th className="py-3 px-4 text-right">Qty Delta</th>
                <th className="py-3 px-4 text-center">Before &rarr; After</th>
                <th className="py-3 px-4 text-right">Unit Cost</th>
                <th className="py-3 px-4 text-right">Total Cost</th>
                <th className="py-3 px-4">Reference Doc</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={9} className="py-10 text-center text-slate-500">
                    Loading immutable movements ledger...
                  </td>
                </tr>
              ) : filteredMovements.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-slate-500">
                    <History className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No stock movements recorded yet.
                  </td>
                </tr>
              ) : (
                filteredMovements.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4 font-mono text-slate-400">
                      {new Date(m.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase ${getMovementBadge(
                          m.movement_type
                        )}`}
                      >
                        {m.movement_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-100">
                        {m.product_name || m.product_id}
                      </div>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {m.warehouse_name || m.warehouse_id.slice(0, 8)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold">
                      <span
                        className={
                          Number(m.quantity) >= 0 ? "text-emerald-400" : "text-rose-400"
                        }
                      >
                        {Number(m.quantity) > 0 ? `+${m.quantity}` : m.quantity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-center font-mono text-slate-400">
                      {m.quantity_before} &rarr;{" "}
                      <span className="font-bold text-slate-200">{m.quantity_after}</span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-300">
                      ${Number(m.unit_cost || 0).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-semibold text-slate-200">
                      ${Number(m.total_cost || 0).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4">
                      <div className="font-mono text-[11px] text-blue-400">
                        {m.reference_type}
                      </div>
                      {m.reference_id && (
                        <div className="text-[10px] text-slate-500 font-mono truncate max-w-[120px]">
                          {m.reference_id}
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
