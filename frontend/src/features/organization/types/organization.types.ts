export interface Branch {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  address_line1: string;
  address_line2?: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone?: string | null;
  email?: string | null;
  is_headquarters: boolean;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Department {
  id: string;
  tenant_id: string;
  organization_id: string;
  parent_department_id?: string | null;
  code: string;
  name: string;
  description?: string | null;
  manager_user_id?: string | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface DepartmentTreeNode extends Department {
  children: DepartmentTreeNode[];
}

export interface Team {
  id: string;
  tenant_id: string;
  organization_id: string;
  department_id?: string | null;
  code: string;
  name: string;
  description?: string | null;
  lead_user_id?: string | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: string;
  tenant_id: string;
  team_id: string;
  user_id: string;
  role: string;
  joined_at: string;
  created_at: string;
}

export interface Designation {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  description?: string | null;
  level: number;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface BusinessUnit {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  description?: string | null;
  head_user_id?: string | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface CostCenter {
  id: string;
  tenant_id: string;
  organization_id: string;
  department_id?: string | null;
  code: string;
  name: string;
  description?: string | null;
  annual_budget: number | string;
  currency: string;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;
  tenant_id: string;
  organization_id: string;
  branch_id?: string | null;
  code: string;
  name: string;
  location_type: string;
  address_line1: string;
  address_line2?: string | null;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  latitude?: number | null;
  longitude?: number | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface WorkingDay {
  id: string;
  tenant_id: string;
  calendar_id: string;
  day_of_week: number;
  is_working_day: boolean;
  start_time?: string | null;
  end_time?: string | null;
  created_at: string;
}

export interface WorkCalendar {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  description?: string | null;
  time_zone: string;
  is_default: boolean;
  standard_hours_per_day: number | string;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
  working_days: WorkingDay[];
}

export interface Holiday {
  id: string;
  tenant_id: string;
  organization_id: string;
  calendar_id?: string | null;
  branch_id?: string | null;
  name: string;
  holiday_date: string;
  holiday_type: string;
  is_recurring: boolean;
  description?: string | null;
  version: number;
  created_at: string;
  updated_at: string;
}
