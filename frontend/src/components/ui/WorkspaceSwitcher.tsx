import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Shield, Briefcase, Users, UserCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

export const WorkspaceSwitcher: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { roles } = useAuthStore();

  const isSuperAdmin = roles.includes("SUPER_ADMIN") || roles.includes("ORG_ADMIN") || roles.length === 0;
  const isHR = roles.includes("HR_MANAGER") || isSuperAdmin;
  const isSales = roles.includes("SALES_MANAGER") || isSuperAdmin;
  const isEmployeeOnly = roles.includes("EMPLOYEE") && !isSuperAdmin;

  const currentPath = location.pathname;

  const isAnalyticsActive = currentPath.startsWith("/analytics") || currentPath === "/";
  const isCRMActive = currentPath.startsWith("/crm");
  const isHRActive = currentPath.startsWith("/hr");
  const isESSActive = currentPath.startsWith("/ess");

  return (
    <div className="inline-flex items-center p-1 rounded-xl bg-[#090e18]/90 border border-[#1e2a44] text-xs shadow-inner">
      {/* Executive / Admin Workspace */}
      {!isEmployeeOnly && (
        <button
          type="button"
          onClick={() => navigate("/analytics")}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all duration-200",
            isAnalyticsActive
              ? "bg-gradient-to-r from-indigo-600 to-indigo-700 text-white shadow-md shadow-indigo-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          )}
          title="Executive Analytics & Operations"
        >
          <Shield className="w-3.5 h-3.5 text-indigo-400" />
          <span className="hidden lg:inline">Executive Suite</span>
          <span className="lg:hidden">Admin</span>
        </button>
      )}

      {/* Sales / CRM Workspace */}
      {(isSales || isSuperAdmin) && (
        <button
          type="button"
          onClick={() => navigate("/crm/home")}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all duration-200",
            isCRMActive
              ? "bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-md shadow-purple-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          )}
          title="Sales Pipeline & CRM Deals"
        >
          <Briefcase className="w-3.5 h-3.5 text-purple-400" />
          <span className="hidden lg:inline">Sales & CRM</span>
          <span className="lg:hidden">Sales</span>
        </button>
      )}

      {/* HRMS Workspace */}
      {(isHR || isSuperAdmin) && (
        <button
          type="button"
          onClick={() => navigate("/hr")}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all duration-200",
            isHRActive
              ? "bg-gradient-to-r from-amber-600 to-amber-700 text-white shadow-md shadow-amber-600/30"
              : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
          )}
          title="People Operations & HRMS"
        >
          <Users className="w-3.5 h-3.5 text-amber-400" />
          <span className="hidden lg:inline">People Ops (HR)</span>
          <span className="lg:hidden">HR</span>
        </button>
      )}

      {/* Employee Self-Service */}
      <button
        type="button"
        onClick={() => navigate("/ess/dashboard")}
        className={cn(
          "flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all duration-200",
          isESSActive
            ? "bg-gradient-to-r from-emerald-600 to-teal-600 text-white shadow-md shadow-emerald-600/30"
            : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
        )}
        title="Employee Self-Service Portal"
      >
        <UserCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span className="hidden lg:inline">Employee ESS</span>
        <span className="lg:hidden">ESS</span>
      </button>
    </div>
  );
};
