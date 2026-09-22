import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { HROverviewPage } from "@/features/hr/pages/HROverviewPage";
import { EmployeesPage } from "@/features/hr/pages/EmployeesPage";
import { AttendancePage } from "@/features/hr/pages/AttendancePage";
import { LeaveManagementPage } from "@/features/hr/pages/LeaveManagementPage";
import { PayrollDashboardPage } from "@/features/hr/pages/PayrollDashboardPage";
import { RecruitmentPage } from "@/features/hr/pages/RecruitmentPage";
import { PerformancePage } from "@/features/hr/pages/PerformancePage";
import { LearningPage } from "@/features/hr/pages/LearningPage";
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

describe("Human Resources (HR) Domain Frontend Component Tests", () => {
  beforeEach(() => {
    // Set authenticated user with all HR permissions
    useAuthStore.getState().setAuth({
      userId: "u-hr-admin",
      email: "hr.admin@vertexerp.io",
      fullName: "HR Admin User",
      tenantId: "t-001",
      organizationId: "org-001",
      roles: ["HRManager", "PayrollOfficer"],
      permissions: [
        "hr:employees:read",
        "hr:employees:write",
        "hr:profiles:read",
        "hr:attendance:read",
        "hr:leaves:read",
        "hr:payroll:read",
        "hr:payroll:write",
        "hr:recruitment:read",
        "hr:performance:read",
        "hr:learning:read",
      ],
    });

    // Mock global fetch for HR endpoints
    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes("/employees/")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "emp-001",
                employee_number: "EMP-0001",
                first_name: "Sarah",
                last_name: "Connor",
                email: "sarah.connor@vertexerp.io",
                employment_type: "FULL_TIME",
                employment_status: "ACTIVE",
                hire_date: "2024-01-01",
              },
            ]),
        });
      }
      if (url.includes("/attendance/shifts")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "shift-001",
                code: "GEN-09-17",
                name: "General Day Shift",
                start_time: "09:00:00",
                end_time: "17:00:00",
                break_duration_minutes: 60,
                grace_period_minutes: 15,
                is_night_shift: false,
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/leaves/types")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "lt-001",
                code: "ANNUAL",
                name: "Annual Paid Leave",
                is_paid: true,
                is_encashable: false,
                max_consecutive_days: 30,
                color_code: "#3B82F6",
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/payroll/runs")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "run-001",
                run_number: "PR-0001",
                pay_period_start: "2024-05-01",
                pay_period_end: "2024-05-31",
                pay_date: "2024-06-01",
                total_gross: 10000.0,
                total_deductions: 1000.0,
                total_net: 9000.0,
                total_employees: 1,
                status: "DISBURSED",
                payment_method: "DIRECT_DEPOSIT",
                created_at: new Date().toISOString(),
              },
            ]),
        });
      }
      if (url.includes("/recruitment/requisitions")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "req-001",
                requisition_number: "REQ-0001",
                title: "Senior AI Backend Engineer",
                headcount: 2,
                employment_type: "FULL_TIME",
                experience_level: "SENIOR",
                salary_min: 120000.0,
                salary_max: 160000.0,
                status: "OPEN",
                created_at: new Date().toISOString(),
              },
            ]),
        });
      }
      if (url.includes("/performance/periods")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "p-001",
                code: "CY2024_H1",
                title: "H1 2024 Performance Appraisal Cycle",
                start_date: "2024-01-01",
                end_date: "2024-06-30",
                status: "ACTIVE",
                is_active: true,
              },
            ]),
        });
      }
      if (url.includes("/learning/courses")) {
        return Promise.resolve({
          ok: true,
          status: 200,
          json: () =>
            Promise.resolve([
              {
                id: "c-001",
                code: "SEC_101",
                title: "Enterprise Information Security & Compliance",
                category: "COMPLIANCE",
                duration_hours: 2.5,
                is_mandatory: true,
                is_active: true,
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

  it("renders HROverviewPage with executive KPI cards and fast actions", async () => {
    renderWithProviders(<HROverviewPage />);
    expect(screen.getByText("HR & Workforce Intelligence")).toBeInTheDocument();
    expect(screen.getByText("Total Headcount")).toBeInTheDocument();
    expect(screen.getByText("Attendance Rate")).toBeInTheDocument();
    expect(screen.getByText("Open Job Requisitions")).toBeInTheDocument();
    expect(screen.getByText("Active Payroll Batches")).toBeInTheDocument();
  });

  it("renders EmployeesPage and displays employee directory table", async () => {
    renderWithProviders(<EmployeesPage />);
    expect(screen.getByText("Employee Directory")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Sarah Connor")).toBeInTheDocument();
      expect(screen.getByText("EMP-0001")).toBeInTheDocument();
      expect(screen.getByText("sarah.connor@vertexerp.io")).toBeInTheDocument();
    });

    const addBtn = screen.getByRole("button", { name: /Add Employee/i });
    fireEvent.click(addBtn);
    expect(screen.getByText("Onboard New Employee")).toBeInTheDocument();
  });

  it("renders AttendancePage with virtual clock-in terminal", async () => {
    renderWithProviders(<AttendancePage />);
    expect(screen.getByText("Attendance & Time Tracking")).toBeInTheDocument();
    expect(screen.getByText("Live Virtual Terminal")).toBeInTheDocument();

    const clockBtn = screen.getByRole("button", { name: /Clock In Now/i });
    expect(clockBtn).toBeInTheDocument();
    fireEvent.click(clockBtn);

    expect(screen.getByText("Clock Out")).toBeInTheDocument();
  });

  it("renders LeaveManagementPage with quotas and balances", async () => {
    renderWithProviders(<LeaveManagementPage />);
    expect(screen.getByText("Leave Management & Entitlements")).toBeInTheDocument();
    expect(screen.getByText("Annual Paid Leave")).toBeInTheDocument();
    expect(screen.getByText("Sick & Medical Leave")).toBeInTheDocument();
  });

  it("renders PayrollDashboardPage with batch calculations", async () => {
    renderWithProviders(<PayrollDashboardPage />);
    expect(screen.getByText("Payroll Processing & Gross-to-Net Engine")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("PR-0001")).toBeInTheDocument();
      expect(screen.getByText("$10,000.00")).toBeInTheDocument();
      expect(screen.getByText("$9,000.00")).toBeInTheDocument();
    });
  });

  it("renders RecruitmentPage and hiring pipeline stages", async () => {
    renderWithProviders(<RecruitmentPage />);
    expect(screen.getByText("Recruitment & Applicant Tracking System")).toBeInTheDocument();
    expect(screen.getByText("Candidate Hiring Pipeline")).toBeInTheDocument();
    expect(screen.getByText("APPLIED")).toBeInTheDocument();
    expect(screen.getByText("HIRED")).toBeInTheDocument();
  });

  it("renders PerformancePage and appraisal review cycle", async () => {
    renderWithProviders(<PerformancePage />);
    expect(screen.getByText("Performance Management & OKRs")).toBeInTheDocument();
    expect(screen.getByText("H1 2024 Performance Review Period")).toBeInTheDocument();
    expect(screen.getByText("Deliver Complete HR Domain Architecture")).toBeInTheDocument();
  });

  it("renders LearningPage with LMS course catalog", async () => {
    renderWithProviders(<LearningPage />);
    expect(screen.getByText("Learning & Talent Development (LMS)")).toBeInTheDocument();
    expect(screen.getByText("Enterprise Course Catalog")).toBeInTheDocument();
  });
});
