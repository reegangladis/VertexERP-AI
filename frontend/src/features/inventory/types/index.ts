export interface UnitOfMeasure {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  symbol: string;
  category: string;
  is_base_unit: boolean;
  conversion_factor: number;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface ProductCategory {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  description?: string | null;
  parent_id?: string | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Product {
  id: string;
  tenant_id: string;
  organization_id: string;
  category_id?: string | null;
  primary_uom_id: string;
  sku: string;
  barcode?: string | null;
  name: string;
  description?: string | null;
  product_type: "STORABLE" | "CONSUMABLE" | "SERVICE";
  cost_method: "STANDARD" | "AVERAGE" | "FIFO";
  standard_cost: number;
  average_cost: number;
  list_price: number;
  currency: string;
  reorder_point: number;
  min_order_qty: number;
  max_order_qty?: number | null;
  is_lot_tracked: boolean;
  is_serial_tracked: boolean;
  allow_negative_stock: boolean;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Location {
  id: string;
  tenant_id: string;
  organization_id: string;
  warehouse_id: string;
  code: string;
  name: string;
  aisle?: string | null;
  rack?: string | null;
  shelf?: string | null;
  bin?: string | null;
  location_type: "STORAGE" | "RECEIVING" | "SHIPPING" | "PICKING" | "QUARANTINE";
  max_weight?: number | null;
  max_volume?: number | null;
  is_active: boolean;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: string;
  tenant_id: string;
  organization_id: string;
  branch_id?: string | null;
  code: string;
  name: string;
  warehouse_type: "STANDARD" | "TRANSIT" | "QUARANTINE" | "RETURN";
  address: Record<string, unknown>;
  manager_id?: string | null;
  is_primary: boolean;
  is_active: boolean;
  version: number;
  locations?: Location[];
  created_at: string;
  updated_at: string;
}

export interface StockBalance {
  id: string;
  tenant_id: string;
  organization_id: string;
  product_id: string;
  warehouse_id: string;
  location_id?: string | null;
  quantity_on_hand: number;
  quantity_reserved: number;
  quantity_available: number;
  quantity_on_order: number;
  average_cost: number;
  total_value: number;
  version: number;
  created_at: string;
  updated_at: string;
  product_name?: string;
  product_sku?: string;
  warehouse_name?: string;
}

export type MovementType =
  | "RECEIPT"
  | "ISSUE"
  | "TRANSFER_OUT"
  | "TRANSFER_IN"
  | "ADJUSTMENT_IN"
  | "ADJUSTMENT_OUT"
  | "RETURN"
  | "SCRAP";

export interface StockMovement {
  id: string;
  tenant_id: string;
  organization_id: string;
  product_id: string;
  warehouse_id: string;
  location_id?: string | null;
  movement_type: MovementType;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  quantity_before: number;
  quantity_after: number;
  reference_type: "PURCHASE_ORDER" | "GOODS_RECEIPT" | "TRANSFER" | "ADJUSTMENT" | "MANUAL" | "SALES_ORDER";
  reference_id?: string | null;
  batch_number?: string | null;
  notes?: string | null;
  created_by_id?: string | null;
  created_at: string;
  product_name?: string;
  warehouse_name?: string;
}

export type TransferStatus = "DRAFT" | "IN_TRANSIT" | "COMPLETED" | "CANCELLED";

export interface StockTransferItem {
  id: string;
  tenant_id: string;
  transfer_id: string;
  product_id: string;
  requested_quantity: number;
  shipped_quantity: number;
  received_quantity: number;
  unit_cost: number;
  total_cost: number;
  source_location_id?: string | null;
  destination_location_id?: string | null;
  batch_number?: string | null;
  notes?: string | null;
  created_at: string;
  product_name?: string;
  product_sku?: string;
}

export interface StockTransfer {
  id: string;
  tenant_id: string;
  organization_id: string;
  transfer_number: string;
  source_warehouse_id: string;
  destination_warehouse_id: string;
  status: TransferStatus;
  requested_by_id?: string | null;
  approved_by_id?: string | null;
  shipped_by_id?: string | null;
  shipped_at?: string | null;
  received_by_id?: string | null;
  received_at?: string | null;
  tracking_number?: string | null;
  notes?: string | null;
  version: number;
  items: StockTransferItem[];
  created_at: string;
  updated_at: string;
}

export type AdjustmentStatus = "DRAFT" | "SUBMITTED" | "APPROVED" | "REJECTED" | "POSTED";

export interface StockAdjustmentItem {
  id: string;
  tenant_id: string;
  adjustment_id: string;
  product_id: string;
  location_id?: string | null;
  system_quantity: number;
  counted_quantity: number;
  variance_quantity: number;
  unit_cost: number;
  variance_value: number;
  reason?: string | null;
  created_at: string;
  product_name?: string;
  product_sku?: string;
}

export interface StockAdjustment {
  id: string;
  tenant_id: string;
  organization_id: string;
  adjustment_number: string;
  warehouse_id: string;
  reason: string;
  status: AdjustmentStatus;
  requested_by_id?: string | null;
  approved_by_id?: string | null;
  approved_at?: string | null;
  posted_at?: string | null;
  rejection_reason?: string | null;
  notes?: string | null;
  version: number;
  items: StockAdjustmentItem[];
  created_at: string;
  updated_at: string;
}

export type GoodsReceiptStatus = "DRAFT" | "POSTED" | "CANCELLED";

export interface GoodsReceiptItem {
  id: string;
  tenant_id: string;
  goods_receipt_id: string;
  po_item_id?: string | null;
  product_id: string;
  location_id?: string | null;
  quantity_received: number;
  quantity_rejected: number;
  unit_cost: number;
  total_cost: number;
  batch_number?: string | null;
  notes?: string | null;
  created_at: string;
  product_name?: string;
  product_sku?: string;
}

export interface GoodsReceipt {
  id: string;
  tenant_id: string;
  organization_id: string;
  grn_number: string;
  purchase_order_id?: string | null;
  supplier_id?: string | null;
  warehouse_id: string;
  status: GoodsReceiptStatus;
  received_by_id?: string | null;
  received_date: string;
  vendor_delivery_note?: string | null;
  carrier_tracking_number?: string | null;
  notes?: string | null;
  version: number;
  items: GoodsReceiptItem[];
  created_at: string;
  updated_at: string;
}
