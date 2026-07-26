import { apiClient } from './apiClient';

export interface ManufacturingDashboardMetrics {
  total_boms: number;
  active_routings: number;
  work_centers_count: number;
  operational_machines_count: number;
  machines_breakdown_count: number;
  production_orders_planned: number;
  production_orders_in_progress: number;
  production_orders_completed: number;
  overall_equipment_efficiency_percent: number;
  quality_pass_rate_percent: number;
  pending_maintenance_tickets: number;
  mrp_runs_count: number;
}

export interface BOMItem {
  id?: string;
  bom_id?: string;
  component_product_id: string;
  parent_item_id?: string;
  quantity: number;
  unit_name: string;
  scrap_factor_percent: number;
  unit_cost: number;
  extended_cost?: number;
  is_alternative: boolean;
  notes?: string;
}

export interface BillOfMaterial {
  id: string;
  organization_id: string;
  product_id: string;
  code: string;
  version: string;
  status: string;
  is_active: boolean;
  base_quantity: number;
  total_cost: number;
  approved_by?: string;
  approved_at?: string;
  notes?: string;
  predicted_yield_rate?: number;
  optimal_batch_size?: number;
  items: BOMItem[];
  created_at: string;
}

export interface RoutingOperation {
  id?: string;
  routing_id?: string;
  work_center_id: string;
  sequence_number: number;
  operation_name: string;
  description?: string;
  setup_time_mins: number;
  machine_time_mins: number;
  labor_time_mins: number;
  standard_time_mins: number;
  hourly_rate: number;
}

export interface Routing {
  id: string;
  organization_id: string;
  product_id: string;
  code: string;
  version: string;
  name: string;
  is_active: boolean;
  total_standard_time_mins: number;
  operations: RoutingOperation[];
  created_at: string;
}

export interface WorkCenter {
  id: string;
  organization_id: string;
  code: string;
  name: string;
  production_line?: string;
  category: string;
  capacity_per_day_hours: number;
  hourly_cost: number;
  efficiency_percent: number;
  shift_calendar?: Record<string, any>;
  status: string;
  failure_risk_index?: number;
  created_at: string;
}

export interface Machine {
  id: string;
  work_center_id: string;
  code: string;
  name: string;
  model_number?: string;
  serial_number?: string;
  status: string;
  hourly_cost: number;
  capacity_units_per_hour: number;
  health_score?: number;
  predicted_failure_date?: string;
  sensor_telemetry_summary?: Record<string, any>;
  created_at: string;
}

export interface ProductionOrderItem {
  id: string;
  production_order_id: string;
  work_center_id: string;
  sequence_number: number;
  operation_name: string;
  status: string;
  planned_hours: number;
  actual_hours: number;
  completed_qty: number;
  scrap_qty: number;
}

export interface ProductionOrder {
  id: string;
  organization_id: string;
  order_number: string;
  product_id: string;
  bom_id?: string;
  routing_id?: string;
  warehouse_id?: string;
  planned_quantity: number;
  completed_quantity: number;
  scrap_quantity: number;
  status: string;
  priority: string;
  planned_start_date: string;
  planned_end_date: string;
  actual_start_date?: string;
  actual_end_date?: string;
  material_reservation_status: string;
  notes?: string;
  predicted_completion_delay_days?: number;
  items: ProductionOrderItem[];
  created_at: string;
}

export interface ProductionLog {
  id: string;
  production_order_id: string;
  work_center_id?: string;
  machine_id?: string;
  operator_name?: string;
  quantity_produced: number;
  scrap_quantity: number;
  log_time: string;
  notes?: string;
}

export interface QualityResult {
  id?: string;
  inspection_id?: string;
  parameter_name: string;
  expected_value: string;
  actual_value: string;
  is_passed: boolean;
  corrective_action?: string;
}

export interface QualityInspection {
  id: string;
  organization_id: string;
  inspection_number: string;
  production_order_id?: string;
  product_id: string;
  lot_number?: string;
  inspector_name?: string;
  inspection_type: string;
  status: string;
  decision: string;
  sample_size: number;
  passed_count: number;
  failed_count: number;
  notes?: string;
  results: QualityResult[];
  created_at: string;
}

export interface MaintenanceRequest {
  id: string;
  organization_id: string;
  ticket_number: string;
  machine_id: string;
  work_center_id?: string;
  priority: string;
  issue_type: string;
  status: string;
  title: string;
  description?: string;
  reported_by?: string;
  assigned_technician?: string;
  reported_at: string;
  resolved_at?: string;
}

export interface ProcurementSuggestion {
  product_id: string;
  product_name: string;
  sku: string;
  suggested_qty: number;
  unit_name: string;
  reorder_reason: string;
  estimated_cost: number;
}

export interface ProductionSuggestion {
  product_id: string;
  product_name: string;
  suggested_order_qty: number;
  planned_start_date: string;
  planned_end_date: string;
  bom_code: string;
}

export interface CapacityPlanItem {
  work_center_id: string;
  work_center_name: string;
  available_hours: number;
  required_hours: number;
  load_percentage: number;
}

export interface MRPRun {
  id: string;
  organization_id: string;
  run_number: string;
  run_date: string;
  status: string;
  total_items_processed: number;
  suggestions_count: number;
  parameters?: Record<string, any>;
  procurement_suggestions?: { items: ProcurementSuggestion[] };
  production_suggestions?: { items: ProductionSuggestion[] };
  capacity_planning?: { items: CapacityPlanItem[] };
}

export const manufacturingService = {
  getDashboardMetrics: async (): Promise<ManufacturingDashboardMetrics> => {
    const res = await apiClient.get<ManufacturingDashboardMetrics>('/manufacturing/dashboard');
    return res.data;
  },

  getBOMs: async (search?: string): Promise<BillOfMaterial[]> => {
    const res = await apiClient.get<BillOfMaterial[]>('/manufacturing/boms', { params: { search } });
    return res.data;
  },

  createBOM: async (data: Partial<BillOfMaterial>): Promise<BillOfMaterial> => {
    const res = await apiClient.post<BillOfMaterial>('/manufacturing/boms', data);
    return res.data;
  },

  approveBOM: async (id: string): Promise<BillOfMaterial> => {
    const res = await apiClient.post<BillOfMaterial>(`/manufacturing/boms/${id}/approve`);
    return res.data;
  },

  calculateCostRollup: async (id: string): Promise<any> => {
    const res = await apiClient.post<any>(`/manufacturing/boms/${id}/cost-rollup`);
    return res.data;
  },

  getRoutings: async (search?: string): Promise<Routing[]> => {
    const res = await apiClient.get<Routing[]>('/manufacturing/routings', { params: { search } });
    return res.data;
  },

  createRouting: async (data: Partial<Routing>): Promise<Routing> => {
    const res = await apiClient.post<Routing>('/manufacturing/routings', data);
    return res.data;
  },

  getWorkCenters: async (search?: string): Promise<WorkCenter[]> => {
    const res = await apiClient.get<WorkCenter[]>('/manufacturing/work-centers', { params: { search } });
    return res.data;
  },

  createWorkCenter: async (data: Partial<WorkCenter>): Promise<WorkCenter> => {
    const res = await apiClient.post<WorkCenter>('/manufacturing/work-centers', data);
    return res.data;
  },

  getMachines: async (work_center_id?: string): Promise<Machine[]> => {
    const res = await apiClient.get<Machine[]>('/manufacturing/machines', { params: { work_center_id } });
    return res.data;
  },

  createMachine: async (data: Partial<Machine>): Promise<Machine> => {
    const res = await apiClient.post<Machine>('/manufacturing/machines', data);
    return res.data;
  },

  getProductionOrders: async (status_filter?: string): Promise<ProductionOrder[]> => {
    const res = await apiClient.get<ProductionOrder[]>('/manufacturing/production-orders', { params: { status_filter } });
    return res.data;
  },

  createProductionOrder: async (data: Partial<ProductionOrder>): Promise<ProductionOrder> => {
    const res = await apiClient.post<ProductionOrder>('/manufacturing/production-orders', data);
    return res.data;
  },

  logShopFloorProgress: async (data: Partial<ProductionLog>): Promise<ProductionLog> => {
    const res = await apiClient.post<ProductionLog>('/manufacturing/shop-floor/logs', data);
    return res.data;
  },

  getQualityInspections: async (): Promise<QualityInspection[]> => {
    const res = await apiClient.get<QualityInspection[]>('/manufacturing/quality/inspections');
    return res.data;
  },

  createQualityInspection: async (data: Partial<QualityInspection>): Promise<QualityInspection> => {
    const res = await apiClient.post<QualityInspection>('/manufacturing/quality/inspections', data);
    return res.data;
  },

  getMaintenanceRequests: async (): Promise<MaintenanceRequest[]> => {
    const res = await apiClient.get<MaintenanceRequest[]>('/manufacturing/maintenance/requests');
    return res.data;
  },

  createMaintenanceRequest: async (data: Partial<MaintenanceRequest>): Promise<MaintenanceRequest> => {
    const res = await apiClient.post<MaintenanceRequest>('/manufacturing/maintenance/requests', data);
    return res.data;
  },

  getMRPRuns: async (): Promise<MRPRun[]> => {
    const res = await apiClient.get<MRPRun[]>('/manufacturing/mrp/runs');
    return res.data;
  },

  executeMRPRun: async (run_number: string): Promise<MRPRun> => {
    const res = await apiClient.post<MRPRun>('/manufacturing/mrp/runs', { run_number });
    return res.data;
  },
};
