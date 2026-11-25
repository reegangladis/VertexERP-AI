import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Shield, Briefcase, Users, UserCheck } from "lucide-react";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";

export const WorkspaceSwitcher: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { roles } = useAuthStore();

  const isSuperAdmin =
    roles.includes("SUPER_ADMIN") ||
    roles.includes("ORG_ADMIN") ||
    roles.includes("TenantAdmin") ||
    roles.length === 0;
  const isHR = roles.includes("HR_MANAGER") || isSuperAdmin;
  const isSales = roles.includes("SALES_MANAGER") || isSuperAdmin;
  const isEmployeeOnly = roles.includes("EMPLOYEE") && !isSuperAdmin && !roles.includes("HR_MANAGER");

  const currentPath = location.pathname;

  const isAnalyticsActive = currentPath.startsWith("/analytics") || currentPath === "/";
  const isCRMActive = currentPath.startsWith("/crm");
  const isHRActive = currentPath.startsWith("/hr");
  const isESSActive = currentPath.startsWith("/ess");

  return (
    <div className="inline-flex items-center p-1 rounded-xl bg-zinc-950/90 border border-zinc-800 text-xs shadow-inner">
      {/* Executive / Admin Workspace */}
      {!isEmployeeOnly && (
        <button
          type="button"
          onClick={() => navigate("/analytics")}
          className={cn(
            "flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-medium transition-all duration-200",
            isAnalyticsActive
              ? "bg-gradient-to-r from-brand-600 to-amber-600 text-white shadow-md shadow-brand-600/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
          )}
          title="Executive Analytics & Operations"
        >
          <Shield className="w-3.5 h-3.5 text-amber-300" />
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
              ? "bg-gradient-to-r from-fuchsia-600 to-rose-600 text-white shadow-md shadow-fuchsia-600/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
          )}
          title="Sales Pipeline & CRM Deals"
        >
          <Briefcase className="w-3.5 h-3.5 text-fuchsia-300" />
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
              ? "bg-gradient-to-r from-amber-600 to-orange-600 text-white shadow-md shadow-amber-600/30"
              : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
          )}
          title="People Operations & HRMS"
        >
          <Users className="w-3.5 h-3.5 text-amber-300" />
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
            ? "bg-gradient-to-r from-emerald-600 to-green-600 text-white shadow-md shadow-emerald-600/30"
            : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
        )}
        title="Employee Self-Service Portal"
      >
        <UserCheck className="w-3.5 h-3.5 text-emerald-300" />
        <span className="hidden lg:inline">Employee ESS</span>
        <span className="lg:hidden">ESS</span>
      </button>
    </div>
  );
};
