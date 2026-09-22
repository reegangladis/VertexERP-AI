import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import {
  ExecutiveDashboardPage,
  FinancialAnalyticsPage,
  SalesAnalyticsPage,
  InventoryAnalyticsPage,
  ManufacturingAnalyticsPage,
  HRAnalyticsPage,
  KPICatalogPage,
  ReportsHubPage,
} from "@/features/analytics";
import { analyticsApi } from "@/features/analytics/api/analyticsApi";

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("Analytics & Reporting Domain Frontend Pages", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders ExecutiveDashboardPage with KPI metric cards and trends with primary_value", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "EXECUTIVE",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          code: "FIN_GROSS_REVENUE",
          name: "Gross Invoiced Revenue",
          category: "FINANCE",
          unit: "CURRENCY",
          current_value: 77000,
          previous_value: 50000,
          delta_value: 27000,
          delta_percentage: 54.0,
          status: "ON_TRACK",
          formatted_value: "$77,000.00",
          period_label: "This Month vs Prior",
        },
        {
          code: "SALES_PIPELINE_VALUE",
          name: "Active Pipeline Value",
          category: "SALES",
          unit: "CURRENCY",
          current_value: 250000,
          status: "ON_TRACK",
          formatted_value: "$250,000.00",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getFinancialTrend").mockResolvedValueOnce({
      metric_name: "Revenue vs Expenses",
      chart_type: "LINE",
      interval: "MONTHLY",
      series: [
        { timestamp: "2026-08-01", label: "Aug 2026", primary_value: 50000, secondary_value: 30000 },
        { timestamp: "2026-09-01", label: "Sep 2026", primary_value: 77000, secondary_value: 33000 },
      ],
    });

    vi.spyOn(analyticsApi, "getSalesPipelineDistribution").mockResolvedValueOnce({
      dimension_name: "Deal Stage",
      chart_type: "BAR",
      breakdowns: [
        { dimension_key: "QUALIFIED", dimension_label: "Qualified", total_amount: 250000, count: 1, percentage_share: 62.5 },
        { dimension_key: "CLOSED_WON", dimension_label: "Closed Won", total_amount: 150000, count: 1, percentage_share: 37.5 },
      ],
    });

    vi.spyOn(analyticsApi, "getInventoryWarehouseBreakdown").mockResolvedValueOnce({
      dimension_name: "Warehouse",
      chart_type: "BAR",
      breakdowns: [
        { dimension_key: "WH-MAIN", dimension_label: "Central Distribution Center", total_amount: 75000, count: 1, percentage_share: 100 },
      ],
    });

    renderWithProviders(<ExecutiveDashboardPage />);

    expect(screen.getByText("Executive Command Center")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("$77,000.00")).toBeInTheDocument();
      expect(screen.getByText("$250,000.00")).toBeInTheDocument();
      expect(screen.getByText("Financial Trajectory & Cash Velocity")).toBeInTheDocument();
    });
  });

  it("regression test: renders ExecutiveDashboardPage without crash when backend returns primary_value: 0 and secondary_value: 0", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "EXECUTIVE",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          code: "FIN_GROSS_REVENUE",
          name: "Gross Invoiced Revenue",
          category: "FINANCE",
          unit: "CURRENCY",
          current_value: 0,
          previous_value: 0,
          delta_value: 0,
          delta_percentage: null,
          status: "ON_TRACK",
          formatted_value: "$0.00",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getFinancialTrend").mockResolvedValueOnce({
      title: "Financial Performance & Profitability Trend",
      chart_type: "LINE",
      series: [
        { timestamp: "2026-09-01", label: "Sep 2026", primary_value: 0, secondary_value: 0, breakdown: { revenue: 0, expenses: 0, net_profit: 0 } },
        { timestamp: "2026-09-02", label: "Sep 2026", primary_value: 0, secondary_value: null },
      ],
      breakdowns: [],
    });

    vi.spyOn(analyticsApi, "getSalesPipelineDistribution").mockResolvedValueOnce({
      title: "Sales Pipeline Funnel Distribution",
      chart_type: "DONUT",
      series: [],
      breakdowns: [],
    });

    vi.spyOn(analyticsApi, "getInventoryWarehouseBreakdown").mockResolvedValueOnce({
      title: "Inventory Valuation by Warehouse",
      chart_type: "BAR",
      series: [],
      breakdowns: [],
    });

    renderWithProviders(<ExecutiveDashboardPage />);

    expect(screen.getByText("Executive Command Center")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("$0.00")).toBeInTheDocument();
      expect(screen.getByText("Period flat")).toBeInTheDocument();
    });
  });

  it("regression test: renders ExecutiveDashboardPage with non-zero primary_value and formats amounts correctly in chart tooltips", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "EXECUTIVE",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          code: "FIN_GROSS_REVENUE",
          name: "Gross Invoiced Revenue",
          category: "FINANCE",
          unit: "CURRENCY",
          current_value: 125000,
          status: "ON_TRACK",
          formatted_value: "$125,000.00",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getFinancialTrend").mockResolvedValueOnce({
      title: "Financial Performance & Profitability Trend",
      chart_type: "LINE",
      series: [
        { timestamp: "2026-09-01", label: "Sep 2026", primary_value: 125000, secondary_value: 45000 },
      ],
      breakdowns: [],
    });

    vi.spyOn(analyticsApi, "getSalesPipelineDistribution").mockResolvedValueOnce({
      title: "Sales Pipeline Funnel Distribution",
      chart_type: "DONUT",
      series: [],
      breakdowns: [
        { dimension_key: "PROPOSAL", dimension_label: "Proposal Sent", total_amount: 88000, count: 3, percentage_share: 100 },
      ],
    });

    vi.spyOn(analyticsApi, "getInventoryWarehouseBreakdown").mockResolvedValueOnce({
      title: "Inventory Valuation by Warehouse",
      chart_type: "BAR",
      series: [],
      breakdowns: [],
    });

    const { container } = renderWithProviders(<ExecutiveDashboardPage />);

    await waitFor(() => {
      expect(screen.getByText("$125,000.00")).toBeInTheDocument();
      expect(screen.getByText("Proposal Sent")).toBeInTheDocument();
      expect(screen.getByText("$88,000")).toBeInTheDocument();
    });

    // Verify revenue tooltip contains formatted $125,000
    const revenueBar = container.querySelector('[title="Revenue: $125,000"]');
    expect(revenueBar).toBeInTheDocument();

    const expensesBar = container.querySelector('[title="Expenses: $45,000"]');
    expect(expensesBar).toBeInTheDocument();
  });

  it("renders FinancialAnalyticsPage with profitability metrics", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "FINANCE",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          kpi_code: "FIN_NET_PROFIT_MARGIN",
          name: "Net Profit Margin",
          category: "FINANCE",
          unit: "PERCENTAGE",
          current_value: 57.14,
          status: "ON_TRACK",
          formatted_value: "57.1%",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getFinancialTrend").mockResolvedValueOnce({
      metric_name: "Revenue vs Expenses",
      chart_type: "LINE",
      interval: "MONTHLY",
      series: [
        { timestamp: "2026-09-01", label: "Sep 2026", primary_value: 77000, value: 77000, secondary_value: 33000 },
      ],
    });

    renderWithProviders(<FinancialAnalyticsPage />);

    expect(screen.getByText("Financial & Profitability Analytics")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("57.1%")).toBeInTheDocument();
    });
  });

  it("renders SalesAnalyticsPage with pipeline funnel breakdown", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "SALES",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          kpi_code: "SALES_WIN_RATE",
          name: "Opportunity Win Rate",
          category: "SALES",
          unit: "PERCENTAGE",
          current_value: 100,
          status: "ON_TRACK",
          formatted_value: "100.0%",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getSalesPipelineDistribution").mockResolvedValueOnce({
      dimension_name: "Deal Stage",
      chart_type: "BAR",
      breakdowns: [
        { dimension_key: "QUALIFIED", dimension_label: "Qualified", total_amount: 250000, count: 1, percentage_share: 62.5, percentage: 62.5 },
      ],
    });

    renderWithProviders(<SalesAnalyticsPage />);

    expect(screen.getByText("Sales & CRM Analytics")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("100.0%")).toBeInTheDocument();
      expect(screen.getByText("Qualified")).toBeInTheDocument();
    });
  });

  it("renders InventoryAnalyticsPage with stock valuation", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "INVENTORY",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          kpi_code: "INV_TOTAL_VALUATION",
          name: "Total Stock Valuation",
          category: "INVENTORY",
          unit: "CURRENCY",
          current_value: 75000,
          status: "ON_TRACK",
          formatted_value: "$75,000.00",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getInventoryWarehouseBreakdown").mockResolvedValueOnce({
      dimension_name: "Warehouse",
      chart_type: "BAR",
      breakdowns: [
        { dimension_key: "WH-MAIN", dimension_label: "Central Distribution Center", total_amount: 75000, count: 1, percentage_share: 100, percentage: 100 },
      ],
    });

    renderWithProviders(<InventoryAnalyticsPage />);

    expect(screen.getByText("Inventory & Stock Analytics")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("$75,000.00")).toBeInTheDocument();
      expect(screen.getByText("Central Distribution Center")).toBeInTheDocument();
    });
  });

  it("renders ManufacturingAnalyticsPage with FPY quality yield", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "MANUFACTURING",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          kpi_code: "MFG_FIRST_PASS_YIELD",
          name: "First-Pass Yield (FPY)",
          category: "MANUFACTURING",
          unit: "PERCENTAGE",
          current_value: 98.0,
          status: "ON_TRACK",
          formatted_value: "98.0%",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getManufacturingFpyTrend").mockResolvedValueOnce({
      metric_name: "FPY Quality Yield",
      chart_type: "BAR",
      interval: "MONTHLY",
      series: [
        { timestamp: "2026-09-01", label: "Sep 2026", primary_value: 98.0, value: 98.0 },
      ],
    });

    renderWithProviders(<ManufacturingAnalyticsPage />);

    expect(screen.getByText("Manufacturing & MRP Analytics")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("98.0%")).toBeInTheDocument();
    });
  });

  it("renders HRAnalyticsPage with workforce headcount", async () => {
    vi.spyOn(analyticsApi, "getDomainSummary").mockResolvedValueOnce({
      domain: "HR",
      period: "THIS_MONTH",
      as_of: new Date().toISOString(),
      kpis: [
        {
          kpi_code: "HR_TOTAL_HEADCOUNT",
          name: "Active Workforce Headcount",
          category: "HR",
          unit: "COUNT",
          current_value: 2,
          status: "ON_TRACK",
          formatted_value: "2",
          period_label: "This Month vs Prior",
        },
      ],
    });

    vi.spyOn(analyticsApi, "getHRDepartmentHeadcount").mockResolvedValueOnce({
      dimension_name: "Department",
      chart_type: "BAR",
      breakdowns: [
        { dimension_key: "Engineering", dimension_label: "Engineering", total_amount: 1, count: 1, percentage_share: 50, percentage: 50 },
        { dimension_key: "Sales", dimension_label: "Sales", total_amount: 1, count: 1, percentage_share: 50, percentage: 50 },
      ],
    });

    renderWithProviders(<HRAnalyticsPage />);

    expect(screen.getByText("Human Resources & Workforce Analytics")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Active Workforce Headcount")).toBeInTheDocument();
    });
  });

  it("renders KPICatalogPage with definitions table", async () => {
    vi.spyOn(analyticsApi, "getKPIDefinitions").mockResolvedValueOnce({
      items: [
        {
          id: "kpi-1",
          tenant_id: "t-1",
          organization_id: "o-1",
          code: "FIN_GROSS_REVENUE",
          name: "Gross Invoiced Revenue",
          description: "Total amount invoiced across customer billings.",
          category: "FINANCE",
          unit: "CURRENCY",
          calculation_method: "SUM",
          target_value: 500000,
          warning_threshold: 250000,
          critical_threshold: 100000,
          is_higher_better: true,
          is_active: true,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
    });

    renderWithProviders(<KPICatalogPage />);

    expect(screen.getByText("Enterprise KPI Catalog")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("FIN_GROSS_REVENUE")).toBeInTheDocument();
      expect(screen.getByText("Gross Invoiced Revenue")).toBeInTheDocument();
    });
  });

  it("renders ReportsHubPage with reports and run button", async () => {
    vi.spyOn(analyticsApi, "listReports").mockResolvedValueOnce({
      items: [
        {
          id: "rep-1",
          tenant_id: "t-1",
          organization_id: "o-1",
          code: "REP_EXEC_SUMMARY",
          title: "Executive Cross-Domain Summary",
          description: "High-level summary of financial, sales, inventory, and operations metrics.",
          category: "EXECUTIVE",
          is_system: true,
          default_parameters: {},
          query_definition: {},
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ],
      total: 1,
    });

    renderWithProviders(<ReportsHubPage />);

    expect(screen.getByText("Parameterized Reports Hub")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Executive Cross-Domain Summary")).toBeInTheDocument();
      expect(screen.getByText("Run Report")).toBeInTheDocument();
    });
  });
});
