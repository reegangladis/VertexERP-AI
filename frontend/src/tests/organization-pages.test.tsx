import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { OrganizationOverviewPage } from "@/features/organization/pages/OrganizationOverviewPage";
import { BranchesPage } from "@/features/organization/pages/BranchesPage";
import { DepartmentsPage } from "@/features/organization/pages/DepartmentsPage";
import { TeamsPage } from "@/features/organization/pages/TeamsPage";
import { DesignationsPage } from "@/features/organization/pages/DesignationsPage";
import { CostCentersPage } from "@/features/organization/pages/CostCentersPage";
import { CalendarsPage } from "@/features/organization/pages/CalendarsPage";
import { RequirePermission } from "@/components/security/RequirePermission";
import { useAuthStore } from "@/stores/auth-store";

// Helper wrapper
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

describe("Organization Domain Frontend Component Tests", () => {
  beforeEach(() => {
    // Reset auth store
    useAuthStore.getState().setAuth({
      userId: "u-admin",
      email: "admin@erp.io",
      fullName: "Admin User",
      tenantId: "t-001",
      organizationId: "org-001",
      roles: ["TenantAdmin"],
      permissions: [
        "organization:organizations:read",
        "organization:branches:read",
        "organization:branches:write",
        "organization:departments:read",
        "organization:departments:write",
        "organization:teams:read",
        "organization:teams:write",
        "organization:designations:read",
        "organization:designations:write",
        "organization:cost_centers:read",
        "organization:cost_centers:write",
        "organization:locations:read",
        "organization:locations:write",
        "organization:calendars:read",
        "organization:calendars:write",
        "organization:holidays:read",
        "organization:holidays:write",
      ],
    });

    // Mock global fetch
    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("/branches/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "b-1",
                code: "BR-NYC",
                name: "New York HQ",
                city: "New York",
                state: "NY",
                country: "USA",
                is_headquarters: true,
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/departments/tree")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "d-1",
                code: "ENG",
                name: "Engineering",
                is_active: true,
                children: [
                  {
                    id: "d-2",
                    code: "FE",
                    name: "Frontend",
                    is_active: true,
                    children: [],
                  },
                ],
              },
            ]),
        });
      }
      if (url.includes("/departments/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "d-1",
                code: "ENG",
                name: "Engineering",
                description: "Core R&D",
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/teams/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "t-1",
                code: "CORE-AI",
                name: "Core AI Squad",
                description: "LLM backend",
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/designations/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "des-1",
                code: "SE-1",
                name: "Software Engineer I",
                level: 2,
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/cost-centers/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "cc-1",
                code: "CC-RD",
                name: "R&D Cloud Center",
                annual_budget: 500000,
                currency: "USD",
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/calendars/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "cal-1",
                code: "CAL-STD",
                name: "Standard 40hr Work Schedule",
                time_zone: "America/New_York",
                is_default: true,
                standard_hours_per_day: 8,
                is_active: true,
                working_days: [],
              },
            ]),
        });
      }
      if (url.includes("/holidays/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "h-1",
                name: "New Year's Day",
                holiday_date: "2026-01-01",
                holiday_type: "NATIONAL",
                is_recurring: true,
              },
            ]),
        });
      }
      return Promise.resolve({
        ok: true,
        status: 200,
        json: () => Promise.resolve([]),
      });
    }) as any;
  });

  it("renders OrganizationOverviewPage with all entity cards", async () => {
    renderWithProviders(<OrganizationOverviewPage />);

    expect(screen.getByText("Organization Domain Hub")).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText("Branches")).toBeInTheDocument();
      expect(screen.getByText("Departments")).toBeInTheDocument();
      expect(screen.getByText("Teams")).toBeInTheDocument();
      expect(screen.getByText("Designations")).toBeInTheDocument();
      expect(screen.getByText("Cost Centers")).toBeInTheDocument();
      expect(screen.getByText("Locations")).toBeInTheDocument();
      expect(screen.getByText("Work Calendars")).toBeInTheDocument();
      expect(screen.getByText("Holidays")).toBeInTheDocument();
    });
  });

  it("renders BranchesPage with data table and opens create modal", async () => {
    renderWithProviders(<BranchesPage />);

    expect(screen.getByText(/Physical Branches/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("BR-NYC")).toBeInTheDocument();
      expect(screen.getByText("New York HQ")).toBeInTheDocument();
    });

    const addBtn = screen.getByRole("button", { name: /Add Branch/i });
    fireEvent.click(addBtn);

    expect(screen.getByText("Add Physical Branch")).toBeInTheDocument();
    expect(screen.getByPlaceholderText("e.g. BR-NYC")).toBeInTheDocument();
  });

  it("renders DepartmentsPage and toggles between Table and Hierarchy Tree views", async () => {
    renderWithProviders(<DepartmentsPage />);

    expect(screen.getByText(/Functional Departments/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("ENG")).toBeInTheDocument();
      expect(screen.getByText("Engineering")).toBeInTheDocument();
    });

    const treeToggle = screen.getByRole("button", { name: /Hierarchy Tree/i });
    fireEvent.click(treeToggle);

    await waitFor(() => {
      expect(screen.getByText("Frontend")).toBeInTheDocument();
    });
  });

  it("renders TeamsPage and displays agile squad records", async () => {
    renderWithProviders(<TeamsPage />);

    expect(screen.getByText(/Teams & Pods/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("CORE-AI")).toBeInTheDocument();
      expect(screen.getByText("Core AI Squad")).toBeInTheDocument();
    });
  });

  it("renders CostCentersPage and formats currency budget allocations", async () => {
    renderWithProviders(<CostCentersPage />);

    expect(screen.getByText(/Cost Centers & Budgets/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("CC-RD")).toBeInTheDocument();
      expect(screen.getByText("$500,000.00")).toBeInTheDocument();
    });
  });

  it("verifies RequirePermission hides protected elements for unauthorized users", () => {
    // Switch to restricted user with NO write permissions
    useAuthStore.getState().setAuth({
      userId: "u-restricted",
      email: "viewer@erp.io",
      fullName: "Viewer User",
      tenantId: "t-001",
      organizationId: "org-001",
      roles: ["StandardUser"],
      permissions: ["organization:branches:read"],
    });

    renderWithProviders(
      <div>
        <RequirePermission permission="organization:branches:read">
          <div>READ_ALLOWED</div>
        </RequirePermission>
        <RequirePermission
          permission="organization:branches:write"
          fallback={<div>WRITE_DENIED</div>}
        >
          <div>WRITE_ALLOWED</div>
        </RequirePermission>
      </div>
    );

    expect(screen.getByText("READ_ALLOWED")).toBeInTheDocument();
    expect(screen.getByText("WRITE_DENIED")).toBeInTheDocument();
    expect(screen.queryByText("WRITE_ALLOWED")).not.toBeInTheDocument();
  });
});
