/**
 * LoginHistoryPage — Enterprise Authentication Login History Log
 *
 * Connects GET /api/v1/auth/login-history
 */

import React, { useState, useEffect } from 'react';
import { History, ShieldCheck, CheckCircle2, XCircle, Globe, RefreshCw } from 'lucide-react';
import { apiClient } from '@/services/apiClient';
import { useNotification } from '@/hooks/useNotification';

export interface LoginHistoryRecord {
  id: string;
  user_id: string;
  ip_address: string | null;
  user_agent: string | null;
  status: string;
  failure_reason: string | null;
  created_at: string;
}

export function LoginHistoryPage() {
  const [history, setHistory] = useState<LoginHistoryRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const { addNotification } = useNotification();

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/auth/login-history');
      const data = res.data?.data ?? res.data;
      setHistory(Array.isArray(data) ? data : []);
    } catch (err: any) {
      addNotification(err.message || 'Failed to load login history', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <History className="h-6 w-6 text-primary" />
            Authentication Login History
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Historical audit log of login attempts, IP addresses, browsers, and security statuses
          </p>
        </div>
        <button
          onClick={fetchHistory}
          className="p-2 rounded-xl bg-card border border-border hover:bg-muted text-foreground transition"
          title="Refresh History"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* History Table */}
      <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
        <table className="w-full text-left text-xs">
          <thead className="bg-muted/50 text-muted-foreground font-semibold border-b border-border uppercase text-[10px]">
            <tr>
              <th className="py-3 px-4">Status</th>
              <th className="py-3 px-4">IP Address</th>
              <th className="py-3 px-4">User Agent / Browser</th>
              <th className="py-3 px-4">Timestamp</th>
              <th className="py-3 px-4 text-right">Details</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/60 text-foreground">
            {history.length === 0 && !loading ? (
              <tr>
                <td colSpan={5} className="py-12 text-center text-muted-foreground">
                  <ShieldCheck className="h-8 w-8 mx-auto mb-2 opacity-50 text-primary" />
                  No login history records found.
                </td>
              </tr>
            ) : (
              history.map((item) => {
                const isSuccess = item.status === 'SUCCESS' || item.status === 'SUCCESSFUL';
                return (
                  <tr key={item.id} className="hover:bg-muted/30 transition">
                    <td className="py-3 px-4">
                      {isSuccess ? (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 inline-flex items-center gap-1">
                          <CheckCircle2 className="h-3 w-3" /> SUCCESS
                        </span>
                      ) : (
                        <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-red-500/10 text-red-500 border border-red-500/20 inline-flex items-center gap-1">
                          <XCircle className="h-3 w-3" /> FAILED
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 font-mono font-bold flex items-center gap-1.5">
                      <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                      {item.ip_address || '127.0.0.1'}
                    </td>
                    <td className="py-3 px-4 text-muted-foreground max-w-xs truncate font-mono text-[11px]">
                      {item.user_agent || 'Standard REST Client'}
                    </td>
                    <td className="py-3 px-4 font-mono text-muted-foreground">
                      {new Date(item.created_at).toLocaleString()}
                    </td>
                    <td className="py-3 px-4 text-right text-muted-foreground font-mono text-[11px]">
                      {item.failure_reason || 'Authenticated'}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default LoginHistoryPage;
