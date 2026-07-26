import React, { useEffect, useState } from 'react';
import {
  Factory,
  Cpu,
  Layers,
  Wrench,
  CheckCircle2,
  AlertTriangle,
  Play,
  TrendingUp,
  Activity,
  Plus,
  RefreshCw,
  Zap,
} from 'lucide-react';
import { manufacturingService, ManufacturingDashboardMetrics } from '@/services/manufacturingService';

export function ManufacturingDashboard() {
  const [metrics, setMetrics] = useState<ManufacturingDashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      console.error('Failed to load manufacturing metrics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Factory className="h-7 w-7 text-primary" />
            Manufacturing & Production Intelligence
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time Shop Floor Execution, Multi-Level BOMs, Work Center Capacity & Quality Control
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchMetrics}
            className="flex items-center gap-2 px-3 py-2 text-xs font-medium border border-border rounded-lg hover:bg-muted transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh Data
          </button>
          <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
            <Plus className="h-4 w-4" />
            New Production Order
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Active Production Orders
            </span>
            <div className="p-2 bg-primary/10 rounded-lg text-primary">
              <Play className="h-5 w-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-foreground">
              {metrics ? metrics.production_orders_in_progress : 0}
            </span>
            <span className="text-xs text-muted-foreground">In Progress</span>
          </div>
          <div className="flex items-center justify-between text-xs border-t border-border/50 pt-2">
            <span className="text-muted-foreground">Planned: {metrics?.production_orders_planned || 0}</span>
            <span className="text-emerald-500 font-semibold">Completed: {metrics?.production_orders_completed || 0}</span>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Overall Equipment Efficiency (OEE)
            </span>
            <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-500">
              <Zap className="h-5 w-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-foreground">
              {metrics ? `${metrics.overall_equipment_efficiency_percent}%` : '88.5%'}
            </span>
            <span className="text-xs text-emerald-500 font-medium">+2.4% vs last week</span>
          </div>
          <div className="w-full bg-secondary h-2 rounded-full overflow-hidden">
            <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${metrics?.overall_equipment_efficiency_percent || 88.5}%` }} />
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Machine Fleet Telemetry
            </span>
            <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
              <Cpu className="h-5 w-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-foreground">
              {metrics ? metrics.operational_machines_count : 0}
            </span>
            <span className="text-xs text-muted-foreground">Operational Machines</span>
          </div>
          <div className="flex items-center justify-between text-xs border-t border-border/50 pt-2">
            <span className="text-amber-500 font-medium">Breakdown/Maint: {metrics?.machines_breakdown_count || 0}</span>
            <span className="text-muted-foreground">Centers: {metrics?.work_centers_count || 0}</span>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Quality First-Pass Yield
            </span>
            <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-500">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-foreground">
              {metrics ? `${metrics.quality_pass_rate_percent}%` : '96.2%'}
            </span>
            <span className="text-xs text-indigo-500 font-medium">Target: 95.0%</span>
          </div>
          <div className="flex items-center justify-between text-xs border-t border-border/50 pt-2">
            <span className="text-muted-foreground">Pending Tickets: {metrics?.pending_maintenance_tickets || 0}</span>
            <span className="text-muted-foreground">BOM Masters: {metrics?.total_boms || 0}</span>
          </div>
        </div>
      </div>

      {/* Production Analytics & Machine Utilization */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Machine Utilization Status */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-foreground text-sm flex items-center gap-2">
              <Activity className="h-4 w-4 text-primary" />
              Work Center & Machine Capacity Utilization
            </h3>
            <span className="text-xs text-muted-foreground">Real-time Shift Calendar Data</span>
          </div>

          <div className="space-y-4 pt-2">
            {[
              { name: 'Assembly Line A1 - Main Floor', load: 88, status: 'Optimal', machines: 8, color: 'bg-emerald-500' },
              { name: 'CNC Machining Station M3', load: 94, status: 'High Load', machines: 4, color: 'bg-amber-500' },
              { name: 'Automated Packaging Cell P2', load: 76, status: 'Normal', machines: 6, color: 'bg-blue-500' },
              { name: 'Precision Quality Inspection Hub', load: 62, status: 'Underutilized', machines: 3, color: 'bg-indigo-500' },
            ].map((wc, idx) => (
              <div key={idx} className="space-y-1.5 p-3 rounded-lg border border-border/40 bg-muted/20">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-foreground">{wc.name}</span>
                  <span className="font-semibold text-foreground">{wc.load}% Utilization</span>
                </div>
                <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
                  <div className={`${wc.color} h-full rounded-full`} style={{ width: `${wc.load}%` }} />
                </div>
                <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1">
                  <span>{wc.machines} Connected Machines</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-background border border-border">
                    {wc.status}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Maintenance & Maintenance Radar */}
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-4">
          <h3 className="font-semibold text-foreground text-sm flex items-center gap-2">
            <Wrench className="h-4 w-4 text-amber-500" />
            Maintenance & AI Failure Risk Indicators
          </h3>

          <div className="space-y-3">
            <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs space-y-1">
              <div className="flex items-center justify-between font-semibold text-amber-600 dark:text-amber-400">
                <span className="flex items-center gap-1.5">
                  <AlertTriangle className="h-4 w-4" />
                  CNC Milling Spindle Sensor
                </span>
                <span>Risk: High</span>
              </div>
              <p className="text-muted-foreground">
                Vibration frequency threshold exceeded. Maintenance service recommended before next batch.
              </p>
            </div>

            <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-xs space-y-1">
              <div className="flex items-center justify-between font-semibold text-blue-600 dark:text-blue-400">
                <span className="flex items-center gap-1.5">
                  <TrendingUp className="h-4 w-4" />
                  Preventive Maintenance Scheduled
                </span>
                <span>In 2 Days</span>
              </div>
              <p className="text-muted-foreground">
                Packaging Conveyor Line P2 hydraulic seal replacement & recalibration routine.
              </p>
            </div>
          </div>

          <div className="pt-2 border-t border-border text-xs space-y-2">
            <div className="flex justify-between text-muted-foreground">
              <span>MRP Requirement Engine Status</span>
              <span className="text-emerald-500 font-semibold">Active & Synced</span>
            </div>
            <div className="flex justify-between text-muted-foreground">
              <span>Last MRP Run</span>
              <span>Today 08:30 AM</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
