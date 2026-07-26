import React, { useEffect, useState } from 'react';
import { Play, Plus, Clock, AlertCircle, CheckCircle2, Calendar, Search } from 'lucide-react';
import { manufacturingService, ProductionOrder } from '@/services/manufacturingService';

export function ProductionOrdersPage() {
  const [orders, setOrders] = useState<ProductionOrder[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getProductionOrders(statusFilter);
      setOrders(data);
    } catch (err) {
      console.error('Error fetching production orders', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [statusFilter]);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Play className="h-6 w-6 text-primary" />
            Production Orders & Scheduling
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Order Status Lifecycle, Material Reservation Check, Completion Tracking & Priority Dispatch
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          New Production Order
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {['', 'PLANNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                statusFilter === st
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-background border-border text-muted-foreground hover:bg-muted'
              }`}
            >
              {st === '' ? 'All Orders' : st.replace('_', ' ')}
            </button>
          ))}
        </div>

        {/* Table */}
        <div className="border border-border rounded-lg overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted/50 border-b border-border font-medium text-muted-foreground uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3">Order Number</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Planned Qty</th>
                <th className="px-4 py-3">Completed Qty</th>
                <th className="px-4 py-3">Scrap Qty</th>
                <th className="px-4 py-3">Planned Start / End</th>
                <th className="px-4 py-3 text-right">Progress</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 text-foreground">
              {orders.map((po) => {
                const progressPct = po.planned_quantity > 0 ? Math.min(round((po.completed_quantity / po.planned_quantity) * 100), 100) : 0;
                return (
                  <tr key={po.id} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-mono font-bold text-foreground">{po.order_number}</td>
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                          po.status === 'COMPLETED'
                            ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                            : po.status === 'IN_PROGRESS'
                            ? 'bg-blue-500/10 text-blue-500 border border-blue-500/20'
                            : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                        }`}
                      >
                        {po.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-semibold">{po.priority}</td>
                    <td className="px-4 py-3 font-mono font-medium">{po.planned_quantity} PCS</td>
                    <td className="px-4 py-3 font-mono text-emerald-500 font-semibold">{po.completed_quantity} PCS</td>
                    <td className="px-4 py-3 font-mono text-red-400">{po.scrap_quantity} PCS</td>
                    <td className="px-4 py-3 text-muted-foreground">{po.planned_start_date} to {po.planned_end_date}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <span className="font-semibold text-xs">{progressPct}%</span>
                        <div className="w-16 bg-secondary h-1.5 rounded-full overflow-hidden">
                          <div className="bg-primary h-full rounded-full" style={{ width: `${progressPct}%` }} />
                        </div>
                      </div>
                    </td>
                  </tr>
                );
              })}

              {orders.length === 0 && !loading && (
                <tr>
                  <td colSpan={8} className="px-4 py-8 text-center text-muted-foreground">
                    No production orders found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function round(val: number) {
  return Math.round(val);
}
