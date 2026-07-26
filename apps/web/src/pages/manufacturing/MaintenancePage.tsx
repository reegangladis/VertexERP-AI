import React, { useEffect, useState } from 'react';
import { Wrench, Plus, AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import { manufacturingService, MaintenanceRequest } from '@/services/manufacturingService';

export function MaintenancePage() {
  const [requests, setRequests] = useState<MaintenanceRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const data = await manufacturingService.getMaintenanceRequests();
      setRequests(data);
    } catch (err) {
      console.error('Error fetching maintenance requests', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Wrench className="h-6 w-6 text-amber-500" />
            Preventive Maintenance & Breakdown Records
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Service Requests, Machine Repair History, Downtime Logs & Technician Dispatch
          </p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-xs font-semibold bg-primary text-primary-foreground rounded-lg shadow hover:bg-primary/90 transition-colors">
          <Plus className="h-4 w-4" />
          File Maintenance Request
        </button>
      </div>

      <div className="space-y-4">
        {requests.map((req) => (
          <div key={req.id} className="bg-card border border-border rounded-xl p-5 shadow-sm space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/50 pb-2">
              <div className="flex items-center gap-3">
                <span className="font-mono text-xs font-bold px-2 py-0.5 rounded bg-muted text-foreground">
                  {req.ticket_number}
                </span>
                <h3 className="font-bold text-base text-foreground">{req.title}</h3>
              </div>
              <div className="flex items-center gap-2 text-xs">
                <span className="font-semibold text-amber-500">{req.priority} Priority</span>
                <span className="px-2 py-0.5 rounded bg-muted text-muted-foreground font-medium">{req.status}</span>
              </div>
            </div>

            <p className="text-xs text-muted-foreground">{req.description || 'No detailed issue breakdown provided.'}</p>

            <div className="flex flex-wrap items-center justify-between text-xs text-muted-foreground pt-2">
              <span>Technician: {req.assigned_technician || 'Unassigned'}</span>
              <span>Type: {req.issue_type}</span>
              <span>Reported At: {new Date(req.reported_at).toLocaleString()}</span>
            </div>
          </div>
        ))}

        {requests.length === 0 && !loading && (
          <div className="text-center py-12 text-xs text-muted-foreground bg-card border border-border rounded-xl">
            No maintenance requests registered.
          </div>
        )}
      </div>
    </div>
  );
}
