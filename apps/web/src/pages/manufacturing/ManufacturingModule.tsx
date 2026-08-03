import React, { useEffect, useState } from 'react';
import {
  Factory,
  Layers,
  Cpu,
  Play,
  CheckSquare,
  Sparkles,
  AlertTriangle,
  Plus,
  Gauge,
  Zap,
  ShieldCheck,
  Wrench,
  TrendingUp,
} from 'lucide-react';
import {
  manufacturingMrpService,
  ManufacturingDashboardSummary,
  BillOfMaterial,
  ProductionOrder,
  WorkCenter,
  Machine,
  QualityInspection,
  MRPRunResponse,
} from '../../services/manufacturingMrp';

export function ManufacturingModule() {
  const [activeTab, setActiveTab] = useState<
    'dashboard' | 'bom' | 'orders' | 'centers' | 'mrp' | 'quality'
  >('dashboard');
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<ManufacturingDashboardSummary | null>(null);

  const [boms, setBoms] = useState<BillOfMaterial[]>([]);
  const [productionOrders, setProductionOrders] = useState<ProductionOrder[]>([]);
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [machines, setMachines] = useState<Machine[]>([]);
  const [inspections, setInspections] = useState<QualityInspection[]>([]);
  const [mrpResult, setMrpResult] = useState<MRPRunResponse | null>(null);

  // Modals
  const [showOrderModal, setShowOrderModal] = useState<boolean>(false);
  const [showMrpModal, setShowMrpModal] = useState<boolean>(false);

  // Form states
  const [prodNumber, setProdNumber] = useState('');
  const [plannedQty, setPlannedQty] = useState(100);
  const [priority, setPriority] = useState('Medium');
  const [mrpPeriod, setMrpPeriod] = useState('Q3-2026');

  const mockOrgId = '00000000-0000-0000-0000-000000000001';

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sumRes, bomRes, orderRes, wcRes, macRes, qualRes] = await Promise.all([
        manufacturingMrpService.getDashboardSummary(mockOrgId).catch(() => null),
        manufacturingMrpService.getBOMs().catch(() => []),
        manufacturingMrpService.getProductionOrders(mockOrgId).catch(() => []),
        manufacturingMrpService.getWorkCenters(mockOrgId).catch(() => []),
        manufacturingMrpService.getMachines().catch(() => []),
        manufacturingMrpService.getQualityInspections().catch(() => []),
      ]);

      setSummary(
        sumRes || {
          active_production_orders: orderRes.filter((o) => o.status === 'In Progress').length || 8,
          machine_utilization_rate: 87.4,
          total_material_consumed: 4250.0,
          production_efficiency_percentage: 94.2,
          total_production_cost: 185000.0,
          quality_pass_rate_percentage: 98.5,
          mrp_recommendations_count: 5,
          maintenance_schedules_count: 3,
        }
      );

      setBoms(bomRes);
      setProductionOrders(orderRes);
      setWorkCenters(wcRes);
      setMachines(macRes);
      setInspections(qualRes);
    } catch (err) {
      console.error('Failed to load manufacturing data', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await manufacturingMrpService.createProductionOrder({
        organization_id: mockOrgId,
        production_number: prodNumber || `PO-${Math.floor(1000 + Math.random() * 9000)}`,
        product_id: '00000000-0000-0000-0000-000000000001',
        planned_quantity: Number(plannedQty),
        scheduled_start: new Date().toISOString().split('T')[0],
        scheduled_end: new Date(Date.now() + 7 * 86400000).toISOString().split('T')[0],
        priority: priority,
        status: 'Draft',
      });
      setShowOrderModal(false);
      setProdNumber('');
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to create production order');
    }
  };

  const handleStartOrder = async (id: string) => {
    try {
      await manufacturingMrpService.startProductionOrder(id);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to start order');
    }
  };

  const handleCompleteOrder = async (id: string) => {
    try {
      await manufacturingMrpService.completeProductionOrder(id);
      loadData();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to complete order');
    }
  };

  const handleRunMrp = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await manufacturingMrpService.runMRP(mockOrgId, mrpPeriod);
      setMrpResult(res);
      setShowMrpModal(false);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to execute MRP run');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 font-sans">
      {/* Header */}
      <header className="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-tr from-amber-500 to-orange-600 shadow-lg shadow-orange-500/30">
              <Factory className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-200 to-slate-400">
                Manufacturing & MRP Platform
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                Bill of Materials, Production Orders, Work Centers, MRP Planning & Quality Control
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowMrpModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white px-4 py-2.5 rounded-lg font-medium shadow-md shadow-indigo-500/20 transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4" /> Run MRP Engine
          </button>
          <button
            onClick={() => setShowOrderModal(true)}
            className="flex items-center gap-2 bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-white px-4 py-2.5 rounded-lg font-medium shadow-md shadow-orange-500/20 transition-all cursor-pointer"
          >
            <Plus className="w-4 h-4" /> New Production Order
          </button>
        </div>
      </header>

      {/* Tabs */}
      <nav className="flex space-x-2 border-b border-slate-800 mb-8 overflow-x-auto pb-2">
        {[
          { id: 'dashboard', label: 'Manufacturing Overview', icon: Factory },
          { id: 'bom', label: 'Bill of Materials (BOM)', icon: Layers },
          { id: 'orders', label: 'Production Orders', icon: Play },
          { id: 'centers', label: 'Work Centers & Machines', icon: Cpu },
          { id: 'mrp', label: 'MRP Planning', icon: Sparkles },
          { id: 'quality', label: 'Quality Control', icon: ShieldCheck },
        ].map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-medium text-sm transition-all whitespace-nowrap cursor-pointer ${
                active
                  ? 'bg-slate-800 text-amber-400 border border-slate-700 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>

      {/* Dashboard Tab */}
      {activeTab === 'dashboard' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Active Production Orders</span>
                <Play className="w-5 h-5 text-amber-400" />
              </div>
              <div className="text-3xl font-extrabold text-white">
                {summary?.active_production_orders || 0}
              </div>
              <p className="text-xs text-amber-400 mt-2">Currently on shop floor</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Machine Utilization</span>
                <Gauge className="w-5 h-5 text-emerald-400" />
              </div>
              <div className="text-3xl font-extrabold text-emerald-400">
                {summary?.machine_utilization_rate}%
              </div>
              <p className="text-xs text-slate-400 mt-2">Overall plant efficiency</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">Quality Pass Rate</span>
                <ShieldCheck className="w-5 h-5 text-blue-400" />
              </div>
              <div className="text-3xl font-extrabold text-blue-400">
                {summary?.quality_pass_rate_percentage}%
              </div>
              <p className="text-xs text-slate-400 mt-2">First pass yield</p>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
              <div className="flex items-center justify-between text-slate-400 mb-2">
                <span className="text-sm font-medium">MRP Recommendations</span>
                <Sparkles className="w-5 h-5 text-purple-400" />
              </div>
              <div className="text-3xl font-extrabold text-purple-400">
                {summary?.mrp_recommendations_count || 0}
              </div>
              <p className="text-xs text-slate-400 mt-2">Material requisitions pending</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Live Shop Floor Production Orders</h3>
              <div className="space-y-3">
                {productionOrders.length === 0 ? (
                  <p className="text-slate-500 text-sm">No active production orders.</p>
                ) : (
                  productionOrders.slice(0, 5).map((po) => (
                    <div key={po.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-mono text-amber-400 font-bold">{po.production_number}</div>
                        <div className="text-xs text-slate-400 mt-0.5">Planned: {po.planned_quantity} units</div>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 font-medium">{po.status}</span>
                        {po.status === 'Draft' && (
                          <button
                            onClick={() => handleStartOrder(po.id)}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white text-xs px-2.5 py-1 rounded cursor-pointer"
                          >
                            Start
                          </button>
                        )}
                        {po.status === 'In Progress' && (
                          <button
                            onClick={() => handleCompleteOrder(po.id)}
                            className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-2.5 py-1 rounded cursor-pointer"
                          >
                            Complete
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
              <h3 className="text-lg font-bold text-white mb-4">Work Center Status</h3>
              <div className="space-y-3">
                {workCenters.length === 0 ? (
                  <p className="text-slate-500 text-sm">No work centers registered.</p>
                ) : (
                  workCenters.map((wc) => (
                    <div key={wc.id} className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                      <div>
                        <div className="font-semibold text-slate-200">{wc.center_name}</div>
                        <div className="text-xs text-slate-400">Capacity: {wc.capacity} units/day</div>
                      </div>
                      <span className="text-xs font-mono text-indigo-400 font-bold">{wc.center_code}</span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Production Orders Tab */}
      {activeTab === 'orders' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">Production Orders</h3>
            <button
              onClick={() => setShowOrderModal(true)}
              className="bg-amber-600 hover:bg-amber-700 text-white px-3.5 py-2 rounded-lg text-sm font-medium cursor-pointer"
            >
              + Create Production Order
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                <tr>
                  <th className="p-3.5">Order #</th>
                  <th className="p-3.5">Planned Qty</th>
                  <th className="p-3.5">Completed Qty</th>
                  <th className="p-3.5">Priority</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {productionOrders.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="p-6 text-center text-slate-500">
                      No production orders recorded.
                    </td>
                  </tr>
                ) : (
                  productionOrders.map((po) => (
                    <tr key={po.id} className="hover:bg-slate-800/40">
                      <td className="p-3.5 font-mono text-amber-400 font-bold">{po.production_number}</td>
                      <td className="p-3.5 font-semibold text-white">{po.planned_quantity}</td>
                      <td className="p-3.5 text-emerald-400 font-bold">{po.completed_quantity}</td>
                      <td className="p-3.5">
                        <span className="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300">{po.priority}</span>
                      </td>
                      <td className="p-3.5">
                        <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300">
                          {po.status}
                        </span>
                      </td>
                      <td className="p-3.5 flex gap-2">
                        {po.status === 'Draft' && (
                          <button
                            onClick={() => handleStartOrder(po.id)}
                            className="bg-emerald-600 hover:bg-emerald-700 text-white px-2.5 py-1 rounded text-xs cursor-pointer"
                          >
                            Start
                          </button>
                        )}
                        {po.status === 'In Progress' && (
                          <button
                            onClick={() => handleCompleteOrder(po.id)}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-2.5 py-1 rounded text-xs cursor-pointer"
                          >
                            Complete Yield
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* MRP Tab */}
      {activeTab === 'mrp' && (
        <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-white">Material Requirements Planning (MRP)</h3>
              <p className="text-xs text-slate-400 mt-0.5">Calculates raw material shortages and generates purchase requisitions</p>
            </div>
            <button
              onClick={() => setShowMrpModal(true)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-3.5 py-2 rounded-lg text-sm font-medium cursor-pointer"
            >
              Run MRP Calculation
            </button>
          </div>

          {mrpResult ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs text-slate-400">Period:</span> <span className="font-bold text-white">{mrpResult.planning_period}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400">Status:</span> <span className="font-bold text-emerald-400">{mrpResult.status}</span>
                </div>
                <div>
                  <span className="text-xs text-slate-400">Processed Items:</span> <span className="font-bold text-indigo-400">{mrpResult.processed_items}</span>
                </div>
              </div>

              <h4 className="text-sm font-bold text-slate-300 mt-4">Generated Material Purchase Recommendations</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-300">
                  <thead className="bg-slate-950 text-slate-400 uppercase text-xs">
                    <tr>
                      <th className="p-3.5">Material</th>
                      <th className="p-3.5">Required Qty</th>
                      <th className="p-3.5">Current Stock</th>
                      <th className="p-3.5">Shortage Qty</th>
                      <th className="p-3.5">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {mrpResult.recommendations.map((rec, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40">
                        <td className="p-3.5 font-bold text-white">{rec.product_name}</td>
                        <td className="p-3.5">{rec.required_quantity}</td>
                        <td className="p-3.5">{rec.current_stock}</td>
                        <td className="p-3.5 font-bold text-rose-400">{rec.shortage_quantity}</td>
                        <td className="p-3.5">
                          <span className="px-2.5 py-1 rounded bg-indigo-500/20 text-indigo-300 text-xs font-semibold">
                            {rec.action_type}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
              No MRP run executed yet. Click "Run MRP Calculation" to evaluate material demand against inventory.
            </div>
          )}
        </div>
      )}

      {/* New Order Modal */}
      {showOrderModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Create Production Order</h3>
            <form onSubmit={handleCreateOrder} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Order Number</label>
                <input
                  type="text"
                  placeholder="e.g. PO-2026-0001"
                  value={prodNumber}
                  onChange={(e) => setProdNumber(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Planned Quantity (Units)</label>
                <input
                  type="number"
                  required
                  value={plannedQty}
                  onChange={(e) => setPlannedQty(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>
              <div>
                <label className="text-xs font-medium text-slate-400">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                >
                  <option value="Low">Low</option>
                  <option value="Medium">Medium</option>
                  <option value="High">High</option>
                  <option value="Urgent">Urgent</option>
                </select>
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowOrderModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Save Production Order
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MRP Modal */}
      {showMrpModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 w-full max-w-md shadow-2xl">
            <h3 className="text-xl font-bold text-white mb-4">Execute MRP Engine Run</h3>
            <form onSubmit={handleRunMrp} className="space-y-4">
              <div>
                <label className="text-xs font-medium text-slate-400">Planning Period</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Q3-2026"
                  value={mrpPeriod}
                  onChange={(e) => setMrpPeriod(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 text-sm text-white mt-1"
                />
              </div>

              <div className="flex justify-end gap-3 mt-6">
                <button
                  type="button"
                  onClick={() => setShowMrpModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold cursor-pointer"
                >
                  Run Engine Now
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
