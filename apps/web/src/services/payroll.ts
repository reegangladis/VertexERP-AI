import { apiClient } from './apiClient';

export interface SalaryStructure {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  currency: string;
  effective_from: string;
  effective_to?: string;
  status: string;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface SalaryComponent {
  id: string;
  organization_id: string;
  name: string;
  component_type: string;
  earning_or_deduction: string;
  calculation_method: string;
  default_value: number;
  taxable: boolean;
  is_recurring: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface SalaryAssignment {
  id: string;
  employee_id: string;
  salary_structure_id: string;
  effective_from: string;
  effective_to?: string;
  monthly_ctc: number;
  annual_ctc: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PayrollItem {
  id: string;
  payslip_id: string;
  salary_component_id?: string;
  component_name: string;
  earning_or_deduction: string;
  amount: number;
  remarks?: string;
}

export interface Payslip {
  id: string;
  payroll_run_id: string;
  employee_id: string;
  gross_salary: number;
  total_earnings: number;
  total_deductions: number;
  net_salary: number;
  payment_status: string;
  generated_at: string;
  items: PayrollItem[];
  created_at: string;
  updated_at: string;
}

export interface PayrollRun {
  id: string;
  organization_id: string;
  month: number;
  year: number;
  pay_period_start: string;
  pay_period_end: string;
  status: string;
  processed_at?: string;
  approved_at?: string;
  payslips: Payslip[];
  created_at: string;
  updated_at: string;
}

export interface Reimbursement {
  id: string;
  employee_id: string;
  category: string;
  amount: number;
  claim_date: string;
  approved_amount: number;
  status: string;
  attachment_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Bonus {
  id: string;
  employee_id: string;
  bonus_type: string;
  amount: number;
  reason: string;
  approved_by?: string;
  payment_date: string;
  created_at: string;
  updated_at: string;
}

export interface Loan {
  id: string;
  employee_id: string;
  loan_type: string;
  principal_amount: number;
  balance_amount: number;
  emi_amount: number;
  interest_rate: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TaxProfile {
  id: string;
  employee_id: string;
  tax_regime: string;
  pan_number?: string;
  tax_identification?: string;
  declarations?: Record<string, any>;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface PayrollSummary {
  current_payroll_run?: PayrollRun;
  total_payroll_cost: number;
  employees_paid_count: number;
  pending_payroll_count: number;
  total_gross_salary: number;
  total_net_salary: number;
  total_bonuses: number;
  total_deductions: number;
  total_reimbursements: number;
  active_loans_total: number;
}

export const payrollService = {
  // Structures & Components
  listStructures: async (orgId: string): Promise<SalaryStructure[]> => {
    const res = await apiClient.get(`/api/v1/payroll/structures?org_id=${orgId}`);
    return res.data;
  },

  createStructure: async (payload: Partial<SalaryStructure>): Promise<SalaryStructure> => {
    const res = await apiClient.post('/api/v1/payroll/structures', payload);
    return res.data;
  },

  listComponents: async (orgId: string): Promise<SalaryComponent[]> => {
    const res = await apiClient.get(`/api/v1/payroll/components?org_id=${orgId}`);
    return res.data;
  },

  createComponent: async (payload: Partial<SalaryComponent>): Promise<SalaryComponent> => {
    const res = await apiClient.post('/api/v1/payroll/components', payload);
    return res.data;
  },

  // Assignments
  assignSalary: async (payload: Partial<SalaryAssignment>): Promise<SalaryAssignment> => {
    const res = await apiClient.post('/api/v1/payroll/assignments', payload);
    return res.data;
  },

  listAssignments: async (orgId: string): Promise<SalaryAssignment[]> => {
    const res = await apiClient.get(`/api/v1/payroll/assignments?org_id=${orgId}`);
    return res.data;
  },

  // Payroll Runs
  generateRun: async (payload: { organization_id: string; month: number; year: number }): Promise<PayrollRun> => {
    const res = await apiClient.post('/api/v1/payroll/runs/generate', payload);
    return res.data;
  },

  listRuns: async (orgId: string): Promise<PayrollRun[]> => {
    const res = await apiClient.get(`/api/v1/payroll/runs?org_id=${orgId}`);
    return res.data;
  },

  approveRun: async (id: string, payload: { approver_id: string; status: string; remarks?: string }): Promise<PayrollRun> => {
    const res = await apiClient.post(`/api/v1/payroll/runs/${id}/approve`, payload);
    return res.data;
  },

  // Payslips
  listPayslips: async (employeeId: string): Promise<Payslip[]> => {
    const res = await apiClient.get(`/api/v1/payroll/payslips?employee_id=${employeeId}`);
    return res.data;
  },

  downloadPayslip: async (payslipId: string): Promise<string> => {
    const res = await apiClient.get(`/api/v1/payroll/payslips/${payslipId}/download`);
    return res.data;
  },

  // Loans, Bonuses & Reimbursements
  listLoans: async (employeeId: string): Promise<Loan[]> => {
    const res = await apiClient.get(`/api/v1/payroll/loans?employee_id=${employeeId}`);
    return res.data;
  },

  createLoan: async (payload: Partial<Loan>): Promise<Loan> => {
    const res = await apiClient.post('/api/v1/payroll/loans', payload);
    return res.data;
  },

  listBonuses: async (employeeId: string): Promise<Bonus[]> => {
    const res = await apiClient.get(`/api/v1/payroll/bonuses?employee_id=${employeeId}`);
    return res.data;
  },

  createBonus: async (payload: Partial<Bonus>): Promise<Bonus> => {
    const res = await apiClient.post('/api/v1/payroll/bonuses', payload);
    return res.data;
  },

  listReimbursements: async (employeeId: string): Promise<Reimbursement[]> => {
    const res = await apiClient.get(`/api/v1/payroll/reimbursements?employee_id=${employeeId}`);
    return res.data;
  },

  createReimbursement: async (payload: Partial<Reimbursement>): Promise<Reimbursement> => {
    const res = await apiClient.post('/api/v1/payroll/reimbursements', payload);
    return res.data;
  },

  // Tax Profiles
  getTaxProfile: async (employeeId: string): Promise<TaxProfile> => {
    const res = await apiClient.get(`/api/v1/payroll/tax-profiles?employee_id=${employeeId}`);
    return res.data;
  },

  createTaxProfile: async (payload: Partial<TaxProfile>): Promise<TaxProfile> => {
    const res = await apiClient.post('/api/v1/payroll/tax-profiles', payload);
    return res.data;
  },

  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<PayrollSummary> => {
    const res = await apiClient.get(`/api/v1/payroll/dashboard-summary?org_id=${orgId}`);
    return res.data;
  },
};
