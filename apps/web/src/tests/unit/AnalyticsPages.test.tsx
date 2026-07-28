import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { CRMAnalyticsPage } from '@/pages/analytics/CRMAnalyticsPage';
import { HRAnalyticsPage } from '@/pages/analytics/HRAnalyticsPage';
import { InventoryAnalyticsPage } from '@/pages/analytics/InventoryAnalyticsPage';
import { FinanceAnalyticsPage } from '@/pages/analytics/FinanceAnalyticsPage';
import { ManufacturingAnalyticsPage } from '@/pages/analytics/ManufacturingAnalyticsPage';
import { expect, test, vi } from 'vitest';

vi.mock('@/services/analyticsService', () => ({
  analyticsService: {
    getCRMAnalytics: vi.fn().mockResolvedValue({
      total_leads: 480,
      converted_leads: 164,
      lead_conversion_rate_percent: 34.2,
      sales_pipeline_value: 8450000.0,
      active_deals_count: 42,
      win_rate_percent: 41.8,
      top_customer_revenue: 1250000.0,
      lead_funnel_stages: [],
      revenue_by_top_customers: [],
    }),
    getHRAnalytics: vi.fn().mockResolvedValue({
      total_employees: 142,
      active_employees: 138,
      headcount_growth_percent: 12.4,
      attendance_rate_percent: 96.5,
      training_completion_rate: 88.0,
      top_performer_count: 24,
      department_headcount_breakdown: [],
      leave_category_distribution: [],
    }),
    getInventoryAnalytics: vi.fn().mockResolvedValue({
      total_stock_value: 4180000.0,
      total_products_count: 840,
      inventory_turnover_ratio: 6.8,
      average_warehouse_utilization_percent: 82.4,
      average_supplier_rating: 4.8,
      stock_aging_breakdown: [],
      warehouse_capacity_utilization: [],
    }),
    getFinanceAnalytics: vi.fn().mockResolvedValue({
      net_income: 4330000.0,
      total_revenue: 12450000.0,
      budget_utilization_percent: 91.2,
      accounts_receivable: 1420000.0,
      accounts_payable: 840000.0,
      budget_vs_actual_by_category: [],
      ar_ap_aging_summary: [],
    }),
    getManufacturingAnalytics: vi.fn().mockResolvedValue({
      overall_equipment_effectiveness_percent: 88.5,
      production_efficiency_percent: 94.2,
      quality_pass_rate_percent: 99.1,
      total_downtime_hours: 14.2,
      open_maintenance_tickets: 3,
      active_production_orders: 18,
      machine_utilization_breakdown: [],
    }),
  },
}));

test('renders InventoryAnalyticsPage without toLocaleString render errors', async () => {
  render(
    <BrowserRouter>
      <InventoryAnalyticsPage />
    </BrowserRouter>
  );

  expect(await screen.findByText(/Inventory & Logistics Analytics/i)).toBeInTheDocument();
});

test('renders CRMAnalyticsPage without render errors', async () => {
  render(
    <BrowserRouter>
      <CRMAnalyticsPage />
    </BrowserRouter>
  );

  expect(await screen.findByText(/CRM & Sales Intelligence/i)).toBeInTheDocument();
});

test('renders HRAnalyticsPage without render errors', async () => {
  render(
    <BrowserRouter>
      <HRAnalyticsPage />
    </BrowserRouter>
  );

  expect(await screen.findByText(/HR & Workforce Intelligence/i)).toBeInTheDocument();
});

test('renders FinanceAnalyticsPage without render errors', async () => {
  render(
    <BrowserRouter>
      <FinanceAnalyticsPage />
    </BrowserRouter>
  );

  expect(await screen.findByText(/Finance & Accounting Intelligence/i)).toBeInTheDocument();
});

test('renders ManufacturingAnalyticsPage without render errors', async () => {
  render(
    <BrowserRouter>
      <ManufacturingAnalyticsPage />
    </BrowserRouter>
  );

  expect(await screen.findByText(/Manufacturing & Plant Intelligence/i)).toBeInTheDocument();
});
