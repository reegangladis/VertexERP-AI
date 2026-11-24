import { apiClient } from "@/lib/api-client";
import {
  AttendanceStatusSummary,
  DailyAttendanceRecord,
  LeaveBalanceSummary,
  LeaveRequestItem,
  EmployeePayslipSummary,
  EmployeeDocumentItem,
  AnnouncementItem,
  RegularizationRequestItem,
} from "../types";

export const essApi = {
  // Clock in / out operations
  clockIn: (employeeId: string) =>
    apiClient("/hr/attendance/clock-in", {
      method: "POST",
      body: JSON.stringify({
        employee_id: employeeId,
        work_date: new Date().toISOString().split("T")[0],
      }),
    }),

  clockOut: (employeeId: string) =>
    apiClient("/hr/attendance/clock-out", {
      method: "POST",
      body: JSON.stringify({
        employee_id: employeeId,
        work_date: new Date().toISOString().split("T")[0],
      }),
    }),

  // Attendance history & monthly calendar
  getAttendanceCalendar: (employeeId: string, month: string) =>
    apiClient<DailyAttendanceRecord[]>(
      `/hr/attendance/records?employee_id=${employeeId}&start_date=${month}-01&end_date=${month}-31`
    ),

  getAttendanceSummary: (employeeId: string, month: string) =>
    apiClient<AttendanceStatusSummary>(
      `/hr/attendance/summary?employee_id=${employeeId}&month=${month}`
    ),

  // Attendance Regularization
  submitRegularization: (data: {
    employeeId: string;
    workDate: string;
    requestedCheckIn: string;
    requestedCheckOut: string;
    reason: string;
  }) =>
    apiClient<RegularizationRequestItem>("/hr/attendance/regularize", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Leave operations
  getLeaveBalances: (employeeId: string) =>
    apiClient<LeaveBalanceSummary[]>(`/hr/leaves/balances/${employeeId}`),

  getLeaveHistory: (employeeId: string) =>
    apiClient<LeaveRequestItem[]>(`/hr/leaves/requests?employee_id=${employeeId}`),

  applyLeave: (data: {
    employeeId: string;
    leaveTypeId: string;
    startDate: string;
    endDate: string;
    totalDays: number;
    reason: string;
  }) =>
    apiClient<LeaveRequestItem>("/hr/leaves/requests", {
      method: "POST",
      body: JSON.stringify({
        employee_id: data.employeeId,
        leave_type_id: data.leaveTypeId,
        start_date: data.startDate,
        end_date: data.endDate,
        total_days: data.totalDays,
        reason: data.reason,
      }),
    }),

  // Payslips
  getMyPayslips: (employeeId: string) =>
    apiClient<EmployeePayslipSummary[]>(`/hr/payroll/payslips/employee/${employeeId}`),

  getPayslipDetail: (payslipId: string) =>
    apiClient<EmployeePayslipSummary>(`/hr/payroll/payslips/${payslipId}`),

  // Documents
  getMyDocuments: (employeeId: string) =>
    apiClient<EmployeeDocumentItem[]>(`/hr/employees/${employeeId}/documents`),

  // Profile
  getMyProfile: (employeeId: string) =>
    apiClient<any>(`/hr/employees/${employeeId}/profile`),

  // Announcements
  getAnnouncements: () =>
    apiClient<AnnouncementItem[]>("/organization/announcements"),
};
