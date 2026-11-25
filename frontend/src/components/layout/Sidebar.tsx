import React, { useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import { useDemoStore } from "@/lib/demo-store";
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
  Layers,
  MapPin,
  Calendar,
} from "lucide-react";

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  badge?: string;
}

const executiveNavItems: NavItem[] = [
  {
    label: "Executive Dashboard",
    to: "/analytics",
    icon: <PieChart className="w-4 h-4 text-brand-400" />,
  },
  {
    label: "KPI Catalog",
    to: "/analytics/kpis",
    icon: <BarChart3 className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Enterprise Reports Hub",
    to: "/analytics/reports",
    icon: <FileSpreadsheet className="w-4 h-4 text-emerald-400" />,
  },
];

const essNavItems: NavItem[] = [
  {
    label: "My Dashboard",
    to: "/ess/dashboard",
    icon: <LayoutDashboard className="w-4 h-4 text-brand-400" />,
  },
  {
    label: "My Profile",
    to: "/ess/profile",
    icon: <UserCheck className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "My Attendance",
    to: "/ess/attendance",
    icon: <Clock className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Apply Leave & Quotas",
    to: "/ess/leave",
    icon: <CalendarOff className="w-4 h-4 text-orange-400" />,
  },
  {
    label: "My Payslips",
    to: "/ess/payslips",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Statutory Documents",
    to: "/ess/documents",
    icon: <FolderOpen className="w-4 h-4 text-fuchsia-400" />,
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
  {
    label: "Holidays Calendar",
    to: "/organization/holidays",
    icon: <Sun className="w-4 h-4 text-yellow-400" />,
  },
];

const crmNavItems: NavItem[] = [
  {
    label: "CRM Dashboard",
    to: "/crm/home",
    icon: <LayoutDashboard className="w-4 h-4 text-fuchsia-400" />,
  },
  {
    label: "Leads Management",
    to: "/crm/leads",
    icon: <Target className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "Customer Accounts",
    to: "/crm/accounts",
    icon: <Building2 className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Business Contacts",
    to: "/crm/contacts",
    icon: <Users className="w-4 h-4 text-orange-400" />,
  },
  {
    label: "Opportunities Pipeline",
    to: "/crm/opportunities",
    icon: <Briefcase className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Sales Quotations",
    to: "/crm/quotations",
    icon: <FileText className="w-4 h-4 text-fuchsia-400" />,
  },
  {
    label: "Sales Orders",
    to: "/crm/orders",
    icon: <ShoppingCart className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Sales Analytics",
    to: "/crm/reports",
    icon: <BarChart3 className="w-4 h-4 text-brand-400" />,
  },
];

const hrNavItems: NavItem[] = [
  {
    label: "HR Overview",
    to: "/hr",
    icon: <LayoutDashboard className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Employees Directory",
    to: "/hr/employees",
    icon: <Users className="w-4 h-4 text-orange-400" />,
  },
  {
    label: "Shift & Attendance",
    to: "/hr/attendance",
    icon: <Clock className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Leave Governance",
    to: "/hr/leaves",
    icon: <CalendarOff className="w-4 h-4 text-brand-400" />,
  },
  {
    label: "Payroll Engine",
    to: "/hr/payroll",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Recruitment & ATS",
    to: "/hr/recruitment",
    icon: <Briefcase className="w-4 h-4 text-fuchsia-400" />,
  },
];

const aiNavItems: NavItem[] = [
  {
    label: "Vertex Copilot",
    to: "/ai/copilot",
    icon: <Bot className="w-4 h-4 text-brand-400" />,
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
    icon: <Target className="w-4 h-4 text-fuchsia-400" />,
  },
  {
    label: "Sales Forecasting",
    to: "/ai/forecast",
    icon: <TrendingUp className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "AI Telemetry & Costs",
    to: "/ai/telemetry",
    icon: <Zap className="w-4 h-4 text-orange-400" />,
  },
];

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
    icon: <Receipt className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Vendor Bills",
    to: "/finance/bills",
    icon: <CreditCard className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "Payments & Ledger",
    to: "/finance/payments",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Financial Reports",
    to: "/finance/reports",
    icon: <FileSpreadsheet className="w-4 h-4 text-brand-400" />,
  },
];

const orgNavItems: NavItem[] = [
  {
    label: "Org Structure Overview",
    to: "/organization",
    icon: <Building2 className="w-4 h-4 text-brand-400" />,
  },
  {
    label: "Branches",
    to: "/organization/branches",
    icon: <Building2 className="w-4 h-4 text-orange-400" />,
  },
  {
    label: "Departments",
    to: "/organization/departments",
    icon: <GitFork className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Teams & Pods",
    to: "/organization/teams",
    icon: <Users className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Designations",
    to: "/organization/designations",
    icon: <Award className="w-4 h-4 text-yellow-400" />,
  },
  {
    label: "Business Units",
    to: "/organization/business-units",
    icon: <Layers className="w-4 h-4 text-fuchsia-400" />,
  },
  {
    label: "Cost Centers",
    to: "/organization/cost-centers",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Locations",
    to: "/organization/locations",
    icon: <MapPin className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "Work Calendars",
    to: "/organization/calendars",
    icon: <Calendar className="w-4 h-4 text-amber-300" />,
  },
  {
    label: "Holidays Calendar",
    to: "/organization/holidays",
    icon: <Sun className="w-4 h-4 text-yellow-400" />,
  },
];

const opsNavItems: NavItem[] = [
  {
    label: "Inventory Balances",
    to: "/inventory/balances",
    icon: <Boxes className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Warehouses",
    to: "/inventory/warehouses",
    icon: <Warehouse className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Suppliers & POs",
    to: "/procurement/orders",
    icon: <ShoppingCart className="w-4 h-4 text-orange-400" />,
  },
  {
    label: "Production Orders",
    to: "/manufacturing/orders",
    icon: <Factory className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "Background Tasks",
    to: "/jobs",
    icon: <Cpu className="w-4 h-4 text-zinc-300" />,
  },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const { tenantId, fullName, roles } = useAuthStore();
  const demoState = useDemoStore();
  const [opsOpen, setOpsOpen] = useState(false);

  const pendingLeavesCount = demoState.leaveRequests.filter(
    (l) => l.status === "SUBMITTED" || l.status === "PENDING"
  ).length;
  const pendingOtherCount = demoState.otherApprovals.filter(
    (o) => o.status === "PENDING" || o.status === "PENDING_APPROVAL"
  ).length;
  const totalPendingApprovals = pendingLeavesCount + pendingOtherCount;

  const approvalNavItems: NavItem[] = [
    {
      label: "Approvals Inbox",
      to: "/approvals",
      icon: <Inbox className="w-4 h-4 text-rose-400" />,
      badge: totalPendingApprovals > 0 ? `${totalPendingApprovals} PENDING` : "CLEAR",
    },
  ];

  const isSuperAdmin =
    roles.includes("SUPER_ADMIN") ||
    roles.includes("ORG_ADMIN") ||
    roles.includes("TenantAdmin") ||
    roles.length === 0;
  const isEmployeeOnly = roles.includes("EMPLOYEE") && !isSuperAdmin && !roles.includes("HR_MANAGER");
  const isSalesManager = roles.includes("SALES_MANAGER") && !isSuperAdmin;
  const isHRManager = roles.includes("HR_MANAGER") && !isSuperAdmin;

  const isESS = location.pathname.startsWith("/ess") || isEmployeeOnly;

  const renderNavGroup = (
    title: string,
    items: NavItem[],
    badgeText?: string,
    badgeColor?: string
  ) => (
    <div className="space-y-1">
      <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-zinc-500 flex items-center justify-between">
        <span>{title}</span>
        {badgeText && (
          <span
            className={cn(
              "text-[9px] px-1.5 py-0.5 rounded font-bold border",
              badgeColor || "bg-brand-500/20 text-brand-300 border-brand-500/30"
            )}
          >
            {badgeText}
          </span>
        )}
      </div>
      <div className="space-y-0.5">
        {items.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={
              item.to === "/crm/home" ||
              item.to === "/ess/dashboard" ||
              item.to === "/hr" ||
              item.to === "/finance" ||
              item.to === "/analytics" ||
              item.to === "/organization"
            }
            className={({ isActive }) =>
              cn(
                "flex items-center justify-between px-3 py-2 rounded-xl text-xs font-medium transition-all duration-150",
                isActive
                  ? "bg-gradient-to-r from-brand-600 to-amber-600 text-white shadow-md shadow-brand-600/25 font-semibold"
                  : "text-zinc-300 hover:bg-zinc-900 hover:text-white"
              )
            }
          >
            <div className="flex items-center gap-3">
              {item.icon}
              <span>{item.label}</span>
            </div>
            {item.badge && (
              <span className="text-[9px] px-1.5 py-0.2 rounded font-bold bg-rose-500/25 text-rose-300 border border-rose-500/35">
                {item.badge}
              </span>
            )}
          </NavLink>
        ))}
      </div>
    </div>
  );

  return (
    <aside className="w-64 bg-[#0b0b0e]/95 border-r border-zinc-800/80 backdrop-blur-2xl flex flex-col shrink-0 h-screen sticky top-0 shadow-xl shadow-black/70">
      {/* Brand Header */}
      <div className="h-16 px-5 border-b border-zinc-800/80 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-brand-600 via-brand-500 to-amber-400 flex items-center justify-center font-extrabold text-white text-base shadow-md shadow-brand-500/30">
            V
          </div>
          <div>
            <div className="font-bold text-sm text-white tracking-tight leading-none">
              VertexERP AI
            </div>
            <div className="text-[10px] text-zinc-400 font-medium mt-1">
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
              ? "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30"
              : isHRManager
              ? "bg-amber-500/20 text-amber-300 border-amber-500/30"
              : "bg-brand-500/20 text-brand-300 border-brand-500/30"
          )}
        >
          {isESS ? "ESS" : isSalesManager ? "Sales" : isHRManager ? "HRMS" : "Admin"}
        </span>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 overflow-y-auto space-y-5 custom-scrollbar">
        {isESS && (
          <>
            {renderNavGroup(
              "Employee Self-Service",
              essNavItems,
              "ESS",
              "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
            )}
          </>
        )}

        {!isESS && isSalesManager && (
          <>
            {renderNavGroup(
              "Sales & Deals Pipeline",
              crmNavItems,
              "CRM",
              "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30"
            )}
            {renderNavGroup(
              "Governance & Approvals",
              approvalNavItems,
              "LIVE",
              "bg-rose-500/20 text-rose-300 border-rose-500/30"
            )}
            {renderNavGroup("AI Copilot", aiNavItems.slice(0, 2), "AI")}
          </>
        )}

        {!isESS && isHRManager && (
          <>
            {renderNavGroup(
              "HR Administration",
              hrNavItems,
              "HRMS",
              "bg-amber-500/20 text-amber-300 border-amber-500/30"
            )}
            {renderNavGroup(
              "Governance & Approvals",
              approvalNavItems,
              "LIVE",
              "bg-rose-500/20 text-rose-300 border-rose-500/30"
            )}
            {renderNavGroup("Organization Structure", orgNavItems)}
          </>
        )}

        {!isESS && isSuperAdmin && (
          <>
            {renderNavGroup("Executive Suite", executiveNavItems, "EXEC")}
            {renderNavGroup(
              "Governance & Workflows",
              approvalNavItems,
              "LIVE",
              "bg-rose-500/20 text-rose-300 border-rose-500/30"
            )}
            {renderNavGroup(
              "HR Administration",
              hrNavItems,
              "HRMS",
              "bg-amber-500/20 text-amber-300 border-amber-500/30"
            )}
            {renderNavGroup("Organization Structure", orgNavItems)}
            {renderNavGroup(
              "CRM & Sales Pipeline",
              crmNavItems,
              "SALES",
              "bg-fuchsia-500/20 text-fuchsia-300 border-fuchsia-500/30"
            )}
            {renderNavGroup("Vertex AI Center", aiNavItems, "GENAI")}
            {renderNavGroup(
              "Finance & Accounting",
              financeNavItems,
              "FIN",
              "bg-emerald-500/20 text-emerald-300 border-emerald-500/30"
            )}

            <div className="pt-2 border-t border-zinc-800/80">
              <button
                type="button"
                onClick={() => setOpsOpen(!opsOpen)}
                className="w-full flex items-center justify-between px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider text-zinc-400 hover:text-zinc-200"
              >
                <span>Operations & SCM</span>
                {opsOpen ? (
                  <ChevronDown className="w-3.5 h-3.5" />
                ) : (
                  <ChevronRight className="w-3.5 h-3.5" />
                )}
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
                            ? "bg-zinc-800 text-white font-semibold"
                            : "text-zinc-400 hover:bg-zinc-900 hover:text-white"
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
      <div className="p-3 border-t border-zinc-800/80 bg-zinc-950/80">
        <div className="flex items-center gap-2.5 px-2.5 py-2 rounded-xl bg-zinc-900 border border-zinc-800">
          <div className="w-7 h-7 rounded-lg bg-brand-600/25 border border-brand-500/40 flex items-center justify-center font-bold text-xs text-brand-300">
            <Sparkles className="w-3.5 h-3.5 text-brand-400" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-semibold text-zinc-200 truncate">
              {fullName ? `${fullName}'s Workspace` : "Vertex Cloud Enterprise"}
            </div>
            <div
              data-testid="sidebar-tenant-id"
              className="text-[10px] text-zinc-400 truncate"
            >
              Tenant: {tenantId || "apex-cloud"}
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
