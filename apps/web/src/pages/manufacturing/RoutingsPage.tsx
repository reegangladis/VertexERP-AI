import React, { useEffect, useState } from 'react';
import { GitBranch, Plus, Search, Clock, Cpu, UserCheck } from 'lucide-react';
import { manufacturingService, Routing } from '@/services/manufacturingService';

export function RoutingsPage() {
  const [routings, setRoutings] = useState<Routing[]>([]);
  const [search, setSearch] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const fetchRoutings = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getRoutings(search);
      setRoutings(data);
    } catch (err) {
      console.error('Error fetching routings', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoutings();
  }, [search]);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <GitBranch className="h-6 w-6 text-primary" />
            Manufacturing Routings & Operations
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Operation Sequences, Work Center Mapping, Standard Time & Machine Labor Allocation
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          Create New Routing
        </button>
      </div>

      <div className="bg-card border border-border rounded-xl p-4 shadow-sm">
        <div className="relative mb-4 max-w-md">
          <Search className="h-4 w-4 absolute left-3 top-3 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by Routing Code or Name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 text-xs bg-background border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>

        <div className="space-y-4">
          {routings.map((routing) => (
            <div key={routing.id} className="border border-border/80 rounded-xl p-5 space-y-4 bg-card hover:border-primary/40 transition-colors">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/50 pb-3">
                <div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold text-base text-foreground">{routing.name}</span>
                    <span className="text-xs font-mono px-2 py-0.5 rounded bg-muted text-muted-foreground">{routing.code}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-primary/10 text-primary font-semibold">v{routing.version}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Clock className="h-4 w-4 text-primary" />
                  Total Standard Cycle Time: <span className="font-bold text-foreground">{routing.total_standard_time_mins} mins</span>
                </div>
              </div>

              {/* Operations Sequence */}
              <div className="space-y-2">
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                  Operation Sequence Breakdown
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {routing.operations && routing.operations.length > 0 ? (
                    routing.operations.map((op, idx) => (
                      <div key={idx} className="p-3 bg-muted/20 border border-border/60 rounded-lg text-xs space-y-2">
                        <div className="flex items-center justify-between font-semibold">
                          <span className="text-primary font-mono">Op #{op.sequence_number}</span>
                          <span className="text-foreground">{op.operation_name}</span>
                        </div>
                        <div className="space-y-1 text-muted-foreground text-[11px]">
                          <div className="flex justify-between">
                            <span>Setup Time:</span>
                            <span className="font-medium text-foreground">{op.setup_time_mins} mins</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Machine Time:</span>
                            <span className="font-medium text-foreground">{op.machine_time_mins} mins</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Labor Time:</span>
                            <span className="font-medium text-foreground">{op.labor_time_mins} mins</span>
                          </div>
                        </div>
                      </div>
                    ))
                  ) : (
                    <div className="col-span-3 text-xs text-muted-foreground py-2 text-center">
                      No operation steps configured.
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}

          {routings.length === 0 && !loading && (
            <div className="text-center py-12 text-xs text-muted-foreground">
              No routings found matching search criteria.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
