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
  Brain,
  Zap,
  Search,
  MessageSquare,
  ShieldCheck,
  RefreshCw,
} from 'lucide-react';
import { useUI } from '@/hooks/useUI';

export function Sidebar() {
  const { isSidebarOpen } = useUI();

  if (!isSidebarOpen) return null;

  const coreItems = [
    { label: 'Overview', path: '/', icon: <Home className="h-4 w-4" /> },
    { label: 'Dashboard', path: '/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
  ];

  const mlItems = [
    { label: 'ML Dashboard', path: '/ml/dashboard', icon: <Brain className="h-4 w-4" /> },
    { label: 'Model Registry', path: '/ml/registry', icon: <Layers className="h-4 w-4" /> },
    { label: 'Training Jobs', path: '/ml/training', icon: <Play className="h-4 w-4" /> },
    { label: 'ML Experiments', path: '/ml/experiments', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Inference & Predictions', path: '/ml/predictions', icon: <Zap className="h-4 w-4" /> },
    { label: 'Evaluation Metrics', path: '/ml/evaluation', icon: <Activity className="h-4 w-4" /> },
  ];

  const mlStudioItems = [
    { label: 'ML Studio Overview', path: '/ml-studio/dashboard', icon: <Brain className="h-4 w-4" /> },
    { label: 'Dataset Registry', path: '/ml-studio/datasets', icon: <BookOpen className="h-4 w-4" /> },
    { label: 'Notebook Registry', path: '/ml-studio/notebooks', icon: <FileText className="h-4 w-4" /> },
    { label: 'Experiment Tracker', path: '/ml-studio/experiments', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Training Manager', path: '/ml-studio/training', icon: <Cpu className="h-4 w-4" /> },
    { label: 'Model Registry', path: '/ml-studio/registry', icon: <Layers className="h-4 w-4" /> },
    { label: 'Model Comparison', path: '/ml-studio/comparison', icon: <Activity className="h-4 w-4" /> },
    { label: 'Evaluation Reports', path: '/ml-studio/evaluation', icon: <CheckCircle2 className="h-4 w-4" /> },
    { label: 'Explainability (XAI)', path: '/ml-studio/explainability', icon: <TrendingUp className="h-4 w-4" /> },
  ];

  const ragItems = [
    { label: 'RAG Dashboard', path: '/rag/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Document Library', path: '/rag/documents', icon: <FileText className="h-4 w-4" /> },
    { label: 'Collections', path: '/rag/collections', icon: <Layers className="h-4 w-4" /> },
    { label: 'Upload Center', path: '/rag/upload', icon: <Play className="h-4 w-4" /> },
    { label: 'Knowledge Search', path: '/rag/search', icon: <Search className="h-4 w-4" /> },
    { label: 'AI Chat', path: '/rag/chat', icon: <MessageSquare className="h-4 w-4" /> },
    { label: 'Chat History', path: '/rag/history', icon: <History className="h-4 w-4" /> },
  ];

  const copilotItems = [
    { label: 'AI Copilot Chat', path: '/copilot/chat', icon: <MessageSquare className="h-4 w-4" /> },
    { label: 'Conversation History', path: '/copilot/history', icon: <History className="h-4 w-4" /> },
    { label: 'Prompt Manager', path: '/copilot/prompts', icon: <FileText className="h-4 w-4" /> },
    { label: 'Tool Registry', path: '/copilot/tools', icon: <Layers className="h-4 w-4" /> },
    { label: 'AI Dashboard', path: '/copilot/dashboard', icon: <Activity className="h-4 w-4" /> },
    { label: 'Copilot Settings', path: '/copilot/settings', icon: <Settings className="h-4 w-4" /> },
  ];

  const mlopsItems = [
    { label: 'MLOps Dashboard', path: '/mlops/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Deployment Center', path: '/mlops/deployments', icon: <Cpu className="h-4 w-4" /> },
    { label: 'Pipeline Manager', path: '/mlops/pipelines', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Monitoring Dashboard', path: '/mlops/monitoring', icon: <Activity className="h-4 w-4" /> },
    { label: 'Approval Queue', path: '/mlops/approvals', icon: <ShieldCheck className="h-4 w-4" /> },
    { label: 'Retraining Center', path: '/mlops/retraining', icon: <RefreshCw className="h-4 w-4" /> },
  ];

  const observabilityItems = [
    { label: 'Ops Dashboard', path: '/observability/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'System Health', path: '/observability/health', icon: <Activity className="h-4 w-4" /> },
    { label: 'Log Explorer', path: '/observability/logs', icon: <FileText className="h-4 w-4" /> },
    { label: 'Metrics Explorer', path: '/observability/metrics', icon: <TrendingUp className="h-4 w-4" /> },
    { label: 'Trace Viewer', path: '/observability/traces', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Alert Center', path: '/observability/alerts', icon: <ShieldAlert className="h-4 w-4" /> },
    { label: 'Business Telemetry', path: '/observability/business', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'AI Monitoring', path: '/observability/ai', icon: <Brain className="h-4 w-4" /> },
  ];

  // Phase 17 – Enterprise Workflow Automation
  const workflowItems = [
    { label: 'WF Dashboard', path: '/workflows/dashboard', icon: <Zap className="h-4 w-4" /> },
    { label: 'Workflow Designer', path: '/workflows/designer', icon: <GitBranch className="h-4 w-4" /> },
    { label: 'Rule Builder', path: '/workflows/rules', icon: <Shield className="h-4 w-4" /> },
    { label: 'Approval Center', path: '/workflows/approvals', icon: <CheckCircle2 className="h-4 w-4" /> },
    { label: 'Job Scheduler', path: '/workflows/scheduler', icon: <Calendar className="h-4 w-4" /> },
    { label: 'Execution Monitor', path: '/workflows/executions', icon: <Activity className="h-4 w-4" /> },
    { label: 'WF Templates', path: '/workflows/templates', icon: <LayoutDashboard className="h-4 w-4" /> },
  ];

  // Phase 18 – Enterprise Integration Platform
  const integrationItems = [
    { label: 'Integration Dashboard', path: '/integrations/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Connector Marketplace', path: '/integrations/connectors', icon: <Layers className="h-4 w-4" /> },
    { label: 'API Gateway', path: '/integrations/gateway', icon: <Network className="h-4 w-4" /> },
    { label: 'Webhook Center', path: '/integrations/webhooks', icon: <MessageSquare className="h-4 w-4" /> },
    { label: 'Event Monitor', path: '/integrations/events', icon: <Zap className="h-4 w-4" /> },
    { label: 'Queue Dashboard', path: '/integrations/queues', icon: <Activity className="h-4 w-4" /> },
    { label: 'API Analytics', path: '/integrations/analytics', icon: <TrendingUp className="h-4 w-4" /> },
  ];


  const analyticsItems = [

    { label: 'Executive Dashboard', path: '/analytics/executive', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'HR Analytics', path: '/analytics/hr', icon: <Briefcase className="h-4 w-4" /> },
    { label: 'CRM Analytics', path: '/analytics/crm', icon: <TrendingUp className="h-4 w-4" /> },
    { label: 'Inventory Analytics', path: '/analytics/inventory', icon: <Package className="h-4 w-4" /> },
    { label: 'Finance Analytics', path: '/analytics/finance', icon: <DollarSign className="h-4 w-4" /> },
    { label: 'Mfg Analytics', path: '/analytics/manufacturing', icon: <Factory className="h-4 w-4" /> },
    { label: 'Custom Report Builder', path: '/analytics/reports', icon: <FileText className="h-4 w-4" /> },
    { label: 'BI Dashboard Builder', path: '/analytics/builder', icon: <Activity className="h-4 w-4" /> },
  ];

  const dataEngineeringItems = [
    { label: 'Platform Overview', path: '/data-engineering/dashboard', icon: <LayoutDashboard className="h-4 w-4" /> },
    { label: 'Pipeline Monitor', path: '/data-engineering/pipelines', icon: <Play className="h-4 w-4" /> },
    { label: 'Dataset Explorer', path: '/data-engineering/datasets', icon: <BookOpen className="h-4 w-4" /> },
    { label: 'AI Feature Store', path: '/data-engineering/feature-store', icon: <Cpu className="h-4 w-4" /> },
    { label: 'Metadata Catalog', path: '/data-engineering/metadata', icon: <FileText className="h-4 w-4" /> },
    { label: 'Data Quality', path: '/data-engineering/quality', icon: <CheckCircle2 className="h-4 w-4" /> },
    { label: 'Data Lineage', path: '/data-engineering/lineage', icon: <GitBranch className="h-4 w-4" /> },
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

        {/* Business Intelligence & Analytics Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            BI & Analytics Platform
          </h3>
          <nav className="space-y-0.5">
            {analyticsItems.map((item) => (
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

        {/* Enterprise Machine Learning Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Machine Learning Platform
          </h3>
          <nav className="space-y-0.5">
            {mlItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Enterprise ML Studio & Model Management Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Enterprise ML Studio
          </h3>
          <nav className="space-y-0.5">
            {mlStudioItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Enterprise RAG & Knowledge Intelligence Platform (Phase 13) */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Enterprise RAG Platform
          </h3>
          <nav className="space-y-0.5">
            {ragItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Enterprise AI Copilot Platform (Phase 14) */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            AI Copilot Platform
          </h3>
          <nav className="space-y-0.5">
            {copilotItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Enterprise MLOps Platform (Phase 15) */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            MLOps Platform
          </h3>
          <nav className="space-y-0.5">
            {mlopsItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Enterprise Monitoring & Observability Platform (Phase 16) */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Monitoring & Observability
          </h3>
          <nav className="space-y-0.5">
            {observabilityItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Enterprise Data Engineering Platform */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Data Engineering Platform
          </h3>

          <nav className="space-y-0.5">
            {dataEngineeringItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-[10px] px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${
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

        {/* Workflow Automation Platform (Phase 17) */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Workflow Automation
          </h3>
          <nav className="space-y-0.5">
            {workflowItems.map((item) => (
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

        {/* Integration Platform (Phase 18) */}
        <div>
          <h3 className="px-3 text-[10px] font-semibold text-muted-foreground/60 uppercase tracking-wider mb-2">
            Integration Platform
          </h3>
          <nav className="space-y-0.5">
            {integrationItems.map((item) => (
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
        <p className="font-mono">Phase 18 Integration Platform Active</p>
      </div>
    </aside>
  );
}
export default Sidebar;


