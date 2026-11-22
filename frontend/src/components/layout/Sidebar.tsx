import React from "react";
import { NavLink } from "react-router-dom";
import { cn } from "@/lib/utils";
import { useAuthStore } from "@/stores/auth-store";
import {
  Building2,
  GitFork,
  Users,
  Award,
  Layers,
  DollarSign,
  MapPin,
  Calendar,
  Sun,
  LayoutDashboard,
  ShieldCheck,
  UserCheck,
  Clock,
  CalendarOff,
  Briefcase,
  TrendingUp,
  GraduationCap,
  Boxes,
  Warehouse,
  History,
  ArrowLeftRight,
  SlidersHorizontal,
  ArrowDownToLine,
  ShoppingCart,
  FileSpreadsheet,
  Scale,
  BookOpen,
  Receipt,
  CreditCard,
  Landmark,
  FileText,
  Factory,
  Cpu,
  BarChart3,
  Activity,
  Sparkles,
  Bot,
  Zap,
} from "lucide-react";

interface NavItem {
  label: string;
  to: string;
  icon: React.ReactNode;
  permission?: string;
}

const aiNavItems: NavItem[] = [
  {
    label: "Vertex Copilot",
    to: "/ai/copilot",
    icon: <Bot className="w-4 h-4 text-indigo-400" />,
  },
  {
    label: "Knowledge Base & RAG",
    to: "/ai/knowledge",
    icon: <BookOpen className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "AI Observability & Costs",
    to: "/ai/telemetry",
    icon: <Zap className="w-4 h-4 text-amber-400" />,
  },
];

const jobsNavItems: NavItem[] = [
  {
    label: "Background Jobs & Tasks",
    to: "/jobs",
    icon: <Cpu className="w-4 h-4 text-cyan-400" />,
  },
];

const analyticsNavItems: NavItem[] = [
  {
    label: "Executive Overview",
    to: "/analytics",
    icon: <Sparkles className="w-4 h-4 text-brand-400" />,
  },
  {
    label: "Financial Analytics",
    to: "/analytics/finance",
    icon: <DollarSign className="w-4 h-4 text-emerald-400" />,
  },
  {
    label: "Sales & CRM Intelligence",
    to: "/analytics/sales",
    icon: <ShoppingCart className="w-4 h-4 text-blue-400" />,
  },
  {
    label: "Inventory Health",
    to: "/analytics/inventory",
    icon: <Boxes className="w-4 h-4 text-amber-400" />,
  },
  {
    label: "Manufacturing Operations",
    to: "/analytics/manufacturing",
    icon: <Factory className="w-4 h-4 text-purple-400" />,
  },
  {
    label: "HR & Workforce",
    to: "/analytics/hr",
    icon: <Users className="w-4 h-4 text-rose-400" />,
  },
  {
    label: "KPI Catalog",
    to: "/analytics/kpis",
    icon: <Award className="w-4 h-4 text-cyan-400" />,
  },
  {
    label: "Reports & Exports",
    to: "/analytics/reports",
    icon: <FileSpreadsheet className="w-4 h-4 text-indigo-400" />,
  },
];

const financeNavItems: NavItem[] = [
  {
    label: "Finance Dashboard",
    to: "/finance",
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: "Chart of Accounts",
    to: "/finance/accounts",
    icon: <BookOpen className="w-4 h-4" />,
  },
  {
    label: "Fiscal Periods",
    to: "/finance/periods",
    icon: <Calendar className="w-4 h-4" />,
  },
  {
    label: "General Journal",
    to: "/finance/journals",
    icon: <Scale className="w-4 h-4" />,
  },
  {
    label: "Customer Invoices",
    to: "/finance/invoices",
    icon: <Receipt className="w-4 h-4" />,
  },
  {
    label: "Vendor Bills",
    to: "/finance/bills",
    icon: <CreditCard className="w-4 h-4" />,
  },
  {
    label: "Payments & Allocation",
    to: "/finance/payments",
    icon: <DollarSign className="w-4 h-4" />,
  },
  {
    label: "Bank & Treasury",
    to: "/finance/banks",
    icon: <Landmark className="w-4 h-4" />,
  },
  {
    label: "Financial Statements",
    to: "/finance/reports",
    icon: <FileSpreadsheet className="w-4 h-4" />,
  },
];

const inventoryNavItems: NavItem[] = [
  {
    label: "Inventory Dashboard",
    to: "/inventory",
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: "Products & SKUs",
    to: "/inventory/products",
    icon: <Boxes className="w-4 h-4" />,
  },
  {
    label: "Warehouses & Bins",
    to: "/inventory/warehouses",
    icon: <Warehouse className="w-4 h-4" />,
  },
  {
    label: "Stock Balances",
    to: "/inventory/balances",
    icon: <Layers className="w-4 h-4" />,
  },
  {
    label: "Movements Ledger",
    to: "/inventory/ledger",
    icon: <History className="w-4 h-4" />,
  },
  {
    label: "Stock Transfers",
    to: "/inventory/transfers",
    icon: <ArrowLeftRight className="w-4 h-4" />,
  },
  {
    label: "Stock Adjustments",
    to: "/inventory/adjustments",
    icon: <SlidersHorizontal className="w-4 h-4" />,
  },
  {
    label: "Goods Receipts (GRN)",
    to: "/inventory/receipts",
    icon: <ArrowDownToLine className="w-4 h-4" />,
  },
];

const procurementNavItems: NavItem[] = [
  {
    label: "Procurement Hub",
    to: "/procurement",
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: "Suppliers & Vendors",
    to: "/procurement/suppliers",
    icon: <Users className="w-4 h-4" />,
  },
  {
    label: "Purchase Requests (PR)",
    to: "/procurement/requests",
    icon: <FileSpreadsheet className="w-4 h-4" />,
  },
  {
    label: "Purchase Orders (PO)",
    to: "/procurement/orders",
    icon: <ShoppingCart className="w-4 h-4" />,
  },
];

const manufacturingNavItems: NavItem[] = [
  {
    label: "Manufacturing Hub",
    to: "/manufacturing",
    icon: <Factory className="w-4 h-4" />,
  },
  {
    label: "Bills of Materials (BOM)",
    to: "/manufacturing/boms",
    icon: <Layers className="w-4 h-4" />,
  },
  {
    label: "Routings & Operations",
    to: "/manufacturing/routings",
    icon: <GitFork className="w-4 h-4" />,
  },
  {
    label: "Work Centers & Machines",
    to: "/manufacturing/work-centers",
    icon: <Cpu className="w-4 h-4" />,
  },
  {
    label: "Production Orders",
    to: "/manufacturing/production-orders",
    icon: <FileSpreadsheet className="w-4 h-4" />,
  },
  {
    label: "Shop Floor Work Orders",
    to: "/manufacturing/work-orders",
    icon: <Briefcase className="w-4 h-4" />,
  },
  {
    label: "Consumption & Scrap Ledger",
    to: "/manufacturing/consumption",
    icon: <History className="w-4 h-4" />,
  },
  {
    label: "MRP Engine (Gross/Net)",
    to: "/manufacturing/mrp",
    icon: <SlidersHorizontal className="w-4 h-4" />,
  },
  {
    label: "Quality Control (QC)",
    to: "/manufacturing/quality",
    icon: <ShieldCheck className="w-4 h-4" />,
  },
];

const hrNavItems: NavItem[] = [
  {
    label: "HR Dashboard",
    to: "/hr",
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: "Employees",
    to: "/hr/employees",
    icon: <UserCheck className="w-4 h-4" />,
  },
  {
    label: "Attendance & Shifts",
    to: "/hr/attendance",
    icon: <Clock className="w-4 h-4" />,
  },
  {
    label: "Leaves & Quotas",
    to: "/hr/leaves",
    icon: <CalendarOff className="w-4 h-4" />,
  },
  {
    label: "Payroll & Payslips",
    to: "/hr/payroll",
    icon: <DollarSign className="w-4 h-4" />,
  },
  {
    label: "Recruitment (ATS)",
    to: "/hr/recruitment",
    icon: <Briefcase className="w-4 h-4" />,
  },
  {
    label: "Performance & OKRs",
    to: "/hr/performance",
    icon: <TrendingUp className="w-4 h-4" />,
  },
  {
    label: "Learning (LMS)",
    to: "/hr/learning",
    icon: <GraduationCap className="w-4 h-4" />,
  },
];

const orgNavItems: NavItem[] = [
  {
    label: "Overview",
    to: "/organization",
    icon: <LayoutDashboard className="w-4 h-4" />,
  },
  {
    label: "Branches",
    to: "/organization/branches",
    icon: <Building2 className="w-4 h-4" />,
    permission: "organization:branches:read",
  },
  {
    label: "Departments",
    to: "/organization/departments",
    icon: <GitFork className="w-4 h-4" />,
    permission: "organization:departments:read",
  },
  {
    label: "Teams",
    to: "/organization/teams",
    icon: <Users className="w-4 h-4" />,
    permission: "organization:teams:read",
  },
  {
    label: "Designations",
    to: "/organization/designations",
    icon: <Award className="w-4 h-4" />,
    permission: "organization:designations:read",
  },
  {
    label: "Business Units",
    to: "/organization/business-units",
    icon: <Layers className="w-4 h-4" />,
    permission: "organization:business_units:read",
  },
  {
    label: "Cost Centers",
    to: "/organization/cost-centers",
    icon: <DollarSign className="w-4 h-4" />,
    permission: "organization:cost_centers:read",
  },
  {
    label: "Locations",
    to: "/organization/locations",
    icon: <MapPin className="w-4 h-4" />,
    permission: "organization:locations:read",
  },
  {
    label: "Work Calendars",
    to: "/organization/calendars",
    icon: <Calendar className="w-4 h-4" />,
    permission: "organization:calendars:read",
  },
  {
    label: "Holidays",
    to: "/organization/holidays",
    icon: <Sun className="w-4 h-4" />,
    permission: "organization:holidays:read",
  },
];

export const Sidebar: React.FC = () => {
  const { tenantId, fullName } = useAuthStore();

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Logo */}
      <div className="h-16 px-6 border-b border-slate-800 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-400 flex items-center justify-center font-bold text-white shadow-md shadow-brand-500/20">
          V
        </div>
        <div>
          <span className="font-bold text-sm tracking-tight text-white">VertexERP</span>
          <span className="text-[10px] uppercase tracking-wider font-semibold ml-1.5 px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300">
            AI V2
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 py-4 px-3 overflow-y-auto space-y-4">
        {/* AI Platform & Copilot */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-indigo-400 flex items-center justify-between">
            <span>AI Platform & Copilot</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-indigo-500/20 text-indigo-300 font-bold">
              GENAI
            </span>
          </div>
          <div className="space-y-1 mt-1">
            {aiNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/ai/copilot"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-indigo-600 text-white shadow-sm shadow-indigo-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Background Processing & Jobs */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-cyan-400 flex items-center justify-between">
            <span>Async Processing</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-cyan-500/20 text-cyan-300 font-bold">
              WORKERS
            </span>
          </div>
          <div className="space-y-1 mt-1">
            {jobsNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-cyan-600 text-white shadow-sm shadow-cyan-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Analytics & Intelligence */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-brand-400 flex items-center justify-between">
            <span>Analytics & Intelligence</span>
            <span className="text-[9px] px-1.5 py-0.5 rounded bg-brand-500/20 text-brand-300 font-bold">
              OLAP
            </span>
          </div>
          <div className="space-y-1 mt-1">
            {analyticsNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/analytics"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Finance & Accounting */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Finance & Accounting
          </div>
          <div className="space-y-1 mt-1">
            {financeNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/finance"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Inventory Management */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Inventory & Stock
          </div>
          <div className="space-y-1 mt-1">
            {inventoryNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/inventory"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Procurement */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Procurement & Purchasing
          </div>
          <div className="space-y-1 mt-1">
            {procurementNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/procurement"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Manufacturing & MRP */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Manufacturing & MRP
          </div>
          <div className="space-y-1 mt-1">
            {manufacturingNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/manufacturing"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Human Resources */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Human Resources (HR)
          </div>
          <div className="space-y-1 mt-1">
            {hrNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/hr"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>

        {/* Organization Domain */}
        <div>
          <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-slate-400">
            Organization Domain
          </div>
          <div className="space-y-1 mt-1">
            {orgNavItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === "/organization"}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-colors",
                    isActive
                      ? "bg-brand-600 text-white shadow-sm shadow-brand-600/30"
                      : "text-slate-300 hover:bg-slate-800/60 hover:text-slate-100"
                  )
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </div>
        </div>
      </div>

      {/* Tenant / Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-900/50">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/60 border border-slate-700/40 text-xs">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <div className="truncate">
            <div className="font-medium text-slate-200 truncate">{fullName ? `${fullName}'s Workspace` : "Enterprise Workspace"}</div>
            <div className="text-[10px] text-slate-400" data-testid="sidebar-tenant-id">Tenant: {tenantId || "authenticated"}</div>
          </div>
        </div>
      </div>
    </aside>
  );
};
