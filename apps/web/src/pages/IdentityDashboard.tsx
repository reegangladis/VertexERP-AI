import React, { useState, useEffect } from 'react';
import { Shield, User, Building2, Monitor, History, Key, Lock, Laptop, CheckCircle2, Clock } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { PageHeader } from '@/components/PageHeader';
import { useAuth } from '@/store/AuthContext';
import { apiClient } from '@/services/apiClient';

export function IdentityDashboard() {
  const { user } = useAuth();
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadIdentityStats() {
      setLoading(true);
      try {
        const res = await apiClient.get<any[]>('/sessions');
        setSessions(res || []);
      } catch (err) {
        console.error('Failed to load session info', err);
      } finally {
        setLoading(false);
      }
    }
    loadIdentityStats();
  }, []);

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-6">
      <PageHeader
        title="Enterprise Identity Dashboard"
        subtitle="Overview of user account, current sessions, security status, and trusted devices."
        icon={Shield}
      />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Current User</CardTitle>
            <User className="w-4 h-4 text-blue-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-zinc-100">{user?.first_name} {user?.last_name}</div>
            <p className="text-xs text-zinc-400 mt-1">{user?.email}</p>
            <div className="mt-3 flex gap-2">
              <span className="px-2 py-0.5 text-xs bg-blue-500/20 text-blue-400 rounded">@{user?.username}</span>
              <span className="px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-400 rounded capitalize">{user?.status || 'Active'}</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Organization & Tenant</CardTitle>
            <Building2 className="w-4 h-4 text-purple-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-zinc-100">VertexERP Enterprise</div>
            <p className="text-xs text-zinc-400 mt-1">Tenant ID: {user?.organization_id || 'Primary Tenant'}</p>
            <div className="mt-3 flex gap-2">
              <span className="px-2 py-0.5 text-xs bg-purple-500/20 text-purple-400 rounded">Multi-Tenant Mode</span>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-zinc-900/60 border-zinc-800">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-zinc-400">Security Status</CardTitle>
            <Lock className="w-4 h-4 text-emerald-400" />
          </CardHeader>
          <CardContent>
            <div className="text-xl font-bold text-zinc-100">
              {user?.mfa_enabled ? 'MFA Protected' : 'Standard Protection'}
            </div>
            <p className="text-xs text-zinc-400 mt-1">
              Email Verified: {user?.email_verified ? 'Yes' : 'Pending'}
            </p>
            <div className="mt-3 flex gap-2">
              <span className={`px-2 py-0.5 text-xs rounded ${user?.mfa_enabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
                {user?.mfa_enabled ? 'MFA Enabled' : 'MFA Off'}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="bg-zinc-900/60 border-zinc-800">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Monitor className="w-5 h-5 text-blue-400" />
            <span>Active Sessions & Trusted Devices</span>
          </CardTitle>
          <CardDescription>
            Live active refresh tokens and authenticated client sessions.
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sessions.length === 0 ? (
            <div className="text-sm text-zinc-400 py-4 text-center">No active sessions found or loaded.</div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Device / Browser</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Last Activity</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sessions.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-medium flex items-center gap-2">
                      <Laptop className="w-4 h-4 text-zinc-400" />
                      <span>{s.device_name || s.browser || 'Web Session'}</span>
                    </TableCell>
                    <TableCell>{s.ip_address}</TableCell>
                    <TableCell>{new Date(s.last_activity).toLocaleString()}</TableCell>
                    <TableCell>
                      <span className="px-2 py-0.5 text-xs bg-emerald-500/20 text-emerald-400 rounded">
                        Active
                      </span>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
