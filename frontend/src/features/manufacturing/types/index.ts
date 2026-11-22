export type WorkCenterType = "MACHINING" | "ASSEMBLY" | "PACKAGING" | "TESTING" | "FABRICATION" | "FINISHING";
export type WorkCenterStatus = "ACTIVE" | "MAINTENANCE" | "INACTIVE";
export type MachineStatus = "OPERATIONAL" | "MAINTENANCE" | "DOWN";

export interface Machine {
  id: string;
  tenant_id: string;
  organization_id: string;
  work_center_id: string;
  code: string;
  name: string;
  serial_number?: string | null;
  hourly_cost: string | number;
  status: MachineStatus;
  last_maintenance_date?: string | null;
  next_maintenance_date?: string | null;
  created_at: string;
  updated_at: string;
}

export interface WorkCenter {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  work_center_type: WorkCenterType;
  capacity_per_day_hours: string | number;
  cost_per_hour: string | number;
  overhead_cost_per_hour: string | number;
  location_id?: string | null;
  status: WorkCenterStatus;
  is_active: boolean;
  machines?: Machine[];
  created_at: string;
  updated_at: string;
}

export interface RoutingOperation {
  id: string;
  tenant_id: string;
  organization_id: string;
  routing_id: string;
  sequence: number;
  operation_name: string;
  work_center_id: string;
  machine_id?: string | null;
  setup_time_hours: string | number;
  run_time_per_unit_hours: string | number;
  description?: string | null;
  created_at: string;
  updated_at: string;
}

export interface Routing {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  product_id: string;
  description?: string | null;
  is_active: boolean;
  operations?: RoutingOperation[];
  created_at: string;
  updated_at: string;
}

export interface BOMComponent {
  id: string;
  tenant_id: string;
  organization_id: string;
  bom_version_id: string;
  component_product_id: string;
  quantity: string | number;
  uom_id: string;
  scrap_percentage: string | number;
  operation_sequence?: number | null;
  position: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface BOMVersion {
  id: string;
  tenant_id: string;
  organization_id: string;
  bom_id: string;
  version_number: number;
  revision_notes?: string | null;
  status: "DRAFT" | "ACTIVE" | "SUPERSEDED" | "ARCHIVED";
  effective_from_date?: string | null;
  effective_to_date?: string | null;
  components?: BOMComponent[];
  created_at: string;
  updated_at: string;
}

export interface BillOfMaterial {
  id: string;
  tenant_id: string;
  organization_id: string;
  code: string;
  name: string;
  product_id: string;
  routing_id?: string | null;
  quantity: string | number;
  uom_id: string;
  status: "DRAFT" | "ACTIVE" | "ARCHIVED";
  is_default: boolean;
  notes?: string | null;
  versions?: BOMVersion[];
  created_at: string;
  updated_at: string;
}

export type ProductionOrderStatus = "PLANNED" | "CONFIRMED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";
export type ProductionOrderPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";
export type WorkOrderStatus = "PENDING" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CANCELLED";

export interface WorkOrder {
  id: string;
  tenant_id: string;
  organization_id: string;
  production_order_id: string;
  sequence: number;
  operation_name: string;
  work_center_id: string;
  machine_id?: string | null;
  planned_duration_hours: string | number;
  actual_duration_hours: string | number;
  technician_id?: string | null;
  status: WorkOrderStatus;
  started_at?: string | null;
  completed_at?: string | null;
  hourly_rate: string | number;
  total_labor_cost: string | number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface MaterialConsumption {
  id: string;
  tenant_id: string;
  organization_id: string;
  production_order_id: string;
  work_order_id?: string | null;
  product_id: string;
  warehouse_id: string;
  location_id?: string | null;
  planned_quantity: string | number;
  consumed_quantity: string | number;
  unit_cost: string | number;
  total_cost: string | number;
  stock_movement_id?: string | null;
  batch_number?: string | null;
  consumed_at: string;
  consumed_by_id?: string | null;
  created_at: string;
}

export interface ProductionOutput {
  id: string;
  tenant_id: string;
  organization_id: string;
  production_order_id: string;
  product_id: string;
  target_warehouse_id: string;
  location_id?: string | null;
  produced_quantity: string | number;
  unit_manufacturing_cost: string | number;
  total_manufacturing_cost: string | number;
  stock_movement_id?: string | null;
  batch_number?: string | null;
  serial_number?: string | null;
  output_date: string;
  created_at: string;
}

export interface ProductionScrap {
  id: string;
  tenant_id: string;
  organization_id: string;
  production_order_id: string;
  work_order_id?: string | null;
  product_id: string;
  scrap_quantity: string | number;
  scrap_reason: string;
  unit_cost: string | number;
  total_scrap_cost: string | number;
  stock_movement_id?: string | null;
  recorded_at: string;
  recorded_by_id?: string | null;
  created_at: string;
}

export interface ProductionOrder {
  id: string;
  tenant_id: string;
  organization_id: string;
  order_number: string;
  product_id: string;
  bom_id: string;
  bom_version_id: string;
  routing_id?: string | null;
  source_sales_order_id?: string | null;
  planned_quantity: string | number;
  produced_quantity: string | number;
  rejected_quantity: string | number;
  scrap_quantity: string | number;
  target_warehouse_id: string;
  planned_start_date: string;
  planned_due_date: string;
  actual_start_date?: string | null;
  actual_end_date?: string | null;
  status: ProductionOrderStatus;
  priority: ProductionOrderPriority;
  unit_cost: string | number;
  total_cost: string | number;
  created_by_id?: string | null;
  notes?: string | null;
  work_orders?: WorkOrder[];
  consumptions?: MaterialConsumption[];
  outputs?: ProductionOutput[];
  scraps?: ProductionScrap[];
  created_at: string;
  updated_at: string;
}

export interface MRPPlannedOrder {
  id: string;
  tenant_id: string;
  organization_id: string;
  mrp_run_id: string;
  product_id: string;
  order_type: "MANUFACTURE" | "PURCHASE";
  gross_requirement: string | number;
  on_hand_stock: string | number;
  scheduled_receipts: string | number;
  net_requirement: string | number;
  planned_quantity: string | number;
  order_date: string;
  required_date: string;
  status: "PLANNED" | "CONVERTED" | "IGNORED";
  converted_doc_type?: string | null;
  converted_doc_id?: string | null;
  created_at: string;
}

export interface MRPRun {
  id: string;
  tenant_id: string;
  organization_id: string;
  run_number: string;
  planning_horizon_days: number;
  status: "RUNNING" | "COMPLETED" | "FAILED";
  run_date: string;
  total_items_planned: number;
  total_purchase_requests_generated: number;
  total_production_orders_generated: number;
  execution_log?: string | null;
  planned_orders?: MRPPlannedOrder[];
  created_at: string;
}

export interface QualityInspection {
  id: string;
  tenant_id: string;
  organization_id: string;
  inspection_number: string;
  production_order_id: string;
  work_order_id?: string | null;
  product_id: string;
  inspection_type: "RECEIVING" | "IN_PROCESS" | "FINAL_ASSEMBLY";
  inspected_quantity: string | number;
  passed_quantity: string | number;
  failed_quantity: string | number;
  result: "PENDING" | "PASSED" | "FAILED" | "CONDITIONALLY_PASSED";
  inspector_id?: string | null;
  inspection_date: string;
  defect_reason?: string | null;
  notes?: string | null;
  status: "COMPLETED" | "DRAFT";
  created_at: string;
  updated_at: string;
}
