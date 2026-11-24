import { apiClient } from "@/lib/api-client";
import {
  LeadItem,
  CustomerAccountItem,
  ContactItem,
  DealItem,
  ActivityLogItem,
  QuotationItemDto,
  SalesOrderItemDto,
  CRMDashboardMetrics,
} from "../types";

export const crmApi = {
  // Metrics & Dashboard
  getMetrics: () => apiClient<CRMDashboardMetrics>("/crm/dashboard/metrics"),

  // Leads
  getLeads: () => apiClient<LeadItem[]>("/crm/leads"),
  getLead: (id: string) => apiClient<LeadItem>(`/crm/leads/${id}`),
  createLead: (data: Partial<LeadItem>) =>
    apiClient<LeadItem>("/crm/leads", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateLead: (id: string, data: Partial<LeadItem>) =>
    apiClient<LeadItem>(`/crm/leads/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),
  convertLead: (leadId: string, data: { deal_title?: string; deal_value?: number }) =>
    apiClient<{ customer: any; contact: any; deal: any }>(`/crm/leads/${leadId}/convert`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Customers (Accounts)
  getCustomers: () => apiClient<CustomerAccountItem[]>("/crm/customers"),
  createCustomer: (data: Partial<CustomerAccountItem>) =>
    apiClient<CustomerAccountItem>("/crm/customers", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Contacts
  getContacts: (customerId?: string) => {
    const q = customerId ? `?customer_id=${customerId}` : "";
    return apiClient<ContactItem[]>(`/crm/contacts${q}`);
  },
  createContact: (data: Partial<ContactItem>) =>
    apiClient<ContactItem>("/crm/contacts", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Deals (Opportunities)
  getDeals: () => apiClient<DealItem[]>("/crm/deals"),
  createDeal: (data: Partial<DealItem>) =>
    apiClient<DealItem>("/crm/deals", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  updateDealStage: (dealId: string, stageId: string, winProbability?: number) =>
    apiClient<DealItem>(`/crm/deals/${dealId}/stage`, {
      method: "PUT",
      body: JSON.stringify({
        stage_id: stageId,
        win_probability_pct: winProbability,
      }),
    }),

  // Activities
  getActivities: () => apiClient<ActivityLogItem[]>("/crm/activities"),
  createActivity: (data: Partial<ActivityLogItem>) =>
    apiClient<ActivityLogItem>("/crm/activities", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // Quotations
  getQuotations: () => apiClient<QuotationItemDto[]>("/crm/quotations"),
  createQuotation: (data: {
    customer_id: string;
    deal_id?: string;
    valid_until: string;
    items: Array<{
      description: string;
      quantity: number;
      unit_price: number;
      discount_pct?: number;
      tax_pct?: number;
    }>;
  }) =>
    apiClient<QuotationItemDto>("/crm/quotations", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  convertQuotationToOrder: (quotationId: string) =>
    apiClient<SalesOrderItemDto>(`/crm/quotations/${quotationId}/convert-order`, {
      method: "POST",
    }),

  // Sales Orders
  getSalesOrders: () => apiClient<SalesOrderItemDto[]>("/crm/orders"),
};
