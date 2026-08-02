/**
 * AuditLogsPage — Enterprise Security Audit Logger Console
 *
 * Connects GET /api/v1/auth/audit-logs
 */

import React, { useState, useEffect } from 'react';
import { ShieldAlert, FileCode, Globe, RefreshCw, UserCheck } from 'lucide-react';
import { apiClient } from '@/services/apiClient';
import { useNotification } from '@/hooks/useNotification';

export interface AuditLogRecord {
  id: string;
  organization_id: string | null;
  user_id: string | null;
  event_type: string;
  category: string;
  ip_address: string | null;
  status: string;
  details: Record<string, any> | string | null;
  created_at: string;
}

export function AuditLogsPage() {
  const [logs, setLogs] = useState<AuditLogRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [categoryFilter, setCategoryFilter] = useState<string>('ALL');
  const { addNotification } = useNotification();

  const fetchAuditLogs = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/auth/audit-logs');
      const data = res.data?.data ?? res.data;
      setLogs(Array.isArray(data) ? data : []);
    } catch (err: any) {
      addNotification(err.message || 'Failed to load security audit logs', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const filteredLogs = logs.filter((item) => {
    if (categoryFilter === 'ALL') return true;
    return item.category?.toUpperCase() === categoryFilter || item.event_type?.toUpperCase().includes(categoryFilter);
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <ShieldAlert className="h-6 w-6 text-primary" />
            Security & System Audit Logs
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Immutable SOC 2 compliant trail of state modifications, logins, password changes, and access events
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="h-9 px-3 border border-border bg-card rounded-xl text-xs font-semibold text-foreground focus:outline-none"
          >
            <option value="ALL">All Event Categories</option>
            <option value="AUTH">Authentication Events</option>
            <option value="SECURITY">Security Changes</option>
            <option value="PROFILE">Profile Updates</option>
            <option value="ORGANIZATION">Organization Administration</option>
          </select>
          <button
            onClick={fetchAuditLogs}
            className="p-2 rounded-xl bg-card border border-border hover:bg-muted text-foreground transition"
            title="Refresh Audit Trail"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 text-muted-foreground font-semibold border-b border-border uppercase text-[10px]">
            <tr>
              <th className="py-3 px-4">Event Type</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">IP Address</th>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4 text-right">Details Payload</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 text-foreground">
            {filteredLogs.length === 0 && !loading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-muted-foreground">
                  <FileCode className="h-8 w-8 mx-auto mb-2 opacity-50 text-primary" />
                  No audit log events found.
                </td>
              </tr>
            ) : (
              filteredLogs.map((item) => (
                <tr key={item.id} className="hover:bg-muted/30 transition">
                  <td className="py-3 px-4 font-sans font-bold text-foreground flex items-center gap-2">
                    <UserCheck className="h-4 w-4 text-primary" />
                    {item.event_type}
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-0.5 rounded-lg bg-primary/10 text-primary font-mono text-[10px] font-bold uppercase">
                      {item.category || 'SECURITY'}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono text-muted-foreground flex items-center gap-1">
                    <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                    {item.ip_address || '127.0.0.1'}
                  </td>
                  <td className="py-3 px-4 font-mono text-muted-foreground">
                    {new Date(item.created_at).toLocaleString()}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-[10px] text-muted-foreground max-w-xs truncate">
                    {typeof item.details === 'object'
                      ? JSON.stringify(item.details)
                      : String(item.details || 'State Modified')}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default AuditLogsPage;
