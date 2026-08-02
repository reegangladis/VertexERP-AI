import React, { useEffect, useState } from 'react';
import {
  Server,
  CheckCircle2,
  AlertCircle,
  XCircle,
  RefreshCw,
  Clock,
  ShieldCheck,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { observabilityService, SystemHealthData } from '@/services/observabilityService';

export function SystemHealth() {
  const [healthData, setHealthData] = useState<SystemHealthData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadHealth = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await observabilityService.getSystemHealth();
      setHealthData(data);
    } catch (err: any) {
      console.error(err);
      setError('Unable to load server health parameters. Please verify backend connection.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
  }, []);

  const formatUptime = (seconds: number) => {
    const d = Math.floor(seconds / (3600 * 24));
    const h = Math.floor((seconds % (3600 * 24)) / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    if (d > 0) return `${d}d ${h}h`;
    if (h > 0) return `${h}h ${m}m`;
    return `${m} mins`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle2 className="h-5 w-5 text-emerald-500" />;
      case 'degraded':
        return <AlertCircle className="h-5 w-5 text-amber-500" />;
      default:
        return <XCircle className="h-5 w-5 text-red-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    let classes = 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/30';
    if (status === 'degraded') {
      classes = 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/30';
    } else if (status === 'unhealthy') {
      classes = 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/30';
    }
    return (
      <span className={`px-2.5 py-0.5 rounded-full border text-[10px] font-bold ${classes}`}>
        {status.toUpperCase()}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="System Health"
        subtitle="Monitors core modules, REST APIs, databases, authentication gates, and microservice uptimes."
        actions={
          <Button variant="outline" size="sm" onClick={loadHealth} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Run Diagnostics
          </Button>
        }
      />

      {error && (
        <Card className="p-4 border-l-4 border-l-red-500 bg-red-50 dark:bg-red-950/10 text-red-700 dark:text-red-400 text-xs">
          <div className="flex items-center">
            <XCircle className="h-4 w-4 mr-2" />
            <p className="font-semibold">{error}</p>
          </div>
        </Card>
      )}

      {/* Summary Diagnostics */}
      {healthData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="p-4 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Overall Liveness</span>
              <div className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 rounded-full ${healthData.status === 'healthy' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                <span className="text-lg font-bold text-foreground capitalize">{healthData.status}</span>
              </div>
            </div>
            {getStatusIcon(healthData.status)}
          </Card>

          <Card className="p-4 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">System Version</span>
              <h4 className="text-lg font-bold text-foreground">v{healthData.version}</h4>
            </div>
            <ShieldCheck className="h-5 w-5 text-indigo-500" />
          </Card>

          <Card className="p-4 flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Operational SLA</span>
              <h4 className="text-lg font-bold text-foreground">{healthData.uptime_ratio_percent}%</h4>
            </div>
            <Clock className="h-5 w-5 text-blue-500" />
          </Card>
        </div>
      )}

      {/* Services List Table */}
      <Card className="overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <h4 className="text-sm font-bold text-foreground font-mono">Microservice Diagnostics</h4>
          <p className="text-xs text-muted-foreground">Detailed status parameters for ERP database connectors and platform services.</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-border bg-muted/20 text-muted-foreground font-semibold uppercase tracking-wider text-[10px]">
                <th className="p-4">Service Name</th>
                <th className="p-4">Liveness / Readiness</th>
                <th className="p-4">Latency</th>
                <th className="p-4">Uptime</th>
                <th className="p-4">State</th>
                <th className="p-4">Dependencies</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-medium text-foreground">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-muted-foreground">
                    <RefreshCw className="h-6 w-6 animate-spin mx-auto mb-2 text-primary" />
                    Running service diagnostics...
                  </td>
                </tr>
              ) : healthData?.services.map((item, idx) => (
                <tr key={idx} className="hover:bg-muted/10 transition-colors">
                  <td className="p-4">
                    <div className="flex items-center gap-2">
                      <div className="p-1 rounded bg-secondary text-foreground">
                        <Server className="h-3.5 w-3.5" />
                      </div>
                      <span className="font-bold text-foreground">{item.name}</span>
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                        item.liveness 
                          ? 'bg-emerald-50/50 text-emerald-600 border-emerald-100 dark:bg-emerald-950/10' 
                          : 'bg-red-50/50 text-red-600 border-red-100 dark:bg-red-950/10'
                      }`}>
                        Live: {item.liveness ? 'PASS' : 'FAIL'}
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[9px] font-bold border ${
                        item.readiness 
                          ? 'bg-emerald-50/50 text-emerald-600 border-emerald-100 dark:bg-emerald-950/10' 
                          : 'bg-red-50/50 text-red-600 border-red-100 dark:bg-red-950/10'
                      }`}>
                        Ready: {item.readiness ? 'PASS' : 'FAIL'}
                      </span>
                    </div>
                  </td>
                  <td className="p-4 text-foreground font-mono">{item.latency_ms.toFixed(1)} ms</td>
                  <td className="p-4 text-muted-foreground">{formatUptime(item.uptime_seconds)}</td>
                  <td className="p-4">{getStatusBadge(item.status)}</td>
                  <td className="p-4">
                    {item.dependency_status && Object.keys(item.dependency_status).length > 0 ? (
                      <div className="flex flex-wrap gap-1.5">
                        {Object.entries(item.dependency_status).map(([dep, status]) => (
                          <span key={dep} className={`px-1.5 py-0.5 rounded text-[9px] font-bold flex items-center gap-1 ${
                            status === 'healthy' 
                              ? 'bg-emerald-50 text-emerald-600 border border-emerald-100 dark:bg-emerald-950/10' 
                              : 'bg-red-50 text-red-600 border border-red-100 dark:bg-red-950/10'
                          }`}>
                            <span className={`h-1 w-1 rounded-full ${status === 'healthy' ? 'bg-emerald-500' : 'bg-red-500'}`} />
                            {dep}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-muted-foreground text-[10px]">None</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
export default SystemHealth;
