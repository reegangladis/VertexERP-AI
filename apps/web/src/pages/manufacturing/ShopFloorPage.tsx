import React, { useEffect, useState } from 'react';
import { Activity, Plus, Play, CheckCircle, Clock, X, User } from 'lucide-react';
import { manufacturingService, ProductionOrder, WorkCenter, Machine } from '@/services/manufacturingService';

export function ShopFloorPage() {
  const [orders, setOrders] = useState<ProductionOrder[]>([]);
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Modal
  const [showLogModal, setShowLogModal] = useState<boolean>(false);
  const [selectedOrderId, setSelectedOrderId] = useState<string>('');
  const [operatorName, setOperatorName] = useState<string>('Operator Mark');
  const [qtyProduced, setQtyProduced] = useState<number>(25);
  const [qtyScrap, setQtyScrap] = useState<number>(1);
  const [notes, setNotes] = useState<string>('');

  const fetchShopFloorData = async () => {
    setLoading(true);
    try {
      const [poList, wcList, mList] = await Promise.all([
        manufacturingService.getProductionOrders('IN_PROGRESS'),
        manufacturingService.getWorkCenters(),
        manufacturingService.getMachines(),
      ]);
      setOrders(poList);
      setWorkCenters(wcList);
      setMachines(mList);
      if (poList.length > 0) setSelectedOrderId(poList[0].id);
    } catch (err) {
      console.error('Error fetching shop floor data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchShopFloorData();
  }, []);

  const handleLogSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedOrderId) return;
    try {
      await manufacturingService.logShopFloorProgress({
        production_order_id: selectedOrderId,
        operator_name: operatorName,
        quantity_produced: qtyProduced,
        scrap_quantity: qtyScrap,
        notes,
      });
      setShowLogModal(false);
      setQtyProduced(0);
      setQtyScrap(0);
      fetchShopFloorData();
    } catch (err) {
      console.error('Error logging shop floor progress', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Activity className="h-6 w-6 text-primary" />
            Shop Floor Execution & Work Orders
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Operator Console, Real-time Production Logging, Machine Utilization & Scrap Recording
          </p>
        </div>
        <button
          onClick={() => setShowLogModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Log Production Output
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {orders.map((po) => {
          const progressPct = po.planned_quantity > 0 ? Math.min(Math.round((po.completed_quantity / po.planned_quantity) * 100), 100) : 0;
          return (
            <div key={po.id} className="p-5 border border-border rounded-xl bg-card space-y-4 shadow-sm hover:border-primary/50 transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-primary/10 text-primary font-bold">
                    {po.status}
                  </span>
                  <h3 className="text-base font-bold text-foreground font-mono mt-1">{po.order_number}</h3>
                </div>
                <button
                  onClick={() => {
                    setSelectedOrderId(po.id);
                    setShowLogModal(true);
                  }}
                  className="px-3 py-1 text-xs font-semibold bg-emerald-600 text-white rounded-lg shadow hover:bg-emerald-700 transition-colors"
                >
                  + Log Qty
                </button>
              </div>

              <div className="space-y-1.5 text-xs">
                <div className="flex justify-between text-muted-foreground">
                  <span>Planned: {po.planned_quantity} PCS</span>
                  <span className="text-emerald-500 font-bold font-mono">{po.completed_quantity} PCS Completed</span>
                </div>
                <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                  <div className="bg-primary h-full rounded-full" style={{ width: `${progressPct}%` }} />
                </div>
                <div className="flex justify-between text-[11px] text-muted-foreground pt-1">
                  <span>Scrap: <strong className="text-red-400 font-mono">{po.scrap_quantity} PCS</strong></span>
                  <span>Progress: <strong className="text-foreground">{progressPct}%</strong></span>
                </div>
              </div>

              <div className="border-t border-border/60 pt-3 text-xs space-y-1 text-muted-foreground">
                <div className="flex items-center gap-1.5">
                  <Clock className="h-3.5 w-3.5 text-primary" />
                  <span>Start: {po.planned_start_date} | End: {po.planned_end_date}</span>
                </div>
              </div>
            </div>
          );
        })}

        {orders.length === 0 && !loading && (
          <div className="col-span-full text-center py-16 text-muted-foreground text-xs">
            No active In-Progress Production Orders on the shop floor console.
          </div>
        )}
      </div>

      {/* LOG OUTPUT MODAL */}
      {showLogModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Log Shop Floor Output</h3>
              <button onClick={() => setShowLogModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleLogSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Production Order</label>
                <select
                  value={selectedOrderId}
                  onChange={(e) => setSelectedOrderId(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono"
                >
                  {orders.map((po) => (
                    <option key={po.id} value={po.id}>
                      {po.order_number} ({po.completed_quantity}/{po.planned_quantity} PCS)
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Operator Name</label>
                <input
                  type="text"
                  required
                  value={operatorName}
                  onChange={(e) => setOperatorName(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Produced Qty (PCS)</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={qtyProduced}
                    onChange={(e) => setQtyProduced(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Scrap Qty (PCS)</label>
                  <input
                    type="number"
                    min="0"
                    value={qtyScrap}
                    onChange={(e) => setQtyScrap(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Notes</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Batch #B-9002 completed on Shift 1..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowLogModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold shadow hover:bg-primary/90"
                >
                  Submit Log
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
