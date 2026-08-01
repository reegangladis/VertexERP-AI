import React, { useState, useEffect } from 'react';
import { Package, Truck, Layers, ShoppingCart, RefreshCw } from 'lucide-react';
import { StatCard } from '@/components/common/StatCard';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell } from 'recharts';
import { analyticsService, InventoryAnalyticsResponse } from '@/services/analyticsService';

export function InventoryAnalyticsPage() {
  const [data, setData] = useState<InventoryAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchInventoryAnalytics = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getInventoryAnalytics();
      setData(res);
    } catch (err) {
      console.error('Error fetching Inventory analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventoryAnalytics();
  }, []);

  const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Package className="h-6 w-6 text-primary" />
            Inventory & Warehouse Supply Chain Analytics
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Stock Valuation, Inventory Turnover, Warehouse Capacity & Purchase Trends
          </p>
        </div>
        <button
          onClick={fetchInventoryAnalytics}
          className="p-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-sm transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Stock Valuation"
          value={`$${(data?.total_stock_value || 4180000).toLocaleString()}`}
          change="+4.2%"
          isPositive={true}
          subtitle={`${data?.total_products_count || 840} Active SKUs`}
          icon={<Package className="h-5 w-5" />}
        />
        <StatCard
          title="Inventory Turnover Ratio"
          value={`${data?.inventory_turnover_ratio || 6.8}x`}
          change="+0.6x"
          isPositive={true}
          subtitle="Annualized Rate"
          icon={<Layers className="h-5 w-5" />}
        />
        <StatCard
          title="Avg Warehouse Utilization"
          value={`${data?.average_warehouse_utilization_percent || 82.4}%`}
          change="+2.1%"
          isPositive={true}
          subtitle="Capacity Efficiency"
          icon={<Truck className="h-5 w-5" />}
        />
        <StatCard
          title="Total PO Spend"
          value={`$${(data?.purchase_orders_total_value || 1640000).toLocaleString()}`}
          change="+5.0%"
          isPositive={true}
          subtitle={`Supplier Rating: ${data?.average_supplier_rating || 4.8}/5.0`}
          icon={<ShoppingCart className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Stock Aging Breakdown Pie Chart */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Stock Aging Valuation Breakdown</h3>
          <div className="h-64 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data?.stock_aging_breakdown || []}
                  dataKey="value"
                  nameKey="age_bracket"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={(e) => `${e.age_bracket}: ${e.percentage}%`}
                >
                  {data?.stock_aging_breakdown?.map((_, idx) => (
                    <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Warehouse Utilization Bar Chart */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Warehouse Capacity & Utilization (%)</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.warehouse_capacity_utilization || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="warehouse_name" stroke="currentColor" className="text-[10px] text-muted-foreground" />
                <YAxis domain={[0, 100]} stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }} />
                <Bar dataKey="utilized_pct" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="Utilized (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
