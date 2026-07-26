import React, { useState } from 'react';
import {
  PieChart,
  Activity,
  TrendingUp,
  CheckCircle2,
  BarChart3,
  Sliders,
  Layers,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';

export function EvaluationReportsPage() {
  const [activeCurveTab, setActiveCurveTab] = useState<'ROC' | 'PR' | 'CONFUSION' | 'LEARNING' | 'CALIBRATION'>('ROC');

  // Seed curve data
  const rocPoints = [
    { fpr: 0.00, tpr: 0.00 },
    { fpr: 0.05, tpr: 0.62 },
    { fpr: 0.10, tpr: 0.81 },
    { fpr: 0.18, tpr: 0.89 },
    { fpr: 0.25, tpr: 0.94 },
    { fpr: 0.40, tpr: 0.97 },
    { fpr: 0.60, tpr: 0.99 },
    { fpr: 1.00, tpr: 1.00 },
  ];

  const confusionMatrix = {
    tp: 207,
    fp: 25,
    tn: 450,
    fn: 18,
    accuracy: 0.938,
    precision: 0.892,
    recall: 0.920,
    f1: 0.906,
  };

  const featureImportances = [
    { feature: 'OverTime Hours', weight: 0.385 },
    { feature: 'Monthly Income', weight: 0.245 },
    { feature: 'Distance From Home', weight: 0.165 },
    { feature: 'Job Satisfaction', weight: 0.125 },
    { feature: 'Years At Company', weight: 0.080 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Evaluation & Diagnostic Reports"
        subtitle="ROC curves, Precision-Recall curves, Confusion Matrices, Feature Importance, Learning Curves, and Calibration diagnostic plots"
      />

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <Card className="p-5 border-l-4 border-indigo-500">
          <p className="text-xs uppercase font-semibold text-slate-500">ROC AUC Score</p>
          <h3 className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">0.924</h3>
          <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1">Excellent Discrimination</p>
        </Card>

        <Card className="p-5 border-l-4 border-emerald-500">
          <p className="text-xs uppercase font-semibold text-slate-500">F1 Score</p>
          <h3 className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">0.906</h3>
          <p className="text-xs text-emerald-600 dark:text-emerald-400 font-medium mt-1">Balanced Precision/Recall</p>
        </Card>

        <Card className="p-5 border-l-4 border-amber-500">
          <p className="text-xs uppercase font-semibold text-slate-500">Accuracy</p>
          <h3 className="text-2xl font-bold text-amber-600 dark:text-amber-400 mt-1">93.8%</h3>
          <p className="text-xs text-slate-500 mt-1">Total Test Set: 700 Records</p>
        </Card>

        <Card className="p-5 border-l-4 border-purple-500">
          <p className="text-xs uppercase font-semibold text-slate-500">Average Precision (AP)</p>
          <h3 className="text-2xl font-bold text-purple-600 dark:text-purple-400 mt-1">0.891</h3>
          <p className="text-xs text-slate-500 mt-1">PR Curve Integration</p>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Curve Selector & Visualizer */}
        <Card className="p-6 lg:col-span-2 space-y-5">
          <div className="flex border-b border-slate-200 dark:border-slate-800 space-x-6 pb-2">
            <button
              onClick={() => setActiveCurveTab('ROC')}
              className={`text-sm font-semibold pb-2 border-b-2 transition-colors ${
                activeCurveTab === 'ROC' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-slate-500'
              }`}
            >
              ROC Curve
            </button>
            <button
              onClick={() => setActiveCurveTab('CONFUSION')}
              className={`text-sm font-semibold pb-2 border-b-2 transition-colors ${
                activeCurveTab === 'CONFUSION' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-slate-500'
              }`}
            >
              Confusion Matrix
            </button>
            <button
              onClick={() => setActiveCurveTab('LEARNING')}
              className={`text-sm font-semibold pb-2 border-b-2 transition-colors ${
                activeCurveTab === 'LEARNING' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-slate-500'
              }`}
            >
              Learning Curve
            </button>
            <button
              onClick={() => setActiveCurveTab('CALIBRATION')}
              className={`text-sm font-semibold pb-2 border-b-2 transition-colors ${
                activeCurveTab === 'CALIBRATION' ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400' : 'border-transparent text-slate-500'
              }`}
            >
              Calibration Curve
            </button>
          </div>

          {/* Tab Display */}
          {activeCurveTab === 'ROC' && (
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Receiver Operating Characteristic (ROC Curve)</h4>
              <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg border border-slate-200 dark:border-slate-800 space-y-2 font-mono text-xs">
                {rocPoints.map((pt, i) => (
                  <div key={i} className="flex justify-between border-b border-slate-200 dark:border-slate-800 pb-1">
                    <span>FPR: {pt.fpr.toFixed(2)}</span>
                    <span className="font-bold text-indigo-600 dark:text-indigo-400">TPR: {pt.tpr.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeCurveTab === 'CONFUSION' && (
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">2x2 Confusion Matrix Visualizer</h4>
              <div className="grid grid-cols-2 gap-3 text-center max-w-sm mx-auto">
                <div className="p-4 bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700 rounded-lg">
                  <span className="text-[10px] text-emerald-700 dark:text-emerald-300 font-bold uppercase">True Positive (TP)</span>
                  <p className="text-2xl font-extrabold text-emerald-900 dark:text-emerald-100 mt-1">{confusionMatrix.tp}</p>
                </div>
                <div className="p-4 bg-rose-100 dark:bg-rose-950/60 border border-rose-300 dark:border-rose-700 rounded-lg">
                  <span className="text-[10px] text-rose-700 dark:text-rose-300 font-bold uppercase">False Positive (FP)</span>
                  <p className="text-2xl font-extrabold text-rose-900 dark:text-rose-100 mt-1">{confusionMatrix.fp}</p>
                </div>
                <div className="p-4 bg-rose-100 dark:bg-rose-950/60 border border-rose-300 dark:border-rose-700 rounded-lg">
                  <span className="text-[10px] text-rose-700 dark:text-rose-300 font-bold uppercase">False Negative (FN)</span>
                  <p className="text-2xl font-extrabold text-rose-900 dark:text-rose-100 mt-1">{confusionMatrix.fn}</p>
                </div>
                <div className="p-4 bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-700 rounded-lg">
                  <span className="text-[10px] text-emerald-700 dark:text-emerald-300 font-bold uppercase">True Negative (TN)</span>
                  <p className="text-2xl font-extrabold text-emerald-900 dark:text-emerald-100 mt-1">{confusionMatrix.tn}</p>
                </div>
              </div>
            </div>
          )}

          {activeCurveTab === 'LEARNING' && (
            <div className="space-y-3">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Learning Curve Convergence (Train vs Validation Loss)</h4>
              <p className="text-xs text-slate-500">Validation score converges cleanly to 0.92 at N=1000 sample size.</p>
            </div>
          )}

          {activeCurveTab === 'CALIBRATION' && (
            <div className="space-y-3">
              <h4 className="text-sm font-bold text-slate-900 dark:text-white">Probability Calibration Curve (Placeholder)</h4>
              <p className="text-xs text-slate-500">Binned predicted probability vs true fraction of positive samples.</p>
            </div>
          )}
        </Card>

        {/* Right Column: Feature Importance Weights */}
        <Card className="p-6 space-y-4 lg:col-span-1">
          <h3 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-indigo-500" /> Feature Importance Ranking
          </h3>
          <div className="space-y-3">
            {featureImportances.map((fi, idx) => (
              <div key={idx} className="space-y-1">
                <div className="flex justify-between text-xs font-semibold text-slate-800 dark:text-slate-200">
                  <span>{fi.feature}</span>
                  <span className="font-mono text-indigo-600 dark:text-indigo-400">{(fi.weight * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${fi.weight * 100}%` }} />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
