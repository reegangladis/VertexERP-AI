import React, { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import {
  LayoutDashboard,
  Users,
  Clock,
  CalendarOff,
  DollarSign,
  FileText,
  Inbox,
  Bell,
  Building2,
  GitFork,
  Award,
  Sun,
  BookOpen,
  Receipt,
  CreditCard,
  FileSpreadsheet,
  BarChart3,
  Sparkles,
  Bot,
  Zap,
  Target,
  Briefcase,
  TrendingUp,
  ShoppingCart,
  Boxes,
  Warehouse,
  Factory,
  Cpu,
  ChevronDown,
  ChevronRight,
  UserCheck,
  FolderOpen,
  PieChart,
} from "lucide-react";

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  badge?: string;
}

// -------------------------------------------------------------
// Executive Analytics Navigation
// -------------------------------------------------------------
const executiveNavItems: NavItem[] = [
  {
    label: "Executive Dashboard",
    to: "/analytics",
    icon: <PieChart className="w-4 h-4 text-indigo-400" />,
  },
  {
    label: "KPI Catalog",
    to: "/analytics/kpis",
    icon: <BarChart3 className="w-4 h-4 text-sky-400" />,
  },
  {
    label: "Enterprise Reports Hub",
    to: "/analytics/reports",
    icon: <FileSpreadsheet className="w-4 h-4 text-emerald-400" />,
  },
];

// -------------------------------------------------------------
// Employee Self-Service (ESS) Navigation
// -------------------------------------------------------------
const essNavItems: NavItem[] = [
  {
    label: "My Dashboard",
    to: "/ess/dashboard",
    icon: <LayoutDashboard className="w-4 h-4 text-indigo-400" />,
  },
  {
    label: "My Profile",
    to: "/ess/profile",
    icon: <UserCheck className="w-4 h-4 text-sky-400" />,
  },
  {
    label: "My Attendance",
    to: "/ess/attendance",
    icon: <Clock className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Apply Leave & Quotas",
    to: "/ess/leave",
    icon: <CalendarOff className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "My Payslips",
    to: "/ess/payslips",
    icon: <DollarSign className="w-4 h-4 text-indigo-400" />,
  },
  {
    label: "Statutory Documents",
    to: "/ess/documents",
    icon: <FolderOpen className="w-4 h-4 text-purple-400" />,
  },
  {
    label: "My Requests & Helpdesk",
    to: "/ess/requests",
    icon: <Inbox className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "Announcements",
    to: "/ess/announcements",
    icon: <Bell className="w-4 h-4 text-amber-400" />,
  },
];

// -------------------------------------------------------------
// CRM & Sales Navigation
// -------------------------------------------------------------
const crmNavItems: NavItem[] = [
  {
    label: "CRM Dashboard",
    to: "/crm/home",
    icon: <LayoutDashboard className="w-4 h-4 text-indigo-400" />,
  },
  {
    label: "Leads Management",
    to: "/crm/leads",
    icon: <Target className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "Customer Accounts",
    to: "/crm/accounts",
    icon: <Building2 className="w-4 h-4 text-blue-400" />,
  },
  {
    label: "Business Contacts",
    to: "/crm/contacts",
    icon: <Users className="w-4 h-4 text-cyan-400" />,
  },
  {
    label: "Opportunities Pipeline",
    to: "/crm/opportunities",
    icon: <Briefcase className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Sales Quotations",
    to: "/crm/quotations",
    icon: <FileText className="w-4 h-4 text-purple-400" />,
  },
  {
    label: "Sales Orders",
    to: "/crm/orders",
    icon: <ShoppingCart className="w-4 h-4 text-teal-400" />,
  },
  {
    label: "Sales Analytics",
    to: "/crm/reports",
    icon: <BarChart3 className="w-4 h-4 text-indigo-400" />,
  },
];

// -------------------------------------------------------------
// Approvals Inbox
// -------------------------------------------------------------
const approvalNavItems: NavItem[] = [
  {
    label: "Approvals Inbox",
    to: "/approvals",
    icon: <Inbox className="w-4 h-4 text-rose-400" />,
    badge: "PENDING",
  },
];

// -------------------------------------------------------------
// HRMS Management Navigation
// -------------------------------------------------------------
const hrNavItems: NavItem[] = [
  {
    label: "HR Overview",
    to: "/hr",
    icon: <LayoutDashboard className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Employees Directory",
    to: "/hr/employees",
    icon: <Users className="w-4 h-4 text-sky-400" />,
  },
  {
    label: "Shift & Attendance",
    to: "/hr/attendance",
    icon: <Clock className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Leave Governance",
    to: "/hr/leaves",
    icon: <CalendarOff className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Payroll Engine",
    to: "/hr/payroll",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Recruitment & ATS",
    to: "/hr/recruitment",
    icon: <Briefcase className="w-4 h-4 text-indigo-400" />,
  },
];

// -------------------------------------------------------------
// Vertex AI Center
// -------------------------------------------------------------
const aiNavItems: NavItem[] = [
  {
    label: "Vertex Copilot",
    to: "/ai/copilot",
    icon: <Bot className="w-4 h-4 text-indigo-400" />,
    badge: "AGENT",
  },
  {
    label: "Knowledge Base & RAG",
    to: "/ai/knowledge",
    icon: <BookOpen className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Predictive ML Workbench",
    to: "/ai/predictive",
    icon: <Target className="w-4 h-4 text-purple-400" />,
  },
  {
    label: "Sales Forecasting",
    to: "/ai/forecast",
    icon: <TrendingUp className="w-4 h-4 text-teal-400" />,
  },
  {
    label: "AI Telemetry & Costs",
    to: "/ai/telemetry",
    icon: <Zap className="w-4 h-4 text-amber-400" />,
  },
];

// -------------------------------------------------------------
// Finance & Accounting Navigation
// -------------------------------------------------------------
const financeNavItems: NavItem[] = [
  {
    label: "Finance Dashboard",
    to: "/finance",
    icon: <LayoutDashboard className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Chart of Accounts",
    to: "/finance/accounts",
    icon: <BookOpen className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Customer Invoices",
    to: "/finance/invoices",
    icon: <Receipt className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Vendor Bills",
    to: "/finance/bills",
    icon: <CreditCard className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Payments & Ledger",
    to: "/finance/payments",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Financial Reports",
    to: "/finance/reports",
    icon: <FileSpreadsheet className="w-4 h-4 text-emerald-400" />,
  },
];

// -------------------------------------------------------------
// Organization Structure Navigation
// -------------------------------------------------------------
const orgNavItems: NavItem[] = [
  {
    label: "Org Structure Overview",
    to: "/organization",
    icon: <Building2 className="w-4 h-4 text-slate-300" />,
  },
  {
    label: "Branches",
    to: "/organization/branches",
    icon: <Building2 className="w-4 h-4 text-slate-300" />,
  },
  {
    label: "Departments",
    to: "/organization/departments",
    icon: <GitFork className="w-4 h-4 text-slate-300" />,
  },
  {
    label: "Designations",
    to: "/organization/designations",
    icon: <Award className="w-4 h-4 text-slate-300" />,
  },
  {
    label: "Holidays Calendar",
    to: "/organization/holidays",
    icon: <Sun className="w-4 h-4 text-amber-300" />,
  },
];

// -------------------------------------------------------------
// Supply Chain & Operations (Collapsible)
// -------------------------------------------------------------
const opsNavItems: NavItem[] = [
  {
    label: "Inventory Balances",
    to: "/inventory/balances",
    icon: <Boxes className="w-4 h-4 text-teal-400" />,
  },
  {
    label: "Warehouses",
    to: "/inventory/warehouses",
    icon: <Warehouse className="w-4 h-4 text-teal-400" />,
  },
  {
    label: "Suppliers & POs",
    to: "/procurement/orders",
    icon: <ShoppingCart className="w-4 h-4 text-teal-400" />,
  },
  {
    label: "Production Orders",
    to: "/manufacturing/orders",
    icon: <Factory className="w-4 h-4 text-teal-400" />,
  },
  {
    label: "Background Tasks",
    to: "/jobs",
    icon: <Cpu className="w-4 h-4 text-teal-400" />,
  },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { tenantId, fullName, roles } = useAuthStore();
  const [opsOpen, setOpsOpen] = useState(false);

  const isSuperAdmin = roles.includes("SUPER_ADMIN") || roles.includes("ORG_ADMIN") || roles.length === 0;
  const isEmployeeOnly = roles.includes("EMPLOYEE") && !isSuperAdmin;
  const isSalesManager = roles.includes("SALES_MANAGER") && !isSuperAdmin;
  const isHRManager = roles.includes("HR_MANAGER") && !isSuperAdmin;

  // Determine current active section
  const isESS = location.pathname.startsWith("/ess") || isEmployeeOnly;

  const renderNavGroup = (title: string, items: NavItem[], badgeText?: string, badgeColor?: string) => (
    <div className="space-y-1">
      <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
        <span>{title}</span>
        {badgeText && (
          <span className={cn("text-[9px] px-1.5 py-0.5 rounded font-bold border", badgeColor || "bg-indigo-500/20 text-indigo-300 border-indigo-500/30")}>
            {badgeText}
          </span>
        )}
      </div>
      <div className="space-y-0.5">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/crm/home" || item.to === "/ess/dashboard" || item.to === "/hr" || item.to === "/finance" || item.to === "/analytics"}
            className={({ isActive }) =>
              cn(
                "flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all duration-150",
                isActive
                  ? "bg-gradient-to-r from-indigo-600 to-purple-600 text-white shadow-md shadow-indigo-600/30 font-semibold"
                  : "text-slate-300 hover:bg-[#152038] hover:text-white"
              )
            }
          >
            <div className="flex items-center gap-3">
              {item.icon}
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span className="text-[9px] px-1.5 py-0.2 rounded font-bold bg-rose-500/30 text-rose-300 border border-rose-500/30">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>
    </div>
  );

  return (
    <aside className="w-64 bg-[#090e18]/95 border-r border-[#1b253b] backdrop-blur-2xl flex flex-col shrink-0 h-screen sticky top-0 shadow-xl shadow-black/60">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-[#1b253b] flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-purple-600 flex items-center justify-center font-extrabold text-white text-base shadow-md shadow-indigo-500/30">
            V
          </div>
          <div>
            <div className="font-bold text-sm text-white tracking-tight leading-none">VertexERP AI</div>
            <div className="text-[10px] text-slate-400 font-medium mt-1">
              {isESS
                ? "Employee Portal"
                : isSalesManager
                ? "Sales & Revenue Ops"
                : isHRManager
                ? "People Operations"
                : "Enterprise Suite"}
            </div>
          </div>
        </div>

        <span
          className={cn(
            "text-[9px] px-2 py-0.5 rounded-full font-bold uppercase border",
            isESS
              ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
              : isSalesManager
              ? "bg-purple-500/20 text-purple-300 border-purple-500/30"
              : isHRManager
              ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
              : "bg-indigo-500/20 text-indigo-300 border-indigo-500/30"
          )}
        >
          {isESS
            ? "ESS"
            : isSalesManager
            ? "Sales"
            : isHRManager
            ? "HRMS"
            : "Admin"}
        </span>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 overflow-y-auto space-y-5 custom-scrollbar">
        {/* CASE 1: Pure Employee View or ESS URL */}
        {isESS && (
          <>
            {renderNavGroup("Employee Self-Service", essNavItems, "greytHR", "bg-emerald-500/20 text-emerald-300 border-emerald-500/30")}
          </>
        )}

        {/* CASE 2: Sales Manager Persona */}
        {!isESS && isSalesManager && (
          <>
            {renderNavGroup("Sales & Deals Pipeline", crmNavItems, "CRM", "bg-purple-500/20 text-purple-300 border-purple-500/30")}
            {renderNavGroup("Governance & Approvals", approvalNavItems, "LIVE", "bg-rose-500/20 text-rose-300 border-rose-500/30")}
            {renderNavGroup("AI Copilot", aiNavItems.slice(0, 2), "AI", "bg-indigo-500/20 text-indigo-300 border-indigo-500/30")}
          </>
        )}

        {/* CASE 3: HR Manager Persona */}
        {!isESS && isHRManager && (
          <>
            {renderNavGroup("HR Administration", hrNavItems, "HRMS", "bg-amber-500/20 text-amber-300 border-amber-500/30")}
            {renderNavGroup("Governance & Approvals", approvalNavItems, "LIVE", "bg-rose-500/20 text-rose-300 border-rose-500/30")}
            {renderNavGroup("Organization Structure", orgNavItems)}
          </>
        )}

        {/* CASE 4: Full Administrator Persona */}
        {!isESS && isSuperAdmin && (
          <>
            {/* Executive Analytics */}
            {renderNavGroup("Executive Suite", executiveNavItems, "EXEC", "bg-indigo-500/20 text-indigo-300 border-indigo-500/30")}

            {/* Approvals Inbox */}
            {renderNavGroup("Governance & Workflows", approvalNavItems, "LIVE", "bg-rose-500/20 text-rose-300 border-rose-500/30")}

            {/* CRM & Sales */}
            {renderNavGroup("CRM & Sales Pipeline", crmNavItems, "SALES", "bg-blue-500/20 text-blue-300 border-blue-500/30")}

            {/* AI Platform & Predictive Center */}
            {renderNavGroup("Vertex AI Center", aiNavItems, "GENAI", "bg-indigo-500/20 text-indigo-300 border-indigo-500/30")}

            {/* HRMS Management */}
            {renderNavGroup("HR Administration", hrNavItems, "HRMS", "bg-amber-500/20 text-amber-300 border-amber-500/30")}

            {/* Finance & Payroll */}
            {renderNavGroup("Finance & Accounting", financeNavItems, "FIN", "bg-emerald-500/20 text-emerald-300 border-emerald-500/30")}

            {/* Organization & Setup */}
            {renderNavGroup("Organization Structure", orgNavItems)}

            {/* Retained Operations Section (Collapsible) */}
            <div className="pt-2 border-t border-[#1e2a44]">
              <button
                type="button"
                onClick={() => setOpsOpen(!opsOpen)}
                className="w-full flex items-center justify-between px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-slate-400 hover:text-slate-200"
              >
                <span>Operations & SCM</span>
                {opsOpen ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
              </button>
              {opsOpen && (
                <div className="space-y-0.5 mt-1">
                  {opsNavItems.map((item) => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      className={({ isActive }) =>
                        cn(
                          "flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-colors",
                          isActive
                            ? "bg-slate-800 text-white font-semibold"
                            : "text-slate-400 hover:bg-[#152038] hover:text-white"
                        )
                      }
                    >
                      {item.icon}
                      <span>{item.label}</span>
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {/* Footer User & Tenant Info */}
      <div className="p-3 border-t border-[#1b253b] bg-[#070b14]/70">
        <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-xl bg-[#0f1728] border border-[#202d48]">
          <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center font-bold text-xs text-indigo-300">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate">
              {fullName ? `${fullName}'s Workspace` : "Vertex Cloud Enterprise"}
            </div>
            <div
              data-testid="sidebar-tenant-id"
              className="text-[10px] text-slate-400 truncate"
            >
              Tenant: {tenantId || "apex-cloud"}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
