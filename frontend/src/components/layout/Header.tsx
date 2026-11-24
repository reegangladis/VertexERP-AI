import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { getInitials } from "@/lib/utils";
import { Building, LogOut, Search, User } from "lucide-react";
import { WorkspaceSwitcher } from "../ui/WorkspaceSwitcher";
import { NotificationCenter } from "../ui/NotificationCenter";

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const { fullName, email, roles, tenantId, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="h-16 px-6 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md flex items-center justify-between sticky top-0 z-30">
      {/* Left: Organization / Workspace Identification */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
          <Building className="w-3.5 h-3.5 text-brand-400" />
          <span className="font-semibold text-slate-100">
            {tenantId ? `Org ${tenantId.substring(0, 8)}` : "Vertex Enterprise"}
          </span>
        </div>
      </div>

      {/* Middle: Workspace Switcher (Admin vs Employee Self-Service) */}
      <div className="hidden md:flex items-center gap-4">
        <WorkspaceSwitcher />
      </div>

      {/* Right: Actions, Notifications, User Profile & Sign Out */}
      <div className="flex items-center gap-3">
        <NotificationCenter />

        <div className="h-5 w-[1px] bg-slate-800 hidden sm:block" />

        {/* User Badge */}
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-brand-600/30 border border-brand-500/40 flex items-center justify-center text-brand-300 text-xs font-bold">
            {getInitials(fullName || "Admin")}
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-xs font-semibold text-slate-200 leading-none">
              {fullName || "Administrator"}
            </div>
            <div className="text-[10px] text-slate-400 mt-1 leading-none">
              {roles[0] || "User"} &bull; {email || "admin@vertexerp.io"}
            </div>
          </div>
        </div>

        <div className="h-5 w-[1px] bg-slate-800" />

        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700/60 bg-slate-800/40 text-slate-300 hover:text-rose-300 hover:bg-rose-500/10 hover:border-rose-500/30 text-xs font-medium transition-all"
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
