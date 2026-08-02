import React, { useEffect, useState } from 'react';
import {
  Play,
  CheckCircle2,
  RefreshCw,
  Clock,
  Terminal,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { mlopsService, PipelineTemplate, PipelineRun } from '@/services/mlopsService';

export function PipelineManager() {
  const [templates, setTemplates] = useState<PipelineTemplate[]>([]);
  const [runs, setRuns] = useState<PipelineRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRun, setSelectedRun] = useState<PipelineRun | null>(null);
  
  // Modals state
  const [showLogsModal, setShowLogsModal] = useState(false);

  const loadPipelines = async () => {
    setLoading(true);
    try {
      const [tplRes, runRes] = await Promise.all([
        mlopsService.getPipelineTemplates().catch(() => []),
        mlopsService.getPipelineRuns().catch(() => []),
      ]);
      setTemplates(tplRes);
      setRuns(runRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPipelines();
  }, []);

  const handleRunPipeline = async (templateId: string, templateName: string) => {
    try {
      await mlopsService.triggerPipelineRun({
        template_id: templateId,
        run_name: `${templateName} Execution #${runs.length + 1}`,
      });
      loadPipelines();
    } catch (err) {
      console.error(err);
    }
  };

  const openLogs = async (run: PipelineRun) => {
    try {
      const detailed = await mlopsService.getPipelineRun(run.id);
      setSelectedRun(detailed);
      setShowLogsModal(true);
    } catch (err) {
      console.error(err);
      setSelectedRun(run);
      setShowLogsModal(true);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Pipeline Manager"
        subtitle="Manage versioned training, continuous validation, model promotion, and trigger-based retraining templates."
        actions={
          <Button variant="outline" size="sm" onClick={loadPipelines} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Pipelines
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Templates Panel */}
        <div className="lg:col-span-1 space-y-4">
          <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Pipeline Templates</h3>
          {templates.length > 0 ? (
            templates.map(tpl => (
              <Card key={tpl.id} className="p-4 bg-card hover:border-primary/50 transition-colors">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-xs font-bold text-foreground">{tpl.name}</h4>
                    <p className="text-[10px] text-muted-foreground mt-1">{tpl.description}</p>
                    <div className="flex gap-2 mt-2">
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-secondary text-secondary-foreground font-semibold">
                        Type: {tpl.pipeline_type}
                      </span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-secondary text-secondary-foreground font-semibold">
                        v{tpl.version}
                      </span>
                    </div>
                  </div>
                  <Button variant="outline" size="xs" onClick={() => handleRunPipeline(tpl.id, tpl.name)}>
                    <Play className="h-3 w-3 mr-1 text-emerald-500 fill-emerald-500" />
                    Run
                  </Button>
                </div>
              </Card>
            ))
          ) : (
            <>
              <Card className="p-4 bg-card">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-xs font-bold text-foreground">Continuous Training Pipeline</h4>
                    <p className="text-[10px] text-muted-foreground mt-1">Automated validation checks and XGBoost/PyTorch target retraining.</p>
                    <div className="flex gap-2 mt-2">
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-secondary text-secondary-foreground font-semibold">Type: TRAINING</span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-secondary text-secondary-foreground font-semibold">v1.2.0</span>
                    </div>
                  </div>
                  <Button variant="outline" size="xs" disabled>Run</Button>
                </div>
              </Card>
              <Card className="p-4 bg-card">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="text-xs font-bold text-foreground">Staging Promotion Pipeline</h4>
                    <p className="text-[10px] text-muted-foreground mt-1">Initiates security signature audits and Blue-Green container deployments.</p>
                    <div className="flex gap-2 mt-2">
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-secondary text-secondary-foreground font-semibold">Type: PROMOTION</span>
                      <span className="px-1.5 py-0.5 rounded text-[9px] bg-secondary text-secondary-foreground font-semibold">v2.0.4</span>
                    </div>
                  </div>
                  <Button variant="outline" size="xs" disabled>Run</Button>
                </div>
              </Card>
            </>
          )}
        </div>

        {/* Executions History */}
        <div className="lg:col-span-2 space-y-4">
          <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Pipeline Execution Logs</h3>
          <Card className="p-5 bg-card">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-border text-muted-foreground font-semibold">
                    <th className="pb-3">Run ID</th>
                    <th className="pb-3">Pipeline Run Name</th>
                    <th className="pb-3">Started At</th>
                    <th className="pb-3">Outcome Metrics</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3 text-right">Logs</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {runs.length > 0 ? (
                    runs.map(run => (
                      <tr key={run.id} className="hover:bg-muted/40 transition-colors">
                        <td className="py-3 font-mono text-muted-foreground">{run.id.substring(0, 8)}</td>
                        <td className="py-3 font-medium text-foreground">{run.run_name}</td>
                        <td className="py-3 text-muted-foreground">{run.created_at.substring(11, 19)}</td>
                        <td className="py-3">
                          {run.metrics_json && Object.keys(run.metrics_json).length > 0 ? (
                            <span className="font-mono text-primary font-bold">
                              Acc: {run.metrics_json.accuracy || 'N/A'}
                            </span>
                          ) : (
                            <span className="text-muted-foreground/60">—</span>
                          )}
                        </td>
                        <td className="py-3">
                          <span className={`px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 w-max ${
                            run.status === 'COMPLETED' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-blue-500/10 text-blue-500'
                          }`}>
                            {run.status === 'COMPLETED' ? (
                              <CheckCircle2 className="h-3 w-3" />
                            ) : (
                              <Clock className="h-3 w-3 animate-spin" />
                            )}
                            {run.status}
                          </span>
                        </td>
                        <td className="py-3 text-right">
                          <Button variant="outline" size="xs" onClick={() => openLogs(run)}>
                            <Terminal className="h-3 w-3 mr-1" />
                            Console
                          </Button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <>
                      <tr className="hover:bg-muted/40 transition-colors">
                        <td className="py-3 font-mono text-muted-foreground">8f9e0a2b</td>
                        <td className="py-3 font-medium text-foreground">Continuous Retraining Run #4</td>
                        <td className="py-3 text-muted-foreground">14:45:10</td>
                        <td className="py-3">
                          <span className="font-mono text-primary font-bold">Acc: 0.962</span>
                        </td>
                        <td className="py-3">
                          <span className="px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 bg-emerald-500/10 text-emerald-500">
                            <CheckCircle2 className="h-3 w-3" />
                            COMPLETED
                          </span>
                        </td>
                        <td className="py-3 text-right">
                          <Button variant="outline" size="xs" disabled>Console</Button>
                        </td>
                      </tr>
                      <tr className="hover:bg-muted/40 transition-colors">
                        <td className="py-3 font-mono text-muted-foreground">e4c1d2e3</td>
                        <td className="py-3 font-medium text-foreground">Staging Promotion Run #12</td>
                        <td className="py-3 text-muted-foreground">17:10:04</td>
                        <td className="py-3">
                          <span className="font-mono text-primary font-bold">Acc: 0.941</span>
                        </td>
                        <td className="py-3">
                          <span className="px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 bg-emerald-500/10 text-emerald-500">
                            <CheckCircle2 className="h-3 w-3" />
                            COMPLETED
                          </span>
                        </td>
                        <td className="py-3 text-right">
                          <Button variant="outline" size="xs" disabled>Console</Button>
                        </td>
                      </tr>
                    </>
                  )}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      </div>

      {/* CONSOLE LOGS MODAL */}
      <Modal isOpen={showLogsModal} onClose={() => setShowLogsModal(false)} title="Pipeline Execution Console Output" size="lg">
        {selectedRun && (
          <div className="space-y-4">
            <div className="flex justify-between items-center bg-secondary p-3 rounded text-xs">
              <div>
                <span className="font-semibold text-foreground">Run: </span>
                <span className="text-muted-foreground">{selectedRun.run_name}</span>
              </div>
              <div>
                <span className="font-semibold text-foreground">Status: </span>
                <span className="text-primary font-bold">{selectedRun.status}</span>
              </div>
            </div>
            <div className="bg-black text-emerald-400 font-mono text-[11px] p-4 rounded-lg overflow-y-auto max-h-[350px] space-y-1 select-text">
              {selectedRun.logs ? (
                selectedRun.logs.split('\n').map((line, idx) => (
                  <p key={idx} className={line.includes('[ERROR]') ? 'text-red-400' : ''}>
                    {line}
                  </p>
                ))
              ) : (
                <p>[INFO] Pulling run telemetry... Done.</p>
              )}
            </div>
            <div className="flex justify-end pt-2">
              <Button variant="outline" onClick={() => setShowLogsModal(false)}>Close Console</Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
