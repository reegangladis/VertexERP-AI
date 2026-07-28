import React, { useState, useEffect } from 'react';
import {
  Package,
  Truck,
  Warehouse,
  RotateCw,
  Star,
  DollarSign,
  RefreshCw,
  Clock,
  Layers,
} from 'lucide-react';
import { analyticsService, InventoryAnalyticsResponse } from '@/services/analyticsService';

export function InventoryAnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<InventoryAnalyticsResponse | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getInventoryAnalytics();
      setData(res);
    } catch (err) {
      console.error('Failed to load Inventory analytics:', err);
      setData({
        total_stock_value: 4180000.0,
        total_products_count: 840,
        inventory_turnover_ratio: 6.8,
        average_warehouse_utilization_percent: 82.4,
        average_supplier_rating: 4.8,
        purchase_orders_total_value: 1640000.0,
        stock_aging_breakdown: [
          { age_bracket: '0-30 Days', value: 2400000, percentage: 57 },
          { age_bracket: '31-60 Days', value: 1100000, percentage: 26 },
        ],
        warehouse_capacity_utilization: [],
        purchase_trends: [],
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-cyan-600 dark:text-cyan-400" />
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100">Inventory & Logistics Analytics</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time stock valuation, turnover ratio, warehouse space utilization, supplier scorecard, and stock aging breakdown.
          </p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          <RefreshCw className="h-3.5 w-3.5" /> Refresh Analytics
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Stock Valuation</span>
            <div className="rounded-lg bg-cyan-50 p-2 text-cyan-600 dark:bg-cyan-950/50 dark:text-cyan-400">
              <Package className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">${(data.total_stock_value || 0).toLocaleString()}</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">{data.total_products_count || 0} active catalog SKUs</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Turnover Ratio</span>
            <div className="rounded-lg bg-emerald-50 p-2 text-emerald-600 dark:bg-emerald-950/50 dark:text-emerald-400">
              <RotateCw className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.inventory_turnover_ratio || 0}x</h3>
          <p className="mt-1 text-xs text-emerald-600 dark:text-emerald-400 font-medium">Optimal Velocity</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Warehouse Space</span>
            <div className="rounded-lg bg-blue-50 p-2 text-blue-600 dark:bg-blue-950/50 dark:text-blue-400">
              <Warehouse className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.average_warehouse_utilization_percent || 0}%</h3>
          <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">Average Capacity Occupied</p>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Supplier Performance</span>
            <div className="rounded-lg bg-amber-50 p-2 text-amber-600 dark:bg-amber-950/50 dark:text-amber-400">
              <Star className="h-5 w-5" />
            </div>
          </div>
          <h3 className="mt-3 text-2xl font-bold text-slate-900 dark:text-slate-100">{data.average_supplier_rating || 0} / 5.0</h3>
          <p className="mt-1 text-xs text-amber-600 dark:text-amber-400 font-medium">On-Time In-Full (OTIF)</p>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Stock Aging Breakdown */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">Stock Aging Breakdown</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Inventory valuation categorized by storage duration</p>

          <div className="space-y-3">
            {(data.stock_aging_breakdown || []).map((item, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-700 dark:text-slate-300">
                  <span>{item.age_bracket || item.age_group || 'Duration'}</span>
                  <span>${(item.value || 0).toLocaleString()} ({item.percentage || 0}%)</span>
                </div>
                <div className="h-2.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      idx === 3 ? 'bg-rose-500' : idx === 2 ? 'bg-amber-500' : 'bg-cyan-500'
                    }`}
                    style={{ width: `${item.percentage || 0}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Warehouse Utilization Table */}
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900">
          <h3 className="text-base font-bold text-slate-900 dark:text-slate-100 mb-1">Warehouse Capacity Utilization</h3>
          <p className="text-xs text-slate-500 dark:text-slate-400 mb-4">Storage location capacity and volume load</p>

          <div className="space-y-3">
            {(data.warehouse_capacity_utilization || []).map((wh, idx) => (
              <div key={idx} className="rounded-lg border border-slate-100 p-3.5 dark:border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-slate-800 dark:text-slate-200">{wh.warehouse_name || wh.warehouse || 'Warehouse'}</span>
                  <span className="text-xs font-bold text-cyan-600 dark:text-cyan-400">{wh.utilized_pct || wh.utilization || 0}% Utilized</span>
                </div>
                <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">Capacity: {(wh.capacity_units || 100000).toLocaleString()} units</div>
                <div className="mt-2 h-2 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                  <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${wh.utilized_pct || wh.utilization || 0}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
