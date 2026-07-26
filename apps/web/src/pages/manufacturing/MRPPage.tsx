import React, { useEffect, useState } from 'react';
import { Cpu, Play, CheckCircle2, ShoppingCart, Factory, Layers, RefreshCw } from 'lucide-react';
import { manufacturingService, MRPRun } from '@/services/manufacturingService';

export function MRPPage() {
  const [runs, setRuns] = useState<MRPRun[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [running, setRunning] = useState<boolean>(false);
  const [selectedRun, setSelectedRun] = useState<MRPRun | null>(null);

  const fetchRuns = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getMRPRuns();
      setRuns(data);
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
    fetchRuns();
  }, []);

  const handleExecuteMRP = async () => {
    setRunning(true);
    try {
      const runNum = `MRP-${Date.now().toString().substring(6)}`;
      const newRun = await manufacturingService.executeMRPRun(runNum);
      setSelectedRun(newRun);
      fetchRuns();
    } catch (err) {
      console.error('MRP Engine execution failed', err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Cpu className="h-6 w-6 text-primary" />
            Material Requirement Planning (MRP) Engine
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Automated Procurement Suggestions, Planned Production Orders & Work Center Capacity Load
          </p>
        </div>
        <button
          onClick={handleExecuteMRP}
          disabled={running}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Play className={`h-4 w-4 ${running ? 'animate-spin' : ''}`} />
          {running ? 'Calculating Net Requirements...' : 'Run MRP Engine'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* MRP Run History */}
        <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            MRP Run History
          </h3>
          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {runs.map((r) => (
              <div
                key={r.id}
                onClick={() => setSelectedRun(r)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                  selectedRun?.id === r.id
                    ? 'border-primary bg-primary/5 font-medium'
                    : 'border-border/60 hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-between font-bold text-foreground">
                  <span>{r.run_number}</span>
                  <span className="text-[10px] font-semibold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded">
                    {r.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground mt-2">
                  <span>{new Date(r.run_date).toLocaleTimeString()}</span>
                  <span>{r.suggestions_count} Recommendations</span>
                </div>
              </div>
            ))}

            {runs.length === 0 && !loading && (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No MRP runs recorded yet. Click "Run MRP Engine" to execute calculation.
              </div>
            )}
          </div>
        </div>

        {/* Selected MRP Run Recommendations */}
        <div className="lg:col-span-2 space-y-6">
          {selectedRun ? (
            <>
              {/* Procurement Recommendations */}
              <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4 text-emerald-500" />
                  Suggested Procurement Purchase Orders
                </h3>

                <div className="border border-border rounded-lg overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-muted/50 border-b border-border text-[10px] font-medium text-muted-foreground uppercase">
                      <tr>
                        <th className="px-4 py-2.5">SKU / Product</th>
                        <th className="px-4 py-2.5">Suggested Qty</th>
                        <th className="px-4 py-2.5">Reason</th>
                        <th className="px-4 py-2.5 text-right">Est. Cost</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/60 text-foreground">
                      {selectedRun.procurement_suggestions?.items && selectedRun.procurement_suggestions.items.length > 0 ? (
                        selectedRun.procurement_suggestions.items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-muted/30">
                            <td className="px-4 py-3 font-semibold">{item.product_name} <span className="font-mono text-muted-foreground">({item.sku})</span></td>
                            <td className="px-4 py-3 font-mono font-medium text-emerald-500">{item.suggested_qty} {item.unit_name}</td>
                            <td className="px-4 py-3 text-muted-foreground">{item.reorder_reason}</td>
                            <td className="px-4 py-3 text-right font-mono font-semibold">${item.estimated_cost.toFixed(2)}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">
                            No immediate raw material procurement required.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Production Recommendations */}
              <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
                <h3 className="font-semibold text-sm text-foreground flex items-center gap-2">
                  <Factory className="h-4 w-4 text-primary" />
                  Suggested Planned Production Orders
                </h3>

                <div className="border border-border rounded-lg overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-muted/50 border-b border-border text-[10px] font-medium text-muted-foreground uppercase">
                      <tr>
                        <th className="px-4 py-2.5">Product Name</th>
                        <th className="px-4 py-2.5">Planned Batch Qty</th>
                        <th className="px-4 py-2.5">BOM Code</th>
                        <th className="px-4 py-2.5 text-right">Suggested Schedule</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/60 text-foreground">
                      {selectedRun.production_suggestions?.items && selectedRun.production_suggestions.items.length > 0 ? (
                        selectedRun.production_suggestions.items.map((p, idx) => (
                          <tr key={idx} className="hover:bg-muted/30">
                            <td className="px-4 py-3 font-semibold">{p.product_name}</td>
                            <td className="px-4 py-3 font-mono text-primary font-semibold">{p.suggested_order_qty} PCS</td>
                            <td className="px-4 py-3 font-mono text-muted-foreground">{p.bom_code}</td>
                            <td className="px-4 py-3 text-right text-muted-foreground">{p.planned_start_date} to {p.planned_end_date}</td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={4} className="px-4 py-6 text-center text-muted-foreground">
                            No planned production orders suggested.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-20 text-xs text-muted-foreground bg-card border border-border rounded-xl">
              Select an MRP Run to view calculated suggestions.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
