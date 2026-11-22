import React, { useEffect, useState } from "react";
import {
  Layers,
  Search,
  Filter,
  Warehouse as WarehouseIcon,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  Boxes,
  RefreshCw,
} from "lucide-react";
import { inventoryApi } from "../api/inventoryApi";
import { StockBalance, Warehouse } from "../types";

export const StockBalancesPage: React.FC = () => {
  const [balances, setBalances] = useState<StockBalance[]>([]);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [selectedWh, setSelectedWh] = useState<string>("");
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      setLoading(true);
      const [balRes, whRes] = await Promise.allSettled([
        inventoryApi.getStockBalances({ warehouse_id: selectedWh || undefined, page: 1, page_size: 100 }),
        inventoryApi.getWarehouses(),
      ]);

      if (balRes.status === "fulfilled") setBalances(balRes.value.items || []);
      if (whRes.status === "fulfilled") setWarehouses(whRes.value.items || []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [selectedWh]);

  const filteredBalances = balances.filter((b) => {
    if (!search) return true;
    const matchSearch =
      (b.product_name || "").toLowerCase().includes(search.toLowerCase()) ||
      (b.product_sku || "").toLowerCase().includes(search.toLowerCase()) ||
      b.product_id.toLowerCase().includes(search.toLowerCase());
    return matchSearch;
  });

  const totalValue = filteredBalances.reduce((acc, b) => acc + (Number(b.total_value) || 0), 0);
  const totalOnHand = filteredBalances.reduce((acc, b) => acc + (Number(b.quantity_on_hand) || 0), 0);
  const totalAvailable = filteredBalances.reduce((acc, b) => acc + (Number(b.quantity_available) || 0), 0);

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl font-bold tracking-tight text-slate-100">
              Stock Balances & Real-Time Availability
            </h1>
            <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
              {filteredBalances.length} Positions
            </span>
          </div>
          <p className="text-sm text-slate-400 mt-1">
            Real-time on-hand, reserved, and available quantities across storage facilities and bins.
          </p>
        </div>

        <button
          onClick={loadData}
          className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5 text-purple-400" />
          Refresh Balances
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Total Inventory Valuation
          </div>
          <div className="text-2xl font-bold text-slate-100 mt-2 font-mono">
            ${totalValue.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Total On-Hand Quantity
          </div>
          <div className="text-2xl font-bold text-emerald-400 mt-2 font-mono">
            {totalOnHand.toLocaleString()} <span className="text-xs font-normal text-slate-400">units</span>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            Total Available for Allocation
          </div>
          <div className="text-2xl font-bold text-purple-400 mt-2 font-mono">
            {totalAvailable.toLocaleString()} <span className="text-xs font-normal text-slate-400">units</span>
          </div>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Filter by product name, SKU or ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700/60 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-purple-500"
          />
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto">
          <WarehouseIcon className="w-4 h-4 text-slate-400" />
          <select
            value={selectedWh}
            onChange={(e) => setSelectedWh(e.target.value)}
            className="bg-slate-800 border border-slate-700/60 rounded-lg px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
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

      {/* Balances Table */}
      <div className="rounded-xl bg-slate-900/60 border border-slate-800 overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-slate-800/80 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700/60">
              <tr>
                <th className="py-3 px-4">Product / SKU</th>
                <th className="py-3 px-4">Warehouse</th>
                <th className="py-3 px-4 text-right">On Hand</th>
                <th className="py-3 px-4 text-right">Reserved</th>
                <th className="py-3 px-4 text-right">Available</th>
                <th className="py-3 px-4 text-right">On Order</th>
                <th className="py-3 px-4 text-right">Avg Unit Cost</th>
                <th className="py-3 px-4 text-right">Total Value</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {loading ? (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-slate-500">
                    Loading stock balance ledger...
                  </td>
                </tr>
              ) : filteredBalances.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-slate-500">
                    <Layers className="w-8 h-8 mx-auto text-slate-600 mb-2" />
                    No stock balance records found. Perform goods receipts to record stock.
                  </td>
                </tr>
              ) : (
                filteredBalances.map((b) => (
                  <tr key={b.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-slate-100">
                        {b.product_name || b.product_id}
                      </div>
                      {b.product_sku && (
                        <div className="text-[10px] font-mono text-blue-400">SKU: {b.product_sku}</div>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="font-mono text-slate-300">
                        {b.warehouse_name || b.warehouse_id.slice(0, 8)}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-100">
                      {Number(b.quantity_on_hand).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-amber-400">
                      {Number(b.quantity_reserved).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-emerald-400">
                      {Number(b.quantity_available).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-purple-400">
                      {Number(b.quantity_on_order).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono text-slate-300">
                      ${Number(b.average_cost || 0).toFixed(2)}
                    </td>
                    <td className="py-3.5 px-4 text-right font-mono font-bold text-slate-100">
                      ${Number(b.total_value || 0).toFixed(2)}
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
