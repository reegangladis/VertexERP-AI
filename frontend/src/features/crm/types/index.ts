export interface LeadItem {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  company_name?: string;
  title?: string;
  source: string;
  status: string; // NEW, CONTACTED, QUALIFIED, CONVERTED, DEAD
  rating: string; // HOT, WARM, COLD
  estimated_value: number;
  created_at?: string;
}

export interface CustomerAccountItem {
  id: string;
  name: string;
  customer_type: string;
  industry?: string;
  website?: string;
  phone?: string;
  email?: string;
  credit_limit: number;
  status: string;
  created_at?: string;
}

export interface ContactItem {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  title?: string;
  department?: string;
  customer_id?: string;
  is_primary: boolean;
}

export interface DealItem {
  id: string;
  title: string;
  value: number;
  currency: string;
  stage_id: string;
  pipeline_id: string;
  customer_id: string;
  win_probability_pct: number;
  status: string; // OPEN, WON, LOST
  expected_close_date?: string;
  created_at?: string;
}

export interface ActivityLogItem {
  id: string;
  activity_type: "CALL" | "MEETING" | "EMAIL" | "EVENT";
  title: string;
  description?: string;
  status: string;
  priority: string;
  scheduled_start?: string;
  created_at?: string;
}

export interface QuotationItemDto {
  id: string;
  quotation_number: string;
  customer_id: string;
  status: string; // DRAFT, SENT, APPROVED, REJECTED, CONVERTED
  subtotal: number;
  tax_amount: number;
  grand_total: number;
  valid_until?: string;
  created_at?: string;
}

export interface SalesOrderItemDto {
  id: string;
  order_number: string;
  customer_id: string;
  status: string;
  grand_total: number;
  created_at?: string;
}

export interface CRMDashboardMetrics {
  leads_total: number;
  leads_open: number;
  leads_converted: number;
  deals_total: number;
  deals_open: number;
  deals_won: number;
  pipeline_value: number;
  won_revenue: number;
  conversion_rate_pct: number;
}
