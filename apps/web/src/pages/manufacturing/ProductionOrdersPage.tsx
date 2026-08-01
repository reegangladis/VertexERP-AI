import React, { useEffect, useState } from 'react';
import { Play, Plus, Clock, AlertCircle, CheckCircle2, Calendar, Search, ShieldCheck, DollarSign, X, Edit, Trash2 } from 'lucide-react';
import { manufacturingService, ProductionOrder, ProductionCostSummaryResponse, MaterialReservationResponse } from '@/services/manufacturingService';

export function ProductionOrdersPage() {
  const [orders, setOrders] = useState<ProductionOrder[]>([]);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showCostModal, setShowCostModal] = useState<boolean>(false);
  const [showReservationModal, setShowReservationModal] = useState<boolean>(false);

  const [selectedCostSummary, setSelectedCostSummary] = useState<ProductionCostSummaryResponse | null>(null);
  const [selectedReservation, setSelectedReservation] = useState<MaterialReservationResponse | null>(null);

  // Form State
  const [orderNumber, setOrderNumber] = useState<string>('');
  const [plannedQty, setPlannedQty] = useState<number>(100);
  const [priority, setPriority] = useState<string>('MEDIUM');
  const [startDate, setStartDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState<string>(new Date(Date.now() + 86400000 * 7).toISOString().split('T')[0]);
  const [notes, setNotes] = useState<string>('');

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

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await manufacturingService.createProductionOrder({
        product_id: '00000000-0000-0000-0000-000000000100',
        order_number: orderNumber,
        planned_quantity: plannedQty,
        priority,
        planned_start_date: startDate,
        planned_end_date: endDate,
        notes,
      });
      setShowCreateModal(false);
      setOrderNumber('');
      fetchOrders();
    } catch (err) {
      console.error('Error creating production order', err);
    }
  };

  const handleReserveMaterials = async (orderId: string) => {
    try {
      const res = await manufacturingService.reserveMaterials(orderId);
      setSelectedReservation(res);
      setShowReservationModal(true);
      fetchOrders();
    } catch (err) {
      console.error('Error reserving materials', err);
    }
  };

  const handleViewCosts = async (orderId: string) => {
    try {
      const costSummary = await manufacturingService.getCostSummary(orderId);
      setSelectedCostSummary(costSummary);
      setShowCostModal(true);
    } catch (err) {
      console.error('Error fetching cost summary', err);
    }
  };

  const handleDelete = async (orderId: string) => {
    if (!confirm('Are you sure you want to delete this production order?')) return;
    try {
      await manufacturingService.deleteProductionOrder(orderId);
      fetchOrders();
    } catch (err) {
      console.error('Error deleting production order', err);
    }
  };

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
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
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
                <th className="px-4 py-3">Reservation</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Planned / Completed</th>
                <th className="px-4 py-3">Dates</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 text-foreground">
              {orders.map((po) => {
                const progressPct = po.planned_quantity > 0 ? Math.min(Math.round((po.completed_quantity / po.planned_quantity) * 100), 100) : 0;
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
                    <td className="px-4 py-3">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-mono font-semibold ${
                          po.material_reservation_status === 'FULL'
                            ? 'bg-emerald-500/10 text-emerald-500'
                            : po.material_reservation_status === 'PARTIAL'
                            ? 'bg-amber-500/10 text-amber-500'
                            : 'bg-muted text-muted-foreground'
                        }`}
                      >
                        {po.material_reservation_status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-semibold">{po.priority}</td>
                    <td className="px-4 py-3">
                      <div className="space-y-1">
                        <div className="font-mono text-muted-foreground">{po.completed_quantity} / {po.planned_quantity} PCS</div>
                        <div className="w-24 bg-secondary h-1.5 rounded-full overflow-hidden">
                          <div className="bg-primary h-full rounded-full" style={{ width: `${progressPct}%` }} />
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-muted-foreground">{po.planned_start_date} to {po.planned_end_date}</td>
                    <td className="px-4 py-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => handleReserveMaterials(po.id)}
                          className="px-2 py-1 text-[11px] font-medium border border-border rounded hover:bg-muted flex items-center gap-1"
                          title="Reserve Materials"
                        >
                          <ShieldCheck className="h-3.5 w-3.5 text-primary" />
                          Reserve
                        </button>
                        <button
                          onClick={() => handleViewCosts(po.id)}
                          className="px-2 py-1 text-[11px] font-medium border border-border rounded hover:bg-muted flex items-center gap-1"
                          title="View Cost Summary"
                        >
                          <DollarSign className="h-3.5 w-3.5 text-emerald-500" />
                          Cost
                        </button>
                        <button
                          onClick={() => handleDelete(po.id)}
                          className="p-1 text-red-500 hover:bg-red-500/10 rounded"
                          title="Delete Order"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}

              {orders.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                    No production orders found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE PRODUCTION ORDER MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Schedule Production Order</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Order Number</label>
                <input
                  type="text"
                  required
                  placeholder="PO-2026-001"
                  value={orderNumber}
                  onChange={(e) => setOrderNumber(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Planned Quantity</label>
                  <input
                    type="number"
                    min="1"
                    required
                    value={plannedQty}
                    onChange={(e) => setPlannedQty(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Priority</label>
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="LOW">LOW</option>
                    <option value="MEDIUM">MEDIUM</option>
                    <option value="HIGH">HIGH</option>
                    <option value="URGENT">URGENT</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Planned Start</label>
                  <input
                    type="date"
                    required
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Planned End</label>
                  <input
                    type="date"
                    required
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
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
                  placeholder="Special customer requirement notes..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold shadow hover:bg-primary/90"
                >
                  Create Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* COST SUMMARY MODAL */}
      {showCostModal && selectedCostSummary && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-emerald-500" />
                Production Order Cost Summary & Variance
              </h3>
              <button onClick={() => setShowCostModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3 p-3 bg-muted/40 rounded-lg">
                <div>
                  <span className="text-muted-foreground">Order Number:</span>
                  <p className="font-bold text-foreground font-mono">{selectedCostSummary.order_number}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Unit Cost:</span>
                  <p className="font-bold text-emerald-500 font-mono">${selectedCostSummary.unit_actual_cost.toFixed(2)} / unit</p>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-2 text-center">
                <div className="p-2 border border-border rounded bg-card">
                  <p className="text-[10px] text-muted-foreground">Material</p>
                  <p className="font-bold font-mono text-foreground mt-1">${selectedCostSummary.material_cost.toFixed(2)}</p>
                </div>
                <div className="p-2 border border-border rounded bg-card">
                  <p className="text-[10px] text-muted-foreground">Labor</p>
                  <p className="font-bold font-mono text-foreground mt-1">${selectedCostSummary.labor_cost.toFixed(2)}</p>
                </div>
                <div className="p-2 border border-border rounded bg-card">
                  <p className="text-[10px] text-muted-foreground">Machine</p>
                  <p className="font-bold font-mono text-foreground mt-1">${selectedCostSummary.machine_cost.toFixed(2)}</p>
                </div>
                <div className="p-2 border border-border rounded bg-card">
                  <p className="text-[10px] text-muted-foreground">Overhead</p>
                  <p className="font-bold font-mono text-foreground mt-1">${selectedCostSummary.overhead_cost.toFixed(2)}</p>
                </div>
              </div>

              <div className="p-3 border border-border rounded-lg flex items-center justify-between">
                <div>
                  <p className="font-semibold text-foreground">Total Actual Cost</p>
                  <p className="text-muted-foreground text-[11px]">Estimated: ${selectedCostSummary.estimated_total_cost.toFixed(2)}</p>
                </div>
                <div className="text-right">
                  <p className="text-base font-bold font-mono text-foreground">${selectedCostSummary.total_actual_cost.toFixed(2)}</p>
                  <span className={`text-[11px] font-bold ${selectedCostSummary.cost_variance > 0 ? 'text-red-500' : 'text-emerald-500'}`}>
                    Variance: {selectedCostSummary.cost_variance > 0 ? '+' : ''}${selectedCostSummary.cost_variance.toFixed(2)} ({selectedCostSummary.cost_variance_percent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowCostModal(false)}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold"
              >
                Done
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MATERIAL RESERVATION MODAL */}
      {showReservationModal && selectedReservation && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <ShieldCheck className="h-5 w-5 text-primary" />
                Material Reservation Result
              </h3>
              <button onClick={() => setShowReservationModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between p-3 bg-muted/40 rounded-lg">
                <span className="font-medium text-foreground">Reservation Status</span>
                <span className="px-2.5 py-1 rounded font-bold font-mono bg-emerald-500/10 text-emerald-500">
                  {selectedReservation.material_reservation_status}
                </span>
              </div>

              <p className="text-muted-foreground">
                Allocated {selectedReservation.allocated_items.length} component line item(s).
                {selectedReservation.shortages.length > 0 && ` Shortages found in ${selectedReservation.shortages.length} items.`}
              </p>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowReservationModal(false)}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
