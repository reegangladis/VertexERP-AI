import React, { useEffect, useState } from 'react';
import { Cpu, Plus, Search, Trash2, Edit, X } from 'lucide-react';
import { manufacturingService, WorkCenter } from '@/services/manufacturingService';

export function WorkCentersPage() {
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  // Modal
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [code, setCode] = useState<string>('');
  const [name, setName] = useState<string>('');
  const [line, setLine] = useState<string>('LINE-A');
  const [category, setCategory] = useState<string>('ASSEMBLY');
  const [hourlyCost, setHourlyCost] = useState<number>(50.0);
  const [capacityHours, setCapacityHours] = useState<number>(16.0);

  const fetchWorkCenters = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getWorkCenters(search);
      setWorkCenters(data);
    } catch (err) {
      console.error('Error fetching Work Centers', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkCenters();
  }, [search]);

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await manufacturingService.createWorkCenter({
        code,
        name,
        production_line: line,
        category,
        hourly_cost: hourlyCost,
        capacity_per_day_hours: capacityHours,
      });
      setShowCreateModal(false);
      setCode('');
      setName('');
      fetchWorkCenters();
    } catch (err) {
      console.error('Error creating Work Center', err);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this Work Center?')) return;
    try {
      await manufacturingService.deleteWorkCenter(id);
      fetchWorkCenters();
    } catch (err) {
      console.error('Error deleting Work Center', err);
    }
  };

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Cpu className="h-6 w-6 text-primary" />
            Work Centers & Production Lines
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Shop Floor Line Configuration, Daily Hour Capacities, Efficiency Tracking & Hourly Costs
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors"
        >
          <Plus className="h-4 w-4" />
          New Work Center
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
        <div className="relative max-w-md">
          <Search className="h-4 w-4 absolute left-3 top-3 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by Work Center Code or Name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workCenters.map((wc) => (
            <div key={wc.id} className="p-4 border border-border rounded-xl bg-card hover:border-primary/50 transition-all space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-muted text-muted-foreground">
                    {wc.category}
                  </span>
                  <h3 className="text-base font-bold text-foreground mt-1">{wc.name}</h3>
                  <p className="text-xs text-muted-foreground font-mono">{wc.code}</p>
                </div>
                <div className="flex items-center gap-1">
                  <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                    {wc.status}
                  </span>
                  <button onClick={() => handleDelete(wc.id)} className="p-1 text-red-400 hover:bg-red-400/10 rounded">
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs pt-2 border-t border-border/60">
                <div>
                  <span className="text-muted-foreground">Production Line</span>
                  <p className="font-semibold text-foreground">{wc.production_line || 'LINE-1'}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Daily Capacity</span>
                  <p className="font-semibold text-foreground">{wc.capacity_per_day_hours} Hours/Day</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Hourly Cost Rate</span>
                  <p className="font-semibold font-mono text-emerald-500">${wc.hourly_cost?.toFixed(2)}/hr</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Efficiency</span>
                  <p className="font-semibold text-foreground">{wc.efficiency_percent}%</p>
                </div>
              </div>
            </div>
          ))}

          {workCenters.length === 0 && !loading && (
            <div className="col-span-full text-center py-12 text-muted-foreground text-xs">
              No Work Centers configured.
            </div>
          )}
        </div>
      </div>

      {/* CREATE WORK CENTER MODAL */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <h3 className="text-lg font-bold text-foreground">Add Work Center</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-muted-foreground hover:text-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-foreground mb-1">Code</label>
                  <input
                    type="text"
                    required
                    placeholder="WC-ASM-01"
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
                </div>
                <div>
                  <label className="block font-medium text-foreground mb-1">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="ASSEMBLY">ASSEMBLY</option>
                    <option value="MACHINING">MACHINING</option>
                    <option value="PACKAGING">PACKAGING</option>
                    <option value="QUALITY">QUALITY</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-foreground mb-1">Work Center Name</label>
                <input
                  type="text"
                  required
                  placeholder="Main SMT Assembly Line 1"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
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
                <div>
                  <label className="block font-medium text-foreground mb-1">Capacity (Hours/Day)</label>
                  <input
                    type="number"
                    required
                    value={capacityHours}
                    onChange={(e) => setCapacityHours(Number(e.target.value))}
                    className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
                  />
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
                  Create Work Center
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
