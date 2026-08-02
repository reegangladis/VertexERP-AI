import uuid
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


class ManufacturingBaseModel(BaseModel):
    class Config:
        from_attributes = True


# --- Product Structure ---
class ProductFamilyCreate(ManufacturingBaseModel):
    name: str
    code: str
    description: str | None = None


class ProductFamilyResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: str | None = None
    created_at: datetime


class ProductVersionCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    version_number: str = "1.0"
    revision_date: date | None = None
    change_summary: str | None = None
    engineering_change_note: str | None = None


class ProductVersionResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    version_number: str
    revision_date: date
    is_active: bool
    change_summary: str | None = None
    engineering_change_note: str | None = None


# --- Bill of Materials (BOM) ---
class BOMItemCreate(ManufacturingBaseModel):
    component_product_id: uuid.UUID
    parent_item_id: uuid.UUID | None = None
    quantity: float = 1.0
    unit_name: str = "PCS"
    scrap_factor_percent: float = 0.0
    unit_cost: float = 0.0
    is_alternative: bool = False
    notes: str | None = None


class BOMItemUpdate(ManufacturingBaseModel):
    quantity: float | None = None
    unit_name: str | None = None
    scrap_factor_percent: float | None = None
    unit_cost: float | None = None
    is_alternative: bool | None = None
    notes: str | None = None


class BOMItemResponse(ManufacturingBaseModel):
    id: uuid.UUID
    bom_id: uuid.UUID
    component_product_id: uuid.UUID
    parent_item_id: uuid.UUID | None = None
    quantity: float
    unit_name: str
    scrap_factor_percent: float
    unit_cost: float
    extended_cost: float
    is_alternative: bool
    notes: str | None = None


class BOMCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    code: str
    version: str = "1.0"
    base_quantity: float = 1.0
    notes: str | None = None
    items: list[BOMItemCreate] = []


class BOMUpdate(ManufacturingBaseModel):
    code: str | None = None
    version: str | None = None
    status: str | None = None
    base_quantity: float | None = None
    notes: str | None = None
    is_active: bool | None = None
    items: list[BOMItemCreate] | None = None


class BOMResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    code: str
    version: str
    status: str
    is_active: bool
    base_quantity: float
    total_cost: float
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
    notes: str | None = None
    predicted_yield_rate: float | None = 98.5
    optimal_batch_size: float | None = 100.0
    items: list[BOMItemResponse] = []
    created_at: datetime


class BOMCostRollupResponse(ManufacturingBaseModel):
    bom_id: uuid.UUID
    product_id: uuid.UUID
    material_cost: float
    operation_cost: float
    total_calculated_cost: float
    cost_breakdown: list[dict[str, Any]]


# --- Routings & Operations ---
class RoutingOperationCreate(ManufacturingBaseModel):
    work_center_id: uuid.UUID
    sequence_number: int = 10
    operation_name: str
    description: str | None = None
    setup_time_mins: float = 0.0
    machine_time_mins: float = 0.0
    labor_time_mins: float = 0.0
    standard_time_mins: float = 0.0
    hourly_rate: float = 0.0


class RoutingOperationResponse(ManufacturingBaseModel):
    id: uuid.UUID
    routing_id: uuid.UUID
    work_center_id: uuid.UUID
    sequence_number: int
    operation_name: str
    description: str | None = None
    setup_time_mins: float
    machine_time_mins: float
    labor_time_mins: float
    standard_time_mins: float
    hourly_rate: float


class RoutingCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    code: str
    version: str = "1.0"
    name: str
    operations: list[RoutingOperationCreate] = []


class RoutingUpdate(ManufacturingBaseModel):
    code: str | None = None
    version: str | None = None
    name: str | None = None
    is_active: bool | None = None
    operations: list[RoutingOperationCreate] | None = None


class RoutingResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    code: str
    version: str
    name: str
    is_active: bool
    total_standard_time_mins: float
    operations: list[RoutingOperationResponse] = []
    created_at: datetime


# --- Work Centers & Machines ---
class WorkCenterCreate(ManufacturingBaseModel):
    code: str
    name: str
    production_line: str | None = None
    category: str = "ASSEMBLY"
    capacity_per_day_hours: float = 16.0
    hourly_cost: float = 50.0
    efficiency_percent: float = 95.0
    shift_calendar: dict[str, Any] | None = None


class WorkCenterUpdate(ManufacturingBaseModel):
    code: str | None = None
    name: str | None = None
    production_line: str | None = None
    category: str | None = None
    capacity_per_day_hours: float | None = None
    hourly_cost: float | None = None
    efficiency_percent: float | None = None
    status: str | None = None


class WorkCenterResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    production_line: str | None = None
    category: str
    capacity_per_day_hours: float
    hourly_cost: float
    efficiency_percent: float
    shift_calendar: dict[str, Any] | None = None
    status: str
    failure_risk_index: float | None = 0.05
    created_at: datetime


class MachineCreate(ManufacturingBaseModel):
    work_center_id: uuid.UUID
    code: str
    name: str
    model_number: str | None = None
    serial_number: str | None = None
    hourly_cost: float = 75.0
    capacity_units_per_hour: float = 100.0


class MachineUpdate(ManufacturingBaseModel):
    code: str | None = None
    name: str | None = None
    status: str | None = None
    hourly_cost: float | None = None
    capacity_units_per_hour: float | None = None
    model_number: str | None = None
    serial_number: str | None = None


class MachineResponse(ManufacturingBaseModel):
    id: uuid.UUID
    work_center_id: uuid.UUID
    code: str
    name: str
    model_number: str | None = None
    serial_number: str | None = None
    status: str
    hourly_cost: float
    capacity_units_per_hour: float
    health_score: float | None = 98.0
    predicted_failure_date: date | None = None
    sensor_telemetry_summary: dict[str, Any] | None = None
    created_at: datetime


# --- Production Orders ---
class ProductionOrderCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    bom_id: uuid.UUID | None = None
    routing_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None
    order_number: str
    planned_quantity: float
    priority: str = "MEDIUM"
    planned_start_date: date
    planned_end_date: date
    notes: str | None = None


class ProductionOrderUpdate(ManufacturingBaseModel):
    status: str | None = None
    priority: str | None = None
    planned_quantity: float | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    notes: str | None = None


class ProductionOrderItemUpdate(ManufacturingBaseModel):
    status: str | None = None
    planned_hours: float | None = None
    actual_hours: float | None = None
    completed_qty: float | None = None
    scrap_qty: float | None = None


class ProductionOrderItemResponse(ManufacturingBaseModel):
    id: uuid.UUID
    production_order_id: uuid.UUID
    routing_operation_id: uuid.UUID | None = None
    work_center_id: uuid.UUID
    sequence_number: int
    operation_name: str
    status: str
    planned_hours: float
    actual_hours: float
    completed_qty: float
    scrap_qty: float


class ProductionOrderResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    order_number: str
    product_id: uuid.UUID
    bom_id: uuid.UUID | None = None
    routing_id: uuid.UUID | None = None
    warehouse_id: uuid.UUID | None = None
    planned_quantity: float
    completed_quantity: float
    scrap_quantity: float
    status: str
    priority: str
    planned_start_date: date
    planned_end_date: date
    actual_start_date: date | None = None
    actual_end_date: date | None = None
    material_reservation_status: str
    notes: str | None = None
    predicted_completion_delay_days: float | None = 0.0
    items: list[ProductionOrderItemResponse] = []
    created_at: datetime


class MaterialReservationResponse(ManufacturingBaseModel):
    production_order_id: uuid.UUID
    material_reservation_status: str
    allocated_items: list[dict[str, Any]]
    shortages: list[dict[str, Any]]


# --- Production Costing Summary ---
class ProductionCostSummaryResponse(ManufacturingBaseModel):
    production_order_id: uuid.UUID
    order_number: str
    product_id: uuid.UUID
    planned_quantity: float
    completed_quantity: float
    material_cost: float
    labor_cost: float
    machine_cost: float
    overhead_cost: float
    total_actual_cost: float
    unit_actual_cost: float
    estimated_total_cost: float
    cost_variance: float
    cost_variance_percent: float


# --- Shop Floor Execution ---
class ProductionLogCreate(ManufacturingBaseModel):
    production_order_id: uuid.UUID
    work_center_id: uuid.UUID | None = None
    machine_id: uuid.UUID | None = None
    operator_name: str | None = None
    quantity_produced: float = 0.0
    scrap_quantity: float = 0.0
    notes: str | None = None


class ProductionLogResponse(ManufacturingBaseModel):
    id: uuid.UUID
    production_order_id: uuid.UUID
    work_center_id: uuid.UUID | None = None
    machine_id: uuid.UUID | None = None
    operator_name: str | None = None
    quantity_produced: float
    scrap_quantity: float
    log_time: datetime
    notes: str | None = None


class MaterialConsumptionCreate(ManufacturingBaseModel):
    production_order_id: uuid.UUID
    product_id: uuid.UUID
    reserved_quantity: float = 0.0
    consumed_quantity: float = 0.0
    scrap_quantity: float = 0.0
    unit_cost: float = 0.0
    batch_number: str | None = None


class MaterialConsumptionResponse(ManufacturingBaseModel):
    id: uuid.UUID
    production_order_id: uuid.UUID
    product_id: uuid.UUID
    reserved_quantity: float
    consumed_quantity: float
    scrap_quantity: float
    unit_cost: float
    total_cost: float
    batch_number: str | None = None


class MachineDowntimeCreate(ManufacturingBaseModel):
    machine_id: uuid.UUID
    work_center_id: uuid.UUID | None = None
    production_order_id: uuid.UUID | None = None
    start_time: datetime
    end_time: datetime | None = None
    reason_category: str = "UNPLANNED_BREAKDOWN"
    comments: str | None = None


class MachineDowntimeResponse(ManufacturingBaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    work_center_id: uuid.UUID | None = None
    production_order_id: uuid.UUID | None = None
    start_time: datetime
    end_time: datetime | None = None
    duration_minutes: float
    reason_category: str
    comments: str | None = None


# --- Quality Management ---
class QualityResultCreate(ManufacturingBaseModel):
    parameter_name: str
    expected_value: str
    actual_value: str
    is_passed: bool = True
    corrective_action: str | None = None


class QualityResultResponse(ManufacturingBaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    parameter_name: str
    expected_value: str
    actual_value: str
    is_passed: bool
    corrective_action: str | None = None


class QualityInspectionCreate(ManufacturingBaseModel):
    inspection_number: str
    production_order_id: uuid.UUID | None = None
    product_id: uuid.UUID
    lot_number: str | None = None
    inspector_name: str | None = None
    inspection_type: str = "IN_PROCESS"
    sample_size: int = 5
    notes: str | None = None
    results: list[QualityResultCreate] = []


class QualityInspectionUpdate(ManufacturingBaseModel):
    status: str | None = None
    decision: str | None = None
    notes: str | None = None
    sample_size: int | None = None
    inspector_name: str | None = None


class QualityInspectionResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    inspection_number: str
    production_order_id: uuid.UUID | None = None
    product_id: uuid.UUID
    lot_number: str | None = None
    inspector_name: str | None = None
    inspection_type: str
    status: str
    decision: str
    sample_size: int
    passed_count: int
    failed_count: int
    notes: str | None = None
    results: list[QualityResultResponse] = []
    created_at: datetime


# --- Maintenance ---
class MaintenanceRequestCreate(ManufacturingBaseModel):
    ticket_number: str
    machine_id: uuid.UUID
    work_center_id: uuid.UUID | None = None
    priority: str = "MEDIUM"
    issue_type: str = "CORRECTIVE"
    title: str
    description: str | None = None
    reported_by: str | None = None
    assigned_technician: str | None = None


class MaintenanceRequestUpdate(ManufacturingBaseModel):
    priority: str | None = None
    issue_type: str | None = None
    status: str | None = None
    assigned_technician: str | None = None
    description: str | None = None
    resolved_at: datetime | None = None


class MaintenanceRequestResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    ticket_number: str
    machine_id: uuid.UUID
    work_center_id: uuid.UUID | None = None
    priority: str
    issue_type: str
    status: str
    title: str
    description: str | None = None
    reported_by: str | None = None
    assigned_technician: str | None = None
    reported_at: datetime
    resolved_at: datetime | None = None


class MaintenanceLogCreate(ManufacturingBaseModel):
    request_id: uuid.UUID | None = None
    machine_id: uuid.UUID
    technician_name: str
    maintenance_date: date | None = None
    duration_hours: float = 1.0
    work_done: str
    parts_replaced: str | None = None
    total_cost: float = 0.0


class MaintenanceLogResponse(ManufacturingBaseModel):
    id: uuid.UUID
    request_id: uuid.UUID | None = None
    machine_id: uuid.UUID
    technician_name: str
    maintenance_date: date
    duration_hours: float
    work_done: str
    parts_replaced: str | None = None
    total_cost: float
    created_at: datetime


# --- MRP (Material Requirement Planning) ---
class MRPRunCreate(ManufacturingBaseModel):
    run_number: str
    parameters: dict[str, Any] | None = None


class ProcurementSuggestion(ManufacturingBaseModel):
    product_id: str
    product_name: str
    sku: str
    suggested_qty: float
    unit_name: str
    reorder_reason: str
    estimated_cost: float


class ProductionSuggestion(ManufacturingBaseModel):
    product_id: str
    product_name: str
    suggested_order_qty: float
    planned_start_date: str
    planned_end_date: str
    bom_code: str


class CapacityPlanItem(ManufacturingBaseModel):
    work_center_id: str
    work_center_name: str
    available_hours: float
    required_hours: float
    load_percentage: float


class MRPRunResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    run_number: str
    run_date: datetime
    status: str
    total_items_processed: int
    suggestions_count: int
    parameters: dict[str, Any] | None = None
    procurement_suggestions: dict[str, Any] | None = None
    production_suggestions: dict[str, Any] | None = None
    capacity_planning: dict[str, Any] | None = None
    created_at: datetime


# --- Manufacturing Dashboard KPIs ---
class ManufacturingDashboardMetrics(ManufacturingBaseModel):
    total_boms: int
    active_routings: int
    work_centers_count: int
    operational_machines_count: int
    machines_breakdown_count: int
    production_orders_planned: int
    production_orders_in_progress: int
    production_orders_completed: int
    overall_equipment_efficiency_percent: float
    quality_pass_rate_percent: float
    pending_maintenance_tickets: int
    mrp_runs_count: int
