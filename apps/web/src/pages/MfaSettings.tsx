import React, { useState, useEffect } from 'react';
import { Shield, Key, QrCode, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/Button';
import { Input } from '@/components/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { Alert } from '@/components/Alert';
import { PageHeader } from '@/components/PageHeader';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

export function MfaSettingsPage() {
  const { addNotification } = useNotification();
  const [loading, setLoading] = useState(false);
  const [mfaData, setMfaData] = useState<{ totp_secret: string; qr_code_url: string; backup_codes: string[] } | null>(null);
  const [otpCode, setOtpCode] = useState('');
  const [isMfaEnabled, setIsMfaEnabled] = useState(false);

  const handleGenerateSecret = async () => {
    setLoading(true);
    try {
      const res = await apiClient.post<{ totp_secret: string; qr_code_url: string; backup_codes: string[] }>('/mfa/generate-secret');
      setMfaData(res);
      addNotification('MFA secret generated successfully', 'success');
    } catch (err: any) {
      addNotification(err?.message || 'Failed to generate MFA secret', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpCode || otpCode.length !== 6) return;
    setLoading(true);
    try {
      await apiClient.post('/mfa/verify', { code: otpCode });
      setIsMfaEnabled(true);
      addNotification('MFA verified and enabled on account', 'success');
    } catch (err: any) {
      addNotification(err?.message || 'Invalid OTP code', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDisableMfa = async () => {
    setLoading(true);
    try {
      await apiClient.post('/mfa/disable');
      setIsMfaEnabled(false);
      setMfaData(null);
      addNotification('MFA disabled successfully', 'info');
    } catch (err: any) {
      addNotification(err?.message || 'Failed to disable MFA', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto p-6">
      <PageHeader
        title="Multi-Factor Authentication (MFA)"
        subtitle="Manage your TOTP two-factor security and backup recovery codes."
        icon={Shield}
      />

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>MFA Security Status</span>
            <span className={`px-3 py-1 text-xs rounded-full font-medium ${isMfaEnabled ? 'bg-emerald-500/20 text-emerald-400' : 'bg-amber-500/20 text-amber-400'}`}>
              {isMfaEnabled ? 'Enabled' : 'Disabled'}
            </span>
          </CardTitle>
          <CardDescription>
            Two-factor authentication adds an extra layer of protection to your account by requiring an authenticator code.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {!mfaData && !isMfaEnabled && (
            <div>
              <Button onClick={handleGenerateSecret} disabled={loading} className="gap-2">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Key className="w-4 h-4" />}
                Setup Authenticator App
              </Button>
            </div>
          )}

          {mfaData && !isMfaEnabled && (
            <div className="space-y-6 border border-zinc-800 rounded-lg p-4 bg-zinc-900/50">
              <div className="flex items-start gap-4">
                <div className="p-3 bg-zinc-800 rounded-lg">
                  <QrCode className="w-8 h-8 text-blue-400" />
                </div>
                <div>
                  <h4 className="font-semibold text-zinc-100">Scan QR Code or enter Secret Key</h4>
                  <p className="text-sm text-zinc-400">Secret Key: <code className="bg-zinc-800 px-2 py-1 rounded text-emerald-400">{mfaData.totp_secret}</code></p>
                </div>
              </div>

              {mfaData.backup_codes?.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium text-zinc-300 mb-2">Backup Recovery Codes (Save these securely)</h5>
                  <div className="grid grid-cols-4 gap-2">
                    {mfaData.backup_codes.map((code, idx) => (
                      <div key={idx} className="bg-zinc-800 px-3 py-1.5 rounded font-mono text-xs text-center text-zinc-200">
                        {code}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <form onSubmit={handleVerifyOtp} className="flex gap-4 items-end">
                <div className="flex-1">
                  <label className="text-xs text-zinc-400 block mb-1">Enter 6-Digit OTP Code</label>
                  <Input
                    value={otpCode}
                    onChange={(e) => setOtpCode(e.target.value)}
                    placeholder="123456"
                    maxLength={6}
                  />
                </div>
                <Button type="submit" disabled={loading || otpCode.length !== 6}>
                  {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Verify & Enable MFA'}
                </Button>
              </form>
            </div>
          )}

          {isMfaEnabled && (
            <div className="flex items-center justify-between border border-emerald-900/50 bg-emerald-950/20 p-4 rounded-lg">
              <div className="flex items-center gap-3">
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
                <div>
                  <p className="font-medium text-emerald-200">MFA is active on your account</p>
                  <p className="text-xs text-emerald-400/80">Your login requests require a TOTP code from your authenticator app.</p>
                </div>
              </div>
              <Button variant="outline" onClick={handleDisableMfa} disabled={loading} className="text-rose-400 border-rose-900 hover:bg-rose-950">
                Disable MFA
              </Button>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
