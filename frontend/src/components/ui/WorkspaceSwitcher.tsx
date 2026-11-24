import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { ShieldCheck, UserCheck } from "lucide-react";
import { cn } from "@/lib/utils";

export const WorkspaceSwitcher: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isESS = location.pathname.startsWith("/ess");

  return (
    <div className="inline-flex p-1 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
      <button
        onClick={() => navigate("/admin/home")}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1 rounded-md font-medium transition-all duration-150",
          !isESS
            ? "bg-brand-600 text-white shadow"
            : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/40"
        )}
      >
        <ShieldCheck className="w-3.5 h-3.5" />
        <span>Admin Workspace</span>
      </button>

      <button
        onClick={() => navigate("/ess/dashboard")}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1 rounded-md font-medium transition-all duration-150",
          isESS
            ? "bg-brand-600 text-white shadow"
            : "text-slate-400 hover:text-slate-200 hover:bg-slate-700/40"
        )}
      >
        <UserCheck className="w-3.5 h-3.5" />
        <span>Employee Self-Service</span>
      </button>
    </div>
  );
};
