import React, { useEffect, useState } from 'react';
import { Cpu, Play, CheckCircle2, ShoppingCart, Calendar, AlertTriangle, X } from 'lucide-react';
import { manufacturingService, MRPRun } from '@/services/manufacturingService';

export function MRPPage() {
  const [mrpRuns, setMrpRuns] = useState<MRPRun[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedRun, setSelectedRun] = useState<MRPRun | null>(null);

  // Modal
  const [showRunModal, setShowRunModal] = useState<boolean>(false);
  const [runNumber, setRunNumber] = useState<string>(`MRP-RUN-${Date.now().toString().slice(-6)}`);

  const fetchMRPRuns = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getMRPRuns();
      setMrpRuns(data);
      if (data.length > 0 && !selectedRun) {
        setSelectedRun(data[0]);
      }
    } catch (err) {
      console.error('Error fetching MRP runs', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMRPRuns();
  }, []);

  const handleExecuteMRP = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const run = await manufacturingService.executeMRPRun(runNumber);
      setShowRunModal(false);
      setRunNumber(`MRP-RUN-${Date.now().toString().slice(-6)}`);
      fetchMRPRuns();
      setSelectedRun(run);
    } catch (err) {
      console.error('Error running MRP engine', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Cpu className="h-6 w-6 text-primary" />
            Material Requirements Planning (MRP II) Engine
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Automated Procurement Suggestions, Multi-Level BOM Explosion & Work Center Capacity Planning
          </p>
        </div>
        <button
          onClick={() => setShowRunModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Play className="h-4 w-4" />
          Run MRP Calculation
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MRP Run History */}
        <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-3">
          <h2 className="text-sm font-bold text-foreground">MRP Execution Runs</h2>
          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {mrpRuns.map((run) => (
              <div
                key={run.id}
                onClick={() => setSelectedRun(run)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                  selectedRun?.id === run.id
                    ? 'border-primary bg-primary/5 font-medium'
                    : 'border-border/60 hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono font-bold text-foreground">{run.run_number}</span>
                  <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                    {run.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground mt-2 text-[11px]">
                  <span>{new Date(run.run_date).toLocaleDateString()}</span>
                  <span className="font-semibold text-primary">{run.suggestions_count} Suggestions</span>
                </div>
              </div>
            ))}

            {mrpRuns.length === 0 && !loading && (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No MRP calculation runs recorded.
              </div>
            )}
          </div>
        </div>

        {/* Selected Run Suggestions & Capacity Details */}
        <div className="lg:col-span-2 space-y-6">
          {selectedRun ? (
            <>
              {/* Summary Banner */}
              <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
                <div className="flex items-center justify-between border-b border-border pb-3">
                  <div>
                    <h2 className="text-lg font-bold text-foreground font-mono">{selectedRun.run_number}</h2>
                    <p className="text-xs text-muted-foreground">
                      Executed on {new Date(selectedRun.run_date).toLocaleString()} | Items Processed: {selectedRun.total_items_processed}
                    </p>
                  </div>
                  <span className="px-3 py-1 text-xs font-bold rounded-lg bg-primary/10 text-primary">
                    {selectedRun.suggestions_count} Total Recommendations
                  </span>
                </div>

                {/* Procurement Suggestions */}
                <div className="space-y-3 pt-2">
                  <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <ShoppingCart className="h-4 w-4 text-emerald-500" />
                    Suggested Reorder Procurement Items
                  </h3>

                  <div className="border border-border rounded-lg overflow-x-auto">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-muted/50 border-b border-border font-medium text-muted-foreground uppercase tracking-wider text-[10px]">
                        <tr>
                          <th className="px-4 py-2.5">Product SKU</th>
                          <th className="px-4 py-2.5">Product Name</th>
                          <th className="px-4 py-2.5">Suggested Qty</th>
                          <th className="px-4 py-2.5">Reorder Reason</th>
                          <th className="px-4 py-2.5 text-right">Est. Cost</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-border/60 text-foreground">
                        {selectedRun.procurement_suggestions?.items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-muted/30">
                            <td className="px-4 py-2.5 font-mono font-bold">{item.sku}</td>
                            <td className="px-4 py-2.5 font-medium">{item.product_name}</td>
                            <td className="px-4 py-2.5 font-mono text-emerald-500 font-bold">{item.suggested_qty} {item.unit_name}</td>
                            <td className="px-4 py-2.5 text-muted-foreground text-[11px]">{item.reorder_reason}</td>
                            <td className="px-4 py-2.5 text-right font-mono font-semibold">${item.estimated_cost?.toFixed(2)}</td>
                          </tr>
                        ))}

                        {(!selectedRun.procurement_suggestions?.items || selectedRun.procurement_suggestions.items.length === 0) && (
                          <tr>
                            <td colSpan={5} className="px-4 py-4 text-center text-muted-foreground">
                              All raw material safety stock levels are optimal.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Capacity Planning */}
                <div className="space-y-3 pt-3 border-t border-border">
                  <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                    <Cpu className="h-4 w-4 text-primary" />
                    Work Center Load Capacity Planning
                  </h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {selectedRun.capacity_planning?.items.map((c, i) => (
                      <div key={i} className="p-3 border border-border rounded-lg bg-card space-y-2">
                        <div className="flex justify-between items-center text-xs">
                          <span className="font-bold text-foreground">{c.work_center_name}</span>
                          <span className="font-mono font-semibold text-primary">{c.load_percentage}% Load</span>
                        </div>
                        <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${c.load_percentage > 90 ? 'bg-red-500' : 'bg-primary'}`}
                            style={{ width: `${c.load_percentage}%` }}
                          />
                        </div>
                        <div className="flex justify-between text-[11px] text-muted-foreground font-mono">
                          <span>Req: {c.required_hours} hrs</span>
                          <span>Avail: {c.available_hours} hrs/day</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-card border border-border rounded-xl p-16 text-center text-muted-foreground text-xs">
              Select an MRP calculation run from the list or trigger a new MRP calculation run.
            </div>
          )}
        </div>
      </div>

      {/* TRIGGER MRP RUN MODAL */}
      {showRunModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Play className="h-5 w-5 text-primary" />
                Run MRP Calculation Engine
              </h3>
              <button onClick={() => setShowRunModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleExecuteMRP} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">MRP Run Identifier</label>
                <input
                  type="text"
                  required
                  value={runNumber}
                  onChange={(e) => setRunNumber(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 font-mono"
                />
              </div>

              <div className="p-3 bg-muted/40 rounded-lg text-muted-foreground leading-relaxed">
                Running the MRP Engine will explode multi-level BOMs for all active production orders, check safety stock thresholds, generate procurement purchase recommendations, and calculate work center load planning.
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowRunModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-semibold shadow hover:bg-primary/90"
                >
                  Execute MRP Run
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
