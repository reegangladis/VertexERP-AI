import React from "react";
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "@/stores/auth-store";
import { Bell, User, Building, LogOut } from "lucide-react";

export const Header: React.FC = () => {
  const navigate = useNavigate();
  const { fullName, email, roles, logout } = useAuthStore();

  const handleLogout = async () => {
    await logout();
    navigate("/login", { replace: true });
  };

  return (
    <header className="h-16 px-8 border-b border-slate-800 bg-slate-900/40 backdrop-blur-md flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/60 border border-slate-700/60 text-xs text-slate-300">
          <Building className="w-3.5 h-3.5 text-brand-400" />
          <span className="font-semibold text-slate-100">Primary Enterprise HQ</span>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition-colors relative">
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-brand-500 absolute top-1.5 right-1.5" />
        </button>

        <div className="h-6 w-[1px] bg-slate-800" />

        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-600/20 border border-brand-500/30 flex items-center justify-center text-brand-300 text-xs font-semibold">
            <User className="w-4 h-4" />
          </div>
          <div className="text-left">
            <div className="text-xs font-semibold text-slate-200">{fullName || "Admin"}</div>
            <div className="text-[10px] text-slate-400">{roles[0] || "User"} &bull; {email}</div>
          </div>
        </div>

        <div className="h-6 w-[1px] bg-slate-800" />

        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-700/60 bg-slate-800/40 text-slate-300 hover:text-rose-300 hover:bg-rose-500/10 hover:border-rose-500/30 text-xs font-medium transition"
          title="Sign Out Session"
          data-testid="header-logout-btn"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Sign Out</span>
        </button>
      </div>
    </header>
  );
};
