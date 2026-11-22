/**
 * Analytics Domain API Client
 * VertexERP AI V2
 */

import { apiClient } from "@/lib/api-client";
import {
  AnalyticsFilterParams,
  AnalyticsReport,
  Dashboard,
  DimensionalDistributionData,
  DomainExecutiveSummary,
  KPIDefinition,
  MetricCardData,
  ReportExecutionResult,
  TimeSeriesData,
} from "../types";

export const analyticsApi = {
  /**
   * Fetches all registered Enterprise and Custom KPI definitions.
   */
  async getKPIDefinitions(category?: string): Promise<{ items: KPIDefinition[]; total: number }> {
    const query = category ? `?category=${category}` : "";
    return apiClient<{ items: KPIDefinition[]; total: number }>(`/analytics/kpis${query}`);
  },

  /**
   * Evaluates a single KPI metric dynamically with date filters and period comparisons.
   */
  async calculateKPI(kpiCode: string, params: AnalyticsFilterParams = {}): Promise<MetricCardData> {
    return apiClient<MetricCardData>(`/analytics/kpis/${kpiCode}/calculate`, {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Retrieves high-level domain executive summaries (EXECUTIVE, FINANCE, SALES, INVENTORY, MFG, HR).
   */
  async getDomainSummary(domain: string, params: AnalyticsFilterParams = {}): Promise<DomainExecutiveSummary> {
    return apiClient<DomainExecutiveSummary>(`/analytics/summary/${domain.toLowerCase()}`, {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Fetches Financial Trend (Revenue vs Expenses) time series.
   */
  async getFinancialTrend(params: AnalyticsFilterParams = {}): Promise<TimeSeriesData> {
    return apiClient<TimeSeriesData>("/analytics/charts/financial-trend", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Fetches Sales Pipeline funnel distribution.
   */
  async getSalesPipelineDistribution(params: AnalyticsFilterParams = {}): Promise<DimensionalDistributionData> {
    return apiClient<DimensionalDistributionData>("/analytics/charts/sales-pipeline-distribution", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Fetches Inventory valuation breakdown by Warehouse.
   */
  async getInventoryWarehouseBreakdown(): Promise<DimensionalDistributionData> {
    return apiClient<DimensionalDistributionData>("/analytics/charts/inventory-by-warehouse");
  },

  /**
   * Fetches Manufacturing First-Pass Yield (FPY) time-series.
   */
  async getManufacturingFpyTrend(params: AnalyticsFilterParams = {}): Promise<TimeSeriesData> {
    return apiClient<TimeSeriesData>("/analytics/charts/mfg-fpy-trend", {
      method: "POST",
      body: JSON.stringify(params),
    });
  },

  /**
   * Fetches HR Active Headcount distributed by Department.
   */
  async getHRDepartmentHeadcount(): Promise<DimensionalDistributionData> {
    return apiClient<DimensionalDistributionData>("/analytics/charts/hr-headcount-by-dept");
  },

  /**
   * Lists all dashboards available to the tenant/organization.
   */
  async listDashboards(): Promise<{ items: Dashboard[]; total: number }> {
    return apiClient<{ items: Dashboard[]; total: number }>("/analytics/dashboards");
  },

  /**
   * Retrieves a specific dashboard with attached widgets.
   */
  async getDashboard(code: string): Promise<Dashboard> {
    return apiClient<Dashboard>(`/analytics/dashboards/${code}`);
  },

  /**
   * Lists all parameterized enterprise reports.
   */
  async listReports(): Promise<{ items: AnalyticsReport[]; total: number }> {
    return apiClient<{ items: AnalyticsReport[]; total: number }>("/analytics/reports");
  },

  /**
   * Executes a parameterized analytical report.
   */
  async executeReport(
    reportCode: string,
    parameters: Record<string, any> = {},
    format: "JSON" | "CSV" = "JSON"
  ): Promise<ReportExecutionResult> {
    return apiClient<ReportExecutionResult>(`/analytics/reports/${reportCode}/execute`, {
      method: "POST",
      body: JSON.stringify({ parameters, format }),
    });
  },

  /**
   * Direct CSV export endpoint URL generator.
   */
  getExportCsvUrl(reportCode: string): string {
    return `/api/v1/analytics/reports/${reportCode}/export-csv`;
  },
};
