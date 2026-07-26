import React, { useEffect, useState } from 'react';
import { Layers, Plus, CheckCircle, Calculator, Search, ChevronRight, FileText } from 'lucide-react';
import { manufacturingService, BillOfMaterial } from '@/services/manufacturingService';

export function BillOfMaterialsPage() {
  const [boms, setBoms] = useState<BillOfMaterial[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedBom, setSelectedBom] = useState<BillOfMaterial | null>(null);

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
      alert(`Cost Rollup Calculated!\nTotal Calculated Cost: $${rollup.total_calculated_cost.toFixed(2)}\nMaterial Cost: $${rollup.material_cost.toFixed(2)}\nOperation Cost: $${rollup.operation_cost.toFixed(2)}`);
      fetchBoms();
    } catch (err) {
      console.error('Cost Rollup failed', err);
    }
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
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
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
                  <span className="font-mono text-foreground font-semibold">${bom.total_cost.toFixed(2)}</span>
                </div>
              </div>
            ))}

            {boms.length === 0 && (
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
                    Base Batch Quantity: {selectedBom.base_quantity} PCS | Total Standard Cost: ${selectedBom.total_cost.toFixed(2)}
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
                </div>
              </div>

              {/* Component Tree Table */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <FileText className="h-4 w-4 text-primary" />
                  Bill of Material Components Breakdown
                </h3>
                <div className="border border-border rounded-lg overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-muted/50 border-b border-border font-medium text-muted-foreground uppercase tracking-wider text-[10px]">
                      <tr>
                        <th className="px-4 py-2.5">Component ID</th>
                        <th className="px-4 py-2.5">Qty / Unit</th>
                        <th className="px-4 py-2.5">Scrap %</th>
                        <th className="px-4 py-2.5">Unit Cost</th>
                        <th className="px-4 py-2.5 text-right">Extended Cost</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/60 text-foreground">
                      {selectedBom.items && selectedBom.items.length > 0 ? (
                        selectedBom.items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-muted/30">
                            <td className="px-4 py-3 font-mono">{item.component_product_id.substring(0, 8)}...</td>
                            <td className="px-4 py-3">{item.quantity} {item.unit_name}</td>
                            <td className="px-4 py-3">{item.scrap_factor_percent}%</td>
                            <td className="px-4 py-3">${item.unit_cost.toFixed(2)}</td>
                            <td className="px-4 py-3 text-right font-mono font-semibold">
                              ${(item.extended_cost || (item.quantity * item.unit_cost)).toFixed(2)}
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={5} className="px-4 py-6 text-center text-muted-foreground">
                            No component items added to this BOM yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* AI Readiness Note */}
              <div className="p-4 bg-primary/5 border border-primary/20 rounded-lg text-xs space-y-1">
                <span className="font-semibold text-primary">AI Yield & Batch Optimization Placeholders</span>
                <p className="text-muted-foreground">
                  Predicted Yield: {selectedBom.predicted_yield_rate || 98.5}% | Recommended Optimal Batch Size: {selectedBom.optimal_batch_size || 100} units.
                </p>
              </div>
            </>
          ) : (
            <div className="text-center py-20 text-muted-foreground text-xs">
              Select a Bill of Materials to inspect components and cost rollup.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
