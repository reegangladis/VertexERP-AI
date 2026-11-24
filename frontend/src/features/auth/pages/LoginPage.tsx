import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, KeyRound, Eye, EyeOff, Sparkles, AlertCircle, CheckCircle2 } from "lucide-react";
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

interface DemoPersona {
  roleName: string;
  roleColor: string;
  email: string;
  label: string;
}

const VERTEX_PERSONAS: DemoPersona[] = [
  {
    roleName: "Admin",
    roleColor: "text-[#5a9cff]",
    email: "admin@vertexerp.com",
    label: "Super Administrator",
  },
  {
    roleName: "Employee (ESS)",
    roleColor: "text-[#34d399]",
    email: "employee@vertexerp.com",
    label: "Self-Service Portal",
  },
  {
    roleName: "Sales Manager",
    roleColor: "text-[#a855f7]",
    email: "sales@vertexerp.com",
    label: "Salesforce CRM & Deals",
  },
  {
    roleName: "HR Manager",
    roleColor: "text-[#fbbf24]",
    email: "hr@vertexerp.com",
    label: "People Ops & Approvals",
  },
];

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const [email, setEmail] = useState("admin@vertexerp.com");
  const [password, setPassword] = useState("DemoPassword123!");
  const [showPassword, setShowPassword] = useState(false);
  const [tenantSlug] = useState("apex");
  const [mfaCode, setMfaCode] = useState("");
  const [mfaRequired, setMfaRequired] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [selectedPersona, setSelectedPersona] = useState<string>("admin@vertexerp.com");

  const selectPersona = (persona: DemoPersona) => {
    setEmail(persona.email);
    setPassword("DemoPassword123!");
    setSelectedPersona(persona.email);
    setError(null);
    setInfoMessage(`Loaded credentials for ${persona.roleName} (${persona.email})`);
    setTimeout(() => setInfoMessage(null), 3500);
  };

  const handleForgotPassword = () => {
    setInfoMessage("Demo Credentials: Use password 'DemoPassword123!' with any demo persona below. In production, a secure reset link will be dispatched to your corporate email.");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setInfoMessage(null);

    try {
      const payload: Record<string, string> = {
        email: email.trim(),
        password: password.trim(),
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

      const roles = res.roles || [];
      setAuth({
        userId: res.user_id,
        email,
        fullName: email.split("@")[0],
        tenantId: res.tenant_id,
        organizationId: res.organization_id,
        roles,
        permissions: res.permissions || [],
      });

      // Navigate based on persona role
      if (roles.includes("EMPLOYEE") && !roles.includes("SUPER_ADMIN") && !roles.includes("TenantAdmin")) {
        navigate("/ess", { replace: true });
      } else if (roles.includes("SALES_MANAGER")) {
        navigate("/crm", { replace: true });
      } else {
        navigate("/analytics", { replace: true });
      }
    } catch (err: any) {
      setError(err?.problem?.detail || err?.message || "Invalid credentials or authentication error.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-[#070b14] p-4 sm:p-6 text-slate-100 selection:bg-indigo-500 selection:text-white overflow-hidden">
      {/* Ambient Radial Background Glows */}
      <div className="pointer-events-none absolute -top-32 left-1/2 h-[450px] w-[650px] -translate-x-1/2 rounded-full bg-indigo-600/10 blur-[130px]" />
      <div className="pointer-events-none absolute -bottom-32 right-[-10%] h-[350px] w-[500px] rounded-full bg-purple-600/10 blur-[120px]" />

      {/* Main Authentication Card */}
      <div className="relative z-10 w-full max-w-[480px] rounded-[28px] border border-[#1b253b] bg-[#0d1424]/90 p-8 sm:p-10 shadow-2xl shadow-black/80 backdrop-blur-2xl">
        {/* Header */}
        <div>
          <h1 className="text-3xl sm:text-[32px] font-bold tracking-tight text-white">
            Log in to continue
          </h1>
          <p className="mt-2 text-sm text-slate-400 font-normal">
            Welcome back! Please enter your account credentials.
          </p>
        </div>

        {/* Notice Info Banner */}
        <div className="mt-6 mb-6 flex items-start gap-3 rounded-2xl border border-[#222e49] bg-[#141d30] p-4">
          <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-[#818cf8] shadow-[0_0_8px_#818cf8]" />
          <p className="text-xs sm:text-[13px] font-normal leading-relaxed text-slate-300">
            Please log in to access your organization workspace, employee portal, and enterprise modules.
          </p>
        </div>

        {/* Error Feedback */}
        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-400">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Info / Toast Feedback */}
        {infoMessage && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-indigo-500/30 bg-indigo-500/10 p-3 text-xs text-indigo-300">
            <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-indigo-400" />
            <span>{infoMessage}</span>
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email Address */}
          <div>
            <label className="mb-2 block text-[11px] font-bold uppercase tracking-wider text-slate-400">
              EMAIL ADDRESS
            </label>
            <div className="relative rounded-xl border border-[#202c44] bg-[#090e18] transition-all focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500">
              <User className="absolute left-4 top-3.5 h-4 w-4 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setSelectedPersona("");
                }}
                placeholder="admin@vertexerp.com"
                className="w-full bg-transparent py-3 pl-11 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="mb-2 block text-[11px] font-bold uppercase tracking-wider text-slate-400">
              PASSWORD
            </label>
            <div className="relative rounded-xl border border-[#202c44] bg-[#090e18] transition-all focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500">
              <KeyRound className="absolute left-4 top-3.5 h-4 w-4 text-slate-400" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-transparent py-3 pl-11 pr-11 text-sm text-white placeholder-slate-500 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-3.5 text-slate-400 transition-colors hover:text-slate-200"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

          {/* MFA TOTP input if required */}
          {mfaRequired && (
            <div>
              <label className="mb-2 block text-[11px] font-bold uppercase tracking-wider text-amber-400">
                2-FACTOR AUTHENTICATION CODE
              </label>
              <input
                type="text"
                required
                value={mfaCode}
                onChange={(e) => setMfaCode(e.target.value)}
                placeholder="123456"
                maxLength={6}
                className="w-full rounded-xl border border-amber-500/50 bg-[#090e18] py-2.5 text-center font-mono text-lg tracking-widest text-amber-300 placeholder-slate-600 focus:border-amber-400 focus:outline-none focus:ring-1 focus:ring-amber-400"
              />
            </div>
          )}

          {/* Forgotten Credentials Link */}
          <div className="pt-1 text-right">
            <button
              type="button"
              onClick={handleForgotPassword}
              className="text-xs font-normal text-slate-400 transition-colors hover:text-indigo-400"
            >
              Forgotten your username or password?
            </button>
          </div>

          {/* Sign In Button */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full items-center justify-center rounded-2xl bg-gradient-to-r from-[#4f46e5] via-[#6366f1] to-[#8b5cf6] py-3.5 px-4 text-sm font-semibold text-white shadow-lg shadow-indigo-600/35 transition-all hover:opacity-95 active:scale-[0.99] disabled:opacity-50"
            >
              {isLoading ? (
                <span className="h-5 w-5 animate-spin rounded-full border-2 border-white border-t-transparent" />
              ) : (
                <span>Sign In to VertexERP</span>
              )}
            </button>
          </div>
        </form>

        {/* Demo Personas Section */}
        <div className="mt-8">
          <div className="mb-3 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-slate-400">
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            <span>DEMO PERSONAS (DEVELOPMENT)</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {VERTEX_PERSONAS.map((p) => {
              const isSelected = selectedPersona === p.email;
              return (
                <button
                  key={p.roleName}
                  type="button"
                  onClick={() => selectPersona(p)}
                  className={`group rounded-xl border p-3 text-left transition-all ${
                    isSelected
                      ? "border-indigo-500 bg-[#162138] ring-1 ring-indigo-500/50"
                      : "border-[#1e2a42] bg-[#0f1728]/80 hover:border-slate-700 hover:bg-[#141d30]"
                  }`}
                >
                  <div className={`text-xs sm:text-sm font-semibold ${p.roleColor}`}>
                    {p.roleName}
                  </div>
                  <div className="mt-0.5 truncate text-[11px] text-slate-400 group-hover:text-slate-300">
                    {p.email}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
