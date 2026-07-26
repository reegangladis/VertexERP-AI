import React, { useState } from 'react';
import {
  Sliders,
  CheckCircle2,
  TrendingUp,
  BarChart3,
  Layers,
  Sparkles,
  Search,
  Filter,
  Plus,
  GitCommit,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';

export function ExperimentTracker() {
  const [selectedExperiment, setSelectedExperiment] = useState<string>('EXP-ATTRITION-01');

  const experiments = [
    {
      id: 'EXP-ATTRITION-01',
      name: 'XGBoost Attrition Hyperparameter Search',
      model_type: 'CLASSIFICATION',
      target: 'left_company',
      runs_count: 5,
      status: 'COMPLETED',
      best_metric: 'AUC: 0.924',
    },
    {
      id: 'EXP-SALES-FORECAST-02',
      name: 'Prophet vs LightGBM Quarterly Revenue Forecast',
      model_type: 'TIME_SERIES',
      target: 'quarterly_revenue',
      runs_count: 4,
      status: 'ACTIVE',
      best_metric: 'RMSE: $12,450',
    },
    {
      id: 'EXP-FRAUD-DETECTION-03',
      name: 'CatBoost Imbalanced Transaction Fraud Tuning',
      model_type: 'ANOMALY_DETECTION',
      target: 'is_fraud',
      runs_count: 6,
      status: 'COMPLETED',
      best_metric: 'Precision: 0.945',
    },
  ];

  const runs = [
    {
      run_id: 'RUN-101',
      run_name: 'xgb_lr_0.01_depth_6',
      params: { learning_rate: 0.01, max_depth: 6, n_estimators: 300, subsample: 0.8 },
      metrics: { accuracy: 0.938, f1_score: 0.906, auc: 0.924, loss: 0.185 },
      duration: '42s',
      status: 'FINISHED',
    },
    {
      run_id: 'RUN-102',
      run_name: 'xgb_lr_0.05_depth_4',
      params: { learning_rate: 0.05, max_depth: 4, n_estimators: 200, subsample: 0.9 },
      metrics: { accuracy: 0.921, f1_score: 0.884, auc: 0.908, loss: 0.210 },
      duration: '28s',
      status: 'FINISHED',
    },
    {
      run_id: 'RUN-103',
      run_name: 'xgb_lr_0.10_depth_8',
      params: { learning_rate: 0.10, max_depth: 8, n_estimators: 500, subsample: 0.7 },
      metrics: { accuracy: 0.905, f1_score: 0.865, auc: 0.892, loss: 0.245 },
      duration: '65s',
      status: 'FINISHED',
    },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Experiment Tracker & Hyperparameter Tuning"
        subtitle="Track multi-trial hyperparameter searches, compare metrics across runs, and inspect trial artifacts"
        actions={
          <Button variant="primary" icon={<Plus className="w-4 h-4" />}>
            New Experiment
          </Button>
        }
      />

      {/* Experiments Registry Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {experiments.map((exp) => (
          <Card
            key={exp.id}
            onClick={() => setSelectedExperiment(exp.id)}
            className={`p-5 cursor-pointer transition-all border ${
              selectedExperiment === exp.id
                ? 'border-indigo-500 bg-indigo-50/40 dark:bg-indigo-950/40'
                : 'border-slate-200 dark:border-slate-800 hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-mono text-xs font-semibold text-indigo-600 dark:text-indigo-400">{exp.id}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-950 text-emerald-700 dark:text-emerald-300">
                {exp.status}
              </span>
            </div>
            <h4 className="text-sm font-bold text-slate-900 dark:text-white line-clamp-1">{exp.name}</h4>
            <div className="mt-3 flex items-center justify-between text-xs text-slate-600 dark:text-slate-400 border-t border-slate-200 dark:border-slate-800 pt-2">
              <span>{exp.runs_count} Trial Runs</span>
              <span className="font-mono font-semibold text-emerald-600 dark:text-emerald-400">{exp.best_metric}</span>
            </div>
          </Card>
        ))}
      </div>

      {/* Comparative Runs Matrix */}
      <Card className="p-6 space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-indigo-500" /> Trial Runs Comparison Matrix ({selectedExperiment})
            </h3>
            <p className="text-xs text-slate-500">Side-by-side metric comparison across hyperparameter configurations</p>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-500 font-semibold">Filter Metric:</span>
            <select className="text-xs bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-700 rounded px-2 py-1 font-semibold text-slate-900 dark:text-white">
              <option value="auc">ROC AUC Score</option>
              <option value="accuracy">Accuracy</option>
              <option value="f1_score">F1 Score</option>
            </select>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left border-collapse">
            <thead>
              <tr className="bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">Run ID</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">Run Name</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">Hyperparameters</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">Accuracy</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">F1 Score</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">ROC AUC</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">Loss</th>
                <th className="p-3 border border-slate-200 dark:border-slate-700 font-semibold">Duration</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r, idx) => (
                <tr key={r.run_id} className={`border-b border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900/50 ${idx === 0 ? 'bg-emerald-50/30 dark:bg-emerald-950/20' : ''}`}>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 font-mono font-bold text-indigo-600 dark:text-indigo-400">
                    {r.run_id} {idx === 0 && <span className="ml-1 text-[10px] bg-emerald-100 text-emerald-800 px-1 rounded">BEST</span>}
                  </td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 font-medium text-slate-900 dark:text-white">{r.run_name}</td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 font-mono text-[11px] text-slate-600 dark:text-slate-400">
                    lr={r.params.learning_rate}, depth={r.params.max_depth}, n_est={r.params.n_estimators}
                  </td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 font-semibold text-slate-900 dark:text-white">{r.metrics.accuracy}</td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 font-semibold text-slate-900 dark:text-white">{r.metrics.f1_score}</td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 font-bold text-emerald-600 dark:text-emerald-400">{r.metrics.auc}</td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400">{r.metrics.loss}</td>
                  <td className="p-3 border border-slate-200 dark:border-slate-800 text-slate-500">{r.duration}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Metric Progress Visualizer */}
        <div className="pt-4 border-t border-slate-200 dark:border-slate-800 space-y-3">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-500">ROC AUC Comparison Across Runs</h4>
          <div className="space-y-2">
            {runs.map((r) => (
              <div key={r.run_id} className="space-y-1">
                <div className="flex justify-between text-xs font-mono text-slate-700 dark:text-slate-300">
                  <span>{r.run_name}</span>
                  <span className="font-bold text-indigo-600 dark:text-indigo-400">AUC {r.metrics.auc}</span>
                </div>
                <div className="w-full h-2.5 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400 rounded-full transition-all"
                    style={{ width: `${r.metrics.auc * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
