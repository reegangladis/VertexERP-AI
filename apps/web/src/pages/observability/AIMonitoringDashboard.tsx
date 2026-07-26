import React, { useEffect, useState } from 'react';
import {
  Brain,
  Cpu,
  Clock,
  TrendingUp,
  RefreshCw,
  Layers,
  Activity,
  Zap,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { observabilityService } from '@/services/observabilityService';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, Legend } from 'recharts';

export function AIMonitoringDashboard() {
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [tokenTrend, setTokenTrend] = useState<any[]>([]);
  const [latencyTrend, setLatencyTrend] = useState<any[]>([]);

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const res = await observabilityService.getAiMetrics();
      setData(res);

      // Generate simulated visual trends
      setTokenTrend([
        { hour: '08:00', prompt: 120000, completion: 80000 },
        { hour: '10:00', prompt: 240000, completion: 150000 },
        { hour: '12:00', prompt: 310000, completion: 210000 },
        { hour: '14:00', prompt: 290000, completion: 190000 },
        { hour: '16:00', prompt: 340000, completion: 230000 },
        { hour: '18:00', prompt: 180000, completion: 120000 },
      ]);

      setLatencyTrend([
        { time: '10:00', p50: 1.5, p95: 2.8 },
        { time: '11:00', p50: 1.8, p95: 3.1 },
        { time: '12:00', p50: 2.1, p95: 3.5 },
        { time: '13:00', p50: 1.9, p95: 3.2 },
        { time: '14:00', p50: 1.7, p95: 2.9 },
        { time: '15:00', p50: 1.6, p95: 2.7 },
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetrics();
  }, []);

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Monitoring Dashboard"
        subtitle="Monitors LLM completion speeds, vector embeddings recall, prompt costs, and vector retriever latency."
        actions={
          <Button variant="outline" size="sm" onClick={loadMetrics} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Metrics
          </Button>
        }
      />

      {/* Summary Metrics */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-4 border-l-4 border-l-teal-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Average LLM Latency</span>
                <h3 className="text-xl font-bold text-foreground">{data.llm_latency.avg_sec}s</h3>
                <p className="text-xs text-teal-600 flex items-center">
                  <Clock className="h-3.5 w-3.5 mr-0.5" />
                  p95 latency: {data.llm_latency.p95_sec}s
                </p>
              </div>
              <div className="p-2 rounded bg-teal-50 dark:bg-teal-950/20 text-teal-600">
                <Zap className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-emerald-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">LLM Daily Costs</span>
                <h3 className="text-xl font-bold text-foreground">${data.token_usage.total_cost_usd.toFixed(2)}</h3>
                <p className="text-xs text-emerald-600 flex items-center">
                  <TrendingUp className="h-3.5 w-3.5 mr-0.5" />
                  {(data.token_usage.prompt_tokens_today / 1000).toFixed(0)}k prompt tokens
                </p>
              </div>
              <div className="p-2 rounded bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600">
                <Brain className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-blue-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">RAG Vector Recall Hit</span>
                <h3 className="text-xl font-bold text-foreground">{data.rag_metrics.vector_hit_rate_percent}%</h3>
                <p className="text-xs text-blue-600 flex items-center">
                  <Layers className="h-3.5 w-3.5 mr-0.5" />
                  Avg retrieve: {data.rag_metrics.avg_retrieval_duration_ms}ms
                </p>
              </div>
              <div className="p-2 rounded bg-blue-50 dark:bg-blue-950/20 text-blue-600">
                <Activity className="h-5 w-5" />
              </div>
            </div>
          </Card>

          <Card className="p-4 border-l-4 border-l-indigo-500 bg-card">
            <div className="flex justify-between items-start">
              <div className="space-y-1">
                <span className="text-[10px] text-muted-foreground uppercase font-bold tracking-wider">Evaluation Score</span>
                <h3 className="text-xl font-bold text-foreground">{(data.inference.accuracy_score_placeholder * 100).toFixed(0)}%</h3>
                <p className="text-xs text-indigo-600 flex items-center">
                  <Cpu className="h-3.5 w-3.5 mr-0.5" />
                  Provider: {data.inference.active_model}
                </p>
              </div>
              <div className="p-2 rounded bg-indigo-50 dark:bg-indigo-950/20 text-indigo-600">
                <Brain className="h-5 w-5" />
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* AI Performance trends */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Token counts Bar Chart */}
        <Card className="p-5 space-y-4">
          <div>
            <h4 className="text-xs font-bold text-foreground">Token Volume Consumption</h4>
            <p className="text-[10px] text-muted-foreground">Prompt and completion token counts consumed today by organizational tenants.</p>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={tokenTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted-foreground/10" />
                <XAxis dataKey="hour" className="text-[10px] fill-muted-foreground font-mono" />
                <YAxis className="text-[10px] fill-muted-foreground font-mono" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--color-border)', borderRadius: '8px' }} />
                <Legend className="text-[10px]" />
                <Bar dataKey="prompt" name="Prompt Tokens" fill="#0d9488" radius={[4, 4, 0, 0]} />
                <Bar dataKey="completion" name="Completion Tokens" fill="#0891b2" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Latency Area Chart */}
        <Card className="p-5 space-y-4">
          <div>
            <h4 className="text-xs font-bold text-foreground">Model Response Latency (seconds)</h4>
            <p className="text-[10px] text-muted-foreground">Historical p50 median and p95 latency values for prompt inference completions.</p>
          </div>

          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={latencyTrend} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="p50Grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="p95Grad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted-foreground/10" />
                <XAxis dataKey="time" className="text-[10px] fill-muted-foreground font-mono" />
                <YAxis className="text-[10px] fill-muted-foreground font-mono" />
                <Tooltip contentStyle={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--color-border)', borderRadius: '8px' }} />
                <Legend className="text-[10px]" />
                <Area type="monotone" dataKey="p50" name="p50 Median Latency" stroke="#3b82f6" fillOpacity={1} fill="url(#p50Grad)" strokeWidth={2} />
                <Area type="monotone" dataKey="p95" name="p95 Alert Latency" stroke="#8b5cf6" fillOpacity={1} fill="url(#p95Grad)" strokeWidth={1.5} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
}
export default AIMonitoringDashboard;
