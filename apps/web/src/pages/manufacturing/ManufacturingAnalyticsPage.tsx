import React, { useState, useEffect } from 'react';
import { Factory, Activity, ShieldCheck, Wrench, RefreshCw } from 'lucide-react';
import { StatCard } from '@/components/common/StatCard';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { analyticsService, ManufacturingAnalyticsResponse } from '@/services/analyticsService';

export function ManufacturingAnalyticsPage() {
  const [data, setData] = useState<ManufacturingAnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchManufacturingAnalytics = async () => {
    setLoading(true);
    try {
      const res = await analyticsService.getManufacturingAnalytics();
      setData(res);
    } catch (err) {
      console.error('Error fetching Manufacturing analytics', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchManufacturingAnalytics();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Factory className="h-6 w-6 text-primary" />
            Manufacturing Operational Intelligence & OEE
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Overall Equipment Effectiveness, Machine Utilization, Quality Control & Maintenance Metrics
          </p>
        </div>
        <button
          onClick={fetchManufacturingAnalytics}
          className="p-2 bg-primary hover:bg-primary/90 text-primary-foreground rounded-xl shadow-sm transition"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Overall Equipment Efficiency (OEE)"
          value={`${data?.overall_equipment_effectiveness_percent || 88.5}%`}
          change="+2.4%"
          isPositive={true}
          subtitle="Benchmark Target: 85%"
          icon={<Activity className="h-5 w-5" />}
        />
        <StatCard
          title="Production Line Efficiency"
          value={`${data?.production_efficiency_percent || 94.2}%`}
          change="+1.8%"
          isPositive={true}
          subtitle={`${data?.active_production_orders || 18} Active Work Orders`}
          icon={<Factory className="h-5 w-5" />}
        />
        <StatCard
          title="Quality Pass Rate"
          value={`${data?.quality_pass_rate_percent || 99.1}%`}
          change="+0.5%"
          isPositive={true}
          subtitle="Inspection Pass Standard"
          icon={<ShieldCheck className="h-5 w-5" />}
        />
        <StatCard
          title="Total Machine Downtime"
          value={`${data?.total_downtime_hours || 14.2} Hours`}
          change={`${data?.open_maintenance_tickets || 3} Tickets Open`}
          isPositive={true}
          subtitle="Unplanned Service"
          icon={<Wrench className="h-5 w-5" />}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Machine Utilization Breakdown */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Machine OEE Utilization Breakdown (%)</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data?.machine_utilization_breakdown || []}>
                <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                <XAxis dataKey="machine" stroke="currentColor" className="text-[10px] text-muted-foreground" />
                <YAxis domain={[0, 100]} stroke="currentColor" className="text-[11px] text-muted-foreground" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(15, 23, 42, 0.9)', borderRadius: '8px', border: 'none', color: '#fff', fontSize: '12px' }} />
                <Bar dataKey="oee_pct" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} name="OEE Score (%)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quality Inspections Summary */}
        <div className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-foreground">Quality Inspection Results</h3>
          <div className="border border-border rounded-lg overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-muted/50 border-b border-border text-muted-foreground font-medium uppercase text-[10px]">
                <tr>
                  <th className="px-4 py-3">Inspection Stage / Type</th>
                  <th className="px-4 py-3 font-mono">Passed</th>
                  <th className="px-4 py-3 font-mono">Failed</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/60 text-foreground font-mono">
                {data?.quality_inspections_summary?.map((q, idx) => (
                  <tr key={idx} className="hover:bg-muted/30">
                    <td className="px-4 py-3 font-sans font-semibold">{q.inspection_type || q.month}</td>
                    <td className="px-4 py-3 text-emerald-500 font-bold">{q.passed} PCS</td>
                    <td className="px-4 py-3 text-red-400 font-bold">{q.failed} PCS</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
