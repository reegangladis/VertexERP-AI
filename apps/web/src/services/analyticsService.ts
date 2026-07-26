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
    const res = await apiClient.get('/api/v1/analytics/dashboards/executive', {
      params: { branch_id: branchId },
    });
    return res.data;
  },

  getHRAnalytics: async (): Promise<HRAnalyticsResponse> => {
    const res = await apiClient.get('/api/v1/analytics/hr');
    return res.data;
  },

  getCRMAnalytics: async (): Promise<CRMAnalyticsResponse> => {
    const res = await apiClient.get('/api/v1/analytics/crm');
    return res.data;
  },

  getInventoryAnalytics: async (): Promise<InventoryAnalyticsResponse> => {
    const res = await apiClient.get('/api/v1/analytics/inventory');
    return res.data;
  },

  getFinanceAnalytics: async (): Promise<FinanceAnalyticsResponse> => {
    const res = await apiClient.get('/api/v1/analytics/finance');
    return res.data;
  },

  getManufacturingAnalytics: async (): Promise<ManufacturingAnalyticsResponse> => {
    const res = await apiClient.get('/api/v1/analytics/manufacturing');
    return res.data;
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
