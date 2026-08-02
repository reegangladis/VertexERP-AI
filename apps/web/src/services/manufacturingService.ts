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

export interface BOMCostRollupResponse {
  bom_id: string;
  product_id: string;
  material_cost: number;
  operation_cost: number;
  total_calculated_cost: number;
  cost_breakdown: Array<Record<string, any>>;
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

export interface MachineDowntime {
  id: string;
  machine_id: string;
  work_center_id?: string;
  production_order_id?: string;
  start_time: string;
  end_time?: string;
  duration_minutes: number;
  reason_category: string;
  comments?: string;
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

export interface MaterialReservationResponse {
  production_order_id: string;
  material_reservation_status: string;
  allocated_items: Array<Record<string, any>>;
  shortages: Array<Record<string, any>>;
}

export interface ProductionCostSummaryResponse {
  production_order_id: string;
  order_number: string;
  product_id: string;
  planned_quantity: number;
  completed_quantity: number;
  material_cost: number;
  labor_cost: number;
  machine_cost: number;
  overhead_cost: number;
  total_actual_cost: number;
  unit_actual_cost: number;
  estimated_total_cost: number;
  cost_variance: number;
  cost_variance_percent: number;
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

export interface MaintenanceLog {
  id?: string;
  request_id?: string;
  machine_id: string;
  technician_name: string;
  maintenance_date?: string;
  duration_hours: number;
  work_done: string;
  parts_replaced?: string;
  total_cost: number;
  created_at?: string;
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

  // --- BOM ---
  getBOMs: async (search?: string): Promise<BillOfMaterial[]> => {
    const res = await apiClient.get<BillOfMaterial[]>('/manufacturing/boms', { params: { search } });
    return res.data;
  },

  createBOM: async (data: Partial<BillOfMaterial>): Promise<BillOfMaterial> => {
    const res = await apiClient.post<BillOfMaterial>('/manufacturing/boms', data);
    return res.data;
  },

  getBOM: async (id: string): Promise<BillOfMaterial> => {
    const res = await apiClient.get<BillOfMaterial>(`/manufacturing/boms/${id}`);
    return res.data;
  },

  updateBOM: async (id: string, data: Partial<BillOfMaterial>): Promise<BillOfMaterial> => {
    const res = await apiClient.put<BillOfMaterial>(`/manufacturing/boms/${id}`, data);
    return res.data;
  },

  deleteBOM: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/boms/${id}`);
  },

  approveBOM: async (id: string): Promise<BillOfMaterial> => {
    const res = await apiClient.post<BillOfMaterial>(`/manufacturing/boms/${id}/approve`);
    return res.data;
  },

  calculateCostRollup: async (id: string): Promise<BOMCostRollupResponse> => {
    const res = await apiClient.post<BOMCostRollupResponse>(`/manufacturing/boms/${id}/cost-rollup`);
    return res.data;
  },

  // --- ROUTINGS ---
  getRoutings: async (search?: string): Promise<Routing[]> => {
    const res = await apiClient.get<Routing[]>('/manufacturing/routings', { params: { search } });
    return res.data;
  },

  createRouting: async (data: Partial<Routing>): Promise<Routing> => {
    const res = await apiClient.post<Routing>('/manufacturing/routings', data);
    return res.data;
  },

  getRouting: async (id: string): Promise<Routing> => {
    const res = await apiClient.get<Routing>(`/manufacturing/routings/${id}`);
    return res.data;
  },

  updateRouting: async (id: string, data: Partial<Routing>): Promise<Routing> => {
    const res = await apiClient.put<Routing>(`/manufacturing/routings/${id}`, data);
    return res.data;
  },

  deleteRouting: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/routings/${id}`);
  },

  // --- WORK CENTERS & MACHINES ---
  getWorkCenters: async (search?: string): Promise<WorkCenter[]> => {
    const res = await apiClient.get<WorkCenter[]>('/manufacturing/work-centers', { params: { search } });
    return res.data;
  },

  createWorkCenter: async (data: Partial<WorkCenter>): Promise<WorkCenter> => {
    const res = await apiClient.post<WorkCenter>('/manufacturing/work-centers', data);
    return res.data;
  },

  updateWorkCenter: async (id: string, data: Partial<WorkCenter>): Promise<WorkCenter> => {
    const res = await apiClient.put<WorkCenter>(`/manufacturing/work-centers/${id}`, data);
    return res.data;
  },

  deleteWorkCenter: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/work-centers/${id}`);
  },

  getMachines: async (work_center_id?: string): Promise<Machine[]> => {
    const res = await apiClient.get<Machine[]>('/manufacturing/machines', { params: { work_center_id } });
    return res.data;
  },

  createMachine: async (data: Partial<Machine>): Promise<Machine> => {
    const res = await apiClient.post<Machine>('/manufacturing/machines', data);
    return res.data;
  },

  updateMachine: async (id: string, data: Partial<Machine>): Promise<Machine> => {
    const res = await apiClient.put<Machine>(`/manufacturing/machines/${id}`, data);
    return res.data;
  },

  deleteMachine: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/machines/${id}`);
  },

  logMachineDowntime: async (data: Partial<MachineDowntime>): Promise<MachineDowntime> => {
    const res = await apiClient.post<MachineDowntime>('/manufacturing/machines/downtime', data);
    return res.data;
  },

  getMachineDowntimes: async (machine_id: string): Promise<MachineDowntime[]> => {
    const res = await apiClient.get<MachineDowntime[]>(`/manufacturing/machines/${machine_id}/downtimes`);
    return res.data;
  },

  // --- PRODUCTION ORDERS ---
  getProductionOrders: async (status_filter?: string): Promise<ProductionOrder[]> => {
    const res = await apiClient.get<ProductionOrder[]>('/manufacturing/production-orders', { params: { status_filter } });
    return res.data;
  },

  createProductionOrder: async (data: Partial<ProductionOrder>): Promise<ProductionOrder> => {
    const res = await apiClient.post<ProductionOrder>('/manufacturing/production-orders', data);
    return res.data;
  },

  getProductionOrder: async (id: string): Promise<ProductionOrder> => {
    const res = await apiClient.get<ProductionOrder>(`/manufacturing/production-orders/${id}`);
    return res.data;
  },

  updateProductionOrder: async (id: string, data: Partial<ProductionOrder>): Promise<ProductionOrder> => {
    const res = await apiClient.put<ProductionOrder>(`/manufacturing/production-orders/${id}`, data);
    return res.data;
  },

  deleteProductionOrder: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/production-orders/${id}`);
  },

  reserveMaterials: async (id: string): Promise<MaterialReservationResponse> => {
    const res = await apiClient.post<MaterialReservationResponse>(`/manufacturing/production-orders/${id}/reserve-materials`);
    return res.data;
  },

  getCostSummary: async (id: string): Promise<ProductionCostSummaryResponse> => {
    const res = await apiClient.get<ProductionCostSummaryResponse>(`/manufacturing/production-orders/${id}/cost-summary`);
    return res.data;
  },

  updateWorkOrderItem: async (itemId: string, data: Partial<ProductionOrderItem>): Promise<ProductionOrderItem> => {
    const res = await apiClient.put<ProductionOrderItem>(`/manufacturing/production-orders/items/${itemId}`, data);
    return res.data;
  },

  // --- SHOP FLOOR ---
  logShopFloorProgress: async (data: Partial<ProductionLog>): Promise<ProductionLog> => {
    const res = await apiClient.post<ProductionLog>('/manufacturing/shop-floor/logs', data);
    return res.data;
  },

  // --- QUALITY CONTROL ---
  getQualityInspections: async (): Promise<QualityInspection[]> => {
    const res = await apiClient.get<QualityInspection[]>('/manufacturing/quality/inspections');
    return res.data;
  },

  createQualityInspection: async (data: Partial<QualityInspection>): Promise<QualityInspection> => {
    const res = await apiClient.post<QualityInspection>('/manufacturing/quality/inspections', data);
    return res.data;
  },

  updateQualityInspection: async (id: string, data: Partial<QualityInspection>): Promise<QualityInspection> => {
    const res = await apiClient.put<QualityInspection>(`/manufacturing/quality/inspections/${id}`, data);
    return res.data;
  },

  deleteQualityInspection: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/quality/inspections/${id}`);
  },

  // --- MAINTENANCE ---
  getMaintenanceRequests: async (): Promise<MaintenanceRequest[]> => {
    const res = await apiClient.get<MaintenanceRequest[]>('/manufacturing/maintenance/requests');
    return res.data;
  },

  createMaintenanceRequest: async (data: Partial<MaintenanceRequest>): Promise<MaintenanceRequest> => {
    const res = await apiClient.post<MaintenanceRequest>('/manufacturing/maintenance/requests', data);
    return res.data;
  },

  updateMaintenanceRequest: async (id: string, data: Partial<MaintenanceRequest>): Promise<MaintenanceRequest> => {
    const res = await apiClient.put<MaintenanceRequest>(`/manufacturing/maintenance/requests/${id}`, data);
    return res.data;
  },

  deleteMaintenanceRequest: async (id: string): Promise<void> => {
    await apiClient.delete(`/manufacturing/maintenance/requests/${id}`);
  },

  logMaintenanceWork: async (data: Partial<MaintenanceLog>): Promise<MaintenanceLog> => {
    const res = await apiClient.post<MaintenanceLog>('/manufacturing/maintenance/logs', data);
    return res.data;
  },

  // --- MRP RUNS ---
  getMRPRuns: async (): Promise<MRPRun[]> => {
    const res = await apiClient.get<MRPRun[]>('/manufacturing/mrp/runs');
    return res.data;
  },

  executeMRPRun: async (run_number: string): Promise<MRPRun> => {
    const res = await apiClient.post<MRPRun>('/manufacturing/mrp/runs', { run_number });
    return res.data;
  },
};
