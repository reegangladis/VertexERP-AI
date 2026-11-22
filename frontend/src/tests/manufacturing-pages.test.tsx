import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { ManufacturingOverviewPage } from "@/features/manufacturing/pages/ManufacturingOverviewPage";
import { BillsOfMaterialsPage } from "@/features/manufacturing/pages/BillsOfMaterialsPage";
import { RoutingsPage } from "@/features/manufacturing/pages/RoutingsPage";
import { WorkCentersPage } from "@/features/manufacturing/pages/WorkCentersPage";
import { ProductionOrdersPage } from "@/features/manufacturing/pages/ProductionOrdersPage";
import { WorkOrdersPage } from "@/features/manufacturing/pages/WorkOrdersPage";
import { MaterialConsumptionPage } from "@/features/manufacturing/pages/MaterialConsumptionPage";
import { MRPEnginePage } from "@/features/manufacturing/pages/MRPEnginePage";
import { QualityInspectionsPage } from "@/features/manufacturing/pages/QualityInspectionsPage";
import { useAuthStore } from "@/stores/auth-store";

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

describe("Manufacturing & MRP Domain Frontend Pages", () => {
  const mockWorkCenter = {
    id: "wc-1",
    code: "WC-ASSY-01",
    name: "Main Electronics Assembly",
    work_center_type: "ASSEMBLY",
    capacity_per_day_hours: "16.00",
    cost_per_hour: "45.0000",
    overhead_cost_per_hour: "15.0000",
    efficiency_percentage: "95.00",
    status: "ACTIVE",
    is_active: true,
    machines: [],
  };

  const mockRouting = {
    id: "rt-1",
    code: "RT-SERVER-X1",
    name: "High-Performance Server Routing",
    product_id: "p-server-01",
    description: "Multi-step electronics routing",
    is_active: true,
    operations: [
      {
        id: "op-1",
        sequence: 10,
        operation_name: "Motherboard Mounting",
        work_center_id: "wc-1",
        setup_time_hours: "0.25",
        run_time_per_unit_hours: "0.50",
      },
    ],
  };

  const mockBOM = {
    id: "bom-1",
    code: "BOM-SERVER-X1",
    name: "Standard Server Assembly BOM",
    product_id: "p-server-01",
    quantity: "1.0000",
    uom_id: "uom-ea",
    status: "ACTIVE",
    is_default: true,
    versions: [
      {
        id: "bom-v1",
        version_number: 1,
        status: "ACTIVE",
        components: [
          {
            id: "comp-1",
            component_product_id: "p-cpu-01",
            quantity: "2.0000",
            scrap_percentage: "0.00",
            line_cost: "400.0000",
          },
        ],
      },
    ],
  };

  const mockProductionOrder = {
    id: "po-1",
    order_number: "MO-2026-0001",
    product_id: "p-server-01",
    bom_id: "bom-1",
    bom_version_id: "bom-v1",
    planned_quantity: 25,
    produced_quantity: 10,
    rejected_quantity: 0,
    scrap_quantity: 0,
    target_warehouse_id: "wh-fg",
    planned_start_date: "2026-09-08T08:00:00Z",
    planned_due_date: "2026-09-15T17:00:00Z",
    status: "IN_PROGRESS",
    priority: "HIGH",
    unit_cost: 1250.0,
    total_cost: 31250.0,
    work_orders: [
      {
        id: "wo-1",
        sequence: 10,
        operation_name: "Mounting & Wiring",
        work_center_id: "wc-1",
        status: "IN_PROGRESS",
        planned_duration_hours: 4.0,
        actual_duration_hours: 2.0,
        hourly_rate: 45.0,
        total_labor_cost: 90.0,
      },
    ],
    consumptions: [
      {
        id: "mc-1",
        product_id: "p-cpu-01",
        warehouse_id: "wh-raw",
        planned_quantity: 50,
        consumed_quantity: 20,
        unit_cost: 200.0,
        total_cost: 4000.0,
        consumed_at: "2026-09-08T09:00:00Z",
      },
    ],
    outputs: [
      {
        id: "out-1",
        product_id: "p-server-01",
        target_warehouse_id: "wh-fg",
        produced_quantity: 10,
        unit_manufacturing_cost: 1250.0,
        total_manufacturing_cost: 12500.0,
        output_date: "2026-09-08T11:00:00Z",
      },
    ],
    scraps: [],
  };

  const mockMRPRun = {
    id: "mrp-run-1",
    run_number: "MRP-20260908-01",
    planning_horizon_days: 30,
    status: "COMPLETED",
    run_date: "2026-09-08T08:00:00Z",
    total_items_planned: 5,
    total_purchase_requests_generated: 3,
    total_production_orders_generated: 2,
    planned_orders: [
      {
        id: "po-plan-1",
        product_id: "p-server-01",
        order_type: "MANUFACTURE",
        gross_requirement: 50,
        on_hand_stock: 10,
        scheduled_receipts: 0,
        net_requirement: 40,
        planned_quantity: 40,
        order_date: "2026-09-08T08:00:00Z",
        required_date: "2026-09-20T00:00:00Z",
        status: "PLANNED",
      },
      {
        id: "po-plan-2",
        product_id: "p-cpu-01",
        order_type: "PURCHASE",
        gross_requirement: 80,
        on_hand_stock: 20,
        scheduled_receipts: 0,
        net_requirement: 60,
        planned_quantity: 60,
        order_date: "2026-09-08T08:00:00Z",
        required_date: "2026-09-18T00:00:00Z",
        status: "PLANNED",
      },
    ],
  };

  const mockQualityInspection = {
    id: "qc-1",
    inspection_number: "QC-2026-0001",
    production_order_id: "po-1",
    product_id: "p-server-01",
    inspection_type: "FINAL_ASSEMBLY",
    inspected_quantity: 10,
    passed_quantity: 10,
    failed_quantity: 0,
    result: "PASSED",
    inspection_date: "2026-09-08T11:30:00Z",
    status: "COMPLETED",
  };

  beforeEach(() => {
    useAuthStore.getState().setAuth({
      userId: "u-mfg-mgr",
      email: "mfg.director@vertexerp.io",
      fullName: "Manufacturing Director",
      tenantId: "t-001",
      organizationId: "org-001",
      roles: ["ManufacturingManager", "ProductionPlanner", "QualityInspector"],
      permissions: [
        "manufacturing:work_centers:read",
        "manufacturing:work_centers:write",
        "manufacturing:routings:read",
        "manufacturing:routings:write",
        "manufacturing:boms:read",
        "manufacturing:boms:write",
        "manufacturing:production_orders:read",
        "manufacturing:production_orders:write",
        "manufacturing:mrp:execute",
        "manufacturing:quality:read",
        "manufacturing:quality:write",
      ],
    });

    global.fetch = vi.fn().mockImplementation((url: string) => {
      // Work Centers
      if (url.includes("/manufacturing/work-centers")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [mockWorkCenter],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Routings
      if (url.includes("/manufacturing/routings")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [mockRouting],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // BOMs
      if (url.includes("/manufacturing/boms")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [mockBOM],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Quality Inspections
      if (url.includes("/manufacturing/quality-inspections")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [mockQualityInspection],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // MRP Runs specific ID
      if (url.includes("/manufacturing/mrp/runs/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => mockMRPRun,
        });
      }

      // MRP Runs list
      if (url.includes("/manufacturing/mrp/runs")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [mockMRPRun],
            total: 1,
            page: 1,
            page_size: 20,
          }),
        });
      }

      // Production Orders
      if (url.includes("/manufacturing/production-orders")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [mockProductionOrder],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      // Fallback
      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ items: [], total: 0 }),
      });
    });
  });

  it("renders ManufacturingOverviewPage without crashing", async () => {
    renderWithProviders(<ManufacturingOverviewPage />);
    expect(screen.getByText(/Manufacturing Control Hub/i)).toBeInTheDocument();
  });

  it("renders BillsOfMaterialsPage and displays active BOMs", async () => {
    renderWithProviders(<BillsOfMaterialsPage />);
    expect(screen.getByText(/Bills of Materials/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("BOM-SERVER-X1")[0]).toBeInTheDocument();
    });
  });

  it("renders RoutingsPage and displays routing operations", async () => {
    renderWithProviders(<RoutingsPage />);
    expect(screen.getByText(/Manufacturing Routings/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("RT-SERVER-X1")[0]).toBeInTheDocument();
    });
  });

  it("renders WorkCentersPage with work center capacities and rates", async () => {
    renderWithProviders(<WorkCentersPage />);
    expect(screen.getByText(/Work Centers & Machinery/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("WC-ASSY-01")).toBeInTheDocument();
    });
  });

  it("renders ProductionOrdersPage with order states", async () => {
    renderWithProviders(<ProductionOrdersPage />);
    expect(screen.getAllByText(/Production Orders/i)[0]).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("MO-2026-0001")).toBeInTheDocument();
    });
  });

  it("renders WorkOrdersPage with shop floor operations", async () => {
    renderWithProviders(<WorkOrdersPage />);
    expect(screen.getByText(/Shop-Floor Work Orders/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Mounting & Wiring")).toBeInTheDocument();
    });
  });

  it("renders MaterialConsumptionPage with ledger transactions", async () => {
    renderWithProviders(<MaterialConsumptionPage />);
    expect(screen.getByText(/Production Inventory Ledger/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("p-cpu-01")).toBeInTheDocument();
    });
  });

  it("renders MRPEnginePage with gross-to-net requirements and run history", async () => {
    renderWithProviders(<MRPEnginePage />);
    expect(screen.getByText(/Material Requirements Planning \(MRP\)/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getAllByText("MRP-20260908-01")[0]).toBeInTheDocument();
    });
  });

  it("renders QualityInspectionsPage with QC pass rates and inspection logs", async () => {
    renderWithProviders(<QualityInspectionsPage />);
    expect(screen.getByText(/Quality Inspections & Audits/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("QC-2026-0001")).toBeInTheDocument();
    });
  });
});
