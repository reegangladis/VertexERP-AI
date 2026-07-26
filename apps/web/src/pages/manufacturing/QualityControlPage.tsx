import React, { useEffect, useState } from 'react';
import { CheckCircle2, XCircle, Plus, ShieldCheck, AlertCircle } from 'lucide-react';
import { manufacturingService, QualityInspection } from '@/services/manufacturingService';

export function QualityControlPage() {
  const [inspections, setInspections] = useState<QualityInspection[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchInspections = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getQualityInspections();
      setInspections(data);
    } catch (err) {
      console.error('Error fetching quality inspections', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInspections();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <CheckCircle2 className="h-6 w-6 text-primary" />
            Quality Control & Inspection Lots
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Inspection Plans, Parameter Validation, Pass/Fail Decisions & Corrective Actions
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          Create Inspection Lot
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {inspections.map((insp) => (
          <div key={insp.id} className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold px-2.5 py-1 rounded bg-muted text-foreground">
                {insp.inspection_number}
              </span>
              <span
                className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
                  insp.decision === 'APPROVED'
                    ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                    : insp.decision === 'REJECTED'
                    ? 'bg-red-500/10 text-red-500 border-red-500/20'
                    : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                }`}
              >
                {insp.decision}
              </span>
            </div>

            <div className="text-xs space-y-1">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Type:</span>
                <span className="font-medium text-foreground">{insp.inspection_type}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Lot Number:</span>
                <span className="font-mono text-foreground">{insp.lot_number || 'LOT-2026-001'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Inspector:</span>
                <span className="font-medium text-foreground">{insp.inspector_name || 'QA Lead'}</span>
              </div>
            </div>

            {/* Test Results */}
            <div className="border border-border/50 rounded-lg p-3 bg-muted/20 space-y-2 text-xs">
              <div className="flex justify-between font-semibold">
                <span>Sample Size: {insp.sample_size}</span>
                <span className="text-emerald-500">Passed: {insp.passed_count}</span>
                <span className="text-red-400">Failed: {insp.failed_count}</span>
              </div>

              {insp.results && insp.results.length > 0 && (
                <div className="space-y-1 pt-2 border-t border-border/40">
                  {insp.results.map((res, idx) => (
                    <div key={idx} className="flex items-center justify-between text-[11px]">
                      <span>{res.parameter_name} (Exp: {res.expected_value})</span>
                      <span className={res.is_passed ? 'text-emerald-500 font-semibold' : 'text-red-400 font-semibold'}>
                        {res.actual_value} ({res.is_passed ? 'PASS' : 'FAIL'})
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {inspections.length === 0 && !loading && (
          <div className="col-span-2 text-center py-12 text-xs text-muted-foreground">
            No Quality Inspections recorded.
          </div>
        )}
      </div>
    </div>
  );
}
