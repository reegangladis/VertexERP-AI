import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { InventoryOverviewPage } from "@/features/inventory/pages/InventoryOverviewPage";
import { ProductsPage } from "@/features/inventory/pages/ProductsPage";
import { WarehousesPage } from "@/features/inventory/pages/WarehousesPage";
import { StockBalancesPage } from "@/features/inventory/pages/StockBalancesPage";
import { StockLedgerPage } from "@/features/inventory/pages/StockLedgerPage";
import { StockTransfersPage } from "@/features/inventory/pages/StockTransfersPage";
import { StockAdjustmentsPage } from "@/features/inventory/pages/StockAdjustmentsPage";
import { GoodsReceiptsPage } from "@/features/inventory/pages/GoodsReceiptsPage";
import { ProcurementOverviewPage } from "@/features/procurement/pages/ProcurementOverviewPage";
import { SuppliersPage } from "@/features/procurement/pages/SuppliersPage";
import { PurchaseRequestsPage } from "@/features/procurement/pages/PurchaseRequestsPage";
import { PurchaseOrdersPage } from "@/features/procurement/pages/PurchaseOrdersPage";
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

describe("Inventory & Procurement Domain Frontend Pages", () => {
  beforeEach(() => {
    useAuthStore.getState().setAuth({
      userId: "u-inv-admin",
      email: "inv.admin@vertexerp.io",
      fullName: "Inventory Officer",
      tenantId: "t-001",
      organizationId: "org-001",
      roles: ["InventoryManager", "ProcurementOfficer"],
      permissions: [
        "inventory:products:read",
        "inventory:products:write",
        "inventory:warehouses:read",
        "inventory:warehouses:write",
        "inventory:ledger:read",
        "inventory:transfers:read",
        "inventory:adjustments:read",
        "inventory:receipts:read",
        "procurement:suppliers:read",
        "procurement:requests:read",
        "procurement:orders:read",
      ],
    });

    global.fetch = vi.fn().mockImplementation((url: string) => {
      // Inventory endpoints
      if (url.includes("/inventory/products")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "prod-1",
                sku: "PROD-TEST-100",
                name: "High Precision Sensor",
                product_type: "STORABLE",
                cost_method: "AVERAGE",
                average_cost: 45.5,
                list_price: 99.0,
                allow_negative_stock: false,
                is_active: true,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/warehouses")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "wh-1",
                code: "WH-MAIN",
                name: "Main Distribution Center",
                warehouse_type: "STANDARD",
                is_primary: true,
                is_active: true,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/ledger/balances") || url.includes("/inventory/balances")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "bal-1",
                product_id: "prod-1",
                product_name: "High Precision Sensor",
                product_sku: "PROD-TEST-100",
                warehouse_id: "wh-1",
                warehouse_name: "Main Distribution Center",
                quantity_on_hand: 500,
                quantity_reserved: 50,
                quantity_available: 450,
                quantity_on_order: 100,
                average_cost: 45.5,
                total_value: 22750.0,
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/ledger/movements") || url.includes("/inventory/movements")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "mov-1",
                product_id: "prod-1",
                product_name: "High Precision Sensor",
                warehouse_id: "wh-1",
                warehouse_name: "Main Distribution Center",
                movement_type: "RECEIPT",
                quantity: 100,
                unit_cost: 45.5,
                total_cost: 4550.0,
                quantity_before: 400,
                quantity_after: 500,
                reference_type: "PURCHASE_ORDER",
                reference_id: "po-100",
                created_at: new Date().toISOString(),
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/transfers")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "tr-1",
                transfer_number: "TR-2026-0001",
                source_warehouse_id: "wh-1",
                destination_warehouse_id: "wh-2",
                status: "IN_TRANSIT",
                tracking_number: "TRK-98765",
                items: [{ product_id: "prod-1", requested_quantity: 50 }],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/adjustments")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "adj-1",
                adjustment_number: "ADJ-2026-0001",
                warehouse_id: "wh-1",
                reason: "PHYSICAL_COUNT",
                status: "SUBMITTED",
                items: [
                  {
                    product_id: "prod-1",
                    system_quantity: 500,
                    counted_quantity: 498,
                    variance_quantity: -2,
                  },
                ],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/receipts")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "grn-1",
                grn_number: "GRN-2026-0001",
                warehouse_id: "wh-1",
                status: "POSTED",
                received_date: "2026-09-07",
                vendor_delivery_note: "DN-1001",
                items: [{ product_id: "prod-1", quantity_received: 100, unit_cost: 45.5 }],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/inventory/uom")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [{ id: "uom-1", code: "PCS", name: "Pieces", symbol: "pcs" }],
            total: 1,
          }),
        });
      }

      if (url.includes("/inventory/categories")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [{ id: "cat-1", code: "ELEC", name: "Electronics" }],
            total: 1,
          }),
        });
      }

      // Procurement endpoints
      if (url.includes("/procurement/suppliers")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "sup-1",
                code: "SUPP-001",
                name: "Apex Component Suppliers",
                email: "sales@apex.io",
                currency: "USD",
                payment_terms_days: 30,
                rating: 5,
                status: "ACTIVE",
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/procurement/requests")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "pr-1",
                request_number: "PR-2026-0001",
                priority: "HIGH",
                reason: "Q3 Manufacturing Line Expansion",
                status: "SUBMITTED",
                items: [{ product_id: "prod-1", quantity: 50, estimated_total_cost: 2275.0 }],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      if (url.includes("/procurement/orders")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            items: [
              {
                id: "po-1",
                order_number: "PO-2026-0001",
                supplier_id: "sup-1",
                warehouse_id: "wh-1",
                subtotal_amount: 4550.0,
                tax_amount: 455.0,
                total_amount: 5005.0,
                status: "ISSUED",
                order_date: "2026-09-07",
                items: [{ product_id: "prod-1", quantity_ordered: 100, unit_price: 45.5 }],
              },
            ],
            total: 1,
            page: 1,
            page_size: 50,
          }),
        });
      }

      return Promise.resolve({
        ok: true,
        status: 200,
        json: async () => ({ items: [], total: 0 }),
      });
    });
  });

  it("renders InventoryOverviewPage with ledger KPIs and quick actions", async () => {
    renderWithProviders(<InventoryOverviewPage />);
    expect(screen.getByText("Inventory Management & Stock Ledger")).toBeInTheDocument();
    expect(screen.getByText("Double-Entry Ledger")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Stock Valuation")).toBeInTheDocument();
      expect(screen.getByText("Products & SKUs")).toBeInTheDocument();
    });
  });

  it("renders ProductsPage with SKU catalog table and modal button", async () => {
    renderWithProviders(<ProductsPage />);
    expect(screen.getByText("Products & Master SKU Catalog")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("High Precision Sensor")).toBeInTheDocument();
      expect(screen.getByText("PROD-TEST-100")).toBeInTheDocument();
    });

    const createBtn = screen.getByText("Create Product");
    fireEvent.click(createBtn);
    expect(screen.getByText("Add New Product / SKU")).toBeInTheDocument();
  });

  it("renders WarehousesPage with facility listing", async () => {
    renderWithProviders(<WarehousesPage />);
    expect(screen.getByText("Warehouses & Location Bins")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText("Main Distribution Center").length).toBeGreaterThan(0);
      expect(screen.getAllByText("WH-MAIN").length).toBeGreaterThan(0);
    });
  });

  it("renders StockBalancesPage with on-hand and available metrics", async () => {
    renderWithProviders(<StockBalancesPage />);
    expect(screen.getByText("Stock Balances & Real-Time Availability")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Total Inventory Valuation")).toBeInTheDocument();
      expect(screen.getByText("High Precision Sensor")).toBeInTheDocument();
    });
  });

  it("renders StockLedgerPage with immutable audit movements", async () => {
    renderWithProviders(<StockLedgerPage />);
    expect(screen.getByText("Immutable Stock Movement Ledger")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getAllByText("RECEIPT").length).toBeGreaterThan(0);
      expect(screen.getByText("+100")).toBeInTheDocument();
    });
  });

  it("renders StockTransfersPage with in-transit workflow", async () => {
    renderWithProviders(<StockTransfersPage />);
    expect(screen.getByText("Inter-Warehouse Stock Transfers")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("TR-2026-0001")).toBeInTheDocument();
      expect(screen.getAllByText("IN_TRANSIT").length).toBeGreaterThan(0);
    });
  });

  it("renders StockAdjustmentsPage with variance items and actions", async () => {
    renderWithProviders(<StockAdjustmentsPage />);
    expect(screen.getByText("Stock Adjustments & Variance Reconciliation")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("ADJ-2026-0001")).toBeInTheDocument();
      expect(screen.getAllByText("SUBMITTED").length).toBeGreaterThan(0);
    });
  });

  it("renders GoodsReceiptsPage with GRN listing", async () => {
    renderWithProviders(<GoodsReceiptsPage />);
    expect(screen.getByText("Goods Receipt Notes (GRN)")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("GRN-2026-0001")).toBeInTheDocument();
      expect(screen.getAllByText("POSTED").length).toBeGreaterThan(0);
    });
  });

  it("renders ProcurementOverviewPage with vendor and PO statistics", async () => {
    renderWithProviders(<ProcurementOverviewPage />);
    expect(screen.getByText("Procurement & Vendor Management")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Active Vendors & Suppliers")).toBeInTheDocument();
      expect(screen.getByText("Open Purchase Orders")).toBeInTheDocument();
    });
  });

  it("renders SuppliersPage with vendor directory", async () => {
    renderWithProviders(<SuppliersPage />);
    expect(screen.getByText("Suppliers & Vendor Directory")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Apex Component Suppliers")).toBeInTheDocument();
      expect(screen.getByText("SUPP-001")).toBeInTheDocument();
    });
  });

  it("renders PurchaseRequestsPage with requisition lines", async () => {
    renderWithProviders(<PurchaseRequestsPage />);
    expect(screen.getByText("Purchase Requests & Requisitions (PR)")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("PR-2026-0001")).toBeInTheDocument();
      expect(screen.getAllByText("HIGH").length).toBeGreaterThan(0);
    });
  });

  it("renders PurchaseOrdersPage with PO listing and lifecycle actions", async () => {
    renderWithProviders(<PurchaseOrdersPage />);
    expect(screen.getByText("Purchase Orders (PO)")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("PO-2026-0001")).toBeInTheDocument();
      expect(screen.getAllByText("ISSUED").length).toBeGreaterThan(0);
    });
  });
});
