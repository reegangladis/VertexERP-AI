import React, { useEffect, useState } from 'react';
import { Play, Activity, CheckCircle2, Clock, Plus, Cpu, Settings, AlertCircle } from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { mlService, MLTrainingJob } from '@/services/mlService';

export function TrainingJobs() {
  const [jobs, setJobs] = useState<MLTrainingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [jobName, setJobName] = useState('XGBoost Attrition Predictor Job');
  const [framework, setFramework] = useState('XGBOOST');
  const [modelType, setModelType] = useState('CLASSIFICATION');
  const [datasetName, setDatasetName] = useState('hr_attrition_dataset.json');

  const loadJobs = async () => {
    setLoading(true);
    try {
      const res = await mlService.getTrainingJobs();
      setJobs(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  const handleCreateAndRun = async () => {
    try {
      const created = await mlService.createTrainingJob({
        job_name: jobName,
        ml_framework: framework,
        model_type: modelType,
        dataset_name: datasetName,
        hyperparameters_json: { n_estimators: 150, max_depth: 6, learning_rate: 0.05, cv_folds: 5 },
      });
      await mlService.executeTrainingJob(created.id);
      setShowCreateModal(false);
      loadJobs();
    } catch (e) {
      console.error(e);
    }
  };

  const handleExecute = async (jobId: string) => {
    try {
      await mlService.executeTrainingJob(jobId);
      loadJobs();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Training Jobs & Hyperparameter Configuration"
        subtitle="Execute Cross-Validation, Train/Test Split, and Hyperparameter Grid Search Training Executions"
        actions={
          <Button size="sm" onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Training Job
          </Button>
        }
      />

      {showCreateModal && (
        <Card className="p-6 border-2 border-purple-500 bg-purple-50/20">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
            <Cpu className="h-5 w-5 mr-2 text-purple-600" />
            Configure New Training Job
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Job Name</label>
              <input
                type="text"
                className="w-full text-sm border border-slate-300 rounded p-2"
                value={jobName}
                onChange={(e) => setJobName(e.target.value)}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Framework</label>
              <select
                className="w-full text-sm border border-slate-300 rounded p-2"
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
              >
                <option value="SCIKIT_LEARN font-semibold">scikit-learn</option>
                <option value="XGBOOST">XGBoost</option>
                <option value="LIGHTGBM">LightGBM</option>
                <option value="CATBOOST">CatBoost</option>
                <option value="TENSORFLOW">TensorFlow</option>
                <option value="PYTORCH">PyTorch</option>
                <option value="PROPHET">Prophet</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Model Task Type</label>
              <select
                className="w-full text-sm border border-slate-300 rounded p-2"
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
              >
                <option value="CLASSIFICATION">Classification</option>
                <option value="REGRESSION">Regression</option>
                <option value="CLUSTERING">Clustering</option>
                <option value="TIME_SERIES">Time Series Forecasting</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Dataset</label>
              <input
                type="text"
                className="w-full text-sm border border-slate-300 rounded p-2"
                value={datasetName}
                onChange={(e) => setDatasetName(e.target.value)}
              />
            </div>
          </div>
          <div className="flex justify-end space-x-2">
            <Button variant="outline" size="sm" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button size="sm" onClick={handleCreateAndRun}>
              Launch Training Job
            </Button>
          </div>
        </Card>
      )}

      {/* Jobs Table */}
      <Card className="p-6">
        <h3 className="text-md font-bold text-slate-900 mb-4">Training Job Executions</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border border-slate-200 rounded-lg overflow-hidden">
            <thead className="bg-slate-100 text-slate-600 text-xs uppercase font-semibold">
              <tr>
                <th className="p-3">Job Name</th>
                <th className="p-3">Framework</th>
                <th className="p-3">Dataset</th>
                <th className="p-3">Status</th>
                <th className="p-3">Hyperparameters</th>
                <th className="p-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-xs text-slate-500">
                    Loading training jobs...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-4 text-center text-xs text-slate-400">
                    No training jobs configured. Click "New Training Job" above.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-slate-50">
                    <td className="p-3 font-semibold text-slate-900">{job.job_name}</td>
                    <td className="p-3 font-mono text-xs text-purple-700">{job.ml_framework}</td>
                    <td className="p-3 font-mono text-xs text-slate-600">{job.dataset_name}</td>
                    <td className="p-3">
                      <span
                        className={`px-2.5 py-0.5 text-xs font-semibold rounded ${
                          job.status === 'COMPLETED'
                            ? 'bg-emerald-100 text-emerald-800'
                            : job.status === 'RUNNING'
                            ? 'bg-blue-100 text-blue-800 animate-pulse'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {job.status}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-xs text-slate-500">
                      {job.hyperparameters_json ? JSON.stringify(job.hyperparameters_json) : '{}'}
                    </td>
                    <td className="p-3 text-right">
                      {job.status !== 'RUNNING' && (
                        <Button size="sm" variant="outline" onClick={() => handleExecute(job.id)}>
                          <Play className="h-3 w-3 mr-1" /> Re-Run
                        </Button>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
