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
  PhoneCall,
  CheckSquare,
  ShoppingCart,
  Boxes,
  Warehouse,
  Factory,
  Cpu,
  ChevronDown,
  ChevronRight,
  UserCheck,
  FolderOpen,
} from "lucide-react";

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  badge?: string;
}

// -------------------------------------------------------------
// Employee Self-Service (ESS) Navigation (greytHR-inspired)
// -------------------------------------------------------------
const essNavItems: NavItem[] = [
  {
    label: "My Dashboard",
    to: "/ess/dashboard",
    icon: <LayoutDashboard className="w-4 h-4 text-brand-400" />,
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
// Admin Navigation: CRM & Sales (Salesforce-inspired)
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
    label: "Sales Activities",
    to: "/crm/activities",
    icon: <CheckSquare className="w-4 h-4 text-emerald-400" />,
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
// Admin Navigation: Centralized Approvals
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
// Admin Navigation: HRMS
// -------------------------------------------------------------
const hrNavItems: NavItem[] = [
  {
    label: "HR Overview",
    to: "/hr",
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: "Employees Directory",
    to: "/hr/employees",
    icon: <Users className="w-4 h-4" />,
  },
  {
    label: "Shift & Attendance",
    to: "/hr/attendance",
    icon: <Clock className="w-4 h-4" />,
  },
  {
    label: "Leave Governance",
    to: "/hr/leaves",
    icon: <CalendarOff className="w-4 h-4" />,
  },
  {
    label: "Payroll Engine",
    to: "/hr/payroll",
    icon: <DollarSign className="w-4 h-4" />,
  },
  {
    label: "Recruitment & ATS",
    to: "/hr/recruitment",
    icon: <Briefcase className="w-4 h-4" />,
  },
];

// -------------------------------------------------------------
// Admin Navigation: Vertex AI Center
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
    label: "AI Resume Intelligence",
    to: "/ai/resume",
    icon: <FileText className="w-4 h-4 text-cyan-400" />,
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
// Admin Navigation: Finance & Payroll
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
// Admin Navigation: Administration & Org Structure
// -------------------------------------------------------------
const orgNavItems: NavItem[] = [
  {
    label: "Org Structure Overview",
    to: "/organization",
    icon: <Building2 className="w-4 h-4" />,
  },
  {
    label: "Branches",
    to: "/organization/branches",
    icon: <Building2 className="w-4 h-4" />,
  },
  {
    label: "Departments",
    to: "/organization/departments",
    icon: <GitFork className="w-4 h-4" />,
  },
  {
    label: "Designations",
    to: "/organization/designations",
    icon: <Award className="w-4 h-4" />,
  },
  {
    label: "Holidays Calendar",
    to: "/organization/holidays",
    icon: <Sun className="w-4 h-4" />,
  },
];

// -------------------------------------------------------------
// Admin Navigation: Retained Supply Chain & Operations (Collapsible)
// -------------------------------------------------------------
const opsNavItems: NavItem[] = [
  {
    label: "Inventory Balances",
    to: "/inventory/balances",
    icon: <Boxes className="w-4 h-4" />,
  },
  {
    label: "Warehouses",
    to: "/inventory/warehouses",
    icon: <Warehouse className="w-4 h-4" />,
  },
  {
    label: "Suppliers & POs",
    to: "/procurement/orders",
    icon: <ShoppingCart className="w-4 h-4" />,
  },
  {
    label: "Production Orders",
    to: "/manufacturing/orders",
    icon: <Factory className="w-4 h-4" />,
  },
  {
    label: "Background Tasks",
    to: "/jobs",
    icon: <Cpu className="w-4 h-4" />,
  },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { tenantId, fullName } = useAuthStore();
  const isESS = location.pathname.startsWith("/ess");
  const [opsOpen, setOpsOpen] = useState(false);

  const renderNavGroup = (title: string, items: NavItem[], badgeText?: string, badgeColor?: string) => (
    <div className="space-y-1">
      <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400 flex items-center justify-between">
        <span>{title}</span>
        {badgeText && (
          <span className={cn("text-[9px] px-1.5 py-0.5 rounded font-bold", badgeColor || "bg-indigo-500/20 text-indigo-300")}>
            {badgeText}
          </span>
        )}
      </div>
      <div className="space-y-0.5">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/crm/home" || item.to === "/ess/dashboard" || item.to === "/hr" || item.to === "/finance"}
            className={({ isActive }) =>
              cn(
                "flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-colors",
                isActive
                  ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/30 font-semibold"
                  : "text-slate-300 hover:bg-slate-800/60 hover:text-white"
              )
            }
          >
            <div className="flex items-center gap-3">
              {item.icon}
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span className="text-[9px] px-1.5 py-0.2 rounded font-bold bg-rose-500/30 text-rose-300">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>
    </div>
  );

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-brand-500 flex items-center justify-center font-extrabold text-white text-sm shadow-md shadow-indigo-500/20">
            V
          </div>
          <div>
            <div className="font-bold text-sm text-white tracking-tight leading-none">VertexERP AI</div>
            <div className="text-[10px] text-slate-400 font-medium mt-0.5">
              {isESS ? "Employee Portal" : "Enterprise Admin"}
            </div>
          </div>
        </div>

        <span
          className={cn(
            "text-[9px] px-2 py-0.5 rounded-full font-bold uppercase",
            isESS ? "bg-emerald-500/20 text-emerald-300" : "bg-indigo-500/20 text-indigo-300"
          )}
        >
          {isESS ? "ESS" : "Admin"}
        </span>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 overflow-y-auto space-y-5">
        {/* ESS Workspace View */}
        {isESS && (
          <>
            {renderNavGroup("Employee Self-Service", essNavItems, "greytHR", "bg-emerald-500/20 text-emerald-300")}
          </>
        )}

        {/* Admin Workspace View */}
        {!isESS && (
          <>
            {/* Approvals Inbox */}
            {renderNavGroup("Governance & Workflows", approvalNavItems, "LIVE", "bg-rose-500/20 text-rose-300")}

            {/* Salesforce-Style CRM */}
            {renderNavGroup("CRM & Sales Pipeline", crmNavItems, "SALES", "bg-blue-500/20 text-blue-300")}

            {/* AI Platform & Predictive Center */}
            {renderNavGroup("Vertex AI Center", aiNavItems, "GENAI", "bg-indigo-500/20 text-indigo-300")}

            {/* HRMS Management */}
            {renderNavGroup("HR Administration", hrNavItems, "HRMS")}

            {/* Finance & Payroll */}
            {renderNavGroup("Finance & Accounting", financeNavItems, "FIN")}

            {/* Organization & Setup */}
            {renderNavGroup("Organization Structure", orgNavItems)}

            {/* Retained Operations Section (Collapsible) */}
            <div className="pt-2 border-t border-slate-800/80">
              <button
                onClick={() => setOpsOpen(!opsOpen)}
                className="w-full flex items-center justify-between px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-500 hover:text-slate-300"
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
                            : "text-slate-400 hover:bg-slate-800/60 hover:text-white"
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

      {/* Footer User Info */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center gap-2.5 px-2 py-1.5 rounded-xl bg-slate-800/40 border border-slate-800">
          <div className="w-7 h-7 rounded-lg bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center font-bold text-xs text-indigo-300">
            AI
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-slate-200 truncate">
              {fullName ? `${fullName}'s Workspace` : "Vertex Cloud Core"}
            </div>
            <div
              data-testid="sidebar-tenant-id"
              className="text-[10px] text-slate-500 truncate"
            >
              Tenant: {tenantId || "apex-cloud"}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
