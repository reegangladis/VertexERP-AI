import React, { useEffect, useState } from 'react';
import { Brain, CheckCircle2, Clock, GitBranch, Plus, ShieldCheck, Tag } from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { mlService, MLModel } from '@/services/mlService';

export function ModelRegistry() {
  const [models, setModels] = useState<MLModel[]>([]);
  const [loading, setLoading] = useState(true);

  const loadModels = async () => {
    setLoading(true);
    try {
      const res = await mlService.getModels();
      setModels(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  const handleApprove = async (versionId: string) => {
    try {
      await mlService.approveModelVersion(versionId, 'Lead Machine Learning Engineer');
      loadModels();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Enterprise Model Registry"
        subtitle="Centralized Machine Learning Model Catalog, Version Control, Status Lifecycle, and Approval Workflows"
        actions={
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Register New Model
          </Button>
        }
      />

      <div className="space-y-4">
        {loading ? (
          <Card className="p-8 text-center text-slate-500">Loading Model Registry catalog...</Card>
        ) : models.length === 0 ? (
          <Card className="p-8 text-center space-y-3">
            <Brain className="h-12 w-12 text-slate-400 mx-auto" />
            <h3 className="text-lg font-semibold text-slate-900">No ML Models Registered Yet</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Register your scikit-learn, XGBoost, LightGBM, PyTorch, or Prophet models in the Enterprise Model Registry.
            </p>
          </Card>
        ) : (
          models.map((model) => (
            <Card key={model.id} className="p-6">
              <div className="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-slate-100 pb-4 mb-4 gap-2">
                <div>
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-bold text-slate-900">{model.name}</h3>
                    <span className="px-2.5 py-0.5 text-xs font-mono font-semibold bg-slate-100 text-slate-700 rounded">
                      {model.model_code}
                    </span>
                    <span className="px-2.5 py-0.5 text-xs font-semibold bg-purple-100 text-purple-700 rounded">
                      {model.ml_framework}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">{model.description || 'Enterprise ML algorithm model'}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs font-semibold px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 flex items-center">
                    <CheckCircle2 className="h-3 w-3 mr-1" />
                    {model.status}
                  </span>
                </div>
              </div>

              {/* Specs Badges */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6 bg-slate-50 p-3 rounded-lg text-xs">
                <div>
                  <span className="text-slate-400 block">Domain:</span>
                  <span className="font-semibold text-slate-800">{model.business_domain}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Model Type:</span>
                  <span className="font-semibold text-slate-800">{model.model_type}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Target Column:</span>
                  <span className="font-mono text-slate-800">{model.target_column || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-slate-400 block">Features Count:</span>
                  <span className="font-semibold text-slate-800">{model.feature_names?.length || 0} features</span>
                </div>
              </div>

              {/* Version History Table */}
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2 flex items-center">
                <GitBranch className="h-4 w-4 mr-1 text-slate-400" />
                Model Versions & Approval Workflow
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border border-slate-200 rounded-lg overflow-hidden">
                  <thead className="bg-slate-100 text-slate-600 text-xs uppercase font-semibold">
                    <tr>
                      <th className="p-3">Version</th>
                      <th className="p-3">Status</th>
                      <th className="p-3">Approval</th>
                      <th className="p-3">Metrics Snapshot</th>
                      <th className="p-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {model.versions && model.versions.length > 0 ? (
                      model.versions.map((ver) => (
                        <tr key={ver.id} className="hover:bg-slate-50">
                          <td className="p-3 font-mono font-bold text-slate-900">{ver.version}</td>
                          <td className="p-3">
                            <span
                              className={`px-2 py-0.5 text-xs font-semibold rounded ${
                                ver.status === 'PRODUCTION'
                                  ? 'bg-emerald-100 text-emerald-800'
                                  : ver.status === 'STAGING'
                                  ? 'bg-blue-100 text-blue-800'
                                  : 'bg-amber-100 text-amber-800'
                              }`}
                            >
                              {ver.status}
                            </span>
                          </td>
                          <td className="p-3">
                            <span className="text-xs font-medium text-slate-600 flex items-center">
                              {ver.approval_status === 'APPROVED' ? (
                                <>
                                  <ShieldCheck className="h-3.5 w-3.5 text-emerald-600 mr-1" />
                                  Approved by {ver.approved_by || 'Admin'}
                                </>
                              ) : (
                                <>
                                  <Clock className="h-3.5 w-3.5 text-amber-500 mr-1" />
                                  Pending Approval
                                </>
                              )}
                            </span>
                          </td>
                          <td className="p-3 text-xs font-mono text-slate-600">
                            {ver.metrics_json ? JSON.stringify(ver.metrics_json) : 'N/A'}
                          </td>
                          <td className="p-3 text-right">
                            {ver.approval_status !== 'APPROVED' && (
                              <Button size="sm" variant="outline" onClick={() => handleApprove(ver.id)}>
                                Approve & Promote
                              </Button>
                            )}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="p-3 text-center text-xs text-slate-400">
                          No version iterations registered yet for this model.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}
