import React, { useEffect, useState } from 'react';
import { Layers, Plus, CheckCircle, Calculator, Search, ChevronRight, FileText, Trash2, Edit, X } from 'lucide-react';
import { manufacturingService, BillOfMaterial, BOMCostRollupResponse } from '@/services/manufacturingService';

export function BillOfMaterialsPage() {
  const [boms, setBoms] = useState<BillOfMaterial[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedBom, setSelectedBom] = useState<BillOfMaterial | null>(null);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showCostModal, setShowCostModal] = useState<boolean>(false);
  const [costRollupData, setCostRollupData] = useState<BOMCostRollupResponse | null>(null);

  // Form State
  const [code, setCode] = useState<string>('');
  const [version, setVersion] = useState<string>('1.0');
  const [baseQuantity, setBaseQuantity] = useState<number>(1);
  const [notes, setNotes] = useState<string>('');
  const [items, setItems] = useState<Array<{ component_product_id: string; quantity: number; unit_name: string; unit_cost: number; scrap_factor_percent: number }>>([
    { component_product_id: '00000000-0000-0000-0000-000000000001', quantity: 2, unit_name: 'PCS', unit_cost: 15.0, scrap_factor_percent: 2.0 },
  ]);

  const fetchBoms = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getBOMs(search);
      setBoms(data);
      if (data.length > 0 && !selectedBom) {
        setSelectedBom(data[0]);
      }
    } catch (err) {
      console.error('Error fetching BOMs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBoms();
  }, [search]);

  const handleApprove = async (id: string) => {
    try {
      const updated = await manufacturingService.approveBOM(id);
      setSelectedBom(updated);
      fetchBoms();
    } catch (err) {
      console.error('BOM approval failed', err);
    }
  };

  const handleCostRollup = async (id: string) => {
    try {
      const rollup = await manufacturingService.calculateCostRollup(id);
      setCostRollupData(rollup);
      setShowCostModal(true);
      fetchBoms();
    } catch (err) {
      console.error('Cost Rollup failed', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this BOM?')) return;
    try {
      await manufacturingService.deleteBOM(id);
      setSelectedBom(null);
      fetchBoms();
    } catch (err) {
      console.error('Delete BOM failed', err);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const newBom = await manufacturingService.createBOM({
        product_id: '00000000-0000-0000-0000-000000000100', // Default product ID fallback
        code,
        version,
        base_quantity: baseQuantity,
        notes,
        items: items as any,
      });
      setShowCreateModal(false);
      setCode('');
      setNotes('');
      fetchBoms();
      setSelectedBom(newBom);
    } catch (err) {
      console.error('Error creating BOM', err);
    }
  };

  const addItemRow = () => {
    setItems([...items, { component_product_id: '00000000-0000-0000-0000-000000000001', quantity: 1, unit_name: 'PCS', unit_cost: 10.0, scrap_factor_percent: 0.0 }]);
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Layers className="h-6 w-6 text-primary" />
            Multi-Level Bill of Materials (BOM)
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Component Hierarchy, Versioning, Approval Workflow & Cost Rollup Engine
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Create New BOM
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* BOM Search & List */}
        <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-3 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by BOM Code or Version..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {boms.map((bom) => (
              <div
                key={bom.id}
                onClick={() => setSelectedBom(bom)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                  selectedBom?.id === bom.id
                    ? 'border-primary bg-primary/5 font-medium'
                    : 'border-border/60 hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">{bom.code}</span>
                  <span
                    className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                      bom.status === 'APPROVED'
                        ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                        : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                    }`}
                  >
                    {bom.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground mt-2">
                  <span>Version {bom.version}</span>
                  <span className="font-mono text-foreground font-semibold">${bom.total_cost?.toFixed(2) || '0.00'}</span>
                </div>
              </div>
            ))}

            {boms.length === 0 && !loading && (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No Bill of Materials found.
              </div>
            )}
          </div>
        </div>

        {/* BOM Detail & Tree View */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
          {selectedBom ? (
            <>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
                <div>
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold text-foreground">{selectedBom.code}</h2>
                    <span className="text-xs px-2.5 py-0.5 rounded-md bg-secondary text-secondary-foreground font-mono">
                      v{selectedBom.version}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Base Batch Quantity: {selectedBom.base_quantity} PCS | Total Standard Cost: ${selectedBom.total_cost?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleCostRollup(selectedBom.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-border rounded-lg hover:bg-muted transition-colors"
                  >
                    <Calculator className="h-4 w-4 text-primary" />
                    Cost Rollup
                  </button>
                  {selectedBom.status !== 'APPROVED' && (
                    <button
                      onClick={() => handleApprove(selectedBom.id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-emerald-600 text-white rounded-lg shadow hover:bg-emerald-700 transition-colors"
                    >
                      <CheckCircle className="h-4 w-4" />
                      Approve BOM
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(selectedBom.id)}
                    className="p-1.5 text-xs text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                    title="Delete BOM"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Component Items Table */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" />
                  Component Line Items ({selectedBom.items?.length || 0})
                </h3>
                <div className="border border-border rounded-lg overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-muted/50 border-b border-border font-medium text-muted-foreground uppercase tracking-wider text-[10px]">
                      <tr>
                        <th className="px-4 py-3">Component Product ID</th>
                        <th className="px-4 py-3">Quantity</th>
                        <th className="px-4 py-3">UOM</th>
                        <th className="px-4 py-3">Unit Cost</th>
                        <th className="px-4 py-3">Scrap %</th>
                        <th className="px-4 py-3 text-right">Extended Cost</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/60 text-foreground">
                      {selectedBom.items?.map((item) => (
                        <tr key={item.id || item.component_product_id} className="hover:bg-muted/30">
                          <td className="px-4 py-3 font-mono font-medium text-foreground">{item.component_product_id}</td>
                          <td className="px-4 py-3 font-mono">{item.quantity}</td>
                          <td className="px-4 py-3">{item.unit_name}</td>
                          <td className="px-4 py-3 font-mono">${item.unit_cost?.toFixed(2)}</td>
                          <td className="px-4 py-3 font-mono text-muted-foreground">{item.scrap_factor_percent}%</td>
                          <td className="px-4 py-3 font-mono text-right font-semibold text-emerald-500">
                            ${(item.extended_cost || (item.quantity * item.unit_cost * (1 + item.scrap_factor_percent / 100))).toFixed(2)}
                          </td>
                        </tr>
                      ))}

                      {(!selectedBom.items || selectedBom.items.length === 0) && (
                        <tr>
                          <td colSpan={6} className="px-4 py-6 text-center text-muted-foreground">
                            No items inside this BOM.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-16 text-muted-foreground text-xs">
              Select a Bill of Materials to inspect hierarchy and calculate cost rollups.
            </div>
          )}
        </div>
      </div>

      {/* CREATE BOM MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-xl w-full p-6 shadow-xl space-y-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Create Bill of Materials</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-foreground mb-1">BOM Code</label>
                  <input
                    type="text"
                    required
                    placeholder="BOM-PRD-100"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Version</label>
                  <input
                    type="text"
                    required
                    value={version}
                    onChange={(e) => setVersion(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Base Quantity (PCS)</label>
                <input
                  type="number"
                  min="1"
                  required
                  value={baseQuantity}
                  onChange={(e) => setBaseQuantity(Number(e.target.value))}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Notes / Engineering Note</label>
                <textarea
                  rows={2}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Assembly specification details..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              {/* Items Dynamic Inputs */}
              <div className="space-y-2 border-t border-border pt-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">Component Items</span>
                  <button type="button" onClick={addItemRow} className="text-primary hover:underline flex items-center gap-1 font-medium">
                    <Plus className="h-3.5 w-3.5" /> Add Component
                  </button>
                </div>

                {items.map((it, idx) => (
                  <div key={idx} className="grid grid-cols-4 gap-2 bg-muted/40 p-2 rounded-lg items-center">
                    <input
                      type="text"
                      placeholder="Component ID"
                      value={it.component_product_id}
                      onChange={(e) => {
                        const newIt = [...items];
                        newIt[idx].component_product_id = e.target.value;
                        setItems(newIt);
                      }}
                      className="col-span-2 px-2 py-1 bg-background border border-border rounded"
                    />
                    <input
                      type="number"
                      placeholder="Qty"
                      value={it.quantity}
                      onChange={(e) => {
                        const newIt = [...items];
                        newIt[idx].quantity = Number(e.target.value);
                        setItems(newIt);
                      }}
                      className="px-2 py-1 bg-background border border-border rounded"
                    />
                    <input
                      type="number"
                      placeholder="Unit Cost"
                      value={it.unit_cost}
                      onChange={(e) => {
                        const newIt = [...items];
                        newIt[idx].unit_cost = Number(e.target.value);
                        setItems(newIt);
                      }}
                      className="px-2 py-1 bg-background border border-border rounded"
                    />
                  </div>
                ))}
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
                  Save BOM
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* COST ROLLUP MODAL */}
      {showCostModal && costRollupData && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-lg w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Calculator className="h-5 w-5 text-primary" />
                Cost Rollup Calculation Results
              </h3>
              <button onClick={() => setShowCostModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-3 bg-muted/40 rounded-lg">
                  <p className="text-muted-foreground font-medium">Material Cost</p>
                  <p className="text-base font-bold font-mono text-emerald-500 mt-1">${costRollupData.material_cost.toFixed(2)}</p>
                </div>
                <div className="p-3 bg-muted/40 rounded-lg">
                  <p className="text-muted-foreground font-medium">Operation Cost</p>
                  <p className="text-base font-bold font-mono text-blue-500 mt-1">${costRollupData.operation_cost.toFixed(2)}</p>
                </div>
                <div className="p-3 bg-primary/10 border border-primary/20 rounded-lg">
                  <p className="text-primary font-semibold">Total Cost</p>
                  <p className="text-base font-bold font-mono text-primary mt-1">${costRollupData.total_calculated_cost.toFixed(2)}</p>
                </div>
              </div>

              <div className="border border-border rounded-lg p-3 space-y-2 max-h-48 overflow-y-auto">
                <p className="font-semibold text-foreground">Cost Breakdown Details</p>
                {costRollupData.cost_breakdown.map((b, i) => (
                  <div key={i} className="flex justify-between items-center py-1 border-b border-border/50 text-[11px]">
                    <span className="text-muted-foreground">
                      {b.component_product_id ? `Component: ${b.component_product_id.substring(0, 8)}...` : `Operation: ${b.operation_name}`}
                    </span>
                    <span className="font-mono font-bold">${b.extended_cost.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setShowCostModal(false)}
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
