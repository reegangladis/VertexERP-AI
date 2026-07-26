import React, { useState } from 'react';
import {
  User,
  ShieldAlert,
  Smartphone,
  History,
  Monitor,
  Trash2,
  Lock,
  Globe,
  Clock,
  QrCode,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { Alert } from '@/components/Alert';
import { PageHeader } from '@/components/PageHeader';
import { useNotification } from '@/hooks/useNotification';

export function UserSettings() {
  const { addNotification } = useNotification();
  const [activeSubTab, setActiveSubTab] = useState('profile');

  // Subsections states
  const [profile, setProfile] = useState({
    firstName: 'Reegangladis',
    lastName: 'AI',
    phone: '+1 (555) 019-2831',
    timezone: 'UTC',
    language: 'en',
  });

  const [passwordForm, setPasswordForm] = useState({
    oldPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  const [sessions, setSessions] = useState([
    { id: 's1', ip: '192.168.1.52', device: 'Chrome (macOS)', location: 'San Jose, CA', current: true },
    { id: 's2', ip: '203.0.113.88', device: 'Safari (iOS)', location: 'New York, NY', current: false },
  ]);

  const [loginHistory] = useState([
    { time: '2026-07-24 15:45 UTC', ip: '192.168.1.52', status: 'success', device: 'Chrome (macOS)' },
    { time: '2026-07-23 09:20 UTC', ip: '203.0.113.88', status: 'success', device: 'Safari (iOS)' },
    { time: '2026-07-22 18:10 UTC', ip: '198.51.100.12', status: 'failed', device: 'Firefox (Windows)', reason: 'Incorrect credentials' },
  ]);

  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [mfaSecret] = useState('JBSWY3DPEHPK3PXP'); // Mock TOTP key
  const [backupCodes, setBackupCodes] = useState<string[]>([]);

  const handleUpdateProfile = (e: React.FormEvent) => {
    e.preventDefault();
    addNotification('Profile settings updated successfully', 'success');
  };

  const handleChangePassword = (e: React.FormEvent) => {
    e.preventDefault();
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      addNotification('Passwords do not match', 'error');
      return;
    }
    addNotification('Password updated successfully', 'success');
    setPasswordForm({ oldPassword: '', newPassword: '', confirmPassword: '' });
  };

  const handleTerminateSession = (id: string) => {
    setSessions((prev) => prev.filter((s) => s.id !== id));
    addNotification('Session terminated successfully', 'info');
  };

  const handleGenerateBackupCodes = () => {
    const codes = Array.from({ length: 8 }, () => Math.random().toString(36).substring(2, 8).toUpperCase());
    setBackupCodes(codes);
    addNotification('Backup recovery codes generated', 'success');
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Account Settings"
        description="Govern your user profiles, Multi-factor auth keys, and concurrent sessions."
      />

      {/* Tabs */}
      <div className="flex border-b border-border select-none gap-4">
        {[
          { id: 'profile', label: 'My Profile', icon: <User className="h-4 w-4" /> },
          { id: 'security', label: 'Security & MFA', icon: <Lock className="h-4 w-4" /> },
          { id: 'sessions', label: 'Active Sessions', icon: <Monitor className="h-4 w-4" /> },
          { id: 'history', label: 'Login History', icon: <History className="h-4 w-4" /> },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={`flex items-center gap-2 pb-3 text-sm font-medium border-b-2 px-1 transition-all cursor-pointer ${
              activeSubTab === tab.id
                ? 'border-primary text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* 1. PROFILE SUBTAB */}
      {activeSubTab === 'profile' && (
        <Card>
          <CardHeader>
            <CardTitle>Profile Details</CardTitle>
            <CardDescription>Adjust your primary identification details, timezone, and language locales.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpdateProfile} className="space-y-4 max-w-lg">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="First Name"
                  value={profile.firstName}
                  onChange={(e) => setProfile((p) => ({ ...p, firstName: e.target.value }))}
                />
                <Input
                  label="Last Name"
                  value={profile.lastName}
                  onChange={(e) => setProfile((p) => ({ ...p, lastName: e.target.value }))}
                />
              </div>
              <Input
                label="Phone Number"
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
                    <option value="EST">EST (GMT-5)</option>
                    <option value="PST">PST (GMT-8)</option>
                  </select>
                </div>
              </div>
              <Button variant="primary" type="submit" className="pt-2">
                Save Adjustments
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* 2. SECURITY SUBTAB */}
      {activeSubTab === 'security' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
              <CardDescription>Verify your existing credentials and set a new secure access key.</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleChangePassword} className="space-y-4 max-w-lg">
                <Input
                  label="Current Password"
                  type="password"
                  value={passwordForm.oldPassword}
                  onChange={(e) => setPasswordForm((p) => ({ ...p, oldPassword: e.target.value }))}
                />
                <Input
                  label="New Password"
                  type="password"
                  value={passwordForm.newPassword}
                  onChange={(e) => setPasswordForm((p) => ({ ...p, newPassword: e.target.value }))}
                />
                <Input
                  label="Confirm New Password"
                  type="password"
                  value={passwordForm.confirmPassword}
                  onChange={(e) => setPasswordForm((p) => ({ ...p, confirmPassword: e.target.value }))}
                />
                <Button variant="primary" type="submit" className="pt-2">
                  Update Key
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Multi-Factor Authentication (MFA)</CardTitle>
              <CardDescription>Harden your profile security using a standard TOTP Authenticator application.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Smartphone className="h-5 w-5 text-muted-foreground" />
                <div className="flex-grow">
                  <h4 className="text-sm font-semibold text-foreground">TOTP Authenticator</h4>
                  <p className="text-xs text-muted-foreground">Google Authenticator, Microsoft, or Authy app checks.</p>
                </div>
                <Button
                  variant={mfaEnabled ? 'danger' : 'outline'}
                  size="sm"
                  onClick={() => setMfaEnabled(!mfaEnabled)}
                >
                  {mfaEnabled ? 'Disable' : 'Enable'}
                </Button>
              </div>

              {mfaEnabled && (
                <div className="border border-border p-4 rounded-lg bg-secondary/10 flex flex-col md:flex-row items-center gap-6 max-w-xl">
                  <div className="bg-white p-2 rounded border border-border shrink-0">
                    <QrCode className="h-28 w-28 text-slate-800" />
                  </div>
                  <div className="space-y-3">
                    <p className="text-xs text-muted-foreground leading-relaxed">
                      Scan the QR code with your mobile authenticator app. If you cannot scan the barcode, enter the key manually:
                    </p>
                    <code className="block text-xs font-mono bg-background border border-border px-2 py-1 rounded select-all font-semibold w-max text-primary">
                      {mfaSecret}
                    </code>
                    
                    <div className="border-t border-border pt-3 space-y-2">
                      <Button variant="outline" size="sm" onClick={handleGenerateBackupCodes}>
                        Generate Backup Codes
                      </Button>
                      
                      {backupCodes.length > 0 && (
                        <div className="grid grid-cols-4 gap-1.5 font-mono text-[10px] text-foreground bg-background border border-border p-2.5 rounded max-w-sm">
                          {backupCodes.map((code) => (
                            <span key={code} className="text-center">{code}</span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* 3. SESSIONS SUBTAB */}
      {activeSubTab === 'sessions' && (
        <Card>
          <CardHeader>
            <CardTitle>Active Telemetry Sessions</CardTitle>
            <CardDescription>Track or terminate active concurrent dashboard sessions.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Browser / OS Client</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sessions.map((sess) => (
                  <TableRow key={sess.id}>
                    <TableCell className="font-semibold flex items-center gap-2">
                      <Monitor className="h-4 w-4 text-muted-foreground" />
                      {sess.device}
                      {sess.current && (
                        <span className="text-[9px] uppercase px-1 bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 rounded">
                          Current
                        </span>
                      )}
                    </TableCell>
                    <TableCell className="font-mono text-xs text-muted-foreground">{sess.ip}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{sess.location}</TableCell>
                    <TableCell className="text-right">
                      {!sess.current && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="p-1.5 h-auto w-auto rounded text-destructive"
                          onClick={() => handleTerminateSession(sess.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}

      {/* 4. HISTORY SUBTAB */}
      {activeSubTab === 'history' && (
        <Card>
          <CardHeader>
            <CardTitle>Audited Login History</CardTitle>
            <CardDescription>Verify dates, client IPs, and status counters for recent authentication requests.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Access Timestamp</TableHead>
                  <TableHead>Browser Client</TableHead>
                  <TableHead>IP Address</TableHead>
                  <TableHead>Resolution Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loginHistory.map((hist, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-xs font-mono text-muted-foreground">{hist.time}</TableCell>
                    <TableCell className="text-xs">{hist.device}</TableCell>
                    <TableCell className="text-xs font-mono text-muted-foreground">{hist.ip}</TableCell>
                    <TableCell>
                      <span
                        className={`inline-flex items-center text-xs font-semibold px-2 py-0.5 rounded-full ${
                          hist.status === 'success'
                            ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                            : 'bg-red-500/10 text-red-500 border border-red-500/20'
                        }`}
                        title={hist.reason}
                      >
                        {hist.status}
                      </span>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
export default UserSettings;
