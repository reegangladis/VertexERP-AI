import React, { useEffect, useState } from 'react';
import {
  RefreshCw,
  Play,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Settings,
  TrendingUp,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { mlopsService, RetrainingJob } from '@/services/mlopsService';

export function RetrainingCenter() {
  const [retrainingJobs, setRetrainingJobs] = useState<RetrainingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [showConfigModal, setShowConfigModal] = useState(false);
  const [showRunModal, setShowRunModal] = useState(false);

  // Form states
  const [modelId, setModelId] = useState('3fa85f64-5717-4562-b3fc-2c963f66afa6');
  const [triggerType, setTriggerType] = useState('MANUAL');
  const [cronExpression, setCronExpression] = useState('0 0 * * 0'); // Every Sunday at midnight
  
  const loadRetrainingJobs = async () => {
    setLoading(true);
    try {
      const res = await mlopsService.getRetrainingHistory();
      setRetrainingJobs(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRetrainingJobs();
  }, []);

  const handleTriggerRetraining = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await mlopsService.triggerRetraining({
        model_id: modelId,
        trigger_type: triggerType,
        config_json: { cron_expression: cronExpression }
      });
      setShowRunModal(false);
      loadRetrainingJobs();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Retraining Center"
        subtitle="Manage scheduled training routines, override retraining limits, and track historical metrics alignment."
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={loadRetrainingJobs}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh History
            </Button>
            <Button variant="outline" size="sm" onClick={() => setShowConfigModal(true)}>
              <Settings className="h-4 w-4 mr-2" />
              Retraining Configs
            </Button>
            <Button variant="default" size="sm" onClick={() => setShowRunModal(true)}>
              <Play className="h-4 w-4 mr-2" />
              Trigger Retraining
            </Button>
          </div>
        }
      />

      {/* Configurations Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-4 bg-card">
          <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5 mb-3">
            <Calendar className="h-4 w-4 text-primary" />
            Active Schedule Policies
          </h4>
          <div className="text-xs space-y-2">
            <div className="flex justify-between py-1 border-b border-border">
              <span className="text-muted-foreground">Cron Policy:</span>
              <span className="font-mono text-primary">{cronExpression}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border">
              <span className="text-muted-foreground">Target Endpoint:</span>
              <span>HR Attrition Predictor</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-muted-foreground">Next Trigger:</span>
              <span>Sunday, 12:00 AM</span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-card">
          <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5 mb-3">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            Drift-Trigger Thresholds
          </h4>
          <div className="text-xs space-y-2">
            <div className="flex justify-between py-1 border-b border-border">
              <span className="text-muted-foreground">Drift Score Trigger:</span>
              <span className="font-semibold">PSI &gt;= 0.25</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border">
              <span className="text-muted-foreground">Auto-Rollback Trigger:</span>
              <span>Error rate &gt;= 5.0%</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-muted-foreground">Auto-Promote Approval:</span>
              <span className="text-emerald-500 font-semibold">Enabled</span>
            </div>
          </div>
        </Card>

        <Card className="p-4 bg-card">
          <h4 className="text-xs font-bold text-foreground flex items-center gap-1.5 mb-3">
            <TrendingUp className="h-4 w-4 text-purple-500" />
            Comparison Summary
          </h4>
          <div className="text-xs space-y-2">
            <div className="flex justify-between py-1 border-b border-border">
              <span className="text-muted-foreground">New Champion Accuracy:</span>
              <span className="font-bold text-emerald-500">96.8%</span>
            </div>
            <div className="flex justify-between py-1 border-b border-border">
              <span className="text-muted-foreground">Baseline Challenger:</span>
              <span>94.2%</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-muted-foreground">Uplift Margin:</span>
              <span className="text-emerald-500 font-bold">+2.6%</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Retraining History Grid */}
      <div className="grid grid-cols-1 gap-6">
        <h3 className="text-xs font-bold text-foreground uppercase tracking-wider">Retraining Executions Audit Trail</h3>
        <Card className="p-5 bg-card">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border text-muted-foreground font-semibold">
                  <th className="pb-3">Job ID</th>
                  <th className="pb-3">Model Baseline ID</th>
                  <th className="pb-3">Trigger Reason</th>
                  <th className="pb-3">Outcome Status</th>
                  <th className="pb-3">Triggered Date</th>
                  <th className="pb-3 text-right">Completion Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {retrainingJobs.length > 0 ? (
                  retrainingJobs.map(job => (
                    <tr key={job.id} className="hover:bg-muted/40 transition-colors">
                      <td className="py-3 font-mono text-muted-foreground">{job.id.substring(0, 8)}</td>
                      <td className="py-3 font-mono">{job.model_id.substring(0, 8)}</td>
                      <td className="py-3 font-semibold text-foreground">{job.trigger_type}</td>
                      <td className="py-3">
                        <span className={`px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 w-max ${
                          job.status === 'COMPLETED'
                            ? 'bg-emerald-500/10 text-emerald-500'
                            : job.status === 'FAILED'
                            ? 'bg-red-500/10 text-red-500'
                            : 'bg-blue-500/10 text-blue-500'
                        }`}>
                          {job.status === 'RUNNING' && <Clock className="h-3 w-3 animate-spin" />}
                          {job.status === 'COMPLETED' && <CheckCircle2 className="h-3 w-3" />}
                          {job.status === 'FAILED' && <XCircle className="h-3 w-3" />}
                          {job.status}
                        </span>
                      </td>
                      <td className="py-3 text-muted-foreground">{job.created_at.substring(0, 19)}</td>
                      <td className="py-3 text-right text-muted-foreground">
                        {job.completed_at ? job.completed_at.substring(11, 19) : '—'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <>
                    <tr className="hover:bg-muted/40 transition-colors">
                      <td className="py-3 font-mono text-muted-foreground">a1b2c3d4</td>
                      <td className="py-3 font-mono">f1c0d4f2</td>
                      <td className="py-3 font-semibold text-foreground">DRIFT_TRIGGERED</td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 bg-emerald-500/10 text-emerald-500 w-max">
                          <CheckCircle2 className="h-3 w-3" />
                          COMPLETED
                        </span>
                      </td>
                      <td className="py-3 text-muted-foreground">2026-07-26 14:22:15</td>
                      <td className="py-3 text-right text-muted-foreground">14:22:58</td>
                    </tr>
                    <tr className="hover:bg-muted/40 transition-colors">
                      <td className="py-3 font-mono text-muted-foreground">e5f6g7h8</td>
                      <td className="py-3 font-mono">f1c0d4f2</td>
                      <td className="py-3 font-semibold text-foreground">MANUAL</td>
                      <td className="py-3">
                        <span className="px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 bg-emerald-500/10 text-emerald-500 w-max">
                          <CheckCircle2 className="h-3 w-3" />
                          COMPLETED
                        </span>
                      </td>
                      <td className="py-3 text-muted-foreground">2026-07-25 10:15:00</td>
                      <td className="py-3 text-right text-muted-foreground">10:15:35</td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* CONFIGURE MODAL */}
      <Modal isOpen={showConfigModal} onClose={() => setShowConfigModal(false)} title="Configure Retraining Schedule Policy">
        <form onSubmit={(e) => { e.preventDefault(); setShowConfigModal(false); }} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Retraining Cron Expression</label>
            <input
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              type="text"
              value={cronExpression}
              onChange={(e) => setCronExpression(e.target.value)}
              required
            />
            <p className="text-[10px] text-muted-foreground mt-1">Standard 5-field cron syntax.</p>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowConfigModal(false)}>Close</Button>
            <Button variant="default" type="submit">Save Configurations</Button>
          </div>
        </form>
      </Modal>

      {/* TRIGGER RUN MODAL */}
      <Modal isOpen={showRunModal} onClose={() => setShowRunModal(false)} title="Trigger Manual Retraining Pipeline">
        <form onSubmit={handleTriggerRetraining} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Model Target ID</label>
            <input
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              type="text"
              value={modelId}
              onChange={(e) => setModelId(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Trigger Execution Reason</label>
            <select
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              value={triggerType}
              onChange={(e) => setTriggerType(e.target.value)}
            >
              <option value="MANUAL">MANUAL OVERRIDE</option>
              <option value="DRIFT_TRIGGERED">DRIFT ADAPTATION</option>
              <option value="SCHEDULED">RUN ON-DEMAND POLICY</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowRunModal(false)}>Cancel</Button>
            <Button variant="default" type="submit">Retrain Model</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
