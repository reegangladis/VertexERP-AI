import { apiClient } from './apiClient';

export interface LeaveType {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  description?: string;
  color: string;
  is_paid: boolean;
  requires_approval: boolean;
  allow_half_day: boolean;
  allow_negative_balance: boolean;
  max_days_per_year: number;
  carry_forward: boolean;
  carry_forward_limit: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface LeavePolicy {
  id: string;
  organization_id: string;
  name: string;
  description?: string;
  effective_from: string;
  effective_to?: string;
  accrual_method: string;
  approval_levels: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveBalance {
  id: string;
  employee_id: string;
  leave_type_id: string;
  available_days: number;
  used_days: number;
  pending_days: number;
  carry_forward_days: number;
  accrued_days: number;
  last_updated: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveApproval {
  id: string;
  leave_request_id: string;
  approver_id: string;
  approval_level: number;
  decision: string;
  remarks?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  leave_type_id: string;
  start_date: string;
  end_date: string;
  number_of_days: number;
  is_half_day: boolean;
  half_day_session?: string;
  reason: string;
  attachment_url?: string;
  status: string;
  applied_at: string;
  approved_at?: string;
  cancelled_at?: string;
  approvals: LeaveApproval[];
  created_at: string;
  updated_at: string;
}

export interface CompOff {
  id: string;
  employee_id: string;
  attendance_id?: string;
  earned_date: string;
  expiry_date: string;
  days: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface HolidayCalendar {
  id: string;
  organization_id: string;
  name: string;
  country: string;
  state?: string;
  year: number;
  created_at: string;
  updated_at: string;
}

export interface HolidayEvent {
  id: string;
  calendar_id: string;
  date: string;
  holiday_name: string;
  holiday_type: string;
  is_optional: boolean;
  created_at: string;
  updated_at: string;
}

export interface LeaveDashboardSummary {
  total_balances: LeaveBalance[];
  pending_requests_count: number;
  approved_leaves_count: number;
  rejected_leaves_count: number;
  upcoming_holidays: HolidayEvent[];
  team_leave_today_count: number;
  comp_off_available_days: number;
}

export const leaveService = {
  // Types & Policies
  listTypes: async (orgId: string): Promise<LeaveType[]> => {
    const res = await apiClient.get(`/api/v1/leave/types?org_id=${orgId}`);
    return res.data;
  },

  createType: async (payload: Partial<LeaveType>): Promise<LeaveType> => {
    const res = await apiClient.post('/api/v1/leave/types', payload);
    return res.data;
  },

  listPolicies: async (orgId: string): Promise<LeavePolicy[]> => {
    const res = await apiClient.get(`/api/v1/leave/policies?org_id=${orgId}`);
    return res.data;
  },

  createPolicy: async (payload: Partial<LeavePolicy>): Promise<LeavePolicy> => {
    const res = await apiClient.post('/api/v1/leave/policies', payload);
    return res.data;
  },

  // Balances
  listBalances: async (employeeId: string): Promise<LeaveBalance[]> => {
    const res = await apiClient.get(`/api/v1/leave/balances?employee_id=${employeeId}`);
    return res.data;
  },

  // Requests
  applyLeave: async (payload: {
    employee_id: string;
    leave_type_id: string;
    start_date: string;
    end_date: string;
    is_half_day?: boolean;
    half_day_session?: string;
    reason: string;
    attachment_url?: string;
  }): Promise<LeaveRequest> => {
    const res = await apiClient.post('/api/v1/leave/requests', payload);
    return res.data;
  },

  listRequests: async (params?: { employee_id?: string; leave_status?: string }): Promise<LeaveRequest[]> => {
    const res = await apiClient.get('/api/v1/leave/requests', { params });
    return res.data;
  },

  approveLeave: async (id: string, payload: { approver_id: string; decision: string; remarks?: string }): Promise<LeaveRequest> => {
    const res = await apiClient.post(`/api/v1/leave/requests/${id}/approve`, payload);
    return res.data;
  },

  rejectLeave: async (id: string, payload: { approver_id: string; decision: string; remarks?: string }): Promise<LeaveRequest> => {
    const res = await apiClient.post(`/api/v1/leave/requests/${id}/reject`, payload);
    return res.data;
  },

  cancelLeave: async (id: string): Promise<LeaveRequest> => {
    const res = await apiClient.post(`/api/v1/leave/requests/${id}/cancel`);
    return res.data;
  },

  // Comp-off & Accruals
  listCompOffs: async (employeeId: string): Promise<CompOff[]> => {
    const res = await apiClient.get(`/api/v1/leave/comp-off?employee_id=${employeeId}`);
    return res.data;
  },

  createCompOff: async (payload: Partial<CompOff>): Promise<CompOff> => {
    const res = await apiClient.post('/api/v1/leave/comp-off', payload);
    return res.data;
  },

  // Holidays
  listCalendars: async (orgId: string): Promise<HolidayCalendar[]> => {
    const res = await apiClient.get(`/api/v1/leave/holiday-calendars?org_id=${orgId}`);
    return res.data;
  },

  listEvents: async (calendarId: string): Promise<HolidayEvent[]> => {
    const res = await apiClient.get(`/api/v1/leave/holiday-events?calendar_id=${calendarId}`);
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (orgId: string, employeeId: string): Promise<LeaveDashboardSummary> => {
    const res = await apiClient.get(`/api/v1/leave/dashboard-summary?org_id=${orgId}&employee_id=${employeeId}`);
    return res.data;
  },
};
