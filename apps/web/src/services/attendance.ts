import { apiClient } from './apiClient';

export interface AttendanceRecord {
  id: string;
  organization_id: string;
  employee_id: string;
  attendance_date: string;
  check_in_time?: string;
  check_out_time?: string;
  working_hours: number;
  break_hours: number;
  overtime_hours: number;
  late_minutes: number;
  early_leave_minutes: number;
  attendance_status: string;
  attendance_source: string;
  remarks?: string;
  created_at: string;
  updated_at: string;
}

export interface WorkShift {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  start_time: string;
  end_time: string;
  break_duration: number;
  grace_time: number;
  weekly_hours: number;
  night_shift: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ShiftAssignment {
  id: string;
  employee_id: string;
  shift_id: string;
  effective_from: string;
  effective_to?: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
}

export interface AttendanceCorrection {
  id: string;
  attendance_id: string;
  employee_id: string;
  requested_check_in: string;
  requested_check_out: string;
  reason: string;
  status: string;
  approved_by?: string;
  approved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface OvertimeRequest {
  id: string;
  employee_id: string;
  attendance_id?: string;
  requested_hours: number;
  approved_hours: number;
  reason: string;
  status: string;
  approved_by?: string;
  created_at: string;
  updated_at: string;
}

export interface AttendanceDevice {
  id: string;
  organization_id: string;
  device_name: string;
  device_code: string;
  device_type: string;
  ip_address?: string;
  location?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface BiometricLog {
  id: string;
  device_id?: string;
  employee_id?: string;
  log_time: string;
  event_type: string;
  raw_data?: Record<string, any>;
  processed: boolean;
  created_at: string;
  updated_at: string;
}

export interface WorkSchedule {
  id: string;
  organization_id: string;
  name: string;
  weekly_schedule: Record<string, any>;
  holiday_calendar?: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface GeofenceLocation {
  id: string;
  organization_id: string;
  name: string;
  latitude: number;
  longitude: number;
  radius: number;
  created_at: string;
  updated_at: string;
}

export interface AttendanceSummary {
  total_employees: number;
  present_today: number;
  absent_today: number;
  late_today: number;
  overtime_today: number;
  remote_today: number;
  on_duty_today: number;
  attendance_rate: number;
  shift_summary: Array<{ shift_name: string; code: string; employee_count: number }>;
  recent_punches: AttendanceRecord[];
}

export const attendanceService = {
  // Check-In / Check-Out
  checkIn: async (payload: {
    organization_id: string;
    employee_id: string;
    attendance_source?: string;
    latitude?: number;
    longitude?: number;
    remarks?: string;
  }): Promise<AttendanceRecord> => {
    const res = await apiClient.post('/api/v1/attendance/check-in', payload);
    return res.data;
  },

  checkOut: async (payload: {
    attendance_id: string;
    break_hours?: number;
    remarks?: string;
  }): Promise<AttendanceRecord> => {
    const res = await apiClient.post('/api/v1/attendance/check-out', payload);
    return res.data;
  },

  listAttendance: async (params?: {
    org_id?: string;
    employee_id?: string;
    start_date?: string;
    end_date?: string;
    attendance_status?: string;
  }): Promise<AttendanceRecord[]> => {
    const res = await apiClient.get('/api/v1/attendance', { params });
    return res.data;
  },

  getDashboardSummary: async (orgId: string): Promise<AttendanceSummary> => {
    const res = await apiClient.get(`/api/v1/attendance/dashboard-summary?org_id=${orgId}`);
    return res.data;
  },

  // Shifts
  listShifts: async (orgId: string): Promise<WorkShift[]> => {
    const res = await apiClient.get(`/api/v1/attendance/shifts?org_id=${orgId}`);
    return res.data;
  },

  createShift: async (payload: Partial<WorkShift>): Promise<WorkShift> => {
    const res = await apiClient.post('/api/v1/attendance/shifts', payload);
    return res.data;
  },

  // Assignments
  assignShift: async (payload: Partial<ShiftAssignment>): Promise<ShiftAssignment> => {
    const res = await apiClient.post('/api/v1/attendance/shift-assignments', payload);
    return res.data;
  },

  listAssignments: async (employeeId?: string): Promise<ShiftAssignment[]> => {
    const res = await apiClient.get('/api/v1/attendance/shift-assignments', {
      params: { employee_id: employeeId },
    });
    return res.data;
  },

  // Corrections
  createCorrection: async (payload: Partial<AttendanceCorrection>): Promise<AttendanceCorrection> => {
    const res = await apiClient.post('/api/v1/attendance/corrections', payload);
    return res.data;
  },

  listCorrections: async (params?: { employee_id?: string; correction_status?: string }): Promise<AttendanceCorrection[]> => {
    const res = await apiClient.get('/api/v1/attendance/corrections', { params });
    return res.data;
  },

  approveCorrection: async (id: string, payload: { status: string; approved_by: string }): Promise<AttendanceCorrection> => {
    const res = await apiClient.post(`/api/v1/attendance/corrections/${id}/approve`, payload);
    return res.data;
  },

  // Overtime
  createOvertime: async (payload: Partial<OvertimeRequest>): Promise<OvertimeRequest> => {
    const res = await apiClient.post('/api/v1/attendance/overtime', payload);
    return res.data;
  },

  listOvertime: async (params?: { employee_id?: string; overtime_status?: string }): Promise<OvertimeRequest[]> => {
    const res = await apiClient.get('/api/v1/attendance/overtime', { params });
    return res.data;
  },

  approveOvertime: async (id: string, payload: { status: string; approved_hours: number; approved_by: string }): Promise<OvertimeRequest> => {
    const res = await apiClient.post(`/api/v1/attendance/overtime/${id}/approve`, payload);
    return res.data;
  },

  // Devices & Biometrics
  listDevices: async (orgId: string): Promise<AttendanceDevice[]> => {
    const res = await apiClient.get(`/api/v1/attendance/devices?org_id=${orgId}`);
    return res.data;
  },

  createDevice: async (payload: Partial<AttendanceDevice>): Promise<AttendanceDevice> => {
    const res = await apiClient.post('/api/v1/attendance/devices', payload);
    return res.data;
  },

  listBiometricLogs: async (params?: { device_id?: string; employee_id?: string }): Promise<BiometricLog[]> => {
    const res = await apiClient.get('/api/v1/attendance/biometric-logs', { params });
    return res.data;
  },

  createBiometricLog: async (payload: Partial<BiometricLog>): Promise<BiometricLog> => {
    const res = await apiClient.post('/api/v1/attendance/biometric-logs', payload);
    return res.data;
  },

  // Schedules & Geofences
  listSchedules: async (orgId: string): Promise<WorkSchedule[]> => {
    const res = await apiClient.get(`/api/v1/attendance/schedules?org_id=${orgId}`);
    return res.data;
  },

  createSchedule: async (payload: Partial<WorkSchedule>): Promise<WorkSchedule> => {
    const res = await apiClient.post('/api/v1/attendance/schedules', payload);
    return res.data;
  },

  listGeofences: async (orgId: string): Promise<GeofenceLocation[]> => {
    const res = await apiClient.get(`/api/v1/attendance/geofences?org_id=${orgId}`);
    return res.data;
  },

  createGeofence: async (payload: Partial<GeofenceLocation>): Promise<GeofenceLocation> => {
    const res = await apiClient.post('/api/v1/attendance/geofences', payload);
    return res.data;
  },
};
