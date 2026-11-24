import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { getInitials } from "@/lib/utils";
import { Building2, LogOut, Sparkles } from "lucide-react";
import { WorkspaceSwitcher } from "../ui/WorkspaceSwitcher";
import { NotificationCenter } from "../ui/NotificationCenter";

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const { fullName, email, roles, tenantId, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  // Determine primary display role & badge color
  const primaryRole = roles[0] || "SUPER_ADMIN";
  const roleDisplay = primaryRole === "SUPER_ADMIN" ? "Super Admin"
    : primaryRole === "EMPLOYEE" ? "Employee (ESS)"
    : primaryRole === "SALES_MANAGER" ? "Sales Manager"
    : primaryRole === "HR_MANAGER" ? "HR Manager"
    : primaryRole === "FINANCE_MANAGER" ? "Finance Manager"
    : primaryRole;

  const roleColorClass = primaryRole === "SUPER_ADMIN"
    ? "bg-blue-500/20 text-blue-400 border-blue-500/30"
    : primaryRole === "EMPLOYEE"
    ? "bg-emerald-500/20 text-emerald-400 border-emerald-500/30"
    : primaryRole === "SALES_MANAGER"
    ? "bg-purple-500/20 text-purple-400 border-purple-500/30"
    : primaryRole === "HR_MANAGER"
    ? "bg-amber-500/20 text-amber-400 border-amber-500/30"
    : "bg-indigo-500/20 text-indigo-400 border-indigo-500/30";

  return (
    <header className="h-16 px-6 border-b border-[#1b253b] bg-[#090e18]/85 backdrop-blur-2xl flex items-center justify-between sticky top-0 z-30 shadow-sm shadow-black/40">
      {/* Left: Organization & Live Indicator */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-[#0e1628] border border-[#202d48] text-xs">
          <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_#34d399]" />
          <Building2 className="w-3.5 h-3.5 text-indigo-400" />
          <span className="font-semibold text-slate-200">
            {tenantId ? "Apex Global Enterprise" : "Vertex Global"}
          </span>
        </div>
      </div>

      {/* Middle: Workspace Switcher (Executive, Sales, HR, ESS) */}
      <div className="hidden md:flex items-center">
        <WorkspaceSwitcher />
      </div>

      {/* Right: Copilot Trigger, Notifications, User Profile & Sign Out */}
      <div className="flex items-center gap-3">
        {/* Quick Copilot Launcher */}
        <button
          type="button"
          onClick={() => navigate("/ai/copilot")}
          className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 hover:bg-indigo-500/20 text-xs font-semibold transition-all hover:scale-[1.02] shadow-[0_0_12px_rgba(99,102,241,0.2)]"
          title="Open Vertex AI Copilot"
        >
          <Sparkles className="w-3.5 h-3.5 text-indigo-400 animate-pulse" />
          <span>Ask Copilot</span>
        </button>

        <NotificationCenter />

        <div className="h-5 w-[1px] bg-[#1e2a44] hidden sm:block" />

        {/* User Badge */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-purple-600 border border-indigo-400/40 flex items-center justify-center text-white text-xs font-bold shadow-md shadow-indigo-600/30">
            {getInitials(fullName || email?.split("@")[0] || "User")}
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-semibold text-slate-100 leading-tight">
              {fullName || email?.split("@")[0] || "Administrator"}
            </div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${roleColorClass}`}>
                {roleDisplay}
              </span>
            </div>
          </div>
        </div>

        <div className="h-5 w-[1px] bg-[#1e2a44]" />

        {/* Sign Out */}
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-rose-500/20 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 hover:border-rose-500/40 text-xs font-medium transition-all"
          title="Sign Out Session"
          data-testid="header-logout-btn"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    </header>
  );
};
