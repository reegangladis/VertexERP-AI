import React, { useEffect, useState } from 'react';
import { Building2, Plus, Search, Calendar, Activity, DollarSign } from 'lucide-react';
import { manufacturingService, WorkCenter } from '@/services/manufacturingService';

export function WorkCentersPage() {
  const [workCenters, setWorkCenters] = useState<WorkCenter[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchWorkCenters = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getWorkCenters(search);
      setWorkCenters(data);
    } catch (err) {
      console.error('Error fetching work centers', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkCenters();
  }, [search]);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Building2 className="h-6 w-6 text-primary" />
            Work Centers & Production Lines
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Plant Layout, Shift Calendars, Daily Capacity & Hourly Overhead Rates
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          Create Work Center
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
        <div className="relative max-w-md">
          <Search className="h-4 w-4 absolute left-3 top-3 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search Work Centers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {workCenters.map((wc) => (
            <div key={wc.id} className="border border-border/80 rounded-xl p-5 space-y-3 bg-card hover:shadow-md transition-all">
              <div className="flex items-center justify-between">
                <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded bg-muted text-foreground">
                  {wc.code}
                </span>
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                  {wc.status}
                </span>
              </div>

              <div>
                <h3 className="font-bold text-base text-foreground">{wc.name}</h3>
                <p className="text-xs text-muted-foreground">Line: {wc.production_line || 'Main Assembly Line'}</p>
              </div>

              <div className="space-y-1.5 text-xs text-muted-foreground pt-2 border-t border-border/50">
                <div className="flex justify-between">
                  <span>Category:</span>
                  <span className="font-medium text-foreground">{wc.category}</span>
                </div>
                <div className="flex justify-between">
                  <span>Daily Capacity:</span>
                  <span className="font-medium text-foreground">{wc.capacity_per_day_hours} Hours / Day</span>
                </div>
                <div className="flex justify-between">
                  <span>Hourly Cost Rate:</span>
                  <span className="font-semibold text-foreground">${wc.hourly_cost}/hr</span>
                </div>
                <div className="flex justify-between">
                  <span>Efficiency Factor:</span>
                  <span className="font-semibold text-emerald-500">{wc.efficiency_percent}%</span>
                </div>
              </div>
            </div>
          ))}

          {workCenters.length === 0 && !loading && (
            <div className="col-span-3 text-center py-12 text-xs text-muted-foreground">
              No Work Centers found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
