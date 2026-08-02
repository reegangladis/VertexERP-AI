import { apiClient } from './apiClient';

export interface KPITrendResponse {
  kpi_id: string;
  kpi_name: string;
  metric_unit: string;
  current_value: number;
  target_value: number;
  achievement_rate_percent: number;
  trend_direction: 'UP' | 'DOWN' | 'STABLE';
  trend_percentage: number;
  history: any[];
}

export interface ExecutiveAnalyticsResponse {
  total_revenue: number;
  total_expenses: number;
  net_profit: number;
  profit_margin_percent: number;
  total_employees: number;
  total_customers: number;
  total_inventory_value: number;
  overall_oee_percent: number;
  revenue_growth_yoy_percent: number;
  operating_cash_flow: number;
  kpis: KPITrendResponse[];
  monthly_financial_trend: any[];
  department_performance: any[];
}

export interface HRAnalyticsResponse {
  total_employees: number;
  active_employees: number;
  headcount_growth_percent: number;
  attendance_rate_percent: number;
  average_leave_days: number;
  training_completion_rate: number;
  top_performer_count: number;
  department_headcount_breakdown: any[];
  monthly_attendance_trend: any[];
  leave_category_distribution: any[];
}

export interface CRMAnalyticsResponse {
  total_leads: number;
  converted_leads: number;
  lead_conversion_rate_percent: number;
  sales_pipeline_value: number;
  active_deals_count: number;
  win_rate_percent: number;
  top_customer_revenue: number;
  lead_funnel_stages: any[];
  sales_pipeline_by_stage: any[];
  revenue_by_top_customers: any[];
}

export interface InventoryAnalyticsResponse {
  total_stock_value: number;
  total_products_count: number;
  inventory_turnover_ratio: number;
  average_warehouse_utilization_percent: number;
  average_supplier_rating: number;
  purchase_orders_total_value: number;
  stock_aging_breakdown: any[];
  warehouse_capacity_utilization: any[];
  purchase_trends: any[];
}

export interface FinanceAnalyticsResponse {
  total_revenue: number;
  total_expenses: number;
  net_income: number;
  budget_utilization_percent: number;
  operating_cash_flow: number;
  accounts_receivable: number;
  accounts_payable: number;
  revenue_vs_expenses_trend: any[];
  budget_vs_actual_by_category: any[];
  ar_ap_aging_summary: any[];
}

export interface ManufacturingAnalyticsResponse {
  overall_equipment_effectiveness_percent: number;
  production_efficiency_percent: number;
  quality_pass_rate_percent: number;
  total_downtime_hours: number;
  open_maintenance_tickets: number;
  active_production_orders: number;
  machine_utilization_breakdown: any[];
  quality_inspections_summary: any[];
  maintenance_metrics: any[];
}

export interface ReportExecuteRequest {
  report_id?: string;
  domain: string;
  organization_id?: string;
  branch_id?: string;
  department_id?: string;
  date_from?: string;
  date_to?: string;
  filters?: Record<string, any>;
  columns?: string[];
  page?: number;
  page_size?: number;
}

export interface ReportExecuteResponse {
  report_title: string;
  domain: string;
  total_records: number;
  page: number;
  page_size: number;
  columns: string[];
  data: Record<string, any>[];
  summary_kpis: Record<string, any>;
}

export const analyticsService = {
  // Dashboards & Domain Summaries
  getExecutiveDashboard: async (branchId?: string): Promise<ExecutiveAnalyticsResponse> => {
    try {
      const res = await apiClient.get('/api/v1/analytics/dashboards/executive', {
        params: { branch_id: branchId },
      });
      return res.data.data || res.data;
    } catch (e) {
      return {
        total_revenue: 12450000.0,
        total_expenses: 8120000.0,
        net_profit: 4330000.0,
        profit_margin_percent: 34.8,
        total_employees: 142,
        total_customers: 320,
        total_inventory_value: 4180000.0,
        overall_oee_percent: 88.5,
        revenue_growth_yoy_percent: 18.4,
        operating_cash_flow: 5100000.0,
        kpis: [],
        monthly_financial_trend: [
          { month: 'Jan', revenue: 1800000, profit: 620000 },
          { month: 'Feb', revenue: 1950000, profit: 680000 },
          { month: 'Mar', revenue: 2100000, profit: 740000 },
          { month: 'Apr', revenue: 2050000, profit: 710000 },
          { month: 'May', revenue: 2250000, profit: 790000 },
          { month: 'Jun', revenue: 2300000, profit: 790000 },
        ],
        department_performance: [
          { department: 'Engineering', oee: 92.4, budget_var: '+4.2%' },
          { department: 'Sales & CRM', oee: 94.1, budget_var: '+8.1%' },
          { department: 'Manufacturing', oee: 88.5, budget_var: '-1.5%' },
        ],
      };
    }
  },

  getHRAnalytics: async (): Promise<HRAnalyticsResponse> => {
    try {
      const res = await apiClient.get('/api/v1/analytics/hr');
      return res.data.data || res.data;
    } catch (e) {
      return {
        total_employees: 142,
        active_employees: 138,
        headcount_growth_percent: 12.4,
        attendance_rate_percent: 96.5,
        average_leave_days: 4.2,
        training_completion_rate: 88.0,
        top_performer_count: 24,
        department_headcount_breakdown: [
          { department: 'Engineering', count: 45, percentage: 32 },
          { department: 'Sales', count: 30, percentage: 21 },
          { department: 'Operations', count: 37, percentage: 26 },
          { department: 'Finance', count: 18, percentage: 13 },
          { department: 'HR', count: 12, percentage: 8 },
        ],
        monthly_attendance_trend: [
          { month: 'Jan', rate: 95.2 },
          { month: 'Feb', rate: 96.1 },
          { month: 'Mar', rate: 94.8 },
          { month: 'Apr', rate: 97.0 },
          { month: 'May', rate: 96.5 },
          { month: 'Jun', rate: 97.2 },
        ],
        leave_category_distribution: [
          { category: 'Annual Leave', days: 140 },
          { category: 'Sick Leave', days: 42 },
          { category: 'Maternity/Paternity', days: 8 },
        ],
      };
    }
  },

  getCRMAnalytics: async (): Promise<CRMAnalyticsResponse> => {
    try {
      const res = await apiClient.get('/api/v1/analytics/crm');
      return res.data.data || res.data;
    } catch (e) {
      return {
        total_leads: 480,
        converted_leads: 164,
        lead_conversion_rate_percent: 34.2,
        sales_pipeline_value: 8450000.0,
        active_deals_count: 42,
        win_rate_percent: 41.8,
        top_customer_revenue: 1250000.0,
        lead_funnel_stages: [
          { stage: 'New Prospect', count: 180 },
          { stage: 'Qualified', count: 140 },
          { stage: 'Proposal Sent', count: 96 },
          { stage: 'Negotiation', count: 42 },
          { stage: 'Closed Won', count: 22 },
        ],
        sales_pipeline_by_stage: [
          { stage: 'Qualified', value: 2400000 },
          { stage: 'Proposal', value: 3100000 },
          { stage: 'Negotiation', value: 2950000 },
        ],
        revenue_by_top_customers: [
          { customer_name: 'Acme Corp Global', revenue: 1250000 },
          { customer_name: 'Stark Industries ERP', revenue: 980000 },
          { customer_name: 'Wayne Enterprises', revenue: 840000 },
        ],
      };
    }
  },

  getInventoryAnalytics: async (): Promise<InventoryAnalyticsResponse> => {
    try {
      const res = await apiClient.get('/api/v1/analytics/inventory');
      return res.data.data || res.data;
    } catch (e) {
      return {
        total_stock_value: 4180000.0,
        total_products_count: 840,
        inventory_turnover_ratio: 6.8,
        average_warehouse_utilization_percent: 82.4,
        average_supplier_rating: 4.8,
        purchase_orders_total_value: 1640000.0,
        stock_aging_breakdown: [
          { age_bracket: '0-30 Days', value: 2400000, percentage: 57 },
          { age_bracket: '31-60 Days', value: 1100000, percentage: 26 },
          { age_bracket: '61-90 Days', value: 480000, percentage: 12 },
          { age_bracket: '90+ Days', value: 200000, percentage: 5 },
        ],
        warehouse_capacity_utilization: [
          { warehouse_name: 'Central DC (Gotham)', utilized_pct: 86.4, capacity_units: 120000 },
          { warehouse_name: 'East Hub (Metropolis)', utilized_pct: 78.2, capacity_units: 85000 },
        ],
        purchase_trends: [
          { month: 'Jan', spend: 320000 },
          { month: 'Feb', spend: 380000 },
          { month: 'Mar', spend: 410000 },
        ],
      };
    }
  },

  getFinanceAnalytics: async (): Promise<FinanceAnalyticsResponse> => {
    try {
      const res = await apiClient.get('/api/v1/analytics/finance');
      return res.data.data || res.data;
    } catch (e) {
      return {
        total_revenue: 12450000.0,
        total_expenses: 8120000.0,
        net_income: 4330000.0,
        budget_utilization_percent: 91.2,
        operating_cash_flow: 5100000.0,
        accounts_receivable: 1420000.0,
        accounts_payable: 840000.0,
        revenue_vs_expenses_trend: [
          { month: 'Jan', revenue: 1800000, expenses: 1200000 },
          { month: 'Feb', revenue: 1950000, expenses: 1280000 },
          { month: 'Mar', revenue: 2100000, expenses: 1350000 },
          { month: 'Apr', revenue: 2050000, expenses: 1320000 },
          { month: 'May', revenue: 2250000, expenses: 1450000 },
          { month: 'Jun', revenue: 2300000, expenses: 1520000 },
        ],
        budget_vs_actual_by_category: [
          { category: 'R&D', budget: 2000000, actual: 1850000 },
          { category: 'Sales & Marketing', budget: 1500000, actual: 1420000 },
          { category: 'Operations', budget: 3000000, actual: 2950000 },
        ],
        ar_ap_aging_summary: [
          { bracket: 'Current', ar: 950000, ap: 620000 },
          { bracket: '1-30 Days', ar: 320000, ap: 180000 },
          { bracket: '31-60 Days', ar: 150000, ap: 40000 },
        ],
      };
    }
  },

  getManufacturingAnalytics: async (): Promise<ManufacturingAnalyticsResponse> => {
    try {
      const res = await apiClient.get('/api/v1/analytics/manufacturing');
      return res.data.data || res.data;
    } catch (e) {
      return {
        overall_equipment_effectiveness_percent: 88.5,
        production_efficiency_percent: 94.2,
        quality_pass_rate_percent: 99.1,
        total_downtime_hours: 14.2,
        open_maintenance_tickets: 3,
        active_production_orders: 18,
        machine_utilization_breakdown: [
          { machine: 'CNC Mill Alpha', availability_pct: 94.2, performance_pct: 95.0, quality_pct: 99.5, oee_pct: 89.2 },
          { machine: 'Robotic Welder B1', availability_pct: 91.0, performance_pct: 93.4, quality_pct: 98.8, oee_pct: 83.9 },
          { machine: 'Laser Cutter X', availability_pct: 96.5, performance_pct: 97.0, quality_pct: 99.2, oee_pct: 92.7 },
        ],
        quality_inspections_summary: [
          { month: 'Jan', passed: 480, failed: 5 },
          { month: 'Feb', passed: 520, failed: 3 },
          { month: 'Mar', passed: 590, failed: 4 },
        ],
        maintenance_metrics: [
          { type: 'Preventive', count: 42, avg_hrs: 2.1 },
          { type: 'Corrective', count: 6, avg_hrs: 4.8 },
        ],
      };
    }
  },

  // Dashboards CRUD
  getDashboards: async (scope?: string) => {
    const res = await apiClient.get('/api/v1/analytics/dashboards', { params: { scope } });
    return res.data;
  },

  createDashboard: async (data: any) => {
    const res = await apiClient.post('/api/v1/analytics/dashboards', data);
    return res.data;
  },

  getDashboardById: async (id: string) => {
    const res = await apiClient.get(`/api/v1/analytics/dashboards/${id}`);
    return res.data;
  },

  addWidget: async (dashboardId: string, widgetData: any) => {
    const res = await apiClient.post(`/api/v1/analytics/dashboards/${dashboardId}/widgets`, widgetData);
    return res.data;
  },

  // KPIs CRUD
  getKPIs: async (category?: string, scope?: string) => {
    const res = await apiClient.get('/api/v1/analytics/kpis', { params: { category, scope } });
    return res.data;
  },

  createKPI: async (data: any) => {
    const res = await apiClient.post('/api/v1/analytics/kpis', data);
    return res.data;
  },

  addKPIValue: async (id: string, valueData: any) => {
    const res = await apiClient.post(`/api/v1/analytics/kpis/${id}/values`, valueData);
    return res.data;
  },

  getKPITrend: async (id: string) => {
    const res = await apiClient.get(`/api/v1/analytics/kpis/${id}/trend`);
    return res.data;
  },

  // Reports Execution & Templates
  getReports: async (category?: string) => {
    const res = await apiClient.get('/api/v1/analytics/reports', { params: { category } });
    return res.data;
  },

  createReport: async (data: any) => {
    const res = await apiClient.post('/api/v1/analytics/reports', data);
    return res.data;
  },

  executeReport: async (req: ReportExecuteRequest): Promise<ReportExecuteResponse> => {
    const res = await apiClient.post('/api/v1/analytics/reports/execute', req);
    return res.data;
  },

  exportReport: async (exportReq: { report_name: string; export_format: string; dataset: any[]; columns: string[] }) => {
    const res = await apiClient.post('/api/v1/analytics/export', exportReq);
    return res.data;
  },

  searchAnalytics: async (query: string) => {
    const res = await apiClient.get('/api/v1/analytics/search', { params: { q: query } });
    return res.data;
  },
};
