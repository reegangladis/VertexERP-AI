import { apiClient } from './apiClient';

export interface Lead {
  id: string;
  organization_id: string;
  lead_source_id?: string;
  assigned_to?: string;
  company_name: string;
  contact_name: string;
  email: string;
  phone?: string;
  website?: string;
  industry?: string;
  status: string;
  priority: string;
  expected_value: number;
  remarks?: string;
  created_at: string;
  updated_at: string;
  activities?: any[];
}

export interface Customer {
  id: string;
  organization_id: string;
  customer_code: string;
  company_name: string;
  display_name: string;
  email: string;
  phone?: string;
  website?: string;
  industry?: string;
  tax_number?: string;
  credit_limit: number;
  payment_terms: string;
  status: string;
  created_at: string;
  updated_at: string;
  contacts?: any[];
  addresses?: any[];
}

export interface Opportunity {
  id: string;
  customer_id: string;
  title: string;
  description?: string;
  expected_revenue: number;
  probability: number;
  stage: string;
  expected_close_date: string;
  assigned_to?: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface QuotationItem {
  id?: string;
  item_name: string;
  description?: string;
  quantity: number;
  unit_price: number;
  subtotal?: number;
  tax_amount: number;
  total_price?: number;
}

export interface Quotation {
  id: string;
  customer_id: string;
  quotation_number: string;
  quotation_date: string;
  valid_until: string;
  subtotal: number;
  tax: number;
  discount: number;
  grand_total: number;
  status: string;
  created_at: string;
  items: QuotationItem[];
}

export interface SalesOrder {
  id: string;
  customer_id: string;
  quotation_id?: string;
  sales_order_number: string;
  order_date: string;
  subtotal: number;
  tax: number;
  discount: number;
  grand_total: number;
  status: string;
  created_at: string;
  items: QuotationItem[];
}

export interface CRMTask {
  id: string;
  customer_id?: string;
  assigned_to?: string;
  title: string;
  description?: string;
  priority: string;
  due_date: string;
  status: string;
  created_at: string;
}

export interface Meeting {
  id: string;
  customer_id?: string;
  title: string;
  agenda?: string;
  meeting_date: string;
  location?: string;
  meeting_type: string;
  status: string;
  created_at: string;
}

export interface CRMDashboardSummary {
  total_leads: number;
  qualified_leads: number;
  total_customers: number;
  open_opportunities: number;
  pipeline_value: number;
  sales_revenue: number;
  pending_quotations: number;
  total_sales_orders: number;
  meetings_today: number;
  tasks_due: number;
}

export const crmSalesService = {
  // Dashboard
  getDashboardSummary: async (orgId: string): Promise<CRMDashboardSummary> => {
    const res = await apiClient.get('/api/v1/crm/dashboard', { params: { org_id: orgId } });
    return res.data;
  },

  // Leads
  getLeads: async (orgId: string): Promise<Lead[]> => {
    const res = await apiClient.get('/api/v1/leads', { params: { org_id: orgId } });
    return res.data;
  },

  createLead: async (data: Partial<Lead>): Promise<Lead> => {
    const res = await apiClient.post('/api/v1/leads', data);
    return res.data;
  },

  convertLead: async (leadId: string, payload: any): Promise<Customer> => {
    const res = await apiClient.post(`/api/v1/leads/${leadId}/convert`, payload);
    return res.data;
  },

  // Customers
  getCustomers: async (orgId: string): Promise<Customer[]> => {
    const res = await apiClient.get('/api/v1/customers', { params: { org_id: orgId } });
    return res.data;
  },

  createCustomer: async (data: Partial<Customer>): Promise<Customer> => {
    const res = await apiClient.post('/api/v1/customers', data);
    return res.data;
  },

  // Opportunities
  getOpportunities: async (customerId?: string): Promise<Opportunity[]> => {
    const res = await apiClient.get('/api/v1/opportunities', { params: { customer_id: customerId } });
    return res.data;
  },

  createOpportunity: async (data: Partial<Opportunity>): Promise<Opportunity> => {
    const res = await apiClient.post('/api/v1/opportunities', data);
    return res.data;
  },

  updateOpportunity: async (id: string, data: Partial<Opportunity>): Promise<Opportunity> => {
    const res = await apiClient.put(`/api/v1/opportunities/${id}`, data);
    return res.data;
  },

  // Quotations
  getQuotations: async (customerId?: string): Promise<Quotation[]> => {
    const res = await apiClient.get('/api/v1/quotations', { params: { customer_id: customerId } });
    return res.data;
  },

  createQuotation: async (data: any): Promise<Quotation> => {
    const res = await apiClient.post('/api/v1/quotations', data);
    return res.data;
  },

  downloadQuotationPDF: async (qNumber: string): Promise<string> => {
    const res = await apiClient.get(`/api/v1/quotations/${qNumber}/download-pdf`, { responseType: 'text' });
    return res.data;
  },

  // Sales Orders
  getSalesOrders: async (customerId?: string): Promise<SalesOrder[]> => {
    const res = await apiClient.get('/api/v1/sales-orders', { params: { customer_id: customerId } });
    return res.data;
  },

  createSalesOrder: async (data: any): Promise<SalesOrder> => {
    const res = await apiClient.post('/api/v1/sales-orders', data);
    return res.data;
  },

  // Tasks & Meetings
  getTasks: async (): Promise<CRMTask[]> => {
    const res = await apiClient.get('/api/v1/crm-tasks');
    return res.data;
  },

  createTask: async (data: Partial<CRMTask>): Promise<CRMTask> => {
    const res = await apiClient.post('/api/v1/crm-tasks', data);
    return res.data;
  },

  getMeetings: async (): Promise<Meeting[]> => {
    const res = await apiClient.get('/api/v1/meetings');
    return res.data;
  },

  createMeeting: async (data: Partial<Meeting>): Promise<Meeting> => {
    const res = await apiClient.post('/api/v1/meetings', data);
    return res.data;
  },

  getCustomerTimeline: async (customerId: string): Promise<any[]> => {
    const res = await apiClient.get('/api/v1/customer-timeline', { params: { customer_id: customerId } });
    return res.data;
  },
};
