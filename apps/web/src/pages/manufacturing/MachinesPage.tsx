import React, { useEffect, useState } from 'react';
import { Cpu, Plus, AlertCircle, Activity, ShieldCheck, HeartPulse } from 'lucide-react';
import { manufacturingService, Machine } from '@/services/manufacturingService';

export function MachinesPage() {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchMachines = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getMachines();
      setMachines(data);
    } catch (err) {
      console.error('Error loading machine fleet', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMachines();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Cpu className="h-6 w-6 text-primary" />
            Machine Telemetry & Fleet Inventory
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Machine Health Scores, Sensor Telemetry Summaries & Operational Status
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          Register New Machine
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {machines.map((machine) => (
          <div key={machine.id} className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4 hover:border-primary/50 transition-all">
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold px-2.5 py-1 rounded bg-muted text-foreground">
                {machine.code}
              </span>
              <span
                className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${
                  machine.status === 'OPERATIONAL'
                    ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                    : machine.status === 'BREAKDOWN'
                    ? 'bg-red-500/10 text-red-500 border-red-500/20'
                    : 'bg-amber-500/10 text-amber-500 border-amber-500/20'
                }`}
              >
                {machine.status}
              </span>
            </div>

            <div>
              <h3 className="font-bold text-lg text-foreground">{machine.name}</h3>
              <p className="text-xs text-muted-foreground font-mono">
                Model: {machine.model_number || 'GENERIC-M1'} | S/N: {machine.serial_number || 'SN-99812'}
              </p>
            </div>

            {/* Health Score Meter */}
            <div className="p-3 bg-muted/30 rounded-lg space-y-2 border border-border/40">
              <div className="flex items-center justify-between text-xs">
                <span className="text-muted-foreground flex items-center gap-1.5 font-medium">
                  <HeartPulse className="h-4 w-4 text-emerald-500" />
                  Health Index
                </span>
                <span className="font-bold text-foreground">{machine.health_score || 98.0}%</span>
              </div>
              <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
                <div
                  className="bg-emerald-500 h-full rounded-full"
                  style={{ width: `${machine.health_score || 98.0}%` }}
                />
              </div>
            </div>

            <div className="text-xs space-y-1.5 text-muted-foreground pt-1">
              <div className="flex justify-between">
                <span>Capacity Rate:</span>
                <span className="font-semibold text-foreground">{machine.capacity_units_per_hour} units / hr</span>
              </div>
              <div className="flex justify-between">
                <span>Machine Hourly Cost:</span>
                <span className="font-semibold text-foreground">${machine.hourly_cost}/hr</span>
              </div>
            </div>
          </div>
        ))}

        {machines.length === 0 && !loading && (
          <div className="col-span-3 text-center py-12 text-xs text-muted-foreground">
            No machines registered in inventory.
          </div>
        )}
      </div>
    </div>
  );
}
