export interface Employee {
  id: string;
  tenant_id: string;
  organization_id: string;
  employee_number: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  department_id?: string | null;
  designation_id?: string | null;
  manager_id?: string | null;
  employment_type: string;
  employment_status: string;
  hire_date: string;
  avatar_url?: string | null;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreateInput {
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  department_id?: string | null;
  designation_id?: string | null;
  manager_id?: string | null;
  employment_type?: string;
  hire_date: string;
}

export interface EmployeeProfile {
  id: string;
  employee_id: string;
  date_of_birth?: string | null;
  gender?: string | null;
  marital_status?: string | null;
  nationality?: string | null;
  personal_email?: string | null;
  personal_phone?: string | null;
  blood_group?: string | null;
  emergency_contacts?: Array<{
    name: string;
    relationship: string;
    phone: string;
    is_primary: boolean;
  }>;
}

export interface BankAccount {
  id: string;
  employee_id: string;
  bank_name: string;
  account_number_masked: string;
  routing_code_masked?: string | null;
  account_type: string;
  currency: string;
  is_primary: boolean;
}

export interface EmploymentContract {
  id: string;
  employee_id: string;
  contract_type: string;
  start_date: string;
  end_date?: string | null;
  terms_summary?: string | null;
  is_current: boolean;
}

export interface Shift {
  id: string;
  code: string;
  name: string;
  start_time: string;
  end_time: string;
  break_duration_minutes: number;
  grace_period_minutes: number;
  is_night_shift: boolean;
  is_active: boolean;
}

export interface AttendanceRecord {
  id: string;
  employee_id: string;
  work_date: string;
  shift_id?: string | null;
  check_in_time?: string | null;
  check_out_time?: string | null;
  regular_hours: number;
  overtime_hours: number;
  status: string;
  verification_method: string;
}

export interface LeaveType {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  is_paid: boolean;
  is_encashable: boolean;
  max_consecutive_days: number;
  color_code: string;
  is_active: boolean;
}

export interface LeaveBalance {
  id: string;
  employee_id: string;
  leave_type_id: string;
  fiscal_year: number;
  allocated_days: number;
  used_days: number;
  pending_days: number;
  carry_forward_days: number;
  balance_days: number;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  leave_type_id: string;
  start_date: string;
  end_date: string;
  total_days: number;
  reason: string;
  status: string;
  approver_id?: string | null;
  approved_at?: string | null;
  remarks?: string | null;
  created_at: string;
}

export interface SalaryComponent {
  id: string;
  code: string;
  name: string;
  component_type: string;
  calculation_type: string;
  is_taxable: boolean;
  is_active: boolean;
}

export interface SalaryStructure {
  id: string;
  code: string;
  name: string;
  description?: string | null;
  is_active: boolean;
  items: Array<{
    id: string;
    component_id: string;
    calculation_type: string;
    amount_or_percentage: number;
    is_active: boolean;
  }>;
}

export interface PayrollRun {
  id: string;
  run_number: string;
  pay_period_start: string;
  pay_period_end: string;
  pay_date: string;
  status: string;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  total_employees: number;
  payment_method: string;
  created_at: string;
}

export interface Payslip {
  id: string;
  payroll_run_id: string;
  employee_id: string;
  payslip_number: string;
  pay_period_start: string;
  pay_period_end: string;
  basic_pay: number;
  allowances: number;
  gross_pay: number;
  deductions: number;
  net_pay: number;
  total_worked_days: number;
  loss_of_pay_days: number;
  status: string;
  transaction_reference?: string | null;
  lines?: Array<{
    id: string;
    component_name: string;
    component_type: string;
    amount: number;
    is_taxable: boolean;
  }>;
}

export interface JobRequisition {
  id: string;
  requisition_number: string;
  title: string;
  department_id?: string | null;
  headcount: number;
  employment_type: string;
  experience_level: string;
  salary_min: number;
  salary_max: number;
  status: string;
  description?: string | null;
  created_at: string;
}

export interface JobApplicant {
  id: string;
  requisition_id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string | null;
  current_stage: string;
  rating: number;
  source?: string | null;
  created_at: string;
}

export interface PerformanceReviewPeriod {
  id: string;
  code: string;
  title: string;
  start_date: string;
  end_date: string;
  status: string;
  is_active: boolean;
}

export interface EmployeeGoal {
  id: string;
  employee_id: string;
  review_period_id?: string | null;
  title: string;
  description?: string | null;
  category: string;
  weightage: number;
  target_date?: string | null;
  progress_percentage: number;
  status: string;
  self_rating?: number | null;
  manager_rating?: number | null;
}

export interface PerformanceReview {
  id: string;
  employee_id: string;
  review_period_id: string;
  status: string;
  self_score?: number | null;
  manager_score?: number | null;
  final_score?: number | null;
  final_rating?: string | null;
  strengths?: string | null;
  improvements?: string | null;
  promotion_recommendation: boolean;
  created_at: string;
}

export interface TrainingCourse {
  id: string;
  code: string;
  title: string;
  description?: string | null;
  category: string;
  duration_hours: number;
  provider?: string | null;
  is_mandatory: boolean;
  is_active: boolean;
  modules?: Array<{
    id: string;
    title: string;
    sequence_order: number;
    content_type: string;
    duration_minutes: number;
  }>;
}

export interface CourseEnrollment {
  id: string;
  employee_id: string;
  course_id: string;
  enrolled_date: string;
  status: string;
  completion_date?: string | null;
  progress_percentage: number;
  score?: number | null;
  certificate_url?: string | null;
}

export interface EmployeeSkill {
  id: string;
  employee_id: string;
  skill_name: string;
  proficiency_level: string;
  years_of_experience: number;
  is_verified: boolean;
}

export interface EmployeeCertification {
  id: string;
  employee_id: string;
  certification_name: string;
  issuing_organization: string;
  issue_date: string;
  expiry_date?: string | null;
  credential_id?: string | null;
  credential_url?: string | null;
}

export interface JobOffer {
  id: string;
  applicant_id: string;
  offered_designation_id?: string | null;
  offered_salary: number;
  currency: string;
  joining_date: string;
  expiry_date?: string | null;
  status: string;
  created_at: string;
}

