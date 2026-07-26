import uuid
from datetime import date, datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class ManufacturingBaseModel(BaseModel):
    class Config:
        from_attributes = True


# --- Product Structure ---
class ProductFamilyCreate(ManufacturingBaseModel):
    name: str
    code: str
    description: Optional[str] = None

class ProductFamilyResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    code: str
    description: Optional[str] = None
    created_at: datetime


class ProductVersionCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    version_number: str = "1.0"
    revision_date: Optional[date] = None
    change_summary: Optional[str] = None
    engineering_change_note: Optional[str] = None

class ProductVersionResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    version_number: str
    revision_date: date
    is_active: bool
    change_summary: Optional[str] = None
    engineering_change_note: Optional[str] = None


# --- Bill of Materials (BOM) ---
class BOMItemCreate(ManufacturingBaseModel):
    component_product_id: uuid.UUID
    parent_item_id: Optional[uuid.UUID] = None
    quantity: float = 1.0
    unit_name: str = "PCS"
    scrap_factor_percent: float = 0.0
    unit_cost: float = 0.0
    is_alternative: bool = False
    notes: Optional[str] = None

class BOMItemResponse(ManufacturingBaseModel):
    id: uuid.UUID
    bom_id: uuid.UUID
    component_product_id: uuid.UUID
    parent_item_id: Optional[uuid.UUID] = None
    quantity: float
    unit_name: str
    scrap_factor_percent: float
    unit_cost: float
    extended_cost: float
    is_alternative: bool
    notes: Optional[str] = None


class BOMCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    code: str
    version: str = "1.0"
    base_quantity: float = 1.0
    notes: Optional[str] = None
    items: List[BOMItemCreate] = []

class BOMUpdate(ManufacturingBaseModel):
    code: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    base_quantity: Optional[float] = None
    notes: Optional[str] = None

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
    approved_by: Optional[uuid.UUID] = None
    approved_at: Optional[datetime] = None
    notes: Optional[str] = None
    predicted_yield_rate: Optional[float] = 98.5
    optimal_batch_size: Optional[float] = 100.0
    items: List[BOMItemResponse] = []
    created_at: datetime

class BOMCostRollupResponse(ManufacturingBaseModel):
    bom_id: uuid.UUID
    product_id: uuid.UUID
    material_cost: float
    operation_cost: float
    total_calculated_cost: float
    cost_breakdown: List[Dict[str, Any]]


# --- Routings & Operations ---
class RoutingOperationCreate(ManufacturingBaseModel):
    work_center_id: uuid.UUID
    sequence_number: int = 10
    operation_name: str
    description: Optional[str] = None
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
    description: Optional[str] = None
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
    operations: List[RoutingOperationCreate] = []

class RoutingUpdate(ManufacturingBaseModel):
    code: Optional[str] = None
    version: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None

class RoutingResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    code: str
    version: str
    name: str
    is_active: bool
    total_standard_time_mins: float
    operations: List[RoutingOperationResponse] = []
    created_at: datetime


# --- Work Centers & Machines ---
class WorkCenterCreate(ManufacturingBaseModel):
    code: str
    name: str
    production_line: Optional[str] = None
    category: str = "ASSEMBLY"
    capacity_per_day_hours: float = 16.0
    hourly_cost: float = 50.0
    efficiency_percent: float = 95.0
    shift_calendar: Optional[Dict[str, Any]] = None

class WorkCenterUpdate(ManufacturingBaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    production_line: Optional[str] = None
    category: Optional[str] = None
    capacity_per_day_hours: Optional[float] = None
    hourly_cost: Optional[float] = None
    efficiency_percent: Optional[float] = None
    status: Optional[str] = None

class WorkCenterResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    code: str
    name: str
    production_line: Optional[str] = None
    category: str
    capacity_per_day_hours: float
    hourly_cost: float
    efficiency_percent: float
    shift_calendar: Optional[Dict[str, Any]] = None
    status: str
    failure_risk_index: Optional[float] = 0.05
    created_at: datetime


class MachineCreate(ManufacturingBaseModel):
    work_center_id: uuid.UUID
    code: str
    name: str
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    hourly_cost: float = 75.0
    capacity_units_per_hour: float = 100.0

class MachineUpdate(ManufacturingBaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
    hourly_cost: Optional[float] = None
    capacity_units_per_hour: Optional[float] = None

class MachineResponse(ManufacturingBaseModel):
    id: uuid.UUID
    work_center_id: uuid.UUID
    code: str
    name: str
    model_number: Optional[str] = None
    serial_number: Optional[str] = None
    status: str
    hourly_cost: float
    capacity_units_per_hour: float
    health_score: Optional[float] = 98.0
    predicted_failure_date: Optional[date] = None
    sensor_telemetry_summary: Optional[Dict[str, Any]] = None
    created_at: datetime


# --- Production Orders ---
class ProductionOrderCreate(ManufacturingBaseModel):
    product_id: uuid.UUID
    bom_id: Optional[uuid.UUID] = None
    routing_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    order_number: str
    planned_quantity: float
    priority: str = "MEDIUM"
    planned_start_date: date
    planned_end_date: date
    notes: Optional[str] = None

class ProductionOrderUpdate(ManufacturingBaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    planned_quantity: Optional[float] = None
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    notes: Optional[str] = None

class ProductionOrderItemResponse(ManufacturingBaseModel):
    id: uuid.UUID
    production_order_id: uuid.UUID
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
    bom_id: Optional[uuid.UUID] = None
    routing_id: Optional[uuid.UUID] = None
    warehouse_id: Optional[uuid.UUID] = None
    planned_quantity: float
    completed_quantity: float
    scrap_quantity: float
    status: str
    priority: str
    planned_start_date: date
    planned_end_date: date
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    material_reservation_status: str
    notes: Optional[str] = None
    predicted_completion_delay_days: Optional[float] = 0.0
    items: List[ProductionOrderItemResponse] = []
    created_at: datetime


# --- Shop Floor Execution ---
class ProductionLogCreate(ManufacturingBaseModel):
    production_order_id: uuid.UUID
    work_center_id: Optional[uuid.UUID] = None
    machine_id: Optional[uuid.UUID] = None
    operator_name: Optional[str] = None
    quantity_produced: float = 0.0
    scrap_quantity: float = 0.0
    notes: Optional[str] = None

class ProductionLogResponse(ManufacturingBaseModel):
    id: uuid.UUID
    production_order_id: uuid.UUID
    work_center_id: Optional[uuid.UUID] = None
    machine_id: Optional[uuid.UUID] = None
    operator_name: Optional[str] = None
    quantity_produced: float
    scrap_quantity: float
    log_time: datetime
    notes: Optional[str] = None


class MaterialConsumptionCreate(ManufacturingBaseModel):
    production_order_id: uuid.UUID
    product_id: uuid.UUID
    reserved_quantity: float = 0.0
    consumed_quantity: float = 0.0
    scrap_quantity: float = 0.0
    unit_cost: float = 0.0
    batch_number: Optional[str] = None

class MaterialConsumptionResponse(ManufacturingBaseModel):
    id: uuid.UUID
    production_order_id: uuid.UUID
    product_id: uuid.UUID
    reserved_quantity: float
    consumed_quantity: float
    scrap_quantity: float
    unit_cost: float
    total_cost: float
    batch_number: Optional[str] = None


class MachineDowntimeCreate(ManufacturingBaseModel):
    machine_id: uuid.UUID
    work_center_id: Optional[uuid.UUID] = None
    production_order_id: Optional[uuid.UUID] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reason_category: str = "UNPLANNED_BREAKDOWN"
    comments: Optional[str] = None

class MachineDowntimeResponse(ManufacturingBaseModel):
    id: uuid.UUID
    machine_id: uuid.UUID
    work_center_id: Optional[uuid.UUID] = None
    production_order_id: Optional[uuid.UUID] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: float
    reason_category: str
    comments: Optional[str] = None


# --- Quality Management ---
class QualityResultCreate(ManufacturingBaseModel):
    parameter_name: str
    expected_value: str
    actual_value: str
    is_passed: bool = True
    corrective_action: Optional[str] = None

class QualityResultResponse(ManufacturingBaseModel):
    id: uuid.UUID
    inspection_id: uuid.UUID
    parameter_name: str
    expected_value: str
    actual_value: str
    is_passed: bool
    corrective_action: Optional[str] = None


class QualityInspectionCreate(ManufacturingBaseModel):
    inspection_number: str
    production_order_id: Optional[uuid.UUID] = None
    product_id: uuid.UUID
    lot_number: Optional[str] = None
    inspector_name: Optional[str] = None
    inspection_type: str = "IN_PROCESS"
    sample_size: int = 5
    notes: Optional[str] = None
    results: List[QualityResultCreate] = []

class QualityInspectionUpdate(ManufacturingBaseModel):
    status: Optional[str] = None
    decision: Optional[str] = None
    notes: Optional[str] = None

class QualityInspectionResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    inspection_number: str
    production_order_id: Optional[uuid.UUID] = None
    product_id: uuid.UUID
    lot_number: Optional[str] = None
    inspector_name: Optional[str] = None
    inspection_type: str
    status: str
    decision: str
    sample_size: int
    passed_count: int
    failed_count: int
    notes: Optional[str] = None
    results: List[QualityResultResponse] = []
    created_at: datetime


# --- Maintenance ---
class MaintenanceRequestCreate(ManufacturingBaseModel):
    ticket_number: str
    machine_id: uuid.UUID
    work_center_id: Optional[uuid.UUID] = None
    priority: str = "MEDIUM"
    issue_type: str = "CORRECTIVE"
    title: str
    description: Optional[str] = None
    reported_by: Optional[str] = None
    assigned_technician: Optional[str] = None

class MaintenanceRequestUpdate(ManufacturingBaseModel):
    priority: Optional[str] = None
    issue_type: Optional[str] = None
    status: Optional[str] = None
    assigned_technician: Optional[str] = None
    description: Optional[str] = None

class MaintenanceRequestResponse(ManufacturingBaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    ticket_number: str
    machine_id: uuid.UUID
    work_center_id: Optional[uuid.UUID] = None
    priority: str
    issue_type: str
    status: str
    title: str
    description: Optional[str] = None
    reported_by: Optional[str] = None
    assigned_technician: Optional[str] = None
    reported_at: datetime
    resolved_at: Optional[datetime] = None


class MaintenanceLogCreate(ManufacturingBaseModel):
    request_id: Optional[uuid.UUID] = None
    machine_id: uuid.UUID
    technician_name: str
    maintenance_date: Optional[date] = None
    duration_hours: float = 1.0
    work_done: str
    parts_replaced: Optional[str] = None
    total_cost: float = 0.0

class MaintenanceLogResponse(ManufacturingBaseModel):
    id: uuid.UUID
    request_id: Optional[uuid.UUID] = None
    machine_id: uuid.UUID
    technician_name: str
    maintenance_date: date
    duration_hours: float
    work_done: str
    parts_replaced: Optional[str] = None
    total_cost: float
    created_at: datetime


# --- MRP (Material Requirement Planning) ---
class MRPRunCreate(ManufacturingBaseModel):
    run_number: str
    parameters: Optional[Dict[str, Any]] = None

class ProcurementSuggestion(ManufacturingBaseModel):
    product_id: uuid.UUID
    product_name: str
    sku: str
    suggested_qty: float
    unit_name: str
    reorder_reason: str
    estimated_cost: float

class ProductionSuggestion(ManufacturingBaseModel):
    product_id: uuid.UUID
    product_name: str
    suggested_order_qty: float
    planned_start_date: date
    planned_end_date: date
    bom_code: str

class CapacityPlanItem(ManufacturingBaseModel):
    work_center_id: uuid.UUID
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
    parameters: Optional[Dict[str, Any]] = None
    procurement_suggestions: Optional[List[ProcurementSuggestion]] = None
    production_suggestions: Optional[List[ProductionSuggestion]] = None
    capacity_planning: Optional[List[CapacityPlanItem]] = None


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
