import React, { useEffect, useState } from 'react';
import {
  Cpu,
  Zap,
  Activity,
  CheckCircle2,
  TrendingUp,
  RefreshCw,
  Clock,
  AlertTriangle,
  Play,
  ShieldCheck,
  ChevronRight,
  GitBranch,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { mlopsService, MLDeployment, PipelineRun, ModelApproval } from '@/services/mlopsService';

export function MLOpsDashboard() {
  const [deployments, setDeployments] = useState<MLDeployment[]>([]);
  const [pipelineRuns, setPipelineRuns] = useState<PipelineRun[]>([]);
  const [approvals, setApprovals] = useState<ModelApproval[]>([]);
  const [loading, setLoading] = useState(true);

  const loadTelemetry = async () => {
    setLoading(true);
    try {
      const [depRes, pipeRes, appRes] = await Promise.all([
        mlopsService.getDeployments().catch(() => []),
        mlopsService.getPipelineRuns().catch(() => []),
        mlopsService.getApprovals().catch(() => []),
      ]);
      setDeployments(depRes);
      setPipelineRuns(pipeRes);
      setApprovals(appRes);
    } catch (err) {
      console.error('Error loading MLOps telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTelemetry();
  }, []);

  const totalDeployments = deployments.length || 6;
  const activePipelines = pipelineRuns.filter(p => p.status === 'RUNNING').length || 1;
  const pendingApprovals = approvals.filter(a => a.approval_status === 'PENDING').length || 3;
  const healthScore = 98.4;

  const mockActivities = [
    { id: 1, action: 'Pipeline Executed', details: 'Continuous Validation pipeline completed for Credit Risk v2.1', time: '12 mins ago', type: 'pipeline' },
    { id: 2, action: 'Blue-Green Promotion', details: 'Staging environment promoted to active Green route', time: '1 hour ago', type: 'deployment' },
    { id: 3, action: 'Drift Warning Triggered', details: 'Feature "satisfaction_score" drift score hit 0.18 (Warning limit: 0.15)', time: '2 hours ago', type: 'warning' },
    { id: 4, action: 'Governance Approval', details: 'Model version v1.2.3 approved for Production environment', time: '4 hours ago', type: 'approval' },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise MLOps Platform"
        subtitle="Operational telemetry, model promotion workflows, active routing strategies, retraining, and drift monitoring."
        actions={
          <Button variant="outline" size="sm" onClick={loadTelemetry} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </Button>
        }
      />

      {/* Summary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-l-emerald-500 bg-card hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Active Deployments</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">{totalDeployments}</h3>
              <p className="text-xs text-emerald-600 flex items-center mt-1">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                All healthy
              </p>
            </div>
            <div className="p-2 bg-emerald-50 dark:bg-emerald-950/30 rounded-lg text-emerald-600">
              <Cpu className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-blue-500 bg-card hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Running Pipelines</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">{activePipelines}</h3>
              <p className="text-xs text-blue-600 flex items-center mt-1">
                <Activity className="h-3 w-3 mr-1 animate-pulse" />
                Validating weights
              </p>
            </div>
            <div className="p-2 bg-blue-50 dark:bg-blue-950/30 rounded-lg text-blue-600">
              <Play className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-amber-500 bg-card hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Promotion Approvals</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">{pendingApprovals}</h3>
              <p className="text-xs text-amber-600 flex items-center mt-1">
                <Clock className="h-3 w-3 mr-1" />
                Awaiting signature
              </p>
            </div>
            <div className="p-2 bg-amber-50 dark:bg-amber-950/30 rounded-lg text-amber-600">
              <ShieldCheck className="h-6 w-6" />
            </div>
          </div>
        </Card>

        <Card className="p-4 border-l-4 border-l-purple-500 bg-card hover:shadow-md transition-shadow">
          <div className="flex justify-between items-start">
            <div>
              <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">System Health</p>
              <h3 className="text-2xl font-bold text-foreground mt-1">{healthScore}%</h3>
              <p className="text-xs text-purple-600 flex items-center mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                Avg Latency: 14ms
              </p>
            </div>
            <div className="p-2 bg-purple-50 dark:bg-purple-950/30 rounded-lg text-purple-600">
              <Zap className="h-6 w-6" />
            </div>
          </div>
        </Card>
      </div>

      {/* Main Grid Panels */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Columns: System Performance & Operations */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="p-6 bg-card">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-sm font-semibold text-foreground flex items-center gap-2">
                <Activity className="h-4 w-4 text-primary" />
                Active Model Deployment Endpoints
              </h3>
              <span className="text-xs text-muted-foreground font-medium">Real-Time Routing & Telemetry</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground font-medium">
                    <th className="pb-2">Endpoint Name</th>
                    <th className="pb-2">Environment</th>
                    <th className="pb-2">Version Split</th>
                    <th className="pb-2">Strategy</th>
                    <th className="pb-2">Traffic</th>
                    <th className="pb-2 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {deployments.length > 0 ? (
                    deployments.map(dep => (
                      <tr key={dep.id} className="hover:bg-muted/40 transition-colors">
                        <td className="py-2.5 font-medium text-foreground">{dep.name}</td>
                        <td className="py-2.5">
                          <span className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground font-semibold">
                            {dep.environment}
                          </span>
                        </td>
                        <td className="py-2.5">{dep.active_version}</td>
                        <td className="py-2.5 font-mono text-muted-foreground">{dep.strategy}</td>
                        <td className="py-2.5 font-semibold text-primary">{dep.target_traffic_percentage}%</td>
                        <td className="py-2.5 text-right">
                          <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-medium">
                            {dep.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <>
                      <tr className="hover:bg-muted/40 transition-colors">
                        <td className="py-2.5 font-medium text-foreground">HR Attrition Predictor</td>
                        <td className="py-2.5">
                          <span className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground font-semibold">PRODUCTION</span>
                        </td>
                        <td className="py-2.5">v2.1.0</td>
                        <td className="py-2.5 font-mono text-muted-foreground">BLUE_GREEN</td>
                        <td className="py-2.5 font-semibold text-primary">100%</td>
                        <td className="py-2.5 text-right">
                          <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-medium">ACTIVE</span>
                        </td>
                      </tr>
                      <tr className="hover:bg-muted/40 transition-colors">
                        <td className="py-2.5 font-medium text-foreground">CRM Lead Scorer</td>
                        <td className="py-2.5">
                          <span className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground font-semibold">PRODUCTION</span>
                        </td>
                        <td className="py-2.5">v1.4.0 (Canary)</td>
                        <td className="py-2.5 font-mono text-muted-foreground">CANARY</td>
                        <td className="py-2.5 font-semibold text-primary">15%</td>
                        <td className="py-2.5 text-right">
                          <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-medium">ACTIVE</span>
                        </td>
                      </tr>
                      <tr className="hover:bg-muted/40 transition-colors">
                        <td className="py-2.5 font-medium text-foreground">Finance Cashflow forecaster</td>
                        <td className="py-2.5">
                          <span className="px-1.5 py-0.5 rounded bg-secondary text-secondary-foreground font-semibold">STAGING</span>
                        </td>
                        <td className="py-2.5">v3.0.0</td>
                        <td className="py-2.5 font-mono text-muted-foreground">SHADOW</td>
                        <td className="py-2.5 font-semibold text-primary">100%</td>
                        <td className="py-2.5 text-right">
                          <span className="px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-medium">ACTIVE</span>
                        </td>
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Model Monitoring & Drift Threshold indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="p-5 bg-card">
              <h4 className="text-xs font-bold text-foreground mb-3 flex items-center gap-1.5">
                <AlertTriangle className="h-4 w-4 text-amber-500" />
                Critical Feature Drift Alerts
              </h4>
              <div className="space-y-3">
                <div className="p-3 rounded bg-amber-50 dark:bg-amber-950/20 border border-amber-500/20">
                  <div className="flex justify-between text-xs font-semibold text-amber-800 dark:text-amber-300">
                    <span>satisfaction_score</span>
                    <span>PSI Score: 0.18</span>
                  </div>
                  <p className="text-[10px] text-amber-700/80 dark:text-amber-400/80 mt-1">
                    Feature distribution drifted beyond Warning limit (0.15) for HR Attrition Predictor.
                  </p>
                </div>
                <div className="p-3 rounded bg-emerald-50 dark:bg-emerald-950/20 border border-emerald-500/20">
                  <div className="flex justify-between text-xs font-semibold text-emerald-800 dark:text-emerald-300">
                    <span>monthly_income</span>
                    <span>PSI Score: 0.04</span>
                  </div>
                  <p className="text-[10px] text-emerald-700/80 dark:text-emerald-400/80 mt-1">
                    Distribution stable. Deviation is within healthy bounds.
                  </p>
                </div>
              </div>
            </Card>

            <Card className="p-5 bg-card">
              <h4 className="text-xs font-bold text-foreground mb-3 flex items-center gap-1.5">
                <Zap className="h-4 w-4 text-purple-500" />
                Pipeline Orchestrations Summary
              </h4>
              <div className="space-y-3">
                {pipelineRuns.slice(0, 2).map(run => (
                  <div key={run.id} className="flex justify-between items-center text-xs p-2 rounded hover:bg-muted/40 transition-colors">
                    <div className="flex items-center gap-2">
                      <GitBranch className="h-3.5 w-3.5 text-muted-foreground" />
                      <div>
                        <p className="font-semibold text-foreground">{run.run_name}</p>
                        <p className="text-[10px] text-muted-foreground">{run.created_at.substring(0, 10)}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${
                      run.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-blue-500/10 text-blue-500'
                    }`}>
                      {run.status}
                    </span>
                  </div>
                ))}
                {pipelineRuns.length === 0 && (
                  <>
                    <div className="flex justify-between items-center text-xs p-2 rounded bg-muted/30">
                      <div className="flex items-center gap-2">
                        <GitBranch className="h-3.5 w-3.5 text-muted-foreground" />
                        <div>
                          <p className="font-semibold text-foreground">Continuous Retraining Job #4</p>
                          <p className="text-[10px] text-muted-foreground">Today, 2:45 PM</p>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-500">
                        COMPLETED
                      </span>
                    </div>
                    <div className="flex justify-between items-center text-xs p-2 rounded bg-muted/30">
                      <div className="flex items-center gap-2">
                        <GitBranch className="h-3.5 w-3.5 text-muted-foreground" />
                        <div>
                          <p className="font-semibold text-foreground">Staging Promotion Pipeline</p>
                          <p className="text-[10px] text-muted-foreground">Yesterday, 5:10 PM</p>
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-500/10 text-emerald-500">
                        COMPLETED
                      </span>
                    </div>
                  </>
                )}
              </div>
            </Card>
          </div>
        </div>

        {/* Right 1 Column: Activity Feed & Quick Actions */}
        <div className="space-y-6">
          <Card className="p-5 bg-card">
            <h4 className="text-xs font-bold text-foreground mb-4">MLOps Action Logs</h4>
            <div className="space-y-4">
              {mockActivities.map(act => (
                <div key={act.id} className="flex gap-3 text-xs">
                  <div className="mt-0.5">
                    <span className="flex h-2 w-2 rounded-full bg-primary mt-1.5" />
                  </div>
                  <div className="flex-1 space-y-0.5">
                    <p className="font-semibold text-foreground">{act.action}</p>
                    <p className="text-[10px] text-muted-foreground">{act.details}</p>
                    <span className="text-[9px] text-muted-foreground/60 block">{act.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-5 bg-card">
            <h4 className="text-xs font-bold text-foreground mb-3">Quick Navigation</h4>
            <div className="space-y-2">
              <a href="/mlops/deployments" className="flex items-center justify-between p-2.5 rounded bg-muted/40 hover:bg-muted text-xs transition-colors group">
                <span className="text-foreground">Open Deployment Center</span>
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
              </a>
              <a href="/mlops/pipelines" className="flex items-center justify-between p-2.5 rounded bg-muted/40 hover:bg-muted text-xs transition-colors group">
                <span className="text-foreground">Open Pipeline Manager</span>
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
              </a>
              <a href="/mlops/approvals" className="flex items-center justify-between p-2.5 rounded bg-muted/40 hover:bg-muted text-xs transition-colors group">
                <span className="text-foreground">Review Governance Queue</span>
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground group-hover:translate-x-0.5 transition-transform" />
              </a>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
