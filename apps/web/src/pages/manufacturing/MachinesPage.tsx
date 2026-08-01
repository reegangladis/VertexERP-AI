import React, { useEffect, useState } from 'react';
import { Cog, Plus, Search, Trash2, AlertTriangle, Activity, X } from 'lucide-react';
import { manufacturingService, Machine, WorkCenter } from '@/services/manufacturingService';

export function MachinesPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Modals
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [showDowntimeModal, setShowDowntimeModal] = useState<boolean>(false);
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);

  // Machine Form
  const [code, setCode] = useState<string>('');
  const [name, setName] = useState<string>('');
  const [workCenterId, setWorkCenterId] = useState<string>('');
  const [hourlyCost, setHourlyCost] = useState<number>(75.0);
  const [capacityUnits, setCapacityUnits] = useState<number>(100);

  // Downtime Form
  const [reasonCategory, setReasonCategory] = useState<string>('UNPLANNED_BREAKDOWN');
  const [downtimeComments, setDowntimeComments] = useState<string>('');

  const fetchInitialData = async () => {
    setLoading(true);
    try {
      const [mList, wcList] = await Promise.all([
        manufacturingService.getMachines(),
        manufacturingService.getWorkCenters(),
      ]);
      setMachines(mList);
      setWorkCenters(wcList);
      if (wcList.length > 0) setWorkCenterId(wcList[0].id);
    } catch (err) {
      console.error('Error fetching machines data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await manufacturingService.createMachine({
        work_center_id: workCenterId,
        code,
        name,
        hourly_cost: hourlyCost,
        capacity_units_per_hour: capacityUnits,
      });
      setShowCreateModal(false);
      setCode('');
      setName('');
      fetchInitialData();
    } catch (err) {
      console.error('Error creating machine', err);
    }
  };

  const handleDowntimeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedMachineId) return;
    try {
      await manufacturingService.logMachineDowntime({
        machine_id: selectedMachineId,
        start_time: new Date().toISOString(),
        end_time: new Date(Date.now() + 3600000).toISOString(),
        reason_category: reasonCategory,
        comments: downtimeComments,
      });
      setShowDowntimeModal(false);
      setDowntimeComments('');
      fetchInitialData();
    } catch (err) {
      console.error('Error logging downtime', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this machine?')) return;
    try {
      await manufacturingService.deleteMachine(id);
      fetchInitialData();
    } catch (err) {
      console.error('Error deleting machine', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Cog className="h-6 w-6 text-primary" />
            Machines & Equipment Asset Management
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Machine Status Telemetry, Downtime Logging, Health Score Monitoring & Maintenance Dispatch
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          Register New Machine
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {machines.map((m) => (
            <div key={m.id} className="p-4 border border-border rounded-xl bg-card hover:border-primary/50 transition-all space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-base font-bold text-foreground">{m.name}</h3>
                  <p className="text-xs text-muted-foreground font-mono">{m.code}</p>
                </div>
                <span
                  className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                    m.status === 'OPERATIONAL'
                      ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                      : 'bg-red-500/10 text-red-500 border border-red-500/20'
                  }`}
                >
                  {m.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-border/60">
                <div>
                  <span className="text-muted-foreground">Hourly Cost Rate</span>
                  <p className="font-semibold font-mono text-emerald-500">${m.hourly_cost?.toFixed(2)}/hr</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Capacity</span>
                  <p className="font-semibold text-foreground">{m.capacity_units_per_hour} units/hr</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Health Score</span>
                  <p className="font-semibold text-primary">{m.health_score || 98.0}%</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-border/60">
                <button
                  onClick={() => {
                    setSelectedMachineId(m.id);
                    setShowDowntimeModal(true);
                  }}
                  className="px-2.5 py-1 text-[11px] font-semibold border border-amber-500/30 text-amber-500 bg-amber-500/10 hover:bg-amber-500/20 rounded-lg flex items-center gap-1"
                >
                  <AlertTriangle className="h-3.5 w-3.5" />
                  Log Downtime
                </button>
                <button onClick={() => handleDelete(m.id)} className="p-1 text-red-400 hover:bg-red-400/10 rounded">
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            </div>
          ))}

          {machines.length === 0 && !loading && (
            <div className="col-span-full text-center py-12 text-muted-foreground text-xs">
              No machines registered in database.
            </div>
          )}
        </div>
      </div>

      {/* CREATE MACHINE MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Register Machine</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Work Center</label>
                <select
                  value={workCenterId}
                  onChange={(e) => setWorkCenterId(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  {workCenters.map((wc) => (
                    <option key={wc.id} value={wc.id}>
                      {wc.name} ({wc.code})
                    </option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Machine Code</label>
                  <input
                    type="text"
                    required
                    placeholder="MCH-CNC-01"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Hourly Cost ($)</label>
                  <input
                    type="number"
                    required
                    value={hourlyCost}
                    onChange={(e) => setHourlyCost(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Machine Name</label>
                <input
                  type="text"
                  required
                  placeholder="5-Axis CNC Milling Machine"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
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
                  Register
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DOWNTIME MODAL */}
      {showDowntimeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-amber-500" />
                Log Machine Downtime Event
              </h3>
              <button onClick={() => setShowDowntimeModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleDowntimeSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-foreground mb-1">Reason Category</label>
                <select
                  value={reasonCategory}
                  onChange={(e) => setReasonCategory(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  <option value="UNPLANNED_BREAKDOWN">UNPLANNED BREAKDOWN</option>
                  <option value="CHANGE_OVER">CHANGE OVER / SETTING</option>
                  <option value="NO_MATERIAL">NO MATERIAL AVAILABILITY</option>
                  <option value="SCHEDULED_MAINTENANCE">SCHEDULED MAINTENANCE</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Comments / Diagnostics</label>
                <textarea
                  rows={3}
                  required
                  value={downtimeComments}
                  onChange={(e) => setDowntimeComments(e.target.value)}
                  placeholder="Spindle bearing overheating detected..."
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="flex justify-end gap-2 pt-3 border-t border-border">
                <button
                  type="button"
                  onClick={() => setShowDowntimeModal(false)}
                  className="px-4 py-2 border border-border rounded-lg hover:bg-muted"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-amber-600 text-white rounded-lg font-semibold shadow hover:bg-amber-700"
                >
                  Log Downtime
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
