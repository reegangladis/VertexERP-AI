import React, { useEffect, useState } from 'react';
import {
  FileText,
  Search,
  RefreshCw,
  SlidersHorizontal,
  ChevronDown,
  ChevronUp,
  Terminal,
  Layers,
  Clock,
} from 'lucide-react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Modal } from '@/components/Modal';
import { observabilityService, ApplicationLog } from '@/services/observabilityService';

export function LogExplorer() {
  const [logs, setLogs] = useState<ApplicationLog[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(50);

  // Search parameters
  const [serviceName, setServiceName] = useState('');
  const [logLevel, setLogLevel] = useState('');
  const [keyword, setKeyword] = useState('');
  const [correlationId, setCorrelationId] = useState('');
  const [requestId, setRequestId] = useState('');

  // UI state
  const [selectedLog, setSelectedLog] = useState<ApplicationLog | null>(null);
  const [showFilters, setShowFilters] = useState(true);

  const fetchLogs = async (currentPage = page) => {
    setLoading(true);
    try {
      const data = await observabilityService.getLogs({
        service_name: serviceName || undefined,
        log_level: logLevel || undefined,
        keyword: keyword || undefined,
        correlation_id: correlationId || undefined,
        request_id: requestId || undefined,
        page: currentPage,
        page_size: pageSize,
      });
      setLogs(data.logs);
      setTotalCount(data.total_count);
    } catch (err) {
      console.error('Failed to fetch logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs(1);
    setPage(1);
  }, [serviceName, logLevel, correlationId, requestId]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchLogs(1);
    setPage(1);
  };

  const getLogLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
      case 'CRITICAL':
        return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-950/20 dark:text-red-400 dark:border-red-900/30';
      case 'WARNING':
        return 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/30';
      case 'INFO':
        return 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-950/20 dark:text-blue-400 dark:border-blue-900/30';
      default:
        return 'bg-secondary text-muted-foreground border-border';
    }
  };

  const totalPages = Math.ceil(totalCount / pageSize) || 1;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Log Explorer"
        subtitle="Full-text and structured trace audits across REST gateways, database handlers, and AI copilot agents."
        actions={
          <Button variant="outline" size="sm" onClick={() => fetchLogs(page)} disabled={loading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Refresh Logs
          </Button>
        }
      />

      {/* Query filters */}
      <Card className="p-4 space-y-4">
        <form onSubmit={handleSearch} className="space-y-4">
          <div className="flex justify-between items-center border-b border-border pb-2">
            <div className="flex items-center gap-2">
              <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
              <h4 className="text-xs font-bold text-foreground">Query Parameters</h4>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="xs"
              onClick={() => setShowFilters(!showFilters)}
            >
              {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </Button>
          </div>

          {showFilters && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <label className="block text-[10px] font-bold text-muted-foreground uppercase mb-1">Service Module</label>
                <select
                  value={serviceName}
                  onChange={(e) => setServiceName(e.target.value)}
                  className="w-full text-xs bg-secondary border border-border rounded-md px-3 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="">All Services</option>
                  <option value="rest-api">REST API Gateway</option>
                  <option value="erp-core">ERP Core Services</option>
                  <option value="auth-service">Identity Provider</option>
                  <option value="rag-service">RAG Retrieval Service</option>
                  <option value="copilot-core">AI Copilot Core</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-muted-foreground uppercase mb-1">Log Level</label>
                <select
                  value={logLevel}
                  onChange={(e) => setLogLevel(e.target.value)}
                  className="w-full text-xs bg-secondary border border-border rounded-md px-3 py-2 text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
                >
                  <option value="">All Levels</option>
                  <option value="INFO">INFO</option>
                  <option value="WARNING">WARNING</option>
                  <option value="ERROR">ERROR</option>
                  <option value="DEBUG">DEBUG</option>
                </select>
              </div>

              <div>
                <label className="block text-[10px] font-bold text-muted-foreground uppercase mb-1">Correlation ID</label>
                <Input
                  placeholder="e.g. corr-xxx"
                  value={correlationId}
                  onChange={(e) => setCorrelationId(e.target.value)}
                  className="py-1.5"
                />
              </div>

              <div>
                <label className="block text-[10px] font-bold text-muted-foreground uppercase mb-1">Request ID</label>
                <Input
                  placeholder="e.g. req-xxx"
                  value={requestId}
                  onChange={(e) => setRequestId(e.target.value)}
                  className="py-1.5"
                />
              </div>
            </div>
          )}

          <div className="flex gap-2">
            <div className="flex-grow">
              <Input
                placeholder="Search log messages, keywords, exceptions..."
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                icon={<Search className="h-4 w-4 text-muted-foreground" />}
                className="py-2"
              />
            </div>
            <Button type="submit" size="sm" disabled={loading}>
              Search Logs
            </Button>
          </div>
        </form>
      </Card>

      {/* Logs View Grid */}
      <Card className="overflow-hidden">
        <div className="divide-y divide-border font-mono text-[11px] bg-secondary/30 max-h-[500px] overflow-y-auto">
          {loading && logs.length === 0 ? (
            <div className="p-12 text-center text-muted-foreground">
              <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-2 text-primary" />
              Polling system-wide logs...
            </div>
          ) : logs.length === 0 ? (
            <div className="p-12 text-center text-muted-foreground border border-dashed border-border m-4 rounded-lg">
              <Terminal className="h-8 w-8 mx-auto mb-2 text-muted-foreground/60" />
              No logs matched your query parameters.
            </div>
          ) : (
            logs.map((log) => (
              <div
                key={log.id}
                onClick={() => setSelectedLog(log)}
                className="p-3 hover:bg-muted/10 cursor-pointer flex flex-col md:flex-row gap-3 transition-colors text-foreground items-start md:items-center"
              >
                <span className="text-muted-foreground/60 select-none shrink-0 w-36">
                  {new Date(log.timestamp).toLocaleTimeString()} {new Date(log.timestamp).toLocaleDateString()}
                </span>
                <span className={`px-2 py-0.5 rounded text-[9px] font-bold border shrink-0 uppercase ${getLogLevelColor(log.log_level)}`}>
                  {log.log_level}
                </span>
                <span className="text-[10px] font-bold bg-muted px-1.5 py-0.5 rounded text-muted-foreground shrink-0 font-mono">
                  {log.service_name}
                </span>
                <span className="truncate flex-grow font-sans text-foreground/90">{log.message}</span>
                {(log.request_id || log.correlation_id) && (
                  <span className="text-[9px] font-bold text-primary bg-primary/5 px-2 py-0.5 border border-primary/10 rounded-full shrink-0">
                    ID: {log.request_id ? 'REQ' : 'CORR'}
                  </span>
                )}
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        <div className="px-4 py-3 border-t border-border flex justify-between items-center bg-card">
          <span className="text-xs text-muted-foreground">
            Total count: <strong className="text-foreground">{totalCount}</strong> entries
          </span>
          <div className="flex gap-2">
            <Button
              size="xs"
              variant="outline"
              disabled={page === 1 || loading}
              onClick={() => {
                const prev = page - 1;
                setPage(prev);
                fetchLogs(prev);
              }}
            >
              Previous
            </Button>
            <span className="text-xs text-muted-foreground flex items-center font-bold px-2">
              Page {page} of {totalPages}
            </span>
            <Button
              size="xs"
              variant="outline"
              disabled={page === totalPages || loading}
              onClick={() => {
                const next = page + 1;
                setPage(next);
                fetchLogs(next);
              }}
            >
              Next
            </Button>
          </div>
        </div>
      </Card>

      {/* Log Detail Modal */}
      {selectedLog && (
        <Modal
          isOpen={!!selectedLog}
          onClose={() => setSelectedLog(null)}
          title="Log Metadata Inspector"
        >
          <div className="space-y-4 text-xs">
            <div className="grid grid-cols-2 gap-4 border-b border-border pb-3">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Service Module</span>
                <p className="font-bold text-foreground font-mono mt-0.5">{selectedLog.service_name}</p>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Log Level</span>
                <p className="mt-0.5">
                  <span className={`px-2 py-0.5 rounded text-[9px] font-bold border uppercase ${getLogLevelColor(selectedLog.log_level)}`}>
                    {selectedLog.log_level}
                  </span>
                </p>
              </div>
            </div>

            <div className="space-y-1">
              <span className="text-[10px] text-muted-foreground uppercase font-bold">Message Details</span>
              <p className="bg-secondary p-3 rounded border font-mono text-foreground whitespace-pre-wrap">
                {selectedLog.message}
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 border-t border-b border-border py-3">
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Request ID</span>
                <p className="font-mono text-foreground mt-0.5">{selectedLog.request_id || 'N/A'}</p>
              </div>
              <div>
                <span className="text-[10px] text-muted-foreground uppercase font-bold">Correlation ID</span>
                <p className="font-mono text-foreground mt-0.5">{selectedLog.correlation_id || 'N/A'}</p>
              </div>
            </div>

            <div className="space-y-1.5">
              <span className="text-[10px] text-muted-foreground uppercase font-bold">Structured Context Payload</span>
              <pre className="bg-secondary p-3 rounded border font-mono text-[10px] text-foreground overflow-x-auto">
                {JSON.stringify(selectedLog.structured_data || {}, null, 2)}
              </pre>
            </div>

            <div className="flex justify-end pt-2">
              <Button size="sm" onClick={() => setSelectedLog(null)}>
                Close Inspector
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
export default LogExplorer;
