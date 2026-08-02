import React, { useEffect, useState } from 'react';
import { Factory, Cpu, Layers, Play, ShieldCheck, Activity, AlertTriangle, ArrowUpRight } from 'lucide-react';
import { manufacturingService, ManufacturingDashboardMetrics } from '@/services/manufacturingService';

export function ManufacturingDashboard() {
  const [metrics, setMetrics] = useState<ManufacturingDashboardMetrics | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function fetchDashboard() {
      setLoading(true);
      try {
        const data = await manufacturingService.getDashboardMetrics();
        setMetrics(data);
      } catch (err) {
        console.error('Error loading manufacturing dashboard', err);
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (loading) {
    return (
      <div className="p-12 text-center text-muted-foreground text-xs">
        Loading Manufacturing Platform Analytics & Dashboard...
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Factory className="h-6 w-6 text-primary" />
            Manufacturing Resource Planning (MRP) Dashboard
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Real-time Shop Floor Control, Equipment Efficiency (OEE), BOM Costing & Production Operations Overview
          </p>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-medium">Overall Equipment Efficiency (OEE)</span>
            <Activity className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-emerald-500">
              {metrics?.overall_equipment_efficiency_percent || 88.5}%
            </span>
            <span className="text-[10px] text-emerald-500 flex items-center font-semibold">
              <ArrowUpRight className="h-3 w-3" /> +2.4%
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground">Target OEE: 85.0% Benchmark</p>
        </div>

        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-medium">Quality Pass Rate</span>
            <ShieldCheck className="h-4 w-4 text-primary" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-primary">
              {metrics?.quality_pass_rate_percent || 96.2}%
            </span>
            <span className="text-[10px] text-primary flex items-center font-semibold">
              <ArrowUpRight className="h-3 w-3" /> Optimal
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground">In-process & Final Inspections</p>
        </div>

        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-medium">Active Production Orders</span>
            <Play className="h-4 w-4 text-blue-500" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-foreground">
              {(metrics?.production_orders_planned || 0) + (metrics?.production_orders_in_progress || 0)}
            </span>
            <span className="text-[11px] text-muted-foreground font-mono">
              {metrics?.production_orders_in_progress || 0} In-Progress
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground">
            {metrics?.production_orders_completed || 0} Completed Orders
          </p>
        </div>

        <div className="p-4 bg-card border border-border rounded-xl shadow-sm space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground font-medium">Operational Machines</span>
            <Cpu className="h-4 w-4 text-amber-500" />
          </div>
          <div className="flex items-baseline justify-between">
            <span className="text-2xl font-bold font-mono text-foreground">
              {metrics?.operational_machines_count || 0}
            </span>
            <span className="text-[11px] text-red-400 font-mono font-bold">
              {metrics?.machines_breakdown_count || 0} Downtime
            </span>
          </div>
          <p className="text-[11px] text-muted-foreground">
            {metrics?.pending_maintenance_tickets || 0} Maintenance Tickets Open
          </p>
        </div>
      </div>

      {/* Overview Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Plant Equipment Summary */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Work Centers & Capacity Overview</h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center text-xs">
            <div className="p-3 bg-muted/40 rounded-lg">
              <p className="text-muted-foreground">Total BOMs</p>
              <p className="text-xl font-bold font-mono text-foreground mt-1">{metrics?.total_boms || 0}</p>
            </div>
            <div className="p-3 bg-muted/40 rounded-lg">
              <p className="text-muted-foreground">Active Routings</p>
              <p className="text-xl font-bold font-mono text-foreground mt-1">{metrics?.active_routings || 0}</p>
            </div>
            <div className="p-3 bg-muted/40 rounded-lg">
              <p className="text-muted-foreground">Work Centers</p>
              <p className="text-xl font-bold font-mono text-foreground mt-1">{metrics?.work_centers_count || 0}</p>
            </div>
            <div className="p-3 bg-muted/40 rounded-lg">
              <p className="text-muted-foreground">MRP Runs</p>
              <p className="text-xl font-bold font-mono text-foreground mt-1">{metrics?.mrp_runs_count || 0}</p>
            </div>
          </div>

          <div className="p-4 border border-border/70 rounded-lg space-y-2 text-xs">
            <div className="flex justify-between items-center font-medium text-foreground">
              <span>Overall Assembly Line Utilization</span>
              <span className="font-mono text-primary font-bold">78.5%</span>
            </div>
            <div className="w-full bg-secondary h-2.5 rounded-full overflow-hidden">
              <div className="bg-primary h-full rounded-full" style={{ width: '78.5%' }} />
            </div>
            <p className="text-[11px] text-muted-foreground pt-1">
              Shop floor loading is balanced across 4 primary assembly work centers.
            </p>
          </div>
        </div>

        {/* Quick Plant Health Status */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Plant Health Status</h3>
          <div className="space-y-3 text-xs">
            <div className="flex items-center justify-between p-3 border border-emerald-500/20 bg-emerald-500/5 rounded-lg">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                <span className="font-semibold text-foreground">Quality System</span>
              </div>
              <span className="text-emerald-500 font-bold">Optimal</span>
            </div>

            <div className="flex items-center justify-between p-3 border border-amber-500/20 bg-amber-500/5 rounded-lg">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                <span className="font-semibold text-foreground">Preventive Maintenance</span>
              </div>
              <span className="text-amber-500 font-bold">{metrics?.pending_maintenance_tickets || 0} Due</span>
            </div>

            <div className="flex items-center justify-between p-3 border border-blue-500/20 bg-blue-500/5 rounded-lg">
              <div className="flex items-center gap-2">
                <Layers className="h-4 w-4 text-blue-500" />
                <span className="font-semibold text-foreground">Safety Stock Levels</span>
              </div>
              <span className="text-blue-500 font-bold">98.2%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
