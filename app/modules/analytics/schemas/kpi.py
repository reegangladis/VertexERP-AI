"""Pydantic schemas for KPI definitions, values, and calculations."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, computed_field


class KPIDefinitionBase(BaseModel):
    code: str = Field(..., max_length=64)
    name: str = Field(..., max_length=128)
    category: Literal["FINANCE", "SALES", "INVENTORY", "MANUFACTURING", "HR", "EXECUTIVE"] = (
        "EXECUTIVE"
    )
    description: str | None = None
    unit: Literal["CURRENCY", "PERCENTAGE", "COUNT", "RATIO", "DAYS", "HOURS"] = "COUNT"
    target_value: Decimal | None = None
    warning_threshold: Decimal | None = None
    critical_threshold: Decimal | None = None
    trend_direction: Literal["HIGHER_IS_BETTER", "LOWER_IS_BETTER"] = "HIGHER_IS_BETTER"
    calculation_method: Literal["REALTIME_SQL", "SNAPSHOT_ROLLUP"] = "REALTIME_SQL"
    required_permission: str | None = None
    is_active: bool = True


class KPIDefinitionCreate(KPIDefinitionBase):
    organization_id: uuid.UUID | None = None


class KPIDefinitionUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    target_value: Decimal | None = None
    warning_threshold: Decimal | None = None
    critical_threshold: Decimal | None = None
    trend_direction: Literal["HIGHER_IS_BETTER", "LOWER_IS_BETTER"] | None = None
    calculation_method: Literal["REALTIME_SQL", "SNAPSHOT_ROLLUP"] | None = None
    required_permission: str | None = None
    is_active: bool | None = None


class KPIDefinitionResponse(KPIDefinitionBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    organization_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricCardData(BaseModel):
    """Calculated dynamic KPI card payload with period comparisons and health status."""

    code: str
    name: str
    category: str
    unit: str
    current_value: Decimal
    previous_value: Decimal | None = None
    delta_value: Decimal | None = None
    delta_percentage: Decimal | None = None
    target_value: Decimal | None = None
    status: Literal["ON_TRACK", "WARNING", "CRITICAL", "NEUTRAL"] = "ON_TRACK"
    sparkline_points: list[Decimal] = Field(default_factory=list)
    formatted_value: str
    period_label: str

    @computed_field
    @property
    def kpi_code(self) -> str:
        """Compatibility field for frontend consumers expecting .kpi_code."""
        return self.code
