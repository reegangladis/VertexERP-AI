import React, { useState } from 'react';
import {
  Building2,
  ShieldCheck,
  FileSearch,
  User,
} from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from '@/components/Table';
import { PageHeader } from '@/components/PageHeader';
import { useNotification } from '@/hooks/useNotification';

export function TenantSettings() {
  const { addNotification } = useNotification();
  const [activeTab, setActiveTab] = useState('organization');

  // Org settings states
  const [org, setOrg] = useState({
    name: 'Acme Corp',
    slug: 'acme-corp',
    email: 'contact@acme.com',
    phone: '+1 (555) 123-4567',
    country: 'United States',
    timezone: 'PST',
    currency: 'USD',
    locale: 'en_US',
    brandPrimary: '#0052FF',
    brandSecondary: '#F4F5F7',
  });

  const [passwordPolicy, setPasswordPolicy] = useState({
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecial: true,
    expiryDays: 90,
    lockoutThreshold: 5,
    lockoutMinutes: 15,
  });

  const [auditLogs] = useState([
    { time: '2026-07-24 15:46 UTC', user: 'admin@vertexerp.ai', action: 'user.login', details: 'Successful authentication check' },
    { time: '2026-07-24 14:30 UTC', user: 'admin@vertexerp.ai', action: 'role.clone', details: 'Cloned custom Employee role' },
    { time: '2026-07-24 11:20 UTC', user: 'emma.stone@acme.com', action: 'user.update', details: 'Updated profile language to French' },
  ]);

  const handleUpdateOrg = (e: React.FormEvent) => {
    e.preventDefault();
    addNotification('Organization settings updated successfully', 'success');
  };

  const handleUpdatePolicy = (e: React.FormEvent) => {
    e.preventDefault();
    addNotification('Password policies updated successfully', 'success');
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Tenant Administration"
        description="Govern corporate details, branding colors, password restrictions, and audit registers."
      />

      {/* Navigation tabs */}
      <div className="flex border-b border-border select-none gap-4">
        {[
          { id: 'organization', label: 'Company Profile', icon: <Building2 className="h-4 w-4" /> },
          { id: 'policies', label: 'Security Policies', icon: <ShieldCheck className="h-4 w-4" /> },
          { id: 'audit', label: 'Audit Timeline', icon: <FileSearch className="h-4 w-4" /> },
        ].map((tab) => (
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

      {/* 1. ORGANIZATION SUBTAB */}
      {activeTab === 'organization' && (
        <Card>
          <CardHeader>
            <CardTitle>Company Details</CardTitle>
            <CardDescription>Setup metadata profiles, support emails, localized timezone contexts, and brand colors.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpdateOrg} className="space-y-4 max-w-xl">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Organization Name"
                  value={org.name}
                  onChange={(e) => setOrg((o) => ({ ...o, name: e.target.value }))}
                />
                <Input
                  label="Organization Slug"
                  disabled
                  value={org.slug}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Tenant Email"
                  type="email"
                  value={org.email}
                  onChange={(e) => setOrg((o) => ({ ...o, email: e.target.value }))}
                />
                <Input
                  label="Tenant Phone"
                  value={org.phone}
                  onChange={(e) => setOrg((o) => ({ ...o, phone: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-3 gap-3 border-t border-border pt-4">
                <div className="flex flex-col space-y-1.5">
                  <label className="text-sm font-medium">Currency</label>
                  <select
                    value={org.currency}
                    onChange={(e) => setOrg((o) => ({ ...o, currency: e.target.value }))}
                    className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="USD">USD ($)</option>
                    <option value="EUR">EUR (€)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>
                <div className="flex flex-col space-y-1.5">
                  <label className="text-sm font-medium">Locale</label>
                  <select
                    value={org.locale}
                    onChange={(e) => setOrg((o) => ({ ...o, locale: e.target.value }))}
                    className="h-10 border border-input rounded-md bg-background px-3 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="en_US">en_US</option>
                    <option value="es_ES">es_ES</option>
                    <option value="fr_FR">fr_FR</option>
                  </select>
                </div>
                <Input
                  label="Working Country"
                  value={org.country}
                  onChange={(e) => setOrg((o) => ({ ...o, country: e.target.value }))}
                />
              </div>

              <div className="border-t border-border pt-4 mt-2 grid grid-cols-2 gap-3">
                <Input
                  label="Brand Primary Color"
                  value={org.brandPrimary}
                  onChange={(e) => setOrg((o) => ({ ...o, brandPrimary: e.target.value }))}
                  helperText="Primary HSL variable mapping"
                />
                <Input
                  label="Brand Secondary Color"
                  value={org.brandSecondary}
                  onChange={(e) => setOrg((o) => ({ ...o, brandSecondary: e.target.value }))}
                  helperText="Secondary backgrounds"
                />
              </div>

              <Button variant="primary" type="submit" className="pt-2">
                Save Tenant Profile
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* 2. POLICIES SUBTAB */}
      {activeTab === 'policies' && (
        <Card>
          <CardHeader>
            <CardTitle>Brute Force & Password Policies</CardTitle>
            <CardDescription>Setup strict character matching, password lifetimes, account lockout triggers, and session timeouts.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleUpdatePolicy} className="space-y-4 max-w-xl">
              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Minimum Characters Length"
                  type="number"
                  value={passwordPolicy.minLength}
                  onChange={(e) => setPasswordPolicy((p) => ({ ...p, minLength: parseInt(e.target.value) }))}
                />
                <Input
                  label="Key Expiry Days"
                  type="number"
                  value={passwordPolicy.expiryDays}
                  onChange={(e) => setPasswordPolicy((p) => ({ ...p, expiryDays: parseInt(e.target.value) }))}
                />
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={passwordPolicy.requireUppercase}
                    onChange={(e) => setPasswordPolicy((p) => ({ ...p, requireUppercase: e.target.checked }))}
                    className="rounded border-border text-primary focus:ring-ring h-4 w-4"
                  />
                  <span>Enforce uppercase characters</span>
                </label>
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={passwordPolicy.requireLowercase}
                    onChange={(e) => setPasswordPolicy((p) => ({ ...p, requireLowercase: e.target.checked }))}
                    className="rounded border-border text-primary focus:ring-ring h-4 w-4"
                  />
                  <span>Enforce lowercase characters</span>
                </label>
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={passwordPolicy.requireNumbers}
                    onChange={(e) => setPasswordPolicy((p) => ({ ...p, requireNumbers: e.target.checked }))}
                    className="rounded border-border text-primary focus:ring-ring h-4 w-4"
                  />
                  <span>Enforce numeric digits</span>
                </label>
                <label className="flex items-center gap-2 text-sm text-foreground cursor-pointer select-none">
                  <input
                    type="checkbox"
                    checked={passwordPolicy.requireSpecial}
                    onChange={(e) => setPasswordPolicy((p) => ({ ...p, requireSpecial: e.target.checked }))}
                    className="rounded border-border text-primary focus:ring-ring h-4 w-4"
                  />
                  <span>Enforce special symbols</span>
                </label>
              </div>

              <div className="border-t border-border pt-4 mt-2 grid grid-cols-2 gap-3">
                <Input
                  label="Lockout Threshold Attempts"
                  type="number"
                  value={passwordPolicy.lockoutThreshold}
                  onChange={(e) => setPasswordPolicy((p) => ({ ...p, lockoutThreshold: parseInt(e.target.value) }))}
                  helperText="Maximum failed log in checks"
                />
                <Input
                  label="Lockout Duration (Minutes)"
                  type="number"
                  value={passwordPolicy.lockoutMinutes}
                  onChange={(e) => setPasswordPolicy((p) => ({ ...p, lockoutMinutes: parseInt(e.target.value) }))}
                  helperText="Lockout duration for accounts"
                />
              </div>

              <Button variant="primary" type="submit" className="pt-2">
                Save Policies
              </Button>
            </form>
          </CardContent>
        </Card>
      )}

      {/* 3. AUDIT SUBTAB */}
      {activeTab === 'audit' && (
        <Card>
          <CardHeader>
            <CardTitle>System Audit Registry</CardTitle>
            <CardDescription>Audited operational logs recording system administrative modifications.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Event Timestamp</TableHead>
                  <TableHead>User Account</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Description Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auditLogs.map((log, i) => (
                  <TableRow key={i}>
                    <TableCell className="text-xs font-mono text-muted-foreground">{log.time}</TableCell>
                    <TableCell className="text-xs flex items-center gap-2 font-semibold">
                      <User className="h-3.5 w-3.5 text-muted-foreground" />
                      {log.user}
                    </TableCell>
                    <TableCell className="text-xs font-mono text-primary select-all font-medium">{log.action}</TableCell>
                    <TableCell className="text-xs text-muted-foreground">{log.details}</TableCell>
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
export default TenantSettings;
