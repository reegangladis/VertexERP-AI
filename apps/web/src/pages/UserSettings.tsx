/**
 * UserSettings — Enterprise Account Management
 *
 * Tabs: Profile | Security & Password | Active Sessions | Login History
 *
 * All data fetched from real API endpoints.
 * All mutations call real backend.
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  User,
  Monitor,
  History,
  Lock,
  Globe,
  Clock,
  Trash2,
  Loader2,
  ShieldCheck,
  LogOut,
  Eye,
  EyeOff,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { Alert } from '@/components/Alert';
import { PageHeader } from '@/components/PageHeader';
import { PasswordStrengthMeter } from '@/components/PasswordStrengthMeter';
import { useNotification } from '@/hooks/useNotification';
import { useAuth } from '@/store/AuthContext';
import { apiClient } from '@/services/apiClient';

// ─────────────────────────────────────────
// Types
// ─────────────────────────────────────────

interface Session {
  id: string;
  ip_address: string;
  user_agent: string;
  device_info: string | null;
  is_active: boolean;
  expires_at: string;
  created_at: string;
}

interface LoginHistoryEntry {
  id: string;
  email: string;
  ip_address: string;
  user_agent: string;
  browser: string | null;
  os: string | null;
  status: string;
  failure_reason: string | null;
  created_at: string;
}

// ─────────────────────────────────────────
// Utility
// ─────────────────────────────────────────

function usePasswordVisibility() {
  const [visible, setVisible] = useState(false);
  const toggle = () => setVisible((v) => !v);
  const type = visible ? 'text' : 'password';
  const Icon = visible ? EyeOff : Eye;
  return { toggle, type, Icon };
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleString(undefined, {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return iso;
  }
}

// ─────────────────────────────────────────
// Component
// ─────────────────────────────────────────

export function UserSettings() {
  const { addNotification } = useNotification();
  const { user, updateUser, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  // ── Profile state ──
  const [profile, setProfile] = useState({
    first_name: user?.first_name ?? '',
    last_name: user?.last_name ?? '',
    phone: user?.phone ?? '',
    timezone: user?.timezone ?? 'UTC',
    language: user?.language ?? 'en',
  });
  const [profileSaving, setProfileSaving] = useState(false);

  // ── Password state ──
  const [passwordForm, setPasswordForm] = useState({
    old_password: '',
    new_password: '',
    confirm_password: '',
  });
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);
  const oldPwd = usePasswordVisibility();
  const newPwd = usePasswordVisibility();
  const confirmPwd = usePasswordVisibility();

  // ── Sessions state ──
  const [sessions, setSessions] = useState<Session[]>([]);
  const [sessionsLoading, setSessionsLoading] = useState(false);
  const [terminatingId, setTerminatingId] = useState<string | null>(null);

  // ── History state ──
  const [loginHistory, setLoginHistory] = useState<LoginHistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // ── Sync profile from auth context ──
  useEffect(() => {
    if (user) {
      setProfile({
        first_name: user.first_name,
        last_name: user.last_name,
        phone: user.phone ?? '',
        timezone: user.timezone,
        language: user.language,
      });
    }
  }, [user]);

  // ── Fetch sessions when tab is active ──
  const fetchSessions = useCallback(async () => {
    setSessionsLoading(true);
    try {
      const res = await apiClient.get('/api/v1/auth/sessions');
      setSessions(res.data?.data ?? []);
    } catch (err: any) {
      addNotification(err.message || 'Failed to load sessions', 'error');
    } finally {
      setSessionsLoading(false);
    }
  }, [addNotification]);

  // ── Fetch login history when tab is active ──
  const fetchHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const res = await apiClient.get('/api/v1/auth/login-history');
      setLoginHistory(res.data?.data ?? []);
    } catch (err: any) {
      addNotification(err.message || 'Failed to load login history', 'error');
    } finally {
      setHistoryLoading(false);
    }
  }, [addNotification]);

  useEffect(() => {
    if (activeTab === 'sessions') fetchSessions();
    if (activeTab === 'history') fetchHistory();
  }, [activeTab, fetchSessions, fetchHistory]);

  // ── Save Profile ──
  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileSaving(true);
    try {
      const res = await apiClient.put('/api/v1/auth/me', {
        first_name: profile.first_name,
        last_name: profile.last_name,
        phone: profile.phone || undefined,
        timezone: profile.timezone,
        language: profile.language,
      });
      const updated = res.data?.data ?? res.data;
      updateUser(updated);
      addNotification('Profile updated successfully', 'success');
    } catch (err: any) {
      addNotification(err.message || 'Failed to update profile', 'error');
    } finally {
      setProfileSaving(false);
    }
  };

  // ── Change Password ──
  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError(null);

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setPasswordError('New password and confirmation do not match');
      return;
    }

    setPasswordSaving(true);
    try {
      await apiClient.put('/api/v1/auth/change-password', {
        old_password: passwordForm.old_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password,
      });
      addNotification('Password updated successfully', 'success');
      setPasswordForm({ old_password: '', new_password: '', confirm_password: '' });
    } catch (err: any) {
      setPasswordError(err.message || 'Failed to change password');
    } finally {
      setPasswordSaving(false);
    }
  };

  // ── Terminate Session ──
  const handleTerminateSession = async (sessionId: string) => {
    setTerminatingId(sessionId);
    try {
      await apiClient.delete(`/api/v1/auth/sessions/${sessionId}`);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      addNotification('Session terminated successfully', 'info');
    } catch (err: any) {
      addNotification(err.message || 'Failed to terminate session', 'error');
    } finally {
      setTerminatingId(null);
    }
  };

  // ── Logout All Sessions ──
  const handleLogoutAll = async () => {
    try {
      await apiClient.delete('/api/v1/auth/logout-all');
      addNotification('All sessions terminated. Logging out…', 'info');
      setTimeout(() => logout(), 1500);
    } catch (err: any) {
      addNotification(err.message || 'Failed to terminate all sessions', 'error');
    }
  };

  // ─────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────

  const TABS = [
    { id: 'profile', label: 'My Profile', icon: <User className="h-4 w-4" /> },
    { id: 'security', label: 'Security', icon: <Lock className="h-4 w-4" /> },
    { id: 'sessions', label: 'Active Sessions', icon: <Monitor className="h-4 w-4" /> },
    { id: 'history', label: 'Login History', icon: <History className="h-4 w-4" /> },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Account Settings"
        description="Manage your profile, security credentials, and active sessions."
      />

      {/* Tab Navigation */}
      <div className="flex border-b border-border select-none gap-4">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 pb-3 text-sm font-medium border-b-2 px-1 transition-all cursor-pointer ${
              activeTab === tab.id
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* ── PROFILE TAB ── */}
      {activeTab === 'profile' && (
        <Card>
          <CardHeader>
            <CardTitle>Profile Details</CardTitle>
            <CardDescription>
              Update your name, contact info, timezone, and language preferences.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSaveProfile} className="space-y-4 max-w-lg">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="First Name"
                  value={profile.first_name}
                  onChange={(e) => setProfile((p) => ({ ...p, first_name: e.target.value }))}
                />
                <Input
                  label="Last Name"
                  value={profile.last_name}
                  onChange={(e) => setProfile((p) => ({ ...p, last_name: e.target.value }))}
                />
              </div>

              {/* Read-only email */}
              <div className="flex flex-col space-y-1.5">
                <label className="text-sm font-medium text-muted-foreground">Email Address</label>
                <div className="flex items-center gap-2 h-10 px-3 border border-input rounded-md bg-secondary/20">
                  <span className="text-sm text-muted-foreground">{user?.email}</span>
                  {user?.email_verified ? (
                    <span className="ml-auto flex items-center gap-1 text-[10px] text-emerald-500 font-bold uppercase">
                      <CheckCircle2 className="h-3 w-3" /> Verified
                    </span>
                  ) : (
                    <span className="ml-auto flex items-center gap-1 text-[10px] text-amber-500 font-bold uppercase">
                      <AlertCircle className="h-3 w-3" /> Unverified
                    </span>
                  )}
                </div>
              </div>

              <Input
                label="Phone Number"
                type="tel"
                placeholder="+1 555 000 0000"
                value={profile.phone}
                onChange={(e) => setProfile((p) => ({ ...p, phone: e.target.value }))}
              />

              <div className="grid grid-cols-2 gap-3">
                <div className="flex flex-col space-y-1.5">
                  <label className="text-sm font-medium flex items-center gap-1.5">
                    <Globe className="h-3.5 w-3.5 text-muted-foreground" />
                    Language
                  </label>
                  <select
                    value={profile.language}
                    onChange={(e) => setProfile((p) => ({ ...p, language: e.target.value }))}
                    className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="en">English (US)</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="de">Deutsch</option>
                    <option value="ja">日本語</option>
                  </select>
                </div>

                <div className="flex flex-col space-y-1.5">
                  <label className="text-sm font-medium flex items-center gap-1.5">
                    <Clock className="h-3.5 w-3.5 text-muted-foreground" />
                    Timezone
                  </label>
                  <select
                    value={profile.timezone}
                    onChange={(e) => setProfile((p) => ({ ...p, timezone: e.target.value }))}
                    className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="UTC">UTC (GMT+0)</option>
                    <option value="America/New_York">EST (GMT-5)</option>
                    <option value="America/Los_Angeles">PST (GMT-8)</option>
                    <option value="Europe/London">BST (GMT+1)</option>
                    <option value="Europe/Paris">CET (GMT+1)</option>
                    <option value="Asia/Kolkata">IST (GMT+5:30)</option>
                    <option value="Asia/Tokyo">JST (GMT+9)</option>
                  </select>
                </div>
              </div>

              <Button
                variant="primary"
                type="submit"
                isLoading={profileSaving}
                className="flex items-center gap-2"
              >
                {!profileSaving && <ShieldCheck className="h-4 w-4" />}
                Save Profile
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* ── SECURITY TAB ── */}
      {activeTab === 'security' && (
        <Card>
          <CardHeader>
            <CardTitle>Change Password</CardTitle>
            <CardDescription>
              Verify your current credentials and set a new secure passphrase.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleChangePassword} className="space-y-4 max-w-lg">
              {passwordError && <Alert variant="danger">{passwordError}</Alert>}

              <div className="relative">
                <Input
                  label="Current Password"
                  type={oldPwd.type}
                  value={passwordForm.old_password}
                  onChange={(e) => setPasswordForm((p) => ({ ...p, old_password: e.target.value }))}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={oldPwd.toggle}
                  className="absolute right-3 top-8 p-1 hover:bg-secondary rounded"
                >
                  <oldPwd.Icon className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>

              <div className="relative">
                <Input
                  label="New Password"
                  type={newPwd.type}
                  value={passwordForm.new_password}
                  onChange={(e) => setPasswordForm((p) => ({ ...p, new_password: e.target.value }))}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={newPwd.toggle}
                  className="absolute right-3 top-8 p-1 hover:bg-secondary rounded"
                >
                  <newPwd.Icon className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>

              {passwordForm.new_password && (
                <PasswordStrengthMeter password={passwordForm.new_password} />
              )}

              <div className="relative">
                <Input
                  label="Confirm New Password"
                  type={confirmPwd.type}
                  value={passwordForm.confirm_password}
                  onChange={(e) => setPasswordForm((p) => ({ ...p, confirm_password: e.target.value }))}
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={confirmPwd.toggle}
                  className="absolute right-3 top-8 p-1 hover:bg-secondary rounded"
                >
                  <confirmPwd.Icon className="h-4 w-4 text-muted-foreground" />
                </button>
              </div>

              <Button variant="primary" type="submit" isLoading={passwordSaving}>
                {!passwordSaving && <Lock className="h-4 w-4 mr-1.5" />}
                Update Password
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* ── SESSIONS TAB ── */}
      {activeTab === 'sessions' && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <div>
                <CardTitle>Active Sessions</CardTitle>
                <CardDescription>
                  View and terminate active login sessions across all devices.
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={fetchSessions}
                  className="flex items-center gap-1.5"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  Refresh
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleLogoutAll}
                  className="flex items-center gap-1.5"
                >
                  <LogOut className="h-3.5 w-3.5" />
                  Logout All
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {sessionsLoading ? (
              <div className="flex justify-center py-10">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : sessions.length === 0 ? (
              <p className="text-sm text-muted-foreground italic text-center py-6">
                No active sessions found.
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Device / Browser</TableHead>
                    <TableHead>IP Address</TableHead>
                    <TableHead>Started</TableHead>
                    <TableHead>Expires</TableHead>
                    <TableHead className="text-right">Action</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sessions.map((sess) => (
                    <TableRow key={sess.id}>
                      <TableCell className="font-medium flex items-center gap-2">
                        <Monitor className="h-4 w-4 text-muted-foreground shrink-0" />
                        <span className="text-xs">{sess.device_info ?? sess.user_agent.slice(0, 40) + '…'}</span>
                      </TableCell>
                      <TableCell className="font-mono text-xs text-muted-foreground">
                        {sess.ip_address}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {formatDate(sess.created_at)}
                      </TableCell>
                      <TableCell className="text-xs text-muted-foreground">
                        {formatDate(sess.expires_at)}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-auto w-auto p-1.5 text-destructive hover:bg-destructive/10"
                          onClick={() => handleTerminateSession(sess.id)}
                          disabled={terminatingId === sess.id}
                        >
                          {terminatingId === sess.id ? (
                            <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Trash2 className="h-3.5 w-3.5" />
                          )}
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}

      {/* ── HISTORY TAB ── */}
      {activeTab === 'history' && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-center">
              <div>
                <CardTitle>Login History</CardTitle>
                <CardDescription>
                  Audited record of all authentication attempts for your account.
                </CardDescription>
              </div>
              <Button
                variant="secondary"
                size="sm"
                onClick={fetchHistory}
                className="flex items-center gap-1.5"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Refresh
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            {historyLoading ? (
              <div className="flex justify-center py-10">
                <Loader2 className="h-6 w-6 animate-spin text-primary" />
              </div>
            ) : loginHistory.length === 0 ? (
              <p className="text-sm text-muted-foreground italic text-center py-6">
                No login history found.
              </p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Timestamp</TableHead>
                    <TableHead>Browser / OS</TableHead>
                    <TableHead>IP Address</TableHead>
                    <TableHead>Status</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {loginHistory.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="text-xs font-mono text-muted-foreground whitespace-nowrap">
                        {formatDate(entry.created_at)}
                      </TableCell>
                      <TableCell className="text-xs">
                        {entry.browser ?? '—'} {entry.os ? `(${entry.os})` : ''}
                      </TableCell>
                      <TableCell className="text-xs font-mono text-muted-foreground">
                        {entry.ip_address}
                      </TableCell>
                      <TableCell>
                        <span
                          title={entry.failure_reason ?? undefined}
                          className={`inline-flex items-center text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide ${
                            entry.status === 'success'
                              ? 'bg-emerald-500/10 text-emerald-600 border border-emerald-500/20'
                              : 'bg-red-500/10 text-red-600 border border-red-500/20'
                          }`}
                        >
                          {entry.status}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default UserSettings;
