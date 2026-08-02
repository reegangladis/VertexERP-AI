import React, { useEffect, useState } from 'react';
import { ShieldCheck, Plus, X, Trash2 } from 'lucide-react';
import { manufacturingService, QualityInspection } from '@/services/manufacturingService';

export function QualityControlPage() {
  const [inspections, setInspections] = useState<QualityInspection[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Modal
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [inspectionNumber, setInspectionNumber] = useState<string>('');
  const [sampleSize, setSampleSize] = useState<number>(5);
  const [inspectorName, setInspectorName] = useState<string>('QC Inspector John');
  const [inspectionType, setInspectionType] = useState<string>('IN_PROCESS');
  const [paramName, setParamName] = useState<string>('Dimensional Accuracy (mm)');
  const [expectedVal, setExpectedVal] = useState<string>('12.50');
  const [actualVal, setActualVal] = useState<string>('12.48');
  const [isPassed, setIsPassed] = useState<boolean>(true);

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

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await manufacturingService.createQualityInspection({
        inspection_number: inspectionNumber,
        product_id: '00000000-0000-0000-0000-000000000100',
        inspector_name: inspectorName,
        inspection_type: inspectionType,
        sample_size: sampleSize,
        results: [
          {
            parameter_name: paramName,
            expected_value: expectedVal,
            actual_value: actualVal,
            is_passed: isPassed,
          },
        ],
      });
      setShowCreateModal(false);
      setInspectionNumber('');
      fetchInspections();
    } catch (err) {
      console.error('Error recording inspection', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this inspection record?')) return;
    try {
      await manufacturingService.deleteQualityInspection(id);
      fetchInspections();
    } catch (err) {
      console.error('Error deleting inspection', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            Quality Control & Defect Tracking
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Inspection Lot Workflows, Parameter Verification, Rework Processing & Quality Decisions
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Create Inspection Lot
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
        <div className="border border-border rounded-lg overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-muted/50 border-b border-border font-medium text-muted-foreground uppercase tracking-wider text-[10px]">
              <tr>
                <th className="px-4 py-3">Inspection Lot #</th>
                <th className="px-4 py-3">Type</th>
                <th className="px-4 py-3">Inspector</th>
                <th className="px-4 py-3">Sample Size</th>
                <th className="px-4 py-3">Passed / Failed</th>
                <th className="px-4 py-3">Decision</th>
                <th className="px-4 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/60 text-foreground">
              {inspections.map((insp) => (
                <tr key={insp.id} className="hover:bg-muted/30">
                  <td className="px-4 py-3 font-mono font-bold text-foreground">{insp.inspection_number}</td>
                  <td className="px-4 py-3">{insp.inspection_type}</td>
                  <td className="px-4 py-3">{insp.inspector_name || 'N/A'}</td>
                  <td className="px-4 py-3 font-mono">{insp.sample_size} PCS</td>
                  <td className="px-4 py-3 font-mono">
                    <span className="text-emerald-500 font-bold">{insp.passed_count} Passed</span> /{' '}
                    <span className="text-red-400 font-bold">{insp.failed_count} Failed</span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        insp.decision === 'APPROVED'
                          ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                          : insp.decision === 'REJECTED'
                          ? 'bg-red-500/10 text-red-500 border border-red-500/20'
                          : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                      }`}
                    >
                      {insp.decision}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button onClick={() => handleDelete(insp.id)} className="p-1 text-red-400 hover:bg-red-400/10 rounded">
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </td>
                </tr>
              ))}

              {inspections.length === 0 && !loading && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-muted-foreground">
                    No Quality Inspections recorded.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* CREATE INSPECTION MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Create Inspection Lot</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Inspection #</label>
                  <input
                    type="text"
                    required
                    placeholder="QC-LOT-901"
                    value={inspectionNumber}
                    onChange={(e) => setInspectionNumber(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Sample Size</label>
                  <input
                    type="number"
                    required
                    value={sampleSize}
                    onChange={(e) => setSampleSize(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Inspector</label>
                  <input
                    type="text"
                    required
                    value={inspectorName}
                    onChange={(e) => setInspectorName(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Type</label>
                  <select
                    value={inspectionType}
                    onChange={(e) => setInspectionType(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="INCOMING">INCOMING</option>
                    <option value="IN_PROCESS">IN_PROCESS</option>
                    <option value="FINAL">FINAL</option>
                  </select>
                </div>
              </div>

              <div className="space-y-2 border-t border-border pt-3">
                <p className="font-semibold text-foreground">Test Parameter</p>
                <div>
                  <label className="block text-muted-foreground mb-1">Parameter Name</label>
                  <input
                    type="text"
                    value={paramName}
                    onChange={(e) => setParamName(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg"
                  />
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div>
                    <label className="block text-muted-foreground mb-1">Expected</label>
                    <input
                      type="text"
                      value={expectedVal}
                      onChange={(e) => setExpectedVal(e.target.value)}
                      className="w-full px-2 py-1 bg-background border border-border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1">Actual</label>
                    <input
                      type="text"
                      value={actualVal}
                      onChange={(e) => setActualVal(e.target.value)}
                      className="w-full px-2 py-1 bg-background border border-border rounded"
                    />
                  </div>
                </div>
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
                  Record Inspection
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
