import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Activity,
  ShieldAlert,
  Server,
  FileText,
  TrendingUp,
  GitBranch,
  DollarSign,
  Brain,
  CheckCircle2,
  AlertTriangle,
  Clock,
  RefreshCw,
  ArrowRight,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { observabilityService, Alert, SystemHealthData } from '@/services/observabilityService';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export function MonitoringDashboard() {
  const navigate = useNavigate();
  const [health, setHealth] = useState<SystemHealthData | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [metricsData, setMetricsData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [healthRes, alertsRes] = await Promise.all([
        observabilityService.getSystemHealth().catch(() => null),
        observabilityService.getAlerts('active').catch(() => []),
      ]);
      
      setHealth(healthRes);
      setAlerts(alertsRes);

      // Generate simulated metric time-series data for chart
      const mockedTimeline = [];
      const baseTime = Date.now();
      for (let i = 10; i >= 0; i--) {
        mockedTimeline.push({
          time: new Date(baseTime - i * 60000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          cpu: Math.floor(40 + Math.random() * 30),
          memory: Math.floor(65 + Math.random() * 10),
          latency: Math.floor(80 + Math.random() * 150),
        });
      }
      setMetricsData(mockedTimeline);
    } catch (err) {
      console.error('Failed to load monitoring dashboard telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const totalAlerts = alerts.length;
  const isHealthy = health?.status === 'healthy';

  const modules = [
    {
      title: 'System Health',
      desc: 'Check live status, liveness/readiness indicators, and uptimes of dependencies.',
      path: '/observability/health',
      icon: <Server className="h-5 w-5" />,
      color: 'text-indigo-600 bg-indigo-50 dark:bg-indigo-950/30',
    },
    {
      title: 'Log Explorer',
      desc: 'Search, audit, and analyze centralized structured records with request IDs.',
      path: '/observability/logs',
      icon: <FileText className="h-5 w-5" />,
      color: 'text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30',
    },
    {
      title: 'Metrics Explorer',
      desc: 'Visualize real-time system performance plots for CPU, memory, and database.',
      path: '/observability/metrics',
      icon: <TrendingUp className="h-5 w-5" />,
      color: 'text-blue-600 bg-blue-50 dark:bg-blue-950/30',
    },
    {
      title: 'Trace Viewer',
      desc: 'Inspect distributed traces, call execution spans, and service maps.',
      path: '/observability/traces',
      icon: <GitBranch className="h-5 w-5" />,
      color: 'text-purple-600 bg-purple-50 dark:bg-purple-950/30',
    },
    {
      title: 'Alert Center',
      desc: 'Triage trigger thresholds alerts, acknowledge incidents, and view history.',
      path: '/observability/alerts',
      icon: <ShieldAlert className="h-5 w-5" />,
      color: 'text-amber-600 bg-amber-50 dark:bg-amber-950/30',
    },
    {
      title: 'Business telemetry',
      desc: 'Observe executive revenue charts, order rates, inventory, and HR turnover KPI values.',
      path: '/observability/business',
      icon: <DollarSign className="h-5 w-5" />,
      color: 'text-pink-600 bg-pink-50 dark:bg-pink-950/30',
    },
    {
      title: 'AI Monitoring',
      desc: 'Monitor vector retrieval, prompt token count usages, and embedding latency metrics.',
      path: '/observability/ai',
      icon: <Brain className="h-5 w-5" />,
      color: 'text-teal-600 bg-teal-50 dark:bg-teal-950/30',
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Monitoring Platform"
        subtitle="Unified, vendor-neutral control dashboard tracking host health, API latency, tracing, logs, and alert rooms."
        actions={
          <Button variant="outline" size="sm" onClick={loadData} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </Button>
        }
      />

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-l-emerald-500 bg-card hover:shadow-md transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Overall Status</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">
                {isHealthy ? 'Healthy' : 'Degraded'}
              </h3>
              <p className="text-xs text-emerald-600 dark:text-emerald-400 flex items-center mt-1">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                All vital signs active
              </p>
            </div>
            <div className={`p-2 rounded-lg text-emerald-600 bg-emerald-50 dark:bg-emerald-950/30`}>
              <Activity className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className={`p-4 border-l-4 ${totalAlerts > 0 ? 'border-l-amber-500' : 'border-l-indigo-500'} bg-card hover:shadow-md transition-all`}>
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Active Alerts</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">{totalAlerts}</h3>
              <p className={`text-xs ${totalAlerts > 0 ? 'text-amber-600' : 'text-indigo-600'} flex items-center mt-1`}>
                <AlertTriangle className="h-3 w-3 mr-1" />
                {totalAlerts > 0 ? 'Awaiting acknowledgement' : 'Zero breaches detected'}
              </p>
            </div>
            <div className={`p-2 rounded-lg ${totalAlerts > 0 ? 'text-amber-600 bg-amber-50 dark:bg-amber-950/30' : 'text-indigo-600 bg-indigo-50 dark:bg-indigo-950/30'}`}>
              <ShieldAlert className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-blue-500 bg-card hover:shadow-md transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Uptime SLA</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">99.98%</h3>
              <p className="text-xs text-blue-600 flex items-center mt-1">
                <Clock className="h-3 w-3 mr-1" />
                Current billing cycle
              </p>
            </div>
            <div className="p-2 rounded-lg text-blue-600 bg-blue-50 dark:bg-blue-950/30">
              <Server className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-purple-500 bg-card hover:shadow-md transition-all">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Avg API Latency</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">45.2 ms</h3>
              <p className="text-xs text-purple-600 flex items-center mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                p95 response duration
              </p>
            </div>
            <div className="p-2 rounded-lg text-purple-600 bg-purple-50 dark:bg-purple-950/30">
              <Activity className="h-6 w-6" />
            </div>
          </div>
        </Card>
      </div>

      {/* Main Grid: Chart & Incident lists */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Visual telemetry plot */}
        <Card className="p-5 lg:col-span-2 space-y-4">
          <div>
            <h4 className="text-sm font-bold text-foreground">Real-time Performance Latency</h4>
            <p className="text-xs text-muted-foreground">Aggregated microservice network delays and host metrics.</p>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={metricsData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorCpu" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorLatency" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted-foreground/10" />
                <XAxis dataKey="time" className="text-[10px] fill-muted-foreground" />
                <YAxis className="text-[10px] fill-muted-foreground" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--color-border)', borderRadius: '8px' }} />
                <Area type="monotone" dataKey="cpu" name="CPU Usage (%)" stroke="#3b82f6" fillOpacity={1} fill="url(#colorCpu)" />
                <Area type="monotone" dataKey="latency" name="Latency (ms)" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorLatency)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Active incidents triage panel */}
        <Card className="p-5 space-y-4">
          <div className="flex justify-between items-center">
            <div>
              <h4 className="text-sm font-bold text-foreground">Active Incidents</h4>
              <p className="text-xs text-muted-foreground">Triggered alarms requiring triage.</p>
            </div>
            <Button size="xs" variant="ghost" onClick={() => navigate('/observability/alerts')}>
              View All
            </Button>
          </div>

          <div className="space-y-3 overflow-y-auto max-h-[260px] pr-1">
            {alerts.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-44 border border-dashed border-border rounded-lg p-4 text-center">
                <CheckCircle2 className="h-8 w-8 text-emerald-500 mb-2" />
                <p className="text-xs font-semibold text-foreground">All systems functional</p>
                <p className="text-[10px] text-muted-foreground mt-0.5">No metrics currently violating threshold boundaries.</p>
              </div>
            ) : (
              alerts.map(a => (
                <div
                  key={a.id}
                  className={`p-3 rounded-lg border text-xs flex justify-between items-start transition-colors ${
                    a.severity === 'critical'
                      ? 'border-red-100 bg-red-50/50 dark:border-red-950/20 dark:bg-red-950/5'
                      : 'border-amber-100 bg-amber-50/50 dark:border-amber-950/20 dark:bg-amber-950/5'
                  }`}
                >
                  <div className="space-y-1">
                    <div className="flex items-center gap-1.5">
                      <span className={`h-2 w-2 rounded-full ${a.severity === 'critical' ? 'bg-red-500' : 'bg-amber-500'}`} />
                      <span className="font-bold text-foreground">{a.rule_name}</span>
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-2">{a.description}</p>
                  </div>
                  <Button size="xs" variant="outline" className="ml-2 py-0.5" onClick={() => navigate('/observability/alerts')}>
                    Triage
                  </Button>
                </div>
              ))
            )}
          </div>
        </Card>
      </div>

      {/* Modular Navigation Grid */}
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-bold text-foreground">Observability Modules</h4>
          <p className="text-xs text-muted-foreground">Access granular telemetry components across core platforms.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {modules.map((m, idx) => (
            <Card
              key={idx}
              className="p-4 hover:shadow-lg hover:-translate-y-0.5 transition-all cursor-pointer bg-card flex flex-col justify-between"
              onClick={() => navigate(m.path)}
            >
              <div className="space-y-3">
                <div className={`p-2 w-fit rounded-lg ${m.color}`}>
                  {m.icon}
                </div>
                <div className="space-y-1">
                  <h5 className="text-xs font-bold text-foreground">{m.title}</h5>
                  <p className="text-[10px] text-muted-foreground line-clamp-2">{m.desc}</p>
                </div>
              </div>
              <div className="pt-4 flex items-center justify-end text-[10px] font-bold text-primary">
                Open module
                <ArrowRight className="h-3 w-3 ml-1" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
export default MonitoringDashboard;
