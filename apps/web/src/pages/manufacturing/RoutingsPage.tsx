import React, { useEffect, useState } from 'react';
import { GitCommit, Plus, Search, Trash2, X, Clock } from 'lucide-react';
import { manufacturingService, Routing, WorkCenter } from '@/services/manufacturingService';

export function RoutingsPage() {
  const [routings, setRoutings] = useState<Routing[]>([]);
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedRouting, setSelectedRouting] = useState<Routing | null>(null);

  // Modal
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [code, setCode] = useState<string>('');
  const [name, setName] = useState<string>('');
  const [version, setVersion] = useState<string>('1.0');
  const [opName, setOpName] = useState<string>('Primary Machining Operation');
  const [setupMins, setSetupMins] = useState<number>(15);
  const [machineMins, setMachineMins] = useState<number>(30);
  const [laborMins, setLaborMins] = useState<number>(15);
  const [hourlyRate, setHourlyRate] = useState<number>(45.0);

  const fetchRoutings = async () => {
    setLoading(true);
    try {
      const [rList, wcList] = await Promise.all([
        manufacturingService.getRoutings(search),
        manufacturingService.getWorkCenters(),
      ]);
      setRoutings(rList);
      setWorkCenters(wcList);
      if (rList.length > 0 && !selectedRouting) {
        setSelectedRouting(rList[0]);
      }
    } catch (err) {
      console.error('Error fetching Routings', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoutings();
  }, [search]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const wcId = workCenters.length > 0 ? workCenters[0].id : '00000000-0000-0000-0000-000000000001';
    try {
      const newR = await manufacturingService.createRouting({
        product_id: '00000000-0000-0000-0000-000000000100',
        code,
        version,
        name,
        operations: [
          {
            work_center_id: wcId,
            sequence_number: 10,
            operation_name: opName,
            setup_time_mins: setupMins,
            machine_time_mins: machineMins,
            labor_time_mins: laborMins,
            standard_time_mins: setupMins + machineMins + laborMins,
            hourly_rate: hourlyRate,
          },
        ],
      });
      setShowCreateModal(false);
      setCode('');
      setName('');
      fetchRoutings();
      setSelectedRouting(newR);
    } catch (err) {
      console.error('Error creating Routing', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this Routing?')) return;
    try {
      await manufacturingService.deleteRouting(id);
      setSelectedRouting(null);
      fetchRoutings();
    } catch (err) {
      console.error('Error deleting Routing', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <GitCommit className="h-6 w-6 text-primary" />
            Manufacturing Routings & Operations
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Standard Operation Sequence, Setup Time, Machine Cycle Times & Work Center Rates
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Create New Routing
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search & List */}
        <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
          <div className="relative">
            <Search className="h-4 w-4 absolute left-3 top-3 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search by Routing Code or Name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
            />
          </div>

          <div className="space-y-2 max-h-[600px] overflow-y-auto pr-1">
            {routings.map((r) => (
              <div
                key={r.id}
                onClick={() => setSelectedRouting(r)}
                className={`p-3 rounded-lg border text-xs cursor-pointer transition-all ${
                  selectedRouting?.id === r.id
                    ? 'border-primary bg-primary/5 font-medium'
                    : 'border-border/60 hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">{r.name}</span>
                  <span className="font-mono text-[10px] text-muted-foreground">{r.code}</span>
                </div>
                <div className="flex items-center justify-between text-muted-foreground mt-2">
                  <span>Version {r.version}</span>
                  <span className="font-mono text-foreground font-semibold">{r.total_standard_time_mins} mins</span>
                </div>
              </div>
            ))}

            {routings.length === 0 && !loading && (
              <div className="text-center py-8 text-xs text-muted-foreground">
                No Routings found.
              </div>
            )}
          </div>
        </div>

        {/* Routing Detail */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
          {selectedRouting ? (
            <>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
                <div>
                  <h2 className="text-xl font-bold text-foreground">{selectedRouting.name}</h2>
                  <p className="text-xs text-muted-foreground mt-1">
                    Code: {selectedRouting.code} | Total Standard Cycle Time: {selectedRouting.total_standard_time_mins} Mins
                  </p>
                </div>
                <button
                  onClick={() => handleDelete(selectedRouting.id)}
                  className="p-1.5 text-xs text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                  <Clock className="h-4 w-4 text-primary" />
                  Operation Sequence ({selectedRouting.operations?.length || 0})
                </h3>

                <div className="space-y-2">
                  {selectedRouting.operations?.map((op) => (
                    <div key={op.id || op.sequence_number} className="p-3 border border-border rounded-lg bg-card flex items-center justify-between text-xs">
                      <div className="flex items-center gap-3">
                        <span className="h-7 w-7 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center font-mono">
                          {op.sequence_number}
                        </span>
                        <div>
                          <p className="font-bold text-foreground">{op.operation_name}</p>
                          <p className="text-muted-foreground text-[11px]">Work Center: {op.work_center_id.substring(0, 8)}...</p>
                        </div>
                      </div>
                      <div className="text-right font-mono">
                        <span className="text-foreground font-semibold">{op.standard_time_mins} mins</span>
                        <p className="text-muted-foreground text-[10px]">${op.hourly_rate?.toFixed(2)}/hr</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center py-16 text-muted-foreground text-xs">
              Select a Routing to view operation steps and standard times.
            </div>
          )}
        </div>
      </div>

      {/* CREATE ROUTING MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Create Manufacturing Routing</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Routing Code</label>
                  <input
                    type="text"
                    required
                    placeholder="RT-ASM-01"
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
                <label className="block font-medium text-foreground mb-1">Routing Name</label>
                <input
                  type="text"
                  required
                  placeholder="Standard Electronic Assembly Process"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="space-y-2 border-t border-border pt-3">
                <p className="font-semibold text-foreground">Initial Operation Step</p>
                <div>
                  <label className="block font-medium text-foreground mb-1">Operation Name</label>
                  <input
                    type="text"
                    required
                    value={opName}
                    onChange={(e) => setOpName(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>

                <div className="grid grid-cols-3 gap-2">
                  <div>
                    <label className="block text-muted-foreground mb-1">Setup (m)</label>
                    <input
                      type="number"
                      value={setupMins}
                      onChange={(e) => setSetupMins(Number(e.target.value))}
                      className="w-full px-2 py-1 bg-background border border-border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1">Machine (m)</label>
                    <input
                      type="number"
                      value={machineMins}
                      onChange={(e) => setMachineMins(Number(e.target.value))}
                      className="w-full px-2 py-1 bg-background border border-border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-muted-foreground mb-1">Labor (m)</label>
                    <input
                      type="number"
                      value={laborMins}
                      onChange={(e) => setLaborMins(Number(e.target.value))}
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
                  Save Routing
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
