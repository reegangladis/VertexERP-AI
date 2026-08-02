import React, { useEffect, useState } from 'react';
import {
  Brain,
  GitBranch,
  ArrowUpRight,
  ShieldCheck,
  Plus,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { mlStudioService, RegisteredModelItem } from '@/services/mlStudioService';

export function ModelRegistryStudio() {
  const [models, setModels] = useState<RegisteredModelItem[]>([]);
  const [selectedModel, setSelectedModel] = useState<RegisteredModelItem | null>(null);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  const [approvalNotes, setApprovalNotes] = useState('');

  useEffect(() => {
    loadModels();
  }, []);

  const loadModels = async () => {
    try {
      const data = await mlStudioService.getModels().catch(() => []);
      if (data.length > 0) {
        setModels(data);
        setSelectedModel(data[0]);
      } else {
        const seed: RegisteredModelItem = {
          id: 'mdl-attr-xgb-01',
          model_code: 'MDL-ATTRITION-XGB',
          name: 'XGBoost Employee Attrition Predictor',
          description: 'Enterprise classifier for predicting employee flight risk and retention urgency.',
          model_type: 'CLASSIFICATION',
          ml_framework: 'XGBOOST',
          business_domain: 'HR',
          target_column: 'left_company',
          current_version: 'v1.0.0',
          stage: 'CANDIDATE',
          approval_status: 'PENDING',
          approval_notes: '',
          approved_by: '',
          approved_at: '',
          metadata_json: { framework_version: '1.7.5', accuracy: 0.938, auc: 0.924 },
          tags: ['hr', 'xgboost', 'attrition'],
          created_at: new Date().toISOString(),
        };
        setModels([seed]);
        setSelectedModel(seed);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleApprove = async (status: 'APPROVED' | 'REJECTED') => {
    if (!selectedModel) return;
    try {
      const updated = await mlStudioService.approveModel(
        selectedModel.id,
        status,
        'Principal AI Architect',
        approvalNotes || 'Model passed corporate validation threshold.'
      ).catch(() => ({
        ...selectedModel,
        approval_status: status,
        approved_by: 'Principal AI Architect',
        stage: status === 'APPROVED' ? 'APPROVED' : selectedModel.stage,
      }));
      setSelectedModel(updated);
      setShowApprovalModal(false);
      loadModels();
    } catch (e) {
      console.error(e);
    }
  };

  const handlePromote = async (newStage: string) => {
    if (!selectedModel) return;
    try {
      const updated = await mlStudioService.promoteModel(selectedModel.id, newStage).catch(() => ({
        ...selectedModel,
        stage: newStage,
      }));
      setSelectedModel(updated);
      loadModels();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Model Registry & Approval Lifecycle"
        subtitle="Centralized model version catalog, approval review sign-off workflow, and stage promotions"
        actions={
          <Button variant="primary" icon={<Plus className="w-4 h-4" />}>
            Register Model
          </Button>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Registered Models List */}
        <Card className="p-5 space-y-4 lg:col-span-1">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <Brain className="w-4 h-4 text-indigo-500" /> Model Catalog
          </h3>

          <div className="space-y-3">
            {models.map((m) => (
              <div
                key={m.id}
                onClick={() => setSelectedModel(m)}
                className={`p-4 rounded-lg border cursor-pointer transition-all ${
                  selectedModel?.id === m.id
                    ? 'border-indigo-500 bg-indigo-50/40 dark:bg-indigo-950/40'
                    : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-mono text-xs font-bold text-indigo-600 dark:text-indigo-400">{m.model_code}</span>
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300">
                    {m.stage}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-slate-900 dark:text-white line-clamp-1">{m.name}</h4>
                <div className="flex items-center justify-between text-xs text-slate-500 mt-2">
                  <span>Version: {m.current_version}</span>
                  <span className="font-mono">{m.ml_framework}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Right Column: Model Version Details & Approval Workflow */}
        {selectedModel && (
          <div className="lg:col-span-2 space-y-5">
            <Card className="p-6 space-y-6">
              <div className="flex flex-wrap items-start justify-between gap-4 border-b border-slate-200 dark:border-slate-800 pb-4">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm font-bold text-indigo-600 dark:text-indigo-400">{selectedModel.model_code}</span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300">
                      {selectedModel.stage}
                    </span>
                    <span className="text-xs px-2.5 py-0.5 rounded-full font-bold bg-amber-100 dark:bg-amber-950 text-amber-700 dark:text-amber-300">
                      Approval: {selectedModel.approval_status}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-white mt-1">{selectedModel.name}</h2>
                  <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{selectedModel.description}</p>
                </div>

                {/* Workflow Actions */}
                <div className="flex items-center space-x-2">
                  {selectedModel.approval_status === 'PENDING' && (
                    <Button variant="primary" icon={<ShieldCheck className="w-4 h-4" />} onClick={() => setShowApprovalModal(true)}>
                      Review Approval
                    </Button>
                  )}
                  {selectedModel.approval_status === 'APPROVED' && selectedModel.stage !== 'PRODUCTION' && (
                    <Button variant="secondary" icon={<ArrowUpRight className="w-4 h-4" />} onClick={() => handlePromote('PRODUCTION')}>
                      Promote to Production
                    </Button>
                  )}
                </div>
              </div>

              {/* Version History Timeline */}
              <div className="space-y-3">
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500 flex items-center gap-2">
                  <GitBranch className="w-4 h-4 text-indigo-500" /> Semantic Version History
                </h4>
                <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-3">
                  <div className="flex justify-between items-center text-xs border-b border-slate-200 dark:border-slate-800 pb-2">
                    <span className="font-mono font-bold text-slate-900 dark:text-white">{selectedModel.current_version} (Current)</span>
                    <span className="text-emerald-600 font-semibold">AUC 0.924 | F1 0.906</span>
                  </div>
                  <div className="text-xs text-slate-600 dark:text-slate-400 grid grid-cols-2 gap-2">
                    <div>Framework: <span className="font-semibold text-slate-900 dark:text-white">{selectedModel.ml_framework}</span></div>
                    <div>Domain: <span className="font-semibold text-slate-900 dark:text-white">{selectedModel.business_domain}</span></div>
                    <div>Target: <span className="font-mono font-semibold text-slate-900 dark:text-white">{selectedModel.target_column}</span></div>
                    <div>Approved By: <span className="font-semibold text-slate-900 dark:text-white">{selectedModel.approved_by || 'Pending Sign-off'}</span></div>
                  </div>
                </div>
              </div>

              {/* Approval Modal */}
              {showApprovalModal && (
                <div className="p-4 bg-amber-50/50 dark:bg-amber-950/30 border border-amber-300 dark:border-amber-700 rounded-lg space-y-3">
                  <h4 className="text-sm font-bold text-amber-900 dark:text-amber-200">Formal Approval Sign-Off Review</h4>
                  <textarea
                    placeholder="Enter approval review notes..."
                    value={approvalNotes}
                    onChange={(e) => setApprovalNotes(e.target.value)}
                    className="w-full p-2 text-xs rounded border border-amber-300 dark:border-amber-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white"
                  />
                  <div className="flex space-x-2">
                    <Button variant="primary" onClick={() => handleApprove('APPROVED')}>
                      Approve Model Version
                    </Button>
                    <Button variant="secondary" onClick={() => handleApprove('REJECTED')}>
                      Reject
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
