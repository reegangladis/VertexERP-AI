export interface AttendanceStatusSummary {
  presentDays: number;
  absentDays: number;
  leaveDays: number;
  holidays: number;
  onDutyDays: number;
  totalWorkingHours: number;
  averageWorkingHours: number;
}

export interface DailyAttendanceRecord {
  id: string;
  workDate: string;
  checkInTime: string | null;
  checkOutTime: string | null;
  totalHours: number;
  status: "PRESENT" | "ABSENT" | "ON_DUTY" | "HOLIDAY" | "LEAVE" | "REST_DAY" | "PENDING";
  shiftCode: string;
  isRegularized?: boolean;
}

export interface LeaveBalanceSummary {
  leaveTypeId: string;
  leaveTypeName: string;
  allocatedDays: number;
  usedDays: number;
  pendingDays: number;
  remainingDays: number;
  colorCode: string;
}

export interface LeaveRequestItem {
  id: string;
  leaveTypeName: string;
  startDate: string;
  endDate: string;
  totalDays: number;
  reason: string;
  status: "PENDING" | "APPROVED" | "REJECTED" | "CANCELLED";
  appliedAt: string;
  approverRemarks?: string;
}

export interface EmployeePayslipSummary {
  id: string;
  payrollMonth: string;
  grossEarnings: number;
  totalDeductions: number;
  netPay: number;
  paymentStatus: "PAID" | "PENDING";
  paymentDate?: string;
  earningsBreakdown: Array<{ name: string; amount: number }>;
  deductionsBreakdown: Array<{ name: string; amount: number }>;
}

export interface EmployeeDocumentItem {
  id: string;
  title: string;
  category: "IDENTITY" | "TAX" | "EDUCATION" | "CONTRACT" | "POLICY";
  fileName: string;
  uploadDate: string;
  fileSize: string;
  verificationStatus: "VERIFIED" | "PENDING" | "REJECTED";
}

export interface AnnouncementItem {
  id: string;
  title: string;
  content: string;
  category: "COMPANY" | "HR" | "EVENT" | "ALERT";
  publishedAt: string;
  authorName: string;
  isPinned: boolean;
}

export interface RegularizationRequestItem {
  id: string;
  workDate: string;
  originalCheckIn: string | null;
  originalCheckOut: string | null;
  requestedCheckIn: string;
  requestedCheckOut: string;
  reason: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  submittedAt: string;
}
