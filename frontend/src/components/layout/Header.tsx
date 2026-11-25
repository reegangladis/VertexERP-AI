import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { getInitials } from "@/lib/utils";
import { useAccentTheme } from "@/lib/theme";
import { Building2, LogOut, Sparkles, Search, Palette } from "lucide-react";
import { WorkspaceSwitcher } from "../ui/WorkspaceSwitcher";
import { NotificationCenter } from "../ui/NotificationCenter";
import { CommandPalette } from "../ui/CommandPalette";

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const { fullName, email, roles, tenantId, logout } = useAuthStore();
  const { themeId, setTheme, themes } = useAccentTheme();
  const [cmdOpen, setCmdOpen] = useState(false);

  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setCmdOpen((v) => !v);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  const primaryRole = roles[0] || "SUPER_ADMIN";
  const roleDisplay =
    primaryRole === "SUPER_ADMIN"
      ? "Super Admin"
      : primaryRole === "EMPLOYEE"
      ? "Employee (ESS)"
      : primaryRole === "SALES_MANAGER"
      ? "Sales Manager"
      : primaryRole === "HR_MANAGER"
      ? "HR Manager"
      : primaryRole === "FINANCE_MANAGER"
      ? "Finance Manager"
      : primaryRole;

  const roleColorClass =
    primaryRole === "SUPER_ADMIN"
      ? "bg-brand-500/20 text-brand-300 border-brand-500/30"
      : primaryRole === "EMPLOYEE"
      ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
      : primaryRole === "SALES_MANAGER"
      ? "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30"
      : primaryRole === "HR_MANAGER"
      ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
      : "bg-orange-500/20 text-orange-300 border-orange-500/30";

  return (
    <>
      <header className="h-16 px-5 border-b border-zinc-800/80 bg-[#0d0d10]/90 backdrop-blur-2xl flex items-center justify-between gap-3 sticky top-0 z-30 shadow-sm shadow-black/50">
        {/* Left: Organization & Interactive Command Bar */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800 text-xs">
            <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
            <Building2 className="w-3.5 h-3.5 text-brand-400" />
            <span className="font-semibold text-zinc-200 hidden xl:inline">
              {tenantId ? "Apex Global Enterprise" : "Vertex Global"}
            </span>
          </div>

          <button
            type="button"
            onClick={() => setCmdOpen(true)}
            className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-zinc-900/90 hover:bg-zinc-800/90 border border-zinc-800 text-xs text-zinc-400 hover:text-zinc-200 transition-all"
            title="Quick Command Navigation (Ctrl+K)"
          >
            <Search className="w-3.5 h-3.5 text-brand-400" />
            <span className="hidden lg:inline">Quick Jump</span>
            <kbd className="px-1.5 py-0.5 text-[10px] font-mono bg-zinc-950 border border-zinc-700 rounded text-zinc-400">
              ⌘K
            </kbd>
          </button>
        </div>

        {/* Middle: Workspace Switcher */}
        <div className="hidden md:flex items-center">
          <WorkspaceSwitcher />
        </div>

        {/* Right: Accent Switcher, Copilot, Notifications, Profile & Sign Out */}
        <div className="flex items-center gap-2.5">
          {/* Interactive Non-Blue Accent Switcher */}
          <div
            className="hidden xl:flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-zinc-900 border border-zinc-800"
            title="Switch Interface Accent"
          >
            <Palette className="w-3.5 h-3.5 text-zinc-400 mr-0.5" />
            {themes.map((t) => (
              <button
                key={t.id}
                type="button"
                onClick={() => setTheme(t.id)}
                title={t.label}
                className={`w-3.5 h-3.5 rounded-full transition-transform ${
                  themeId === t.id
                    ? "ring-2 ring-white ring-offset-2 ring-offset-zinc-900 scale-110"
                    : "opacity-60 hover:opacity-100"
                }`}
                style={{ backgroundColor: t.swatch }}
              />
            ))}
          </div>

          {/* Quick Copilot Launcher */}
          <button
            type="button"
            onClick={() => navigate("/ai/copilot")}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-brand-500/30 bg-brand-500/10 text-brand-300 hover:bg-brand-500/20 text-xs font-semibold transition-all hover:scale-[1.02] shadow-[0_0_12px_rgba(249,115,22,0.18)]"
            title="Open Vertex AI Copilot"
          >
            <Sparkles className="w-3.5 h-3.5 text-brand-400 animate-pulse" />
            <span>Ask Copilot</span>
          </button>

          <NotificationCenter />

          <div className="h-5 w-[1px] bg-zinc-800 hidden sm:block" />

          {/* User Badge */}
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-amber-500 border border-brand-400/40 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-brand-600/25">
              {getInitials(fullName || email?.split("@")[0] || "User")}
            </div>
            <div className="text-left hidden sm:block">
              <div className="text-xs font-semibold text-zinc-100 leading-tight">
                {fullName || email?.split("@")[0] || "Administrator"}
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${roleColorClass}`}>
                  {roleDisplay}
                </span>
              </div>
            </div>
          </div>

          <div className="h-5 w-[1px] bg-zinc-800" />

          {/* Sign Out */}
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-rose-500/25 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 hover:border-rose-500/40 text-xs font-medium transition-all"
            title="Sign Out Session"
            data-testid="header-logout-btn"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Sign Out</span>
          </button>
        </div>
      </header>

      <CommandPalette isOpen={cmdOpen} onClose={() => setCmdOpen(false)} />
    </>
  );
};
