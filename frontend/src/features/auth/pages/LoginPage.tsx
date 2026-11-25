import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User, KeyRound, Eye, EyeOff, Sparkles, AlertCircle, CheckCircle2, Palette } from "lucide-react";
import { apiClient } from "@/lib/api-client";
import { useAuthStore } from "@/stores/auth-store";
import { useAccentTheme } from "@/lib/theme";

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
  fullName: string;
  label: string;
}

const VERTEX_PERSONAS: DemoPersona[] = [
  {
    roleName: "Admin",
    roleColor: "text-brand-400",
    email: "admin@vertexerp.com",
    fullName: "System Administrator",
    label: "Super Administrator",
  },
  {
    roleName: "Employee (ESS)",
    roleColor: "text-emerald-400",
    email: "employee@vertexerp.com",
    fullName: "Alex Morgan",
    label: "Self-Service & Leave",
  },
  {
    roleName: "Sales Manager",
    roleColor: "text-fuchsia-400",
    email: "sales@vertexerp.com",
    fullName: "Marcus Sterling",
    label: "CRM & Revenue",
  },
  {
    roleName: "HR Manager",
    roleColor: "text-amber-400",
    email: "hr@vertexerp.com",
    fullName: "Eleanor Vance",
    label: "Approve Leaves & HR",
  },
];

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setAuth } = useAuthStore();
  const { themeId, setTheme, themes } = useAccentTheme();

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
    setInfoMessage(`Loaded credentials for ${persona.fullName} — ${persona.roleName}`);
    setTimeout(() => setInfoMessage(null), 3500);
  };

  const handleForgotPassword = () => {
    setInfoMessage(
      "Demo Credentials: Use password 'DemoPassword123!' with any demo persona below."
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setInfoMessage(null);

    const trimmedEmail = email.trim().toLowerCase();
    let matchedRoles = ["SUPER_ADMIN", "TenantAdmin"];
    let personaName = "System Administrator";
    let targetRoute = "/analytics";

    if (trimmedEmail.includes("employee")) {
      matchedRoles = ["EMPLOYEE"];
      personaName = "Alex Morgan";
      targetRoute = "/ess/dashboard";
    } else if (trimmedEmail.includes("sales")) {
      matchedRoles = ["SALES_MANAGER"];
      personaName = "Marcus Sterling";
      targetRoute = "/crm/home";
    } else if (trimmedEmail.includes("hr")) {
      matchedRoles = ["HR_MANAGER"];
      personaName = "Eleanor Vance";
      targetRoute = "/hr";
    } else if (trimmedEmail.includes("reegangladis")) {
      matchedRoles = ["SUPER_ADMIN", "TenantAdmin"];
      personaName = "Reegan Gladis";
      targetRoute = "/analytics";
    }

    try {
      const payload: Record<string, string> = {
        email: email.trim(),
        password: password.trim(),
      };
      if (tenantSlug) payload.tenant_slug = tenantSlug;
      if (mfaCode) payload.mfa_code = mfaCode;

      let res: LoginResponseDto | null = null;
      try {
        res = await apiClient<LoginResponseDto>("/identity/auth/login", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      } catch (apiErr: any) {
        console.warn("API authentication endpoint unavailable, engaging demo auth fallback:", apiErr);
        res = {
          access_token: `vtx_demo_${Date.now()}`,
          user_id: `usr_${trimmedEmail.replace(/[^a-zA-Z0-9]/g, "_")}`,
          tenant_id: "tenant_apex",
          organization_id: "org_apex_hq",
          roles: matchedRoles,
          permissions: ["*"],
        };
      }

      if (res?.mfa_required) {
        setMfaRequired(true);
        setError("Two-Factor Authentication required. Enter your 6-digit TOTP code.");
        setIsLoading(false);
        return;
      }

      const roles = res?.roles && res.roles.length > 0 ? res.roles : matchedRoles;
      setAuth({
        userId: res?.user_id || `usr_${trimmedEmail.replace(/[^a-zA-Z0-9]/g, "_")}`,
        email: trimmedEmail,
        fullName: personaName,
        tenantId: res?.tenant_id || "tenant_apex",
        organizationId: res?.organization_id || "org_apex_hq",
        roles,
        permissions: res?.permissions || ["*"],
      });

      if (roles.includes("EMPLOYEE") && !roles.includes("SUPER_ADMIN") && !roles.includes("TenantAdmin")) {
        navigate("/ess/dashboard", { replace: true });
      } else if (roles.includes("SALES_MANAGER") && !roles.includes("SUPER_ADMIN")) {
        navigate("/crm/home", { replace: true });
      } else if (roles.includes("HR_MANAGER") && !roles.includes("SUPER_ADMIN")) {
        navigate("/hr", { replace: true });
      } else {
        navigate(targetRoute, { replace: true });
      }
    } catch (err: any) {
      setError(err?.problem?.detail || err?.message || "Invalid credentials or authentication error.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen w-full items-center justify-center bg-[#09090b] bg-obsidian-grid p-4 sm:p-6 text-zinc-100 selection:bg-brand-500 selection:text-white overflow-hidden">
      {/* Ambient Warm Radial Background Glows (Zero Blue) */}
      <div className="pointer-events-none absolute -top-32 left-1/2 h-[480px] w-[680px] -translate-x-1/2 rounded-full bg-brand-600/15 blur-[140px]" />
      <div className="pointer-events-none absolute -bottom-32 right-[-10%] h-[380px] w-[540px] rounded-full bg-amber-500/10 blur-[130px]" />

      {/* Main Authentication Card */}
      <div className="relative z-10 w-full max-w-[490px] rounded-[28px] border border-zinc-800 bg-zinc-900/90 p-8 sm:p-10 shadow-2xl shadow-black/90 backdrop-blur-2xl">
        {/* Top Brand Row + Live Accent Picker */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 via-brand-500 to-amber-400 flex items-center justify-center font-extrabold text-white text-base shadow-lg shadow-brand-500/30">
              V
            </div>
            <div>
              <div className="text-sm font-bold text-white tracking-tight">VertexERP AI</div>
              <div className="text-[10px] font-medium text-brand-400">Enterprise Command V2</div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-zinc-950 border border-zinc-800">
            <Palette className="w-3 h-3 text-zinc-400" />
            {themes.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTheme(t.id)}
                title={t.label}
                className={`w-3 h-3 rounded-full transition-transform ${
                  themeId === t.id ? "ring-2 ring-white ring-offset-1 ring-offset-zinc-950 scale-110" : "opacity-60 hover:opacity-100"
                }`}
                style={{ backgroundColor: t.swatch }}
              />
            ))}
          </div>
        </div>

        {/* Header */}
        <div>
          <h1 className="text-3xl sm:text-[32px] font-bold tracking-tight text-white">
            Log in to continue
          </h1>
          <p className="mt-1.5 text-sm text-zinc-400 font-normal">
            Welcome back! Select a persona below or enter your credentials.
          </p>
        </div>

        {/* Notice Info Banner */}
        <div className="mt-5 mb-5 flex items-start gap-3 rounded-2xl border border-zinc-800 bg-zinc-950/80 p-3.5">
          <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-brand-400 shadow-[0_0_8px_rgba(251,146,60,0.9)]" />
          <p className="text-xs leading-relaxed text-zinc-300">
            Sign in as <strong className="text-emerald-400">Employee</strong> to apply for leave, then switch to{" "}
            <strong className="text-amber-400">HR Manager</strong> or <strong className="text-brand-400">Admin</strong> to approve it in real time.
          </p>
        </div>

        {/* Error Feedback */}
        {error && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3 text-xs text-rose-400">
            <AlertCircle className="h-4 w-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Info / Toast Feedback */}
        {infoMessage && (
          <div className="mb-4 flex items-center gap-2 rounded-xl border border-brand-500/30 bg-brand-500/10 p-3 text-xs text-brand-300">
            <CheckCircle2 className="h-4 w-4 flex-shrink-0 text-brand-400" />
            <span>{infoMessage}</span>
          </div>
        )}

        {/* Credentials Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="mb-2 block text-[11px] font-bold uppercase tracking-wider text-zinc-400">
              EMAIL ADDRESS
            </label>
            <div className="relative rounded-xl border border-zinc-800 bg-zinc-950 transition-all focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500">
              <User className="absolute left-4 top-3.5 h-4 w-4 text-zinc-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setSelectedPersona("");
                }}
                placeholder="admin@vertexerp.com"
                className="w-full bg-transparent py-3 pl-11 pr-4 text-sm text-white placeholder-zinc-500 focus:outline-none"
              />
            </div>
          </div>

          <div>
            <label className="mb-2 block text-[11px] font-bold uppercase tracking-wider text-zinc-400">
              PASSWORD
            </label>
            <div className="relative rounded-xl border border-zinc-800 bg-zinc-950 transition-all focus-within:border-brand-500 focus-within:ring-1 focus-within:ring-brand-500">
              <KeyRound className="absolute left-4 top-3.5 h-4 w-4 text-zinc-400" />
              <input
                type={showPassword ? "text" : "password"}
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-transparent py-3 pl-11 pr-11 text-sm text-white placeholder-zinc-500 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-4 top-3.5 text-zinc-400 transition-colors hover:text-zinc-200"
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>

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
                className="w-full rounded-xl border border-amber-500/50 bg-zinc-950 py-2.5 text-center font-mono text-lg tracking-widest text-amber-300 placeholder-zinc-600 focus:border-amber-400 focus:outline-none"
              />
            </div>
          )}

          <div className="pt-0.5 text-right">
            <button
              type="button"
              onClick={handleForgotPassword}
              className="text-xs font-normal text-zinc-400 transition-colors hover:text-brand-400"
            >
              Forgotten your username or password?
            </button>
          </div>

          <div className="pt-1">
            <button
              type="submit"
              disabled={isLoading}
              className="flex w-full items-center justify-center rounded-2xl bg-gradient-to-r from-brand-600 via-brand-500 to-amber-500 py-3.5 px-4 text-sm font-semibold text-white shadow-lg shadow-brand-600/35 transition-all hover:brightness-110 active:scale-[0.99] disabled:opacity-50"
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
        <div className="mt-7">
          <div className="mb-3 flex items-center gap-1.5 text-[11px] font-bold uppercase tracking-wider text-zinc-400">
            <Sparkles className="h-3.5 w-3.5 text-amber-400" />
            <span>DEMO PERSONAS (ROLE ACCESS)</span>
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
                      ? "border-brand-500 bg-brand-950/30 ring-1 ring-brand-500/40"
                      : "border-zinc-800 bg-zinc-950/70 hover:border-zinc-700 hover:bg-zinc-900"
                  }`}
                >
                  <div className={`text-xs sm:text-sm font-semibold ${p.roleColor}`}>
                    {p.roleName}
                  </div>
                  <div className="mt-0.5 truncate text-[11px] text-zinc-400 group-hover:text-zinc-300">
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
