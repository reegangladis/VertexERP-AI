import React, { useEffect, useState } from 'react';
import {
  Plus,
  RotateCcw,
  Sliders,
  RefreshCw,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { mlopsService, MLDeployment } from '@/services/mlopsService';

export function DeploymentCenter() {
  const [deployments, setDeployments] = useState<MLDeployment[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDep, setSelectedDep] = useState<MLDeployment | null>(null);
  
  // Modals state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showTrafficModal, setShowTrafficModal] = useState(false);
  const [showRollbackModal, setShowRollbackModal] = useState(false);

  // Form states
  const [newName, setNewName] = useState('');
  const [newEnv, setNewEnv] = useState('TESTING');
  const [newStrategy, setNewStrategy] = useState('BLUE_GREEN');
  const [newModelId, setNewModelId] = useState('3fa85f64-5717-4562-b3fc-2c963f66afa6');
  const [newVersionId, setNewVersionId] = useState('3fa85f64-5717-4562-b3fc-2c963f66afa6');
  
  const [trafficPct, setTrafficPct] = useState(50);
  const [rollbackVersion, setRollbackVersion] = useState('');
  const [rollbackNotes, setRollbackNotes] = useState('');

  const loadDeployments = async () => {
    setLoading(true);
    try {
      const res = await mlopsService.getDeployments();
      setDeployments(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeployments();
  }, []);

  const handleCreateDeployment = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await mlopsService.createDeployment({
        name: newName,
        environment: newEnv,
        strategy: newStrategy,
        model_id: newModelId,
        model_version_id: newVersionId,
        target_traffic_percentage: 100.0,
      });
      setShowCreateModal(false);
      setNewName('');
      loadDeployments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpdateTraffic = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDep) return;
    try {
      await mlopsService.updateTraffic(selectedDep.id, trafficPct);
      setShowTrafficModal(false);
      loadDeployments();
    } catch (err) {
      console.error(err);
    }
  };

  const handleRollback = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDep || !rollbackVersion) return;
    try {
      await mlopsService.rollbackDeployment(
        selectedDep.id,
        rollbackVersion,
        'principal.architect@vertex.ai',
        rollbackNotes
      );
      setShowRollbackModal(false);
      setRollbackVersion('');
      setRollbackNotes('');
      loadDeployments();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Deployment Center"
        subtitle="Orchestrate Blue-Green promotions, adjust Canary weights, configure Shadow pipelines, and rollback configurations."
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={loadDeployments}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Button variant="default" size="sm" onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Deployment
            </Button>
          </div>
        }
      />

      {/* Grid of active deployments */}
      <div className="grid grid-cols-1 gap-6">
        <Card className="p-6 bg-card">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border text-muted-foreground font-semibold">
                  <th className="pb-3">Endpoint Name</th>
                  <th className="pb-3">Environment</th>
                  <th className="pb-3">Active Version</th>
                  <th className="pb-3">Routing Strategy</th>
                  <th className="pb-3">Traffic Split</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {deployments.length > 0 ? (
                  deployments.map(dep => (
                    <tr key={dep.id} className="hover:bg-muted/40 transition-colors">
                      <td className="py-3.5 font-medium text-foreground">{dep.name}</td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-secondary text-secondary-foreground font-semibold">
                          {dep.environment}
                        </span>
                      </td>
                      <td className="py-3.5 font-mono text-muted-foreground">{dep.active_version}</td>
                      <td className="py-3.5 font-mono">{dep.strategy}</td>
                      <td className="py-3.5 font-bold text-primary">{dep.target_traffic_percentage}%</td>
                      <td className="py-3.5">
                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-500 font-semibold">
                          {dep.status}
                        </span>
                      </td>
                      <td className="py-3.5 text-right space-x-1.5">
                        <Button
                          variant="outline"
                          size="xs"
                          onClick={() => {
                            setSelectedDep(dep);
                            setTrafficPct(dep.target_traffic_percentage);
                            setShowTrafficModal(true);
                          }}
                        >
                          <Sliders className="h-3 w-3 mr-1" />
                          Traffic
                        </Button>
                        <Button
                          variant="outline"
                          size="xs"
                          onClick={() => {
                            setSelectedDep(dep);
                            setShowRollbackModal(true);
                          }}
                        >
                          <RotateCcw className="h-3 w-3 mr-1" />
                          Rollback
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <>
                    <tr className="hover:bg-muted/40 transition-colors">
                      <td className="py-3.5 font-medium text-foreground">HR Attrition Predictor</td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-secondary text-secondary-foreground font-semibold">PRODUCTION</span>
                      </td>
                      <td className="py-3.5 font-mono text-muted-foreground">v2.1.0</td>
                      <td className="py-3.5 font-mono">BLUE_GREEN</td>
                      <td className="py-3.5 font-bold text-primary">100%</td>
                      <td className="py-3.5">
                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-500 font-semibold">ACTIVE</span>
                      </td>
                      <td className="py-3.5 text-right space-x-1.5">
                        <Button variant="outline" size="xs" disabled>Traffic</Button>
                        <Button variant="outline" size="xs" disabled>Rollback</Button>
                      </td>
                    </tr>
                    <tr className="hover:bg-muted/40 transition-colors">
                      <td className="py-3.5 font-medium text-foreground">CRM Lead Scorer</td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-secondary text-secondary-foreground font-semibold">PRODUCTION</span>
                      </td>
                      <td className="py-3.5 font-mono text-muted-foreground">v1.4.0 (Canary)</td>
                      <td className="py-3.5 font-mono">CANARY</td>
                      <td className="py-3.5 font-bold text-primary">15%</td>
                      <td className="py-3.5">
                        <span className="px-1.5 py-0.5 rounded text-[10px] bg-emerald-500/10 text-emerald-500 font-semibold">ACTIVE</span>
                      </td>
                      <td className="py-3.5 text-right space-x-1.5">
                        <Button variant="outline" size="xs" disabled>Traffic</Button>
                        <Button variant="outline" size="xs" disabled>Rollback</Button>
                      </td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* CREATE DEPLOYMENT MODAL */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Initialize New Endpoint Deployment">
        <form onSubmit={handleCreateDeployment} className="space-y-4">
          <Input
            label="Deployment Name"
            placeholder="e.g. Sales Forecast Classifier"
            value={newName}
            onChange={(e: any) => setNewName(e.target.value)}
            required
          />
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Target Environment</label>
            <select
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              value={newEnv}
              onChange={(e) => setNewEnv(e.target.value)}
            >
              <option value="DEVELOPMENT">DEVELOPMENT</option>
              <option value="TESTING">TESTING</option>
              <option value="STAGING">STAGING</option>
              <option value="PRODUCTION">PRODUCTION</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Deployment Strategy</label>
            <select
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              value={newStrategy}
              onChange={(e) => setNewStrategy(e.target.value)}
            >
              <option value="BLUE_GREEN">BLUE-GREEN ROUTING</option>
              <option value="CANARY">CANARY SPLIT</option>
              <option value="SHADOW">SHADOW DEPLOYMENT</option>
            </select>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="default" type="submit">Deploy Endpoint</Button>
          </div>
        </form>
      </Modal>

      {/* TRAFFIC ROUTING MODAL */}
      <Modal isOpen={showTrafficModal} onClose={() => setShowTrafficModal(false)} title="Adjust Traffic Routing Split">
        <form onSubmit={handleUpdateTraffic} className="space-y-4">
          <div>
            <p className="text-xs text-muted-foreground mb-4">
              Configure what percentage of queries route to the target active version.
            </p>
            <div className="flex justify-between text-xs font-semibold mb-2">
              <span>Traffic Shift</span>
              <span className="text-primary font-bold">{trafficPct}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              value={trafficPct}
              onChange={(e) => setTrafficPct(Number(e.target.value))}
              className="w-full h-1 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary"
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowTrafficModal(false)}>Cancel</Button>
            <Button variant="default" type="submit">Commit Shift</Button>
          </div>
        </form>
      </Modal>

      {/* ROLLBACK MODAL */}
      <Modal isOpen={showRollbackModal} onClose={() => setShowRollbackModal(false)} title="Trigger Emergency Rollback">
        <form onSubmit={handleRollback} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Target Stable Version ID</label>
            <input
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              type="text"
              placeholder="UUID of target version"
              value={rollbackVersion}
              onChange={(e) => setRollbackVersion(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Audit/Rollback Notes</label>
            <textarea
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground min-h-[60px]"
              placeholder="Describe reasons for initiating rollback..."
              value={rollbackNotes}
              onChange={(e) => setRollbackNotes(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowRollbackModal(false)}>Cancel</Button>
            <Button variant="default" type="submit">Initiate Rollback</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
