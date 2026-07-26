import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Home,
  Users,
  Briefcase,
  Layers,
  Settings,
  Shield,
  ShieldAlert,
  User,
  History,
  Lock,
  Building2,
  GitBranch,
  Network,
  MapPin,
  Award,
  Clock,
  Calendar,
  BookOpen,
  FileText,
  DollarSign,
  Activity,
  TrendingUp,
  Package,
  Truck,
  Building,
  Factory,
  Cpu,
  Wrench,
  Play,
  CheckCircle2,
} from 'lucide-react';
import { useUI } from '@/hooks/useUI';

export function Sidebar() {
  const { isSidebarOpen } = useUI();

  if (!isSidebarOpen) return null;

  const coreItems = [
    { label: 'Overview', path: '/', icon: <Home className="h-4 w-4" /> },
    { label: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
  ];

  const manufacturingItems = [
    { label: 'Mfg Dashboard', path: '/manufacturing/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Bill of Materials', path: '/manufacturing/boms', icon: <Layers className="h-4 w-4" /> },
    { label: 'Routings', path: '/manufacturing/routings', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Work Centers', path: '/manufacturing/work-centers', icon: <Factory className="h-4 w-4" /> },
    { label: 'Machines Fleet', path: '/manufacturing/machines', icon: <Cpu className="h-4 w-4" /> },
    { label: 'Production Orders', path: '/manufacturing/production-orders', icon: <Play className="h-4 w-4" /> },
    { label: 'Shop Floor Execution', path: '/manufacturing/shop-floor', icon: <Activity className="h-4 w-4" /> },
    { label: 'Quality Control', path: '/manufacturing/quality', icon: <CheckCircle2 className="h-4 w-4" /> },
    { label: 'Maintenance', path: '/manufacturing/maintenance', icon: <Wrench className="h-4 w-4" /> },
    { label: 'MRP Engine', path: '/manufacturing/mrp', icon: <Cpu className="h-4 w-4" /> },
  ];

  const orgItems = [
    { label: 'Org Dashboard', path: '/org/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Org Profile', path: '/org/profile', icon: <Building2 className="h-4 w-4" /> },
    { label: 'Branches', path: '/org/branches', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Departments', path: '/org/departments', icon: <Network className="h-4 w-4" /> },
    { label: 'Teams', path: '/org/teams', icon: <Users className="h-4 w-4" /> },
    { label: 'Designations', path: '/org/designations', icon: <Award className="h-4 w-4" /> },
    { label: 'Locations', path: '/org/locations', icon: <MapPin className="h-4 w-4" /> },
    { label: 'Reporting Structure', path: '/org/reporting', icon: <History className="h-4 w-4" /> },
    { label: 'Business Calendar', path: '/org/calendar', icon: <Layers className="h-4 w-4" /> },
    { label: 'Org Settings', path: '/org/settings', icon: <Settings className="h-4 w-4" /> },
  ];

  const adminItems = [
    { label: 'User Administration', path: '/admin/users', icon: <Users className="h-4 w-4" /> },
    { label: 'Role Mapping', path: '/admin/roles', icon: <Shield className="h-4 w-4" /> },
    { label: 'Permission Matrix', path: '/admin/permissions', icon: <Lock className="h-4 w-4" /> },
    { label: 'Tenant Administration', path: '/admin/settings', icon: <Settings className="h-4 w-4" /> },
  ];

  const userItems = [
    { label: 'Account Settings', path: '/settings/profile', icon: <User className="h-4 w-4" /> },
  ];

  const hrItems = [
    { label: 'HR Dashboard', path: '/hr/dashboard', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'Employees', path: '/hr/employees', icon: <Users className="h-4 w-4" /> },
    { label: 'Attendance', path: '/hr/attendance', icon: <Clock className="h-4 w-4" /> },
    { label: 'Leave Management', path: '/hr/leaves', icon: <Calendar className="h-4 w-4" /> },
    { label: 'Recruitment', path: '/hr/recruitment', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'Performance', path: '/hr/performance', icon: <Award className="h-4 w-4" /> },
    { label: 'Training L&D', path: '/hr/training', icon: <BookOpen className="h-4 w-4" /> },
    { label: 'Documents Vault', path: '/hr/documents', icon: <FileText className="h-4 w-4" /> },
    { label: 'Payroll Setup', path: '/hr/payroll', icon: <DollarSign className="h-4 w-4" /> },
  ];

  const crmItems = [
    { label: 'CRM Dashboard', path: '/crm/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Customers', path: '/crm/customers', icon: <Users className="h-4 w-4" /> },
    { label: 'Leads', path: '/crm/leads', icon: <TrendingUp className="h-4 w-4" /> },
    { label: 'Sales Pipeline', path: '/crm/pipeline', icon: <Layers className="h-4 w-4" /> },
    { label: 'Deals', path: '/crm/deals', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'Activities Log', path: '/crm/activities', icon: <Clock className="h-4 w-4" /> },
    { label: 'Support Tickets', path: '/crm/support-tickets', icon: <ShieldAlert className="h-4 w-4" /> },
    { label: 'Campaigns', path: '/crm/campaigns', icon: <Activity className="h-4 w-4" /> },
  ];

  const inventoryItems = [
    { label: 'Inventory Dashboard', path: '/inventory/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Products Master', path: '/inventory/products', icon: <Package className="h-4 w-4" /> },
    { label: 'Categories', path: '/inventory/categories', icon: <Layers className="h-4 w-4" /> },
    { label: 'Warehouses', path: '/inventory/warehouses', icon: <Building className="h-4 w-4" /> },
    { label: 'Suppliers', path: '/inventory/suppliers', icon: <Truck className="h-4 w-4" /> },
    { label: 'Purchase Orders', path: '/inventory/purchase-orders', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'Stock Transfers', path: '/inventory/transfers', icon: <Activity className="h-4 w-4" /> },
    { label: 'Inventory Counts', path: '/inventory/counts', icon: <Clock className="h-4 w-4" /> },
  ];

  const financeItems = [
    { label: 'Finance Dashboard', path: '/finance/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Chart of Accounts', path: '/finance/accounts', icon: <Layers className="h-4 w-4" /> },
    { label: 'Journal Entries', path: '/finance/journals', icon: <FileText className="h-4 w-4" /> },
    { label: 'Invoices (AR)', path: '/finance/invoices', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'Bills (AP)', path: '/finance/bills', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'Expenses', path: '/finance/expenses', icon: <Activity className="h-4 w-4" /> },
    { label: 'Budgets', path: '/finance/budgets', icon: <TrendingUp className="h-4 w-4" /> },
    { label: 'Banking & Cash', path: '/finance/banking', icon: <Building2 className="h-4 w-4" /> },
    { label: 'Fixed Assets', path: '/finance/assets', icon: <Package className="h-4 w-4" /> },
    { label: 'Taxes', path: '/finance/taxes', icon: <Shield className="h-4 w-4" /> },
    { label: 'Financial Reports', path: '/finance/reports', icon: <FileText className="h-4 w-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-border bg-card shrink-0 h-[calc(100vh-4rem)] flex flex-col justify-between p-4 select-none">
      <div className="space-y-6 overflow-y-auto pr-1">
        
        {/* Core Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Core Platform
          </h3>
          <nav className="space-y-0.5">
            {coreItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Finance Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Finance & Accounting
          </h3>
          <nav className="space-y-0.5">
            {financeItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Manufacturing Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Manufacturing & Production
          </h3>
          <nav className="space-y-0.5">
            {manufacturingItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Organization Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Organization Platform
          </h3>
          <nav className="space-y-0.5">
            {orgItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* HR Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            HR Platform
          </h3>
          <nav className="space-y-0.5">
            {hrItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* CRM Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            CRM Platform
          </h3>
          <nav className="space-y-0.5">
            {crmItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Inventory Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Inventory Platform
          </h3>
          <nav className="space-y-0.5">
            {inventoryItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                  }`
                }
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </div>

      <div className="border-t border-border pt-3 text-[10px] text-muted-foreground/60 text-center">
        <p className="font-mono">Phase 7 Platform Active</p>
      </div>
    </aside>
  );
}
export default Sidebar;

