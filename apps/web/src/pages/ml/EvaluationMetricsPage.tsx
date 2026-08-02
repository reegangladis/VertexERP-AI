import React from 'react';
import { BarChart2, Layers } from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';

export function EvaluationMetricsPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Model Evaluation Metrics & Diagnostics"
        subtitle="Classification & Regression Performance Auditing, Confusion Matrices, ROC AUC Curves, and Feature Importances"
      />

      {/* Classification Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {[
          { name: 'Accuracy', val: '94.8%', sub: 'Overall Correctness' },
          { name: 'Precision', val: '93.2%', sub: 'Positive Value Accuracy' },
          { name: 'Recall', val: '92.5%', sub: 'True Positive Rate' },
          { name: 'F1 Score', val: '92.8%', sub: 'Harmonic Mean' },
          { name: 'ROC AUC', val: '0.962', sub: 'Discriminative Power' },
        ].map((m) => (
          <Card key={m.name} className="p-4 border-t-4 border-t-purple-500 text-center">
            <span className="text-xs font-semibold uppercase text-slate-500 tracking-wider">{m.name}</span>
            <h3 className="text-2xl font-bold text-slate-900 mt-1">{m.val}</h3>
            <p className="text-[11px] text-slate-500 mt-0.5">{m.sub}</p>
          </Card>
        ))}
      </div>

      {/* Diagnostics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Card */}
        <Card className="p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
            <BarChart2 className="h-5 w-5 mr-2 text-indigo-600" />
            Classification Confusion Matrix (Test Split)
          </h3>
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="p-6 bg-emerald-50 border border-emerald-200 rounded-lg">
              <span className="text-xs font-semibold text-emerald-800 uppercase block">True Positives (TP)</span>
              <span className="text-3xl font-extrabold text-emerald-900 mt-2 block">148</span>
              <span className="text-xs text-emerald-700 mt-1 block">Correctly Predicted Attrition</span>
            </div>
            <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
              <span className="text-xs font-semibold text-red-800 uppercase block">False Positives (FP)</span>
              <span className="text-3xl font-extrabold text-red-900 mt-2 block">11</span>
              <span className="text-xs text-red-700 mt-1 block">False Alarm Attrition</span>
            </div>
            <div className="p-6 bg-amber-50 border border-amber-200 rounded-lg">
              <span className="text-xs font-semibold text-amber-800 uppercase block">False Negatives (FN)</span>
              <span className="text-3xl font-extrabold text-amber-900 mt-2 block">12</span>
              <span className="text-xs text-amber-700 mt-1 block">Missed Attrition</span>
            </div>
            <div className="p-6 bg-blue-50 border border-blue-200 rounded-lg">
              <span className="text-xs font-semibold text-blue-800 uppercase block">True Negatives (TN)</span>
              <span className="text-3xl font-extrabold text-blue-900 mt-2 block">429</span>
              <span className="text-xs text-blue-700 mt-1 block">Correctly Retained Staff</span>
            </div>
          </div>
        </Card>

        {/* Feature Importance Card */}
        <Card className="p-6">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
            <Layers className="h-5 w-5 mr-2 text-purple-600" />
            Top Feature Importance Weights
          </h3>
          <div className="space-y-4">
            {[
              { feature: 'satisfaction_score', weight: 0.38, pct: '38%' },
              { feature: 'overtime_hours', weight: 0.26, pct: '26%' },
              { feature: 'salary_percentile', weight: 0.18, pct: '18%' },
              { feature: 'tenure_months', weight: 0.12, pct: '12%' },
              { feature: 'department_sales', weight: 0.06, pct: '6%' },
            ].map((f) => (
              <div key={f.feature}>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-1">
                  <span className="font-mono">{f.feature}</span>
                  <span>{f.pct}</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2.5">
                  <div
                    className="bg-purple-600 h-2.5 rounded-full"
                    style={{ width: f.pct }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
