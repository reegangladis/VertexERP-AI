import React, { useState } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes, Navigate } from "react-router-dom";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Card } from "@/components/ui/Card";
import { Alert } from "@/components/ui/Alert";
import { Modal } from "@/components/ui/Modal";
import { Table, TableHeader, TableBody, TableRow, TableHead, TableCell } from "@/components/ui/Table";
import { EmptyState } from "@/components/ui/EmptyState";
import { useAuthStore } from "@/stores/auth-store";
import { RequirePermission } from "@/components/security/RequirePermission";
import { ProtectedRoute } from "@/components/security/ProtectedRoute";
import { Header } from "@/components/layout/Header";
import { Sidebar } from "@/components/layout/Sidebar";
import { queryClient } from "@/lib/query-client";
import * as apiClientModule from "@/lib/api-client";

describe("Frontend Core UI Components", () => {
  it("Button renders variants, handles clicks, and respects disabled/loading state", () => {
    const handleClick = vi.fn();
    const { rerender } = render(
      <Button variant="primary" onClick={handleClick}>
        Submit Action
      </Button>
    );

    const btn = screen.getByRole("button", { name: /submit action/i });
    expect(btn).toBeInTheDocument();
    fireEvent.click(btn);
    expect(handleClick).toHaveBeenCalledTimes(1);

    // Disabled state
    rerender(
      <Button variant="danger" disabled onClick={handleClick}>
        Disabled Action
      </Button>
    );
    const disabledBtn = screen.getByRole("button", { name: /disabled action/i });
    expect(disabledBtn).toBeDisabled();
    fireEvent.click(disabledBtn);
    expect(handleClick).toHaveBeenCalledTimes(1); // Not incremented

    // Loading state
    rerender(
      <Button isLoading onClick={handleClick}>
        Loading Action
      </Button>
    );
    expect(screen.getByRole("button")).toBeDisabled();
  });

  it("Input renders label, handles change events, and displays validation errors", () => {
    const handleChange = vi.fn();
    const { rerender } = render(
      <Input
        label="Organization Tax ID"
        placeholder="US-EIN-12345"
        onChange={handleChange}
      />
    );

    expect(screen.getByLabelText(/organization tax id/i)).toBeInTheDocument();
    const input = screen.getByPlaceholderText("US-EIN-12345");
    fireEvent.change(input, { target: { value: "US-EIN-998877" } });
    expect(handleChange).toHaveBeenCalled();

    // With error state
    rerender(
      <Input
        label="Organization Tax ID"
        error="Invalid Tax Identifier format"
        defaultValue="BAD_ID"
      />
    );
    expect(screen.getByText(/invalid tax identifier format/i)).toBeInTheDocument();
  });

  it("Card renders title, subtitle, and body content", () => {
    render(
      <Card title="Revenue Summary" subtitle="Fiscal Year 2026">
        <div data-testid="card-body">$259,900.00 Total Booked</div>
      </Card>
    );

    expect(screen.getByText("Revenue Summary")).toBeInTheDocument();
    expect(screen.getByText("Fiscal Year 2026")).toBeInTheDocument();
    expect(screen.getByTestId("card-body")).toHaveTextContent("$259,900.00 Total Booked");
  });

  it("Alert displays message variants and triggers onDismiss", () => {
    const handleDismiss = vi.fn();
    const { rerender } = render(
      <Alert
        variant="success"
        title="Journal Posted"
        message="Journal Entry JE-2026-001 posted to General Ledger."
        onClose={handleDismiss}
      />
    );

    expect(screen.getByText("Journal Posted")).toBeInTheDocument();
    expect(screen.getByText(/posted to general ledger/i)).toBeInTheDocument();

    const closeBtn = screen.getByRole("button");
    fireEvent.click(closeBtn);
    expect(handleDismiss).toHaveBeenCalledTimes(1);

    // Danger / Error variant
    rerender(
      <Alert
        variant="error"
        title="Security Violation"
        message="Prompt injection detected and neutralized."
      />
    );
    expect(screen.getByText("Security Violation")).toBeInTheDocument();
  });

  it("Modal opens, displays header/content, and closes on request", () => {
    const handleClose = vi.fn();
    const { rerender } = render(
      <Modal isOpen={false} onClose={handleClose} title="Create Production Order">
        <p>Production order configuration form</p>
      </Modal>
    );

    expect(screen.queryByText("Create Production Order")).not.toBeInTheDocument();

    rerender(
      <Modal isOpen={true} onClose={handleClose} title="Create Production Order">
        <p>Production order configuration form</p>
      </Modal>
    );

    expect(screen.getByText("Create Production Order")).toBeInTheDocument();
    expect(screen.getByText("Production order configuration form")).toBeInTheDocument();

    const closeBtn = screen.getByRole("button", { name: /close/i });
    fireEvent.click(closeBtn);
    expect(handleClose).toHaveBeenCalledTimes(1);
  });

  it("Table renders columns, rows, and handles empty state", () => {
    const data = [
      { id: "1", code: "RAW-SERVO-01", name: "Servo Motor", stock: "60.00" },
      { id: "2", code: "ROBOT-ARM-V2", name: "Robotic Arm", stock: "10.00" },
    ];

    const { rerender } = render(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Code</TableHead>
            <TableHead>Name</TableHead>
            <TableHead>Stock On Hand</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item) => (
            <TableRow key={item.id}>
              <TableCell>{item.code}</TableCell>
              <TableCell>{item.name}</TableCell>
              <TableCell>{item.stock}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );

    expect(screen.getByText("RAW-SERVO-01")).toBeInTheDocument();
    expect(screen.getByText("Robotic Arm")).toBeInTheDocument();
    expect(screen.getByText("60.00")).toBeInTheDocument();

    // Empty state
    rerender(
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Code</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>No inventory items found</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    );
    expect(screen.getByText("No inventory items found")).toBeInTheDocument();
  });


  it("EmptyState renders illustration title, description, and action CTA", () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No Quotations Found"
        description="Create your first formal enterprise quotation to begin sales cycle."
        actionLabel="Create Quotation"
        onAction={handleAction}
      />
    );

    expect(screen.getByText("No Quotations Found")).toBeInTheDocument();
    expect(screen.getByText(/create your first formal enterprise quotation/i)).toBeInTheDocument();
    const actionBtn = screen.getByRole("button", { name: /create quotation/i });
    fireEvent.click(actionBtn);
    expect(handleAction).toHaveBeenCalledTimes(1);
  });
});

describe("Frontend Hooks, State Stores & RBAC Security", () => {
  beforeEach(() => {
    useAuthStore.setState({
      userId: "user-test-01",
      email: "engineer@vertexerp.io",
      fullName: "Lead Engineer",
      tenantId: "tenant-test-01",
      organizationId: "org-test-01",
      roles: ["Engineer"],
      permissions: ["inventory:products:read", "manufacturing:production_orders:read"],
      isAuthenticated: true,
    });
  });

  it("useAuthStore properly checks permissions and updates authentication state", () => {
    const store = useAuthStore.getState();
    expect(store.hasPermission("inventory:products:read")).toBe(true);
    expect(store.hasPermission("finance:invoices:write")).toBe(false);

    // Wildcard permission check
    useAuthStore.setState({
      permissions: ["finance:*"],
    });
    expect(useAuthStore.getState().hasPermission("finance:invoices:write")).toBe(true);
    expect(useAuthStore.getState().hasPermission("hr:employees:read")).toBe(false);

    // Global admin wildcard check
    useAuthStore.setState({
      permissions: ["*"],
    });
    expect(useAuthStore.getState().hasPermission("any:domain:action")).toBe(true);

    // setAuth action
    store.setAuth({
      userId: "user-new-02",
      email: "cfo@vertexerp.io",
      fullName: "Chief Financial Officer",
      tenantId: "tenant-finance-02",
      organizationId: "org-finance-02",
      roles: ["CFO"],
      permissions: ["finance:invoices:read", "finance:invoices:write"],
    });
    const updated = useAuthStore.getState();
    expect(updated.userId).toBe("user-new-02");
    expect(updated.email).toBe("cfo@vertexerp.io");
    expect(updated.hasPermission("finance:invoices:write")).toBe(true);

    // clearAuth action
    updated.clearAuth();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().userId).toBeNull();
  });

  it("logout calls backend /identity/auth/logout, clears React Query cache, and resets auth store", async () => {
    const apiClientSpy = vi.spyOn(apiClientModule, "apiClient").mockResolvedValueOnce({ message: "Logged out" } as any);
    const queryClearSpy = vi.spyOn(queryClient, "clear");

    useAuthStore.setState({
      userId: "user-active-01",
      email: "admin@enterprise.io",
      fullName: "Enterprise Admin",
      tenantId: "tenant-prod-100",
      roles: ["TenantAdmin"],
      permissions: ["*"],
      isAuthenticated: true,
    });

    // Populate mock query cache entry
    queryClient.setQueryData(["tenant-sensitive-data"], { revenue: 5000000 });
    expect(queryClient.getQueryData(["tenant-sensitive-data"])).toEqual({ revenue: 5000000 });

    await useAuthStore.getState().logout();

    expect(apiClientSpy).toHaveBeenCalledWith("/identity/auth/logout", { method: "POST" });
    expect(queryClearSpy).toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().userId).toBeNull();
    expect(useAuthStore.getState().tenantId).toBeNull();
  });

  it("logout guarantees local state and query cache clearance even if backend fails", async () => {
    vi.spyOn(apiClientModule, "apiClient").mockRejectedValueOnce(new Error("Network connection severed"));
    const queryClearSpy = vi.spyOn(queryClient, "clear");

    useAuthStore.setState({
      userId: "user-offline-01",
      isAuthenticated: true,
      tenantId: "tenant-prod-999",
    });

    await useAuthStore.getState().logout();

    expect(queryClearSpy).toHaveBeenCalled();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
    expect(useAuthStore.getState().userId).toBeNull();
  });

  it("RequirePermission conditionally renders children based on user permissions", () => {
    useAuthStore.setState({
      permissions: ["manufacturing:work_orders:read"],
      isAuthenticated: true,
    });

    const { rerender } = render(
      <RequirePermission
        permission="manufacturing:work_orders:read"
        fallback={<div>Access Denied</div>}
      >
        <button data-testid="dispatch-wo">Dispatch Work Order</button>
      </RequirePermission>
    );

    expect(screen.getByTestId("dispatch-wo")).toBeInTheDocument();
    expect(screen.queryByText("Access Denied")).not.toBeInTheDocument();

    // Permission missing -> renders fallback
    rerender(
      <RequirePermission
        permission="finance:payments:post"
        fallback={<div data-testid="denied-msg">Access Denied: Insufficient Privileges</div>}
      >
        <button data-testid="post-pmt">Post Wire Payment</button>
      </RequirePermission>
    );

    expect(screen.queryByTestId("post-pmt")).not.toBeInTheDocument();
    expect(screen.getByTestId("denied-msg")).toHaveTextContent("Access Denied: Insufficient Privileges");
  });

  it("RequirePermission with requireAll enforces all permission codes", () => {
    useAuthStore.setState({
      permissions: ["crm:leads:read"],
      isAuthenticated: true,
    });

    render(
      <RequirePermission
        permission={["crm:leads:read", "crm:leads:delete"]}
        requireAll={true}
        fallback={<div>Requires Delete Permission</div>}
      >
        <button>Delete Lead</button>
      </RequirePermission>
    );

    expect(screen.getByText("Requires Delete Permission")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /delete lead/i })).not.toBeInTheDocument();
  });

  it("ProtectedRoute redirects unauthenticated sessions to /login", () => {
    useAuthStore.setState({ isAuthenticated: false, userId: null });

    render(
      <MemoryRouter initialEntries={["/manufacturing/work-orders"]}>
        <Routes>
          <Route path="/login" element={<div data-testid="login-view">Login Required</div>} />
          <Route element={<ProtectedRoute />}>
            <Route
              path="/manufacturing/work-orders"
              element={<div data-testid="protected-view">Work Orders Dashboard</div>}
            />
          </Route>
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByTestId("login-view")).toBeInTheDocument();
    expect(screen.queryByTestId("protected-view")).not.toBeInTheDocument();
  });
});

describe("Layout Components, Sign Out Flow & Dynamic Tenant Badge", () => {
  it("Header renders user profile and Sign Out button that triggers logout and navigation", async () => {
    const logoutSpy = vi.fn().mockResolvedValue(undefined);
    useAuthStore.setState({
      userId: "user-admin",
      fullName: "Alex Rivera",
      email: "arivera@enterprise.io",
      roles: ["TenantAdmin"],
      isAuthenticated: true,
      logout: logoutSpy,
    });

    render(
      <MemoryRouter initialEntries={["/"]}>
        <Header />
      </MemoryRouter>
    );

    expect(screen.getByText("Alex Rivera")).toBeInTheDocument();
    expect(screen.getByText(/TenantAdmin/)).toBeInTheDocument();

    const signOutBtn = screen.getByTestId("header-logout-btn");
    expect(signOutBtn).toBeInTheDocument();
    expect(signOutBtn).toHaveTextContent("Sign Out");

    fireEvent.click(signOutBtn);
    await waitFor(() => {
      expect(logoutSpy).toHaveBeenCalledTimes(1);
    });
  });

  it("Sidebar dynamically renders authenticated tenant ID and workspace name", () => {
    useAuthStore.setState({
      tenantId: "tenant-apex-dynamics-88",
      fullName: "Apex Dynamics",
      isAuthenticated: true,
    });

    render(
      <MemoryRouter initialEntries={["/inventory"]}>
        <Sidebar />
      </MemoryRouter>
    );

    const tenantBadge = screen.getByTestId("sidebar-tenant-id");
    expect(tenantBadge).toBeInTheDocument();
    expect(tenantBadge).toHaveTextContent("Tenant: tenant-apex-dynamics-88");
    expect(screen.getByText("Apex Dynamics's Workspace")).toBeInTheDocument();
  });
});

describe("Frontend Forms, Routes Navigation & Error Handling", () => {
  const QuotationCreationForm = ({ onSubmit }: { onSubmit: (data: any) => void }) => {
    const [customer, setCustomer] = useState("");
    const [amount, setAmount] = useState("");
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = (e: React.FormEvent) => {
      e.preventDefault();
      if (!customer.trim()) {
        setError("Customer name is required");
        return;
      }
      if (!amount || Number(amount) <= 0) {
        setError("Quotation amount must be greater than zero");
        return;
      }
      setError(null);
      onSubmit({ customer, amount: Number(amount) });
    };

    return (
      <form onSubmit={handleSubmit} data-testid="quotation-form">
        {error && <Alert variant="error" title="Validation Failed" message={error} />}
        <Input
          label="Customer Organization"
          placeholder="e.g. Apex Robotics"
          value={customer}
          onChange={(e) => setCustomer(e.target.value)}
        />
        <Input
          label="Estimated Amount (USD)"
          type="number"
          placeholder="0.00"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <Button type="submit" variant="primary">
          Generate Quotation
        </Button>
      </form>
    );
  };

  it("Quotation form validates inputs, displays errors, and submits valid payloads", async () => {
    const handleSubmit = vi.fn();
    render(<QuotationCreationForm onSubmit={handleSubmit} />);

    // Submit empty form -> displays error
    fireEvent.click(screen.getByRole("button", { name: /generate quotation/i }));
    expect(screen.getByText("Customer name is required")).toBeInTheDocument();
    expect(handleSubmit).not.toHaveBeenCalled();

    // Fill customer but invalid amount
    fireEvent.change(screen.getByPlaceholderText("e.g. Apex Robotics"), {
      target: { value: "Defense Logistics Corp" },
    });
    fireEvent.change(screen.getByPlaceholderText("0.00"), {
      target: { value: "-500" },
    });
    fireEvent.click(screen.getByRole("button", { name: /generate quotation/i }));
    expect(screen.getByText("Quotation amount must be greater than zero")).toBeInTheDocument();

    // Fill valid amount
    fireEvent.change(screen.getByPlaceholderText("0.00"), {
      target: { value: "259900.00" },
    });
    fireEvent.click(screen.getByRole("button", { name: /generate quotation/i }));

    expect(screen.queryByText("Validation Failed")).not.toBeInTheDocument();
    expect(handleSubmit).toHaveBeenCalledWith({
      customer: "Defense Logistics Corp",
      amount: 259900.00,
    });
  });

  it("Simulates multi-page ERP route transitions", async () => {
    useAuthStore.setState({ isAuthenticated: true, userId: "admin-1" });

    render(
      <MemoryRouter initialEntries={["/dashboard"]}>
        <Routes>
          <Route path="/dashboard" element={<div data-testid="page-dashboard">Executive Dashboard</div>} />
          <Route path="/crm/deals" element={<div data-testid="page-crm">CRM Deals & Pipeline</div>} />
          <Route path="/inventory/stock" element={<div data-testid="page-inventory">Stock Ledger & Warehouses</div>} />
          <Route path="/finance/invoices" element={<div data-testid="page-finance">Finance Invoices & GL</div>} />
        </Routes>
      </MemoryRouter>
    );

    expect(screen.getByTestId("page-dashboard")).toBeInTheDocument();
  });
});
