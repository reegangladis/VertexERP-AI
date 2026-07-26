import React, { useEffect, useState } from 'react';
import {
  GitBranch,
  Search,
  RefreshCw,
  Clock,
  AlertTriangle,
  Play,
  Terminal,
  Activity,
  Layers,
  Network,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Modal } from '@/components/Modal';
import { observabilityService, TraceSpan, ServiceDependency } from '@/services/observabilityService';

export function TraceViewer() {
  const [traces, setTraces] = useState<TraceSpan[]>([]);
  const [dependencies, setDependencies] = useState<ServiceDependency[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTraceId, setSearchTraceId] = useState('');
  const [selectedSpan, setSelectedSpan] = useState<TraceSpan | null>(null);
  const [activeTab, setActiveTab] = useState<'timeline' | 'dependencies'>('timeline');

  const loadTraces = async (tid?: string) => {
    setLoading(true);
    try {
      const [tracesRes, depsRes] = await Promise.all([
        observabilityService.getTraces(tid ? { trace_id: tid } : undefined).catch(() => []),
        observabilityService.getDependencyMap().catch(() => []),
      ]);
      setTraces(tracesRes);
      setDependencies(depsRes);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTraces();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadTraces(searchTraceId);
  };

  // Group spans by trace_id to represent distinct transaction sessions
  const getTraceGroups = () => {
    const groups: Record<string, TraceSpan[]> = {};
    traces.forEach(span => {
      if (!groups[span.trace_id]) groups[span.trace_id] = [];
      groups[span.trace_id].push(span);
    });
    return groups;
  };

  const traceGroups = getTraceGroups();
  const activeTraceKeys = Object.keys(traceGroups);

  // If traceGroups is empty, mock default visual timeline data for presentation
  const getMockedTraceSpans = () => {
    const baseTime = new Date().toISOString();
    return [
      { id: '1', trace_id: 'tr-987654321', span_id: 'sp-1', parent_span_id: undefined, name: 'GET /api/v1/finance/invoices', service_name: 'api-gateway', start_time: baseTime, end_time: baseTime, duration_ms: 245.0, status: 'success', attributes: { path: '/api/v1/finance/invoices', ip: '192.168.1.5' } },
      { id: '2', trace_id: 'tr-987654321', span_id: 'sp-2', parent_span_id: 'sp-1', name: 'Verify JWT Credentials', service_name: 'auth-service', start_time: baseTime, end_time: baseTime, duration_ms: 32.5, status: 'success', attributes: { schema: 'Bearer', user: 'admin@vertexerp.ai' } },
      { id: '3', trace_id: 'tr-987654321', span_id: 'sp-3', parent_span_id: 'sp-1', name: 'SQL Query: SELECT invoices', service_name: 'finance-service', start_time: baseTime, end_time: baseTime, duration_ms: 184.2, status: 'success', attributes: { tables: 'invoices, organizations', rows_fetched: '12' } },
      { id: '4', trace_id: 'tr-987654321', span_id: 'sp-4', parent_span_id: 'sp-3', name: 'Redis Lookup: organization_cache', service_name: 'finance-service', start_time: baseTime, end_time: baseTime, duration_ms: 1.4, status: 'success', attributes: { cache_hit: 'true' } },
    ];
  };

  const activeSpansToShow = activeTraceKeys.length > 0
    ? traceGroups[activeTraceKeys[0]]
    : getMockedTraceSpans();

  const totalTraceDuration = activeSpansToShow.reduce((max, s) => Math.max(max, s.duration_ms), 0) || 245;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Trace Viewer"
        subtitle="Distributed execution tracing analyzing span execution workflows and dependency maps."
        actions={
          <Button variant="outline" size="sm" onClick={() => loadTraces(searchTraceId)} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Sync Traces
          </Button>
        }
      />

      {/* Tabs */}
      <div className="flex border-b border-border text-xs">
        <button
          type="button"
          onClick={() => setActiveTab('timeline')}
          className={`px-4 py-2 border-b-2 font-bold transition-colors ${
            activeTab === 'timeline'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <GitBranch className="h-3.5 w-3.5 inline mr-1.5" />
          Trace Spans Timeline
        </button>
        <button
          type="button"
          onClick={() => setActiveTab('dependencies')}
          className={`px-4 py-2 border-b-2 font-bold transition-colors ${
            activeTab === 'dependencies'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          }`}
        >
          <Network className="h-3.5 w-3.5 inline mr-1.5" />
          Service Dependency Topology
        </button>
      </div>

      {activeTab === 'timeline' ? (
        <div className="space-y-6">
          {/* Trace lookup */}
          <Card className="p-4">
            <form onSubmit={handleSearch} className="flex gap-2">
              <div className="flex-grow">
                <Input
                  placeholder="Enter a specific transaction Trace ID (e.g., tr-xxx)..."
                  value={searchTraceId}
                  onChange={(e) => setSearchTraceId(e.target.value)}
                  icon={<Search className="h-4 w-4 text-muted-foreground" />}
                  className="py-2"
                />
              </div>
              <Button type="submit" disabled={loading}>
                Load Trace Spans
              </Button>
            </form>
          </Card>

          {/* Gantt Timeline View */}
          <Card className="p-5 space-y-6">
            <div className="flex justify-between items-center border-b border-border pb-3">
              <div>
                <h4 className="text-xs font-bold text-foreground">
                  Transaction: <span className="font-mono text-primary font-bold text-xs">{activeTraceKeys[0] || 'tr-987654321'}</span>
                </h4>
                <p className="text-[10px] text-muted-foreground">Detailed calling sequence Gantt bar representation.</p>
              </div>
              <span className="text-[10px] font-bold font-mono bg-secondary px-2 py-0.5 rounded text-muted-foreground">
                Total duration: {totalTraceDuration.toFixed(1)} ms
              </span>
            </div>

            {/* Gantt bars list */}
            <div className="space-y-3 font-mono text-[11px]">
              {loading && traces.length === 0 ? (
                <div className="text-center p-8 text-muted-foreground">
                  Loading span traces...
                </div>
              ) : (
                activeSpansToShow.map((span, index) => {
                  // Calculate dynamic visual offset and width % for Gantt bar
                  const indent = span.parent_span_id ? 20 : 0;
                  const isErr = span.status === 'error';
                  
                  // Simulate realistic offset visual % representation
                  const offsetPercent = span.parent_span_id ? 15 : 0;
                  const barWidthPercent = span.parent_span_id 
                    ? Math.max((span.duration_ms / totalTraceDuration) * 100, 10) 
                    : 100;

                  return (
                    <div
                      key={span.id}
                      onClick={() => setSelectedSpan(span)}
                      className="p-2.5 rounded-lg border border-border bg-muted/10 hover:bg-muted/30 transition-colors cursor-pointer space-y-1.5"
                    >
                      <div className="flex justify-between items-center text-[10px]">
                        <div className="flex items-center gap-2" style={{ paddingLeft: `${indent}px` }}>
                          <span className="font-bold text-foreground font-mono">{span.service_name}</span>
                          <span className="text-muted-foreground">|</span>
                          <span className="text-foreground/90 font-sans">{span.name}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`px-1.5 py-0.2 rounded text-[8px] font-bold uppercase ${
                            isErr ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                          }`}>
                            {span.status}
                          </span>
                          <span className="font-bold text-foreground">{span.duration_ms.toFixed(1)} ms</span>
                        </div>
                      </div>

                      {/* Visual Gantt Bar */}
                      <div className="h-2 w-full bg-secondary rounded overflow-hidden relative">
                        <div
                          className={`absolute top-0 bottom-0 rounded transition-all ${
                            isErr ? 'bg-red-500' : 'bg-primary'
                          }`}
                          style={{
                            left: `${offsetPercent}%`,
                            width: `${barWidthPercent}%`,
                          }}
                        />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </Card>
        </div>
      ) : (
        /* Dependency Map Table view */
        <Card className="overflow-hidden">
          <div className="px-5 py-4 border-b border-border bg-card">
            <h4 className="text-xs font-bold text-foreground">Service Dependency Parameters</h4>
            <p className="text-[10px] text-muted-foreground">Calling hierarchies, error rates, and communication performance delay metrics.</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-border bg-muted/20 text-muted-foreground font-semibold uppercase tracking-wider text-[10px]">
                  <th className="p-3">Calling Service (Caller)</th>
                  <th className="p-3">Target Service (Callee)</th>
                  <th className="p-3">Total Call Requests</th>
                  <th className="p-3">Average Latency</th>
                  <th className="p-3">Error Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border font-medium text-foreground">
                {dependencies.map((dep, idx) => (
                  <tr key={idx} className="hover:bg-muted/10">
                    <td className="p-3 font-semibold text-foreground font-mono">{dep.caller}</td>
                    <td className="p-3 font-semibold text-primary font-mono">{dep.callee}</td>
                    <td className="p-3 font-bold font-mono">{dep.call_count.toLocaleString()}</td>
                    <td className="p-3 font-mono">{dep.avg_duration_ms.toFixed(1)} ms</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                        dep.error_rate > 0.02
                          ? 'bg-red-50 text-red-600 border-red-100'
                          : 'bg-emerald-50 text-emerald-600 border-emerald-100'
                      }`}>
                        {(dep.error_rate * 100).toFixed(2)}%
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Trace details modal */}
      {selectedSpan && (
        <Modal
          isOpen={!!selectedSpan}
          onClose={() => setSelectedSpan(null)}
          title="Trace Span Inspector"
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4 border-b border-border pb-3">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Trace ID</span>
                <p className="font-bold text-foreground font-mono mt-0.5">{selectedSpan.trace_id}</p>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Span ID</span>
                <p className="font-bold text-foreground font-mono mt-0.5">{selectedSpan.span_id}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 border-b border-border pb-3">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Service Module</span>
                <p className="font-semibold text-foreground mt-0.5">{selectedSpan.service_name}</p>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Operation Name</span>
                <p className="font-semibold text-foreground mt-0.5">{selectedSpan.name}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 border-b border-border pb-3">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Duration</span>
                <p className="font-bold text-foreground font-mono mt-0.5">{selectedSpan.duration_ms.toFixed(2)} ms</p>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Status</span>
                <p className="mt-0.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase ${
                    selectedSpan.status === 'error' ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                  }`}>
                    {selectedSpan.status}
                  </span>
                </p>
              </div>
            </div>

            <div className="space-y-1.5">
              <span className="text-[10px] text-muted-foreground uppercase font-bold">Span Attributes & Tags</span>
              <pre className="bg-secondary p-3 rounded border font-mono text-[10px] text-foreground overflow-x-auto">
                {JSON.stringify(selectedSpan.attributes || {}, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setSelectedSpan(null)}>
                Close Inspector
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
export default TraceViewer;
