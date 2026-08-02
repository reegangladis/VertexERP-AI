import React, { useEffect, useState } from 'react';
import { Plus, Sparkles } from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { mlService, MLExperiment } from '@/services/mlService';

export function ExperimentsPage() {
  const [experiments, setExperiments] = useState<MLExperiment[]>([]);
  const [loading, setLoading] = useState(true);

  const loadExperiments = async () => {
    setLoading(true);
    try {
      const res = await mlService.getExperiments();
      setExperiments(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExperiments();
  }, []);

  const handleCreateDemoExp = async () => {
    try {
      const exp = await mlService.createExperiment({
        name: 'Employee Attrition Hyperparameter Search',
        description: 'Comparison of XGBoost vs RandomForest vs LightGBM learning rates',
        model_type: 'CLASSIFICATION',
        target_column: 'attrition_flag',
      });
      await mlService.createExperimentRun(exp.id, {
        run_name: 'Trial 1 - XGBoost lr=0.01',
        parameters_json: { n_estimators: 100, learning_rate: 0.01, max_depth: 4 },
        metrics_json: { accuracy: 0.912, f1_score: 0.894, roc_auc: 0.935 },
        duration_seconds: 4.5,
      });
      await mlService.createExperimentRun(exp.id, {
        run_name: 'Trial 2 - XGBoost lr=0.05',
        parameters_json: { n_estimators: 150, learning_rate: 0.05, max_depth: 6 },
        metrics_json: { accuracy: 0.948, f1_score: 0.931, roc_auc: 0.962 },
        duration_seconds: 6.2,
      });
      loadExperiments();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="ML Experiment Registry & Tracking"
        subtitle="Track Runs, Parameters, Metrics, Artifact Metadata, and Training History Comparisons"
        actions={
          <Button size="sm" onClick={handleCreateDemoExp}>
            <Plus className="h-4 w-4 mr-2" />
            Create Experiment
          </Button>
        }
      />

      <div className="space-y-4">
        {loading ? (
          <Card className="p-8 text-center text-slate-500">Loading Experiment Registry...</Card>
        ) : experiments.length === 0 ? (
          <Card className="p-8 text-center space-y-3">
            <Sparkles className="h-12 w-12 text-slate-400 mx-auto" />
            <h3 className="text-lg font-semibold text-slate-900">No Experiments Registered Yet</h3>
            <p className="text-sm text-slate-500 max-w-md mx-auto">
              Track multi-trial hyperparameter searches and metric benchmarking runs in the Experiment Registry.
            </p>
            <Button size="sm" onClick={handleCreateDemoExp}>
              Seed Demo Experiment
            </Button>
          </Card>
        ) : (
          experiments.map((exp) => (
            <Card key={exp.id} className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{exp.name}</h3>
                  <p className="text-sm text-slate-500">{exp.description}</p>
                </div>
                <span className="px-2.5 py-1 text-xs font-semibold bg-emerald-100 text-emerald-800 rounded">
                  {exp.status}
                </span>
              </div>

              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Experiment Trial Runs</h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm border border-slate-200 rounded-lg overflow-hidden">
                  <thead className="bg-slate-100 text-slate-600 text-xs uppercase font-semibold">
                    <tr>
                      <th className="p-3">Run Name</th>
                      <th className="p-3">Hyperparameters</th>
                      <th className="p-3">Metrics (Accuracy / F1 / ROC AUC)</th>
                      <th className="p-3">Duration</th>
                      <th className="p-3">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {exp.runs && exp.runs.length > 0 ? (
                      exp.runs.map((run) => (
                        <tr key={run.id} className="hover:bg-slate-50">
                          <td className="p-3 font-semibold text-slate-900">{run.run_name}</td>
                          <td className="p-3 font-mono text-xs text-slate-600">
                            {run.parameters_json ? JSON.stringify(run.parameters_json) : '{}'}
                          </td>
                          <td className="p-3 font-mono text-xs text-emerald-700">
                            {run.metrics_json ? JSON.stringify(run.metrics_json) : '{}'}
                          </td>
                          <td className="p-3 text-xs text-slate-500">{run.duration_seconds}s</td>
                          <td className="p-3">
                            <span className="px-2 py-0.5 text-xs font-semibold bg-emerald-50 text-emerald-700 rounded">
                              {run.status}
                            </span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={5} className="p-3 text-center text-xs text-slate-400">
                          No runs recorded for this experiment.
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
