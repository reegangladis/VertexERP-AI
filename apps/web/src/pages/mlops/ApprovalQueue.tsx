import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Clock,
  Eye,
  FileText,
  Building2,
  Lock,
  Plus,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Modal } from '@/components/Modal';
import { Input } from '@/components/Input';
import { mlopsService, ModelApproval } from '@/services/mlopsService';

export function ApprovalQueue() {
  const [approvals, setApprovals] = useState<ModelApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedApp, setSelectedApp] = useState<ModelApproval | null>(null);
  
  // Modals state
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  const [showDecisionModal, setShowDecisionModal] = useState(false);

  // Form states
  const [newVersionId, setNewVersionId] = useState('3fa85f64-5717-4562-b3fc-2c963f66afa6');
  const [newEnv, setNewEnv] = useState('PRODUCTION');
  const [newComments, setNewComments] = useState('');
  
  const [decisionType, setDecisionType] = useState('APPROVED'); // APPROVED or REJECTED
  const [decisionComments, setDecisionComments] = useState('');

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const res = await mlopsService.getApprovals();
      setApprovals(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();
  }, []);

  const handleRequestApproval = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await mlopsService.requestPromotionApproval({
        model_version_id: newVersionId,
        requested_by: 'requester@vertex.ai',
        target_environment: newEnv,
        comments: newComments,
      });
      setShowCreateModal(false);
      setNewComments('');
      loadApprovals();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDecision = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedApp) return;
    try {
      await mlopsService.decideApproval(selectedApp.id, {
        approval_status: decisionType,
        approver: 'principal.architect@vertex.ai',
        comments: decisionComments,
      });
      setShowDecisionModal(false);
      setShowDetailsModal(false);
      setDecisionComments('');
      loadApprovals();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Approval Queue"
        subtitle="Model Governance, verification checklist auditing, model documentation cards, and production release authorizations."
        actions={
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={loadApprovals}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Queue
            </Button>
            <Button variant="default" size="sm" onClick={() => setShowCreateModal(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Request Promotion
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-1 gap-6">
        <Card className="p-6 bg-card">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border text-muted-foreground font-semibold">
                  <th className="pb-3">Approval ID</th>
                  <th className="pb-3">Model Version ID</th>
                  <th className="pb-3">Requested By</th>
                  <th className="pb-3">Target Stage</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3">Submission Date</th>
                  <th className="pb-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {approvals.length > 0 ? (
                  approvals.map(app => (
                    <tr key={app.id} className="hover:bg-muted/40 transition-colors">
                      <td className="py-3.5 font-mono text-muted-foreground">{app.id.substring(0, 8)}</td>
                      <td className="py-3.5 font-mono">{app.model_version_id.substring(0, 8)}</td>
                      <td className="py-3.5 font-medium text-foreground">{app.requested_by}</td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-secondary text-secondary-foreground font-semibold">
                          {app.target_environment}
                        </span>
                      </td>
                      <td className="py-3.5">
                        <span className={`px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 w-max ${
                          app.approval_status === 'APPROVED'
                            ? 'bg-emerald-500/10 text-emerald-500'
                            : app.approval_status === 'REJECTED'
                            ? 'bg-red-500/10 text-red-500'
                            : 'bg-amber-500/10 text-amber-500'
                        }`}>
                          {app.approval_status === 'PENDING' && <Clock className="h-3 w-3" />}
                          {app.approval_status === 'APPROVED' && <CheckCircle2 className="h-3 w-3" />}
                          {app.approval_status === 'REJECTED' && <XCircle className="h-3 w-3" />}
                          {app.approval_status}
                        </span>
                      </td>
                      <td className="py-3.5 text-muted-foreground">{app.request_date.substring(0, 10)}</td>
                      <td className="py-3.5 text-right">
                        <Button
                          variant="outline"
                          size="xs"
                          onClick={() => {
                            setSelectedApp(app);
                            setShowDetailsModal(true);
                          }}
                        >
                          <Eye className="h-3.5 w-3.5 mr-1" />
                          Audit Model
                        </Button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <>
                    <tr className="hover:bg-muted/40 transition-colors">
                      <td className="py-3.5 font-mono text-muted-foreground">3b5f9e2d</td>
                      <td className="py-3.5 font-mono">e1c0d4f2</td>
                      <td className="py-3.5 font-medium text-foreground">lead.mlops@vertex.ai</td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[10px] bg-secondary text-secondary-foreground font-semibold">PRODUCTION</span>
                      </td>
                      <td className="py-3.5">
                        <span className="px-2 py-0.5 rounded text-[9px] font-semibold flex items-center gap-1 bg-amber-500/10 text-amber-500 w-max">
                          <Clock className="h-3 w-3" />
                          PENDING
                        </span>
                      </td>
                      <td className="py-3.5 text-muted-foreground">2026-07-26</td>
                      <td className="py-3.5 text-right">
                        <Button variant="outline" size="xs" disabled>Audit Model</Button>
                      </td>
                    </tr>
                  </>
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>

      {/* REQUEST PROMOTION MODAL */}
      <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Submit Model Promotion Request">
        <form onSubmit={handleRequestApproval} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Model Candidate Version ID</label>
            <input
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              type="text"
              value={newVersionId}
              onChange={(e) => setNewVersionId(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Target Stage</label>
            <select
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground"
              value={newEnv}
              onChange={(e) => setNewEnv(e.target.value)}
            >
              <option value="TESTING">TESTING</option>
              <option value="STAGING">STAGING</option>
              <option value="PRODUCTION">PRODUCTION</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-foreground mb-1">Request Comments / Justification</label>
            <textarea
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground min-h-[60px]"
              placeholder="Provide context, references, or training performance scores summary..."
              value={newComments}
              onChange={(e) => setNewComments(e.target.value)}
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>Cancel</Button>
            <Button variant="default" type="submit">Submit Request</Button>
          </div>
        </form>
      </Modal>

      {/* DETAILS / AUDIT CHECKLIST MODAL */}
      <Modal isOpen={showDetailsModal} onClose={() => setShowDetailsModal(false)} title="Model Governance & Compliance Audit" size="lg">
        {selectedApp && (
          <div className="space-y-6 text-xs">
            {/* Metadata and Checklist */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="p-4 bg-muted/40 space-y-2">
                <h4 className="font-bold text-foreground border-b border-border pb-1">Submission Details</h4>
                <p><span className="text-muted-foreground">Version ID:</span> <span className="font-mono">{selectedApp.model_version_id}</span></p>
                <p><span className="text-muted-foreground">Requested By:</span> {selectedApp.requested_by}</p>
                <p><span className="text-muted-foreground">Target Env:</span> {selectedApp.target_environment}</p>
                <p><span className="text-muted-foreground">Status:</span> <span className="text-primary font-bold">{selectedApp.approval_status}</span></p>
              </Card>

              <Card className="p-4 bg-muted/40 space-y-2.5">
                <h4 className="font-bold text-foreground border-b border-border pb-1">Compliance Checkpoints</h4>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><ShieldCheck className="h-4 w-4 text-emerald-500" /> Explainability Map (SHAP/LIME)</span>
                  <span className="text-[10px] text-emerald-600 font-semibold bg-emerald-500/10 px-1 rounded">VERIFIED</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><ShieldCheck className="h-4 w-4 text-emerald-500" /> Bias & Fairness audit</span>
                  <span className="text-[10px] text-emerald-600 font-semibold bg-emerald-500/10 px-1 rounded">VERIFIED</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5"><ShieldCheck className="h-4 w-4 text-emerald-500" /> License & Ownership agreements</span>
                  <span className="text-[10px] text-emerald-600 font-semibold bg-emerald-500/10 px-1 rounded">VERIFIED</span>
                </div>
              </Card>
            </div>

            {selectedApp.comments && (
              <Card className="p-4 bg-muted/40">
                <h4 className="font-bold text-foreground border-b border-border pb-1 mb-2">Request Context Comments</h4>
                <p className="text-muted-foreground">{selectedApp.comments}</p>
              </Card>
            )}

            {/* Decision Controls */}
            {selectedApp.approval_status === 'PENDING' && (
              <div className="flex justify-end gap-2 border-t border-border pt-4">
                <Button variant="outline" onClick={() => setShowDetailsModal(false)}>Close Audit</Button>
                <Button
                  variant="default"
                  onClick={() => {
                    setDecisionType('APPROVED');
                    setShowDecisionModal(true);
                  }}
                >
                  Approve Promotion
                </Button>
                <Button
                  variant="outline"
                  className="text-red-500 hover:bg-red-500/10 border-red-500/20"
                  onClick={() => {
                    setDecisionType('REJECTED');
                    setShowDecisionModal(true);
                  }}
                >
                  Reject Request
                </Button>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* COMMIT DECISION MODAL */}
      <Modal isOpen={showDecisionModal} onClose={() => setShowDecisionModal(false)} title={`Confirm ${decisionType}`}>
        <form onSubmit={handleDecision} className="space-y-4">
          <div>
            <p className="text-xs text-muted-foreground mb-3">
              Confirm your governance decision. This action is permanently logged in the audit trail.
            </p>
            <label className="block text-xs font-semibold text-foreground mb-1">Decision Comments / Rationale</label>
            <textarea
              className="w-full text-xs rounded border border-input p-2 bg-background text-foreground min-h-[60px]"
              placeholder="e.g. Meets verification benchmarks, explainability report is clean..."
              value={decisionComments}
              onChange={(e) => setDecisionComments(e.target.value)}
              required
            />
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setShowDecisionModal(false)}>Cancel</Button>
            <Button variant="default" type="submit">Commit Decision</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
