/**
 * SessionsPage — Enterprise Active Session Management Console
 *
 * Connects GET /api/v1/auth/sessions, DELETE /api/v1/auth/sessions/{id}, DELETE /api/v1/auth/logout-all
 */

import React, { useState, useEffect } from 'react';
import { ShieldCheck, Monitor, Smartphone, Globe, Trash2, LogOut, RefreshCw } from 'lucide-react';
import { apiClient } from '@/services/apiClient';
import { useNotification } from '@/hooks/useNotification';
import { useAuth } from '@/store/AuthContext';

export interface UserSession {
  id: string;
  user_id: string;
  ip_address: string | null;
  user_agent: string | null;
  device_type?: string | null;
  browser?: string | null;
  os?: string | null;
  is_current: boolean;
  created_at: string;
  last_activity_at: string;
  expires_at: string;
}

export function SessionsPage() {
  const [sessions, setSessions] = useState<UserSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [terminatingId, setTerminatingId] = useState<string | null>(null);
  const { addNotification } = useNotification();
  const { logoutAll } = useAuth();

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/auth/sessions');
      const data = res.data?.data ?? res.data;
      setSessions(Array.isArray(data) ? data : []);
    } catch (err: any) {
      addNotification(err.message || 'Failed to load active sessions', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleTerminateSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to terminate this active session?')) return;
    setTerminatingId(sessionId);
    try {
      await apiClient.delete(`/api/v1/auth/sessions/${sessionId}`);
      addNotification('Session terminated successfully', 'success');
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    } catch (err: any) {
      addNotification(err.message || 'Failed to terminate session', 'error');
    } finally {
      setTerminatingId(null);
    }
  };

  const handleTerminateAll = async () => {
    if (!confirm('Are you sure you want to log out of ALL active sessions on all devices?')) return;
    try {
      await logoutAll();
      addNotification('All active sessions terminated', 'info');
    } catch (err: any) {
      addNotification(err.message || 'Failed to terminate all sessions', 'error');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <ShieldCheck className="h-6 w-6 text-primary" />
            Active User Sessions
          </h1>
          <p className="text-xs text-muted-foreground mt-1">
            Manage your active authentication sessions, devices, and remote IP connections
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchSessions}
            className="p-2 rounded-xl bg-card border border-border hover:bg-muted text-foreground transition"
            title="Refresh Sessions"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={handleTerminateAll}
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-red-500/10 text-red-500 border border-red-500/20 hover:bg-red-500/20 font-semibold text-xs transition"
          >
            <LogOut className="h-4 w-4" />
            Revoke All Other Sessions
          </button>
        </div>
      </div>

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {sessions.length === 0 && !loading ? (
          <div className="col-span-2 p-12 text-center text-muted-foreground bg-card rounded-2xl border border-border">
            <ShieldCheck className="h-10 w-10 mx-auto mb-2 opacity-50 text-primary" />
            <p className="font-semibold text-sm">No active sessions found.</p>
          </div>
        ) : (
          sessions.map((session) => {
            const isMobile = session.user_agent?.toLowerCase().includes('mobile');
            return (
              <div
                key={session.id}
                className={`p-5 rounded-2xl bg-card border ${
                  session.is_current ? 'border-primary/50 ring-1 ring-primary/20' : 'border-border'
                } shadow-sm space-y-4 relative`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-primary/10 text-primary">
                      {isMobile ? <Smartphone className="h-6 w-6" /> : <Monitor className="h-6 w-6" />}
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <h3 className="font-bold text-sm text-foreground">
                          {session.browser || 'Web Browser'} {session.os ? `(${session.os})` : ''}
                        </h3>
                        {session.is_current && (
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                            Current Session
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground font-mono mt-0.5 flex items-center gap-1">
                        <Globe className="h-3 w-3" /> {session.ip_address || '127.0.0.1'}
                      </p>
                    </div>
                  </div>

                  {!session.is_current && (
                    <button
                      onClick={() => handleTerminateSession(session.id)}
                      disabled={terminatingId === session.id}
                      className="p-2 text-muted-foreground hover:text-red-500 rounded-lg hover:bg-muted transition"
                      title="Terminate Session"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>

                <div className="border-t border-border/60 pt-3 grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <div>
                    <span className="text-[10px] uppercase font-bold text-muted-foreground/70 block">
                      Started At
                    </span>
                    <span className="font-mono text-foreground">
                      {new Date(session.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase font-bold text-muted-foreground/70 block">
                      Last Activity
                    </span>
                    <span className="font-mono text-foreground">
                      {new Date(session.last_activity_at || session.created_at).toLocaleString()}
                    </span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default SessionsPage;
