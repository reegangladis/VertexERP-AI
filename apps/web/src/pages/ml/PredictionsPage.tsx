import React, { useEffect, useState } from 'react';
import { Zap, Play, CheckCircle2, History, AlertTriangle, Cpu, Layers } from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { mlService, MLPrediction, BusinessModulePredictResponse } from '@/services/mlService';

export function PredictionsPage() {
  const [history, setHistory] = useState<MLPrediction[]>([]);
  const [selectedModule, setSelectedModule] = useState('attrition');
  const [predictionResult, setPredictionResult] = useState<BusinessModulePredictResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const loadHistory = async () => {
    try {
      const res = await mlService.getPredictionHistory();
      setHistory(res);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const handleRunInference = async () => {
    setLoading(true);
    try {
      let sampleData: Record<string, any> = {};
      if (selectedModule === 'attrition') {
        sampleData = { tenure_months: 18, satisfaction_score: 2.2, overtime_hours: 22, salary_percentile: 35 };
      } else if (selectedModule === 'sales') {
        sampleData = { historical_sales: 180000, growth_rate: 0.10, deals_in_pipeline: 20 };
      } else if (selectedModule === 'inventory') {
        sampleData = { current_stock: 250, reorder_point: 300, holding_cost: 3.5 };
      } else if (selectedModule === 'churn') {
        sampleData = { support_tickets_opened: 10, nps_score: 3, days_since_last_login: 28 };
      } else if (selectedModule === 'fraud') {
        sampleData = { transaction_amount: 14500, is_foreign_ip: true, hour_of_day: 2 };
      } else {
        sampleData = { machine_temperature: 98.2, vibration_amplitude: 0.85, operator_experience_years: 2 };
      }

      const result = await mlService.predictBusinessModule(selectedModule, sampleData);
      setPredictionResult(result);
      loadHistory();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Real-Time & Batch Inference Predictions"
        subtitle="Execute Business ML Predictions, Monitor Latency Telemetry, and Audit Prediction History"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Inference Simulator Form */}
        <Card className="p-6 lg:col-span-1">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
            <Zap className="h-5 w-5 mr-2 text-indigo-600" />
            Inference Engine Simulator
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1">Target Business Module</label>
              <select
                className="w-full text-sm border border-slate-300 rounded p-2.5"
                value={selectedModule}
                onChange={(e) => setSelectedModule(e.target.value)}
              >
                <option value="attrition">Employee Attrition Risk (HR)</option>
                <option value="sales">Sales Pipeline Forecasting (Sales)</option>
                <option value="inventory">Inventory EOQ & Reorder (Inventory)</option>
                <option value="churn">Customer Churn Predictor (CRM)</option>
                <option value="fraud">Fraud Detection Engine (Finance)</option>
                <option value="quality">Quality Defect Predictor (Mfg)</option>
              </select>
            </div>

            <Button className="w-full" onClick={handleRunInference} disabled={loading}>
              <Play className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Run Real-Time Prediction
            </Button>

            {predictionResult && (
              <div className="p-4 bg-slate-900 text-white rounded-lg space-y-2 text-xs font-mono">
                <div className="flex justify-between items-center text-emerald-400 font-semibold border-b border-slate-800 pb-2">
                  <span>Status: 200 OK</span>
                  <span>{predictionResult.latency_ms} ms</span>
                </div>
                <div>
                  <span className="text-slate-400">Module:</span> {predictionResult.module_key}
                </div>
                <div>
                  <span className="text-slate-400">Confidence:</span> {(predictionResult.confidence_score * 100).toFixed(1)}%
                </div>
                <div>
                  <span className="text-slate-400">Risk Level:</span>{' '}
                  <span className={predictionResult.risk_level === 'HIGH' ? 'text-red-400 font-bold' : 'text-emerald-400'}>
                    {predictionResult.risk_level}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400 block mb-1">Payload Output:</span>
                  <pre className="p-2 bg-slate-950 rounded text-purple-300 overflow-x-auto">
                    {JSON.stringify(predictionResult.prediction_result, null, 2)}
                  </pre>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Prediction History Log */}
        <Card className="p-6 lg:col-span-2">
          <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
            <History className="h-5 w-5 mr-2 text-slate-600" />
            Prediction History & Latency Log
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm border border-slate-200 rounded-lg overflow-hidden">
              <thead className="bg-slate-100 text-slate-600 text-xs uppercase font-semibold">
                <tr>
                  <th className="p-3">Type</th>
                  <th className="p-3">Module</th>
                  <th className="p-3">Confidence</th>
                  <th className="p-3">Latency</th>
                  <th className="p-3">Output JSON</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-4 text-center text-xs text-slate-400">
                      No predictions logged yet. Use simulator on the left to trigger predictions.
                    </td>
                  </tr>
                ) : (
                  history.map((pred) => (
                    <tr key={pred.id} className="hover:bg-slate-50">
                      <td className="p-3">
                        <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-100 text-indigo-700 rounded">
                          {pred.prediction_type}
                        </span>
                      </td>
                      <td className="p-3 font-semibold text-slate-800">{pred.business_module || 'custom'}</td>
                      <td className="p-3 font-mono text-xs text-emerald-600">
                        {((pred.confidence_score || 0.95) * 100).toFixed(1)}%
                      </td>
                      <td className="p-3 font-mono text-xs text-slate-700">{pred.latency_ms} ms</td>
                      <td className="p-3 font-mono text-xs text-slate-500 max-w-xs truncate">
                        {JSON.stringify(pred.output_data_json)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </Card>
      </div>
    </div>
  );
}
