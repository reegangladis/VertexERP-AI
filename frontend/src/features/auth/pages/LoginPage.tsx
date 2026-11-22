import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Lock, Mail, Building2, ShieldCheck, ArrowRight } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";

interface LoginResponseDto {
  access_token: string;
  user_id: string;
  tenant_id: string;
  organization_id: string;
  roles: string[];
  permissions: string[];
  mfa_required?: boolean;
}

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [tenantSlug, setTenantSlug] = useState("");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const payload: Record<string, string> = {
        email,
        password,
      };
      if (tenantSlug) payload.tenant_slug = tenantSlug;
      if (mfaCode) payload.mfa_code = mfaCode;

      const res = await apiClient<LoginResponseDto>("/identity/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      if (res.mfa_required) {
        setMfaRequired(true);
        setError("Two-Factor Authentication required. Enter your 6-digit TOTP code.");
        setIsLoading(false);
        return;
      }

      setAuth({
        userId: res.user_id,
        email,
        fullName: email.split("@")[0],
        tenantId: res.tenant_id,
        organizationId: res.organization_id,
        roles: res.roles || [],
        permissions: res.permissions || [],
      });

      navigate("/analytics", { replace: true });
    } catch (err: any) {
      setError(err?.problem?.detail || err?.message || "Invalid credentials or authentication error.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 items-center justify-center p-4">
      <div className="w-full max-w-md space-y-8 rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl backdrop-blur-xl">
        <div className="text-center space-y-2">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600/20 text-indigo-400 ring-1 ring-indigo-500/30">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white">VertexERP AI V2</h2>
          <p className="text-sm text-slate-400">Enterprise Multi-Tenant Management Portal</p>
        </div>

        {error && (
          <div className="rounded-lg border border-red-500/20 bg-red-500/10 p-3 text-xs text-red-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Corporate Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@enterprise.io"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/60 pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/60 pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-300 mb-1">Tenant Slug (Optional)</label>
            <div className="relative">
              <Building2 className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                value={tenantSlug}
                onChange={(e) => setTenantSlug(e.target.value)}
                placeholder="enterprise-prod"
                className="w-full rounded-lg border border-slate-800 bg-slate-950/60 pl-9 pr-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
          </div>

          {mfaRequired && (
            <div>
              <label className="block text-xs font-medium text-amber-400 mb-1">MFA TOTP Code</label>
              <input
                type="text"
                required
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                placeholder="123456"
                maxLength={6}
                className="w-full rounded-lg border border-amber-500/50 bg-slate-950/60 px-3 py-2 text-center text-lg font-mono tracking-widest text-amber-300 placeholder-slate-600 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="flex w-full items-center justify-center space-x-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-600/30 transition-all hover:bg-indigo-500 disabled:opacity-50"
          >
            {isLoading ? (
              <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            ) : (
              <>
                <span>Sign In Securely</span>
                <ArrowRight className="h-4 w-4" />
              </>
            )}
          </button>
        </form>

        <div className="text-center text-xs text-slate-500">
          VertexERP AI V2 Enterprise Security Gateway • Dual-Cookie Session
        </div>
      </div>
    </div>
  );
};
