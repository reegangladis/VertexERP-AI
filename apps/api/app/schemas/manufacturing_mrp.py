import uuid
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field


# --- BOM Schemas ---
class BOMItemBase(BaseModel):
    raw_material_id: uuid.UUID
    quantity: float = Field(default=1.0, gt=0)
    unit: str = Field(default="Pcs", max_length=50)
    scrap_percentage: float = Field(default=0.0, ge=0)
    sequence: int = Field(default=1, ge=1)


class BOMItemCreate(BOMItemBase):
    pass


class BOMItemResponse(BOMItemBase):
    id: uuid.UUID
    bom_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BOMBase(BaseModel):
    bom_code: str = Field(..., min_length=1, max_length=100)
    revision: str = Field(default="Rev A", max_length=50)
    description: str | None = Field(None, max_length=1000)
    status: str = Field(default="Active", max_length=50)


class BOMCreate(BOMBase):
    product_id: uuid.UUID
    version_id: uuid.UUID | None = None
    items: list[BOMItemCreate] = Field(..., min_length=1)


class BOMResponse(BOMBase):
    id: uuid.UUID
    product_id: uuid.UUID
    version_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime
    items: list[BOMItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Work Center & Machine Schemas ---
class WorkCenterBase(BaseModel):
    center_name: str = Field(..., min_length=1, max_length=255)
    center_code: str = Field(..., min_length=1, max_length=50)
    capacity: float = Field(default=100.0, gt=0)
    location: str | None = Field(None, max_length=255)
    status: str = Field(default="Active", max_length=50)


class WorkCenterCreate(WorkCenterBase):
    organization_id: uuid.UUID
    manager_uuid: uuid.UUID | None = None


class WorkCenterResponse(WorkCenterBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    manager_uuid: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MachineBase(BaseModel):
    machine_name: str = Field(..., min_length=1, max_length=255)
    machine_code: str = Field(..., min_length=1, max_length=50)
    manufacturer: str | None = Field(None, max_length=255)
    serial_number: str | None = Field(None, max_length=100)
    installation_date: date | None = None
    status: str = Field(default="Operational", max_length=50)


class MachineCreate(MachineBase):
    work_center_id: uuid.UUID


class MachineResponse(MachineBase):
    id: uuid.UUID
    work_center_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MachineMaintenanceBase(BaseModel):
    maintenance_type: str = Field(default="Preventive", max_length=50)
    scheduled_date: date
    completed_date: date | None = None
    cost: float = Field(default=0.0, ge=0)
    status: str = Field(default="Scheduled", max_length=50)


class MachineMaintenanceCreate(MachineMaintenanceBase):
    machine_id: uuid.UUID


class MachineMaintenanceResponse(MachineMaintenanceBase):
    id: uuid.UUID
    machine_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Production Order Schemas ---
class ProductionOrderBase(BaseModel):
    production_number: str = Field(..., min_length=1, max_length=100)
    planned_quantity: float = Field(..., gt=0)
    scheduled_start: date
    scheduled_end: date
    priority: str = Field(default="Medium", max_length=50)
    status: str = Field(default="Draft", max_length=50)


class ProductionOrderCreate(ProductionOrderBase):
    organization_id: uuid.UUID
    product_id: uuid.UUID


class ProductionOrderResponse(ProductionOrderBase):
    id: uuid.UUID
    organization_id: uuid.UUID
    product_id: uuid.UUID
    completed_quantity: float
    actual_start: date | None = None
    actual_end: date | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Quality Inspection Schemas ---
class QualityInspectionBase(BaseModel):
    inspection_type: str = Field(default="In-Process", max_length=50)
    inspection_date: date
    status: str = Field(default="Passed", max_length=50)


class QualityInspectionCreate(QualityInspectionBase):
    production_order_id: uuid.UUID
    inspector_id: uuid.UUID | None = None


class QualityInspectionResponse(QualityInspectionBase):
    id: uuid.UUID
    production_order_id: uuid.UUID
    inspector_id: uuid.UUID | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- MRP Schemas ---
class MRPRunCreate(BaseModel):
    organization_id: uuid.UUID
    planning_period: str = Field(..., min_length=1, max_length=100)


class MRPRecommendation(BaseModel):
    product_id: uuid.UUID
    product_name: str
    required_quantity: float
    current_stock: float
    shortage_quantity: float
    action_type: str  # Purchase Requisition, Production Order


class MRPRunResponse(BaseModel):
    id: uuid.UUID
    organization_id: uuid.UUID
    run_date: date
    planning_period: str
    status: str
    processed_items: int
    recommendations: list[MRPRecommendation] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Manufacturing Dashboard Summary ---
class ManufacturingDashboardSummary(BaseModel):
    active_production_orders: int
    machine_utilization_rate: float
    total_material_consumed: float
    production_efficiency_percentage: float
    total_production_cost: float
    quality_pass_rate_percentage: float
    mrp_recommendations_count: int
    maintenance_schedules_count: int
