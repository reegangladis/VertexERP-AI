import React from "react";
import { describe, it, expect, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { demoStore } from "@/lib/demo-store";
import { useAuthStore } from "@/stores/auth-store";
import { ApplyLeavePage } from "@/features/ess/pages/ApplyLeavePage";
import { LeaveManagementPage } from "@/features/hr/pages/LeaveManagementPage";

function wrap(ui: React.ReactElement) {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("End-to-End Employee Apply Leave -> Manager Approval Workflow", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it("populates rich demo data for all 9 Organization categories in demoStore", () => {
    const state = demoStore.getState();
    expect(state.branches.length).toBeGreaterThanOrEqual(5);
    expect(state.departments.length).toBeGreaterThanOrEqual(6);
    expect(state.teams.length).toBeGreaterThanOrEqual(5);
    expect(state.designations.length).toBeGreaterThanOrEqual(8);
    expect(state.businessUnits.length).toBeGreaterThanOrEqual(4);
    expect(state.costCenters.length).toBeGreaterThanOrEqual(5);
    expect(state.locations.length).toBeGreaterThanOrEqual(5);
    expect(state.calendars.length).toBeGreaterThanOrEqual(3);
    expect(state.holidays.length).toBeGreaterThanOrEqual(10);
  });

  it("synchronizes Employee leave submission with Manager approval queue and updates leave balance", async () => {
    // 1. Logged in as Employee Alex Morgan
    useAuthStore.getState().setAuth({
      userId: "9d6bcc63-5acf-471e-afac-18d4b7386ee6",
      email: "employee@vertexerp.com",
      fullName: "Alex Morgan",
      tenantId: "tenant_apex",
      organizationId: "org_apex_hq",
      roles: ["EMPLOYEE"],
      permissions: ["hr:leaves:read", "hr:leaves:write"],
    });

    const initialCasual = demoStore.getState().leaveBalances.find((b) => b.code === "CL")!;
    const startingBalance = initialCasual.balance;

    // 2. Employee applies for 2 days of Casual Leave
    const createdReq = demoStore.applyLeave({
      employeeId: "9d6bcc63-5acf-471e-afac-18d4b7386ee6",
      employeeName: "Alex Morgan",
      employeeEmail: "employee@vertexerp.com",
      leaveTypeCode: "CL",
      startDate: "2026-12-21",
      endDate: "2026-12-22",
      totalDays: 2,
      reason: "Year-end family trip to Vermont",
    });

    expect(createdReq.status).toBe("SUBMITTED");
    expect(demoStore.getState().leaveRequests[0].reason).toBe("Year-end family trip to Vermont");

    // Verify ApplyLeavePage displays the new request
    wrap(<ApplyLeavePage />);
    expect(screen.getByText("Year-end family trip to Vermont")).toBeInTheDocument();

    // 3. Switch persona to HR Manager Eleanor Vance and verify LeaveManagementPage renders it with Approve CTA
    useAuthStore.getState().setAuth({
      userId: "ff1e3c98-181a-4f97-a217-caabf7aa3342",
      email: "hr@vertexerp.com",
      fullName: "Eleanor Vance",
      tenantId: "tenant_apex",
      organizationId: "org_apex_hq",
      roles: ["HR_MANAGER"],
      permissions: ["hr:leaves:read", "hr:leaves:approve"],
    });

    wrap(<LeaveManagementPage />);
    const approveButtons = await screen.findAllByRole("button", { name: /approve/i });
    expect(approveButtons.length).toBeGreaterThanOrEqual(1);

    // 4. Manager approves the submitted leave via demoStore
    const approved = demoStore.reviewLeave({
      requestId: createdReq.id,
      action: "APPROVE",
      reviewerName: "Eleanor Vance",
      remarks: "Approved for year-end break.",
    });

    expect(approved?.status).toBe("APPROVED");
    const updatedCasual = demoStore.getState().leaveBalances.find((b) => b.code === "CL")!;
    expect(updatedCasual.balance).toBe(startingBalance - 2);
  });
});
