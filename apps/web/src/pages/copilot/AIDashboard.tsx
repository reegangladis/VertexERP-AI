import React, { useState, useEffect } from 'react';
import {
  CheckCircle2,
  ThumbsUp,
  Cpu,
  Clock,
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { copilotService, CopilotAnalytics } from '@/services/copilotService';
import { useNotification } from '@/hooks/useNotification';
import PageHeader from '@/components/PageHeader';

export function AIDashboard() {
  const { addNotification } = useNotification();
  const [metrics, setMetrics] = useState<CopilotAnalytics | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    setIsLoading(true);
    try {
      const data = await copilotService.getAnalytics();
      setMetrics(data);
    } catch (err) {
      addNotification('Could not retrieve dashboard analytics', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || !metrics) {
    return (
      <div className="p-12 text-center text-xs text-muted-foreground">
        Gathering platform telemetry records...
      </div>
    );
  }

  // Charts Mock Datasets
  const tokenTrendData = [
    { name: 'Mon', prompt: metrics.total_prompt_tokens * 0.12, completion: metrics.total_completion_tokens * 0.11 },
    { name: 'Tue', prompt: metrics.total_prompt_tokens * 0.15, completion: metrics.total_completion_tokens * 0.13 },
    { name: 'Wed', prompt: metrics.total_prompt_tokens * 0.18, completion: metrics.total_completion_tokens * 0.19 },
    { name: 'Thu', prompt: metrics.total_prompt_tokens * 0.14, completion: metrics.total_completion_tokens * 0.15 },
    { name: 'Fri', prompt: metrics.total_prompt_tokens * 0.22, completion: metrics.total_completion_tokens * 0.24 },
    { name: 'Sat', prompt: metrics.total_prompt_tokens * 0.08, completion: metrics.total_completion_tokens * 0.07 },
    { name: 'Sun', prompt: metrics.total_prompt_tokens * 0.11, completion: metrics.total_completion_tokens * 0.11 },
  ];

  const toolData = [
    { name: 'Success', value: metrics.tool_success_rate },
    { name: 'Failed', value: 100 - metrics.tool_success_rate },
  ];

  const ratingData = [
    { stars: '5 Stars', count: Math.round(metrics.total_feedbacks * 0.65) || 5 },
    { stars: '4 Stars', count: Math.round(metrics.total_feedbacks * 0.20) || 2 },
    { stars: '3 Stars', count: Math.round(metrics.total_feedbacks * 0.10) || 1 },
    { stars: '2 Stars', count: Math.round(metrics.total_feedbacks * 0.03) || 0 },
    { stars: '1 Star', count: Math.round(metrics.total_feedbacks * 0.02) || 0 },
  ];

  const COLORS = ['#10b981', '#ef4444'];

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <PageHeader
        title="Copilot Observability Dashboard"
        description="Monitor system-wide LLM token budgets, API execution speed statistics, tool success metrics, and user feedback surveys."
      />

      {/* Analytics widgets metrics cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Token Usage</span>
            <h2 className="text-xl font-bold text-foreground">
              {(metrics.total_prompt_tokens + metrics.total_completion_tokens).toLocaleString()}
            </h2>
            <p className="text-[9px] text-muted-foreground">
              In: {metrics.total_prompt_tokens.toLocaleString()} | Out: {metrics.total_completion_tokens.toLocaleString()}
            </p>
          </div>
          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary">
            <Cpu className="h-5 w-5" />
          </div>
        </div>

        {/* Card 2 */}
        <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Avg Latency</span>
            <h2 className="text-xl font-bold text-foreground">{metrics.average_latency_ms}ms</h2>
            <p className="text-[9px] text-muted-foreground">Synthesizing & execution round-trip</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center text-blue-500">
            <Clock className="h-5 w-5" />
          </div>
        </div>

        {/* Card 3 */}
        <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Tool Success</span>
            <h2 className="text-xl font-bold text-foreground">{metrics.tool_success_rate.toFixed(1)}%</h2>
            <p className="text-[9px] text-muted-foreground">Runs: {metrics.total_tool_executions} logs</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500">
            <CheckCircle2 className="h-5 w-5" />
          </div>
        </div>

        {/* Card 4 */}
        <div className="bg-card border border-border rounded-xl p-4 flex items-center justify-between shadow-sm">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider">Feedback Score</span>
            <h2 className="text-xl font-bold text-foreground">{metrics.average_feedback_rating.toFixed(2)} / 5</h2>
            <p className="text-[9px] text-muted-foreground">Audits: {metrics.total_feedbacks} ratings</p>
          </div>
          <div className="w-10 h-10 rounded-full bg-amber-500/10 flex items-center justify-center text-amber-500">
            <ThumbsUp className="h-5 w-5" />
          </div>
        </div>
      </div>

      {/* Chart Layout area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Token consumption trend AreaChart */}
        <div className="lg:col-span-2 bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
          <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Daily Token Consumption Trend</h4>
          <div className="h-72 text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={tokenTrendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#888888" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={10} tickLine={false} axisLine={false} />
                <Tooltip />
                <Legend iconType="circle" />
                <Area type="monotone" dataKey="prompt" name="Prompt Input" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.2} />
                <Area type="monotone" dataKey="completion" name="Assistant Output" stackId="1" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Tool success PieChart */}
        <div className="lg:col-span-1 bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
          <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Tool Execution Summary</h4>
          <div className="h-72 flex items-center justify-center text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={toolData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label
                >
                  {toolData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend verticalAlign="bottom" />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Feedback rating distribution BarChart */}
        <div className="lg:col-span-1 bg-card border border-border rounded-xl p-4 shadow-sm space-y-4">
          <h4 className="text-xs font-bold text-foreground uppercase tracking-wider">Ratings Distribution</h4>
          <div className="h-72 text-xs">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ratingData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="stars" stroke="#888888" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={10} tickLine={false} axisLine={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#f59e0b" radius={[4, 4, 0, 0]}>
                  {ratingData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill="#f59e0b" fillOpacity={0.8} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
export default AIDashboard;
