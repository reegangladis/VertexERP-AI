import { apiClient } from "@/lib/api-client";
import {
  AttendanceRecord,
  BankAccount,
  CourseEnrollment,
  Employee,
  EmployeeCertification,
  EmployeeCreateInput,
  EmployeeGoal,
  EmployeeProfile,
  EmployeeSkill,
  EmploymentContract,
  JobApplicant,
  JobOffer,
  JobRequisition,
  LeaveBalance,
  LeaveRequest,
  LeaveType,
  PayrollRun,
  Payslip,
  PerformanceReview,
  PerformanceReviewPeriod,
  SalaryComponent,
  SalaryStructure,
  Shift,
  TrainingCourse,
} from "../types";

export const hrApi = {
  // Employees
  getEmployees: (params?: { department_id?: string; search?: string }) => {
    const q = new URLSearchParams();
    if (params?.department_id) q.set("department_id", params.department_id);
    if (params?.search) q.set("search", params.search);
    return apiClient<Employee[]>(`/hr/employees/?${q.toString()}`);
  },
  getEmployee: (id: string) => apiClient<Employee>(`/hr/employees/${id}`),
  createEmployee: (data: EmployeeCreateInput) =>
    apiClient<Employee>("/hr/employees/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Profiles & Sensitive Data
  getProfile: (employeeId: string) => apiClient<EmployeeProfile>(`/hr/employees/${employeeId}/profile`),
  getBankAccounts: (employeeId: string) => apiClient<BankAccount[]>(`/hr/employees/${employeeId}/bank-accounts`),
  getContracts: (employeeId: string) => apiClient<EmploymentContract[]>(`/hr/lifecycle/contracts/employee/${employeeId}`),

  // Attendance
  getAttendanceRecords: (params?: { employee_id?: string; start_date?: string; end_date?: string }) => {
    const q = new URLSearchParams();
    if (params?.employee_id) q.set("employee_id", params.employee_id);
    if (params?.start_date) q.set("start_date", params.start_date);
    if (params?.end_date) q.set("end_date", params.end_date);
    return apiClient<AttendanceRecord[]>(`/hr/attendance/records?${q.toString()}`);
  },
  clockIn: (data: { employee_id: string; work_date: string; check_in_time?: string }) =>
    apiClient<AttendanceRecord>("/hr/attendance/clock-in", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  clockOut: (data: { employee_id: string; work_date: string; check_out_time?: string }) =>
    apiClient<AttendanceRecord>("/hr/attendance/clock-out", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getShifts: () => apiClient<Shift[]>("/hr/attendance/shifts"),

  // Leaves
  getLeaveTypes: () => apiClient<LeaveType[]>("/hr/leaves/types"),
  getLeaveBalances: (employeeId: string, fiscalYear: number = 2024) =>
    apiClient<LeaveBalance[]>(`/hr/leaves/balances/${employeeId}?fiscal_year=${fiscalYear}`),
  getLeaveRequests: (params?: { employee_id?: string; status?: string }) => {
    const q = new URLSearchParams();
    if (params?.employee_id) q.set("employee_id", params.employee_id);
    if (params?.status) q.set("status", params.status);
    return apiClient<LeaveRequest[]>(`/hr/leaves/requests?${q.toString()}`);
  },
  applyLeave: (data: { employee_id: string; leave_type_id: string; start_date: string; end_date: string; total_days: number; reason: string }) =>
    apiClient<LeaveRequest>("/hr/leaves/requests", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  reviewLeave: (requestId: string, data: { status: "APPROVED" | "REJECTED"; remarks?: string }) =>
    apiClient<LeaveRequest>(`/hr/leaves/requests/${requestId}/review`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  // Payroll
  getSalaryComponents: () => apiClient<SalaryComponent[]>("/hr/payroll/components"),
  getSalaryStructures: () => apiClient<SalaryStructure[]>("/hr/payroll/structures"),
  getPayrollRuns: () => apiClient<PayrollRun[]>("/hr/payroll/runs"),
  createPayrollRun: (data: { pay_period_start: string; pay_period_end: string; pay_date: string; payment_method?: string }) =>
    apiClient<PayrollRun>("/hr/payroll/runs", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  processPayrollRun: (runId: string) =>
    apiClient<PayrollRun>(`/hr/payroll/runs/${runId}/process`, {
      method: "POST",
    }),
  approvePayrollRun: (runId: string, remarks?: string) =>
    apiClient<PayrollRun>(`/hr/payroll/runs/${runId}/approve`, {
      method: "PUT",
      body: JSON.stringify({ status: "APPROVED", remarks }),
    }),
  disbursePayrollRun: (runId: string) =>
    apiClient<PayrollRun>(`/hr/payroll/runs/${runId}/disburse`, {
      method: "POST",
    }),
  getPayslipsForRun: (runId: string) => apiClient<Payslip[]>(`/hr/payroll/payslips/run/${runId}`),
  getPayslipDetail: (payslipId: string) => apiClient<Payslip>(`/hr/payroll/payslips/${payslipId}`),

  // Recruitment
  getRequisitions: () => apiClient<JobRequisition[]>("/hr/recruitment/requisitions"),
  createRequisition: (data: Partial<JobRequisition>) =>
    apiClient<JobRequisition>("/hr/recruitment/requisitions", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getApplicants: (requisitionId?: string) => {
    const q = requisitionId ? `?requisition_id=${requisitionId}` : "";
    return apiClient<JobApplicant[]>(`/hr/recruitment/applicants${q}`);
  },
  createApplicant: (data: Partial<JobApplicant>) =>
    apiClient<JobApplicant>("/hr/recruitment/applicants", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateApplicantStage: (applicantId: string, current_stage: string, rating: number = 3) =>
    apiClient<JobApplicant>(`/hr/recruitment/applicants/${applicantId}/stage`, {
      method: "PUT",
      body: JSON.stringify({ current_stage, rating }),
    }),

  // Performance
  getReviewPeriods: () => apiClient<PerformanceReviewPeriod[]>("/hr/performance/periods"),
  getGoals: (employeeId?: string) => {
    const q = employeeId ? `?employee_id=${employeeId}` : "";
    return apiClient<EmployeeGoal[]>(`/hr/performance/goals${q}`);
  },
  createGoal: (data: Partial<EmployeeGoal>) =>
    apiClient<EmployeeGoal>("/hr/performance/goals", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getPerformanceReviews: () => apiClient<PerformanceReview[]>("/hr/performance/reviews"),

  // Learning
  getCourses: () => apiClient<TrainingCourse[]>("/hr/learning/courses"),
  createCourse: (data: Partial<TrainingCourse>) =>
    apiClient<TrainingCourse>("/hr/learning/courses", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getEnrollments: (employeeId: string) => apiClient<CourseEnrollment[]>(`/hr/learning/enrollments/employee/${employeeId}`),
  getSkills: (employeeId: string) => apiClient<EmployeeSkill[]>(`/hr/learning/skills/employee/${employeeId}`),
};
