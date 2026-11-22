export type SupplierStatus = "ACTIVE" | "INACTIVE" | "BLOCKED" | "ON_HOLD";

export interface Supplier {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  legal_name?: string | null;
  tax_identifier?: string | null;
  email?: string | null;
  phone?: string | null;
  website?: string | null;
  currency: string;
  payment_terms_days: number;
  rating?: number | null;
  status: SupplierStatus;
  notes?: string | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export type PRStatus = "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED" | "ORDERED" | "CANCELLED";

export interface PurchaseRequestItem {
  id: string;
  tenant_id: string;
  request_id: string;
  product_id: string;
  quantity: number;
  estimated_unit_cost: number;
  estimated_total_cost: number;
  required_by_date?: string | null;
  notes?: string | null;
  created_at: string;
  product_name?: string;
  product_sku?: string;
}

export interface PurchaseRequest {
  id: string;
  tenant_id: string;
  organization_id: string;
  request_number: string;
  department_id?: string | null;
  requested_by_id?: string | null;
  priority: "LOW" | "MEDIUM" | "HIGH" | "URGENT";
  status: PRStatus;
  reason?: string | null;
  target_date?: string | null;
  approved_by_id?: string | null;
  rejection_reason?: string | null;
  version: number;
  items: PurchaseRequestItem[];
  created_at: string;
  updated_at: string;
}

export type POStatus =
  | "DRAFT"
  | "ISSUED"
  | "CONFIRMED"
  | "PARTIALLY_RECEIVED"
  | "RECEIVED"
  | "CANCELLED"
  | "CLOSED";

export interface PurchaseOrderItem {
  id: string;
  tenant_id: string;
  order_id: string;
  product_id: string;
  quantity_ordered: number;
  quantity_received: number;
  quantity_billed: number;
  unit_price: number;
  tax_rate: number;
  discount_amount: number;
  net_amount: number;
  tax_amount: number;
  total_amount: number;
  expected_delivery_date?: string | null;
  notes?: string | null;
  created_at: string;
  product_name?: string;
  product_sku?: string;
}

export interface PurchaseOrder {
  id: string;
  tenant_id: string;
  organization_id: string;
  order_number: string;
  supplier_id: string;
  warehouse_id: string;
  purchase_request_id?: string | null;
  currency: string;
  subtotal_amount: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  status: POStatus;
  order_date: string;
  expected_delivery_date?: string | null;
  payment_terms?: string | null;
  shipping_address: Record<string, unknown>;
  issued_by_id?: string | null;
  issued_at?: string | null;
  cancelled_reason?: string | null;
  notes?: string | null;
  version: number;
  supplier?: Supplier;
  items: PurchaseOrderItem[];
  created_at: string;
  updated_at: string;
}
