import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  Clock,
  RefreshCw,
  UserCheck,
  CheckCircle,
  History,
  XCircle,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { observabilityService, Alert } from '@/services/observabilityService';

export function AlertCenter() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [filterStatus, setFilterStatus] = useState('');
  const [triageActionLoading, setTriageActionLoading] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await observabilityService.getAlerts(filterStatus || undefined);
      setAlerts(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [filterStatus]);

  const handleTriageAlert = async (alertId: string, action: 'acknowledged' | 'resolved') => {
    setTriageActionLoading(true);
    try {
      await observabilityService.updateAlertStatus(alertId, action);
      await fetchAlerts();
      setSelectedAlert(null);
    } catch (err) {
      console.error('Failed to update alert state:', err);
    } finally {
      setTriageActionLoading(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    let classes = 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/30';
    if (severity === 'warning') {
      classes = 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/30';
    } else if (severity === 'info') {
      classes = 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/30';
    }
    return (
      <span className={`px-2.5 py-0.5 rounded-full border text-[9px] font-bold ${classes}`}>
        {severity.toUpperCase()}
      </span>
    );
  };

  const getStatusBadge = (status: string) => {
    let classes = 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/30';
    if (status === 'acknowledged') {
      classes = 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/30';
    } else if (status === 'resolved') {
      classes = 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/30';
    }
    return (
      <span className={`px-2 py-0.5 rounded border text-[9px] font-bold ${classes}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  // Summarize count data
  const criticalCount = alerts.filter(a => a.severity === 'critical' && a.status === 'active').length;
  const warningCount = alerts.filter(a => a.severity === 'warning' && a.status === 'active').length;
  const acknowledgedCount = alerts.filter(a => a.status === 'acknowledged').length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Alert Center"
        subtitle="Manage metric alarms, acknowledge active incidents, and analyze transition audit trails."
        actions={
          <Button variant="outline" size="sm" onClick={fetchAlerts} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Incidents
          </Button>
        }
      />

      {/* Incident Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="p-4 flex items-center justify-between border-l-4 border-l-red-500 bg-card">
          <div className="space-y-1">
            <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Critical Alarms</span>
            <h4 className="text-xl font-bold text-foreground">{criticalCount} Active</h4>
          </div>
          <XCircle className="h-6 w-6 text-red-500" />
        </Card>

        <Card className="p-4 flex items-center justify-between border-l-4 border-l-amber-500 bg-card">
          <div className="space-y-1">
            <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Warnings pending</span>
            <h4 className="text-xl font-bold text-foreground">{warningCount} Active</h4>
          </div>
          <AlertTriangle className="h-6 w-6 text-amber-500" />
        </Card>

        <Card className="p-4 flex items-center justify-between border-l-4 border-l-blue-500 bg-card">
          <div className="space-y-1">
            <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Acknowledged Incidents</span>
            <h4 className="text-xl font-bold text-foreground">{acknowledgedCount} in triage</h4>
          </div>
          <UserCheck className="h-6 w-6 text-blue-500" />
        </Card>
      </div>

      {/* Filter panel */}
      <Card className="p-4 flex gap-4 items-center">
        <span className="text-xs font-bold text-muted-foreground uppercase">Incident Filters:</span>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="text-xs bg-secondary border border-border rounded-md px-3 py-1.5 text-foreground focus:outline-none focus:ring-1 focus:ring-primary w-44 font-semibold"
        >
          <option value="">All Statuses</option>
          <option value="active">Active Alarms</option>
          <option value="acknowledged">Acknowledged</option>
          <option value="resolved">Resolved</option>
        </select>
      </Card>

      {/* Incident List */}
      <Card className="overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/20 text-muted-foreground font-semibold uppercase tracking-wider text-[10px]">
                <th className="p-4">Incident Severity</th>
                <th className="p-4">Alarm Rule Name</th>
                <th className="p-4">Metric Checked</th>
                <th className="p-4">Threshold Condition</th>
                <th className="p-4">Status State</th>
                <th className="p-4">Time Triggered</th>
                <th className="p-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-medium text-foreground">
              {loading && alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-muted-foreground">
                    <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
                    Fetching metric alarms...
                  </td>
                </tr>
              ) : alerts.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-12 text-center text-muted-foreground">
                    <CheckCircle2 className="h-8 w-8 text-emerald-500 mx-auto mb-2" />
                    No active alert incidents recorded.
                  </td>
                </tr>
              ) : (
                alerts.map((alert) => (
                  <tr key={alert.id} className="hover:bg-muted/10">
                    <td className="p-4">{getSeverityBadge(alert.severity)}</td>
                    <td className="p-4">
                      <div className="space-y-0.5">
                        <span className="font-bold text-foreground">{alert.rule_name}</span>
                        {alert.description && (
                          <p className="text-[10px] text-muted-foreground line-clamp-1">{alert.description}</p>
                        )}
                      </div>
                    </td>
                    <td className="p-4 font-mono">{alert.metric_name}</td>
                    <td className="p-4 font-mono text-foreground">
                      {alert.comparison_operator} {alert.threshold} (Actual: {alert.current_value?.toFixed(2) || 'N/A'})
                    </td>
                    <td className="p-4">{getStatusBadge(alert.status)}</td>
                    <td className="p-4 text-muted-foreground">{new Date(alert.created_at).toLocaleString()}</td>
                    <td className="p-4 text-right space-x-1.5">
                      <Button size="xs" variant="outline" onClick={() => setSelectedAlert(alert)}>
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Incident Detail Modal */}
      {selectedAlert && (
        <Modal
          isOpen={!!selectedAlert}
          onClose={() => setSelectedAlert(null)}
          title="Incident Triage Center"
        >
          <div className="space-y-4 text-xs">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase font-bold">Alarm Rule Name</span>
              <h4 className="text-sm font-bold text-foreground">{selectedAlert.rule_name}</h4>
              <p className="text-[10px] text-muted-foreground">{selectedAlert.description || 'No description provided.'}</p>
            </div>

            <div className="grid grid-cols-2 gap-4 border-t border-b border-border py-3">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Severity</span>
                <p className="mt-0.5">{getSeverityBadge(selectedAlert.severity)}</p>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Current State</span>
                <p className="mt-0.5">{getStatusBadge(selectedAlert.status)}</p>
              </div>
            </div>

            {/* Actions for active/acknowledged alerts */}
            {selectedAlert.status !== 'resolved' && (
              <div className="bg-secondary p-3 rounded border space-y-2.5">
                <span className="text-[10px] font-bold text-muted-foreground uppercase">Incident Response Actions</span>
                <div className="flex gap-2">
                  {selectedAlert.status === 'active' && (
                    <Button
                      size="xs"
                      onClick={() => handleTriageAlert(selectedAlert.id, 'acknowledged')}
                      disabled={triageActionLoading}
                    >
                      <UserCheck className="h-3.5 w-3.5 mr-1" />
                      Acknowledge Alert
                    </Button>
                  )}
                  <Button
                    size="xs"
                    variant="outline"
                    className="border-emerald-200 text-emerald-700 hover:bg-emerald-50 dark:border-emerald-900/30 dark:text-emerald-400 dark:hover:bg-emerald-950/20"
                    onClick={() => handleTriageAlert(selectedAlert.id, 'resolved')}
                    disabled={triageActionLoading}
                  >
                    <CheckCircle className="h-3.5 w-3.5 mr-1" />
                    Resolve Incident
                  </Button>
                </div>
              </div>
            )}

            {/* History transition list */}
            <div className="space-y-2">
              <span className="text-[10px] text-muted-foreground uppercase font-bold flex items-center gap-1">
                <History className="h-3.5 w-3.5 text-muted-foreground" />
                Incident Lifecycle Audit Trace
              </span>
              <div className="border border-border rounded-md divide-y divide-border font-mono text-[10px] bg-secondary/20">
                {selectedAlert.history && selectedAlert.history.length > 0 ? (
                  selectedAlert.history.map((h, idx) => (
                    <div key={idx} className="p-2.5 flex justify-between items-start">
                      <div>
                        <div className="flex items-center gap-1.5">
                          <span className="font-semibold text-foreground">{h.status_from.toUpperCase()}</span>
                          <span className="text-muted-foreground">&rarr;</span>
                          <span className="font-bold text-primary">{h.status_to.toUpperCase()}</span>
                        </div>
                        {h.transition_reason && (
                          <p className="text-muted-foreground font-sans mt-0.5">{h.transition_reason}</p>
                        )}
                      </div>
                      <div className="text-right text-muted-foreground shrink-0">
                        <p className="font-bold">{h.changed_by || 'system'}</p>
                        <p className="text-[9px]">{new Date(h.timestamp).toLocaleTimeString()}</p>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="p-3 text-center text-muted-foreground">
                    No state history transitions logged.
                  </div>
                )}
              </div>
            </div>

            <div className="flex justify-end pt-2 border-t border-border">
              <Button size="sm" variant="ghost" onClick={() => setSelectedAlert(null)}>
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
export default AlertCenter;
